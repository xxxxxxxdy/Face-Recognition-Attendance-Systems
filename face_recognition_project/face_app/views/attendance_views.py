from cgitb import reset
import datetime
from django.http import JsonResponse
from ..models import AttendanceSession, StudentUser, Course, StudentAttendance, CourseStudentTeacher, ClassGroup, Teacher, LeaveRequest
from ..utils import success_response, error_response
from ..decorators import custom_auth_required, get_token_data, get_token_from_request
from datetime import datetime
from rest_framework.decorators import api_view
from django.db.models import Q

# 考勤查询接口
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin'])
def attendance_query_api(request):
    all_attendance_data = []
    try:
        token_data = get_token_from_request(request)
        user_type = token_data.get('user_type')
        user_id = token_data.get('user_id')
        if user_type == 'admin':
            attendances = AttendanceSession.objects.all()
        elif user_type == 'teacher':
            course_ids = CourseStudentTeacher.objects.filter(teacher=user_id).values_list('course_id', flat=True)
            attendances = AttendanceSession.objects.filter(course__in=course_ids)
        else:
            return error_response(message="无效的用户类型", code=400)

        for session in attendances:
            participant_count = StudentUser.objects.filter(class_id=session.class_group_id).count()
            # 当 end_time 为 None 时，避免与 datetime 比较导致异常；此时沿用数据库中的 is_active
            if session.end_time is not None:
                is_active_val = session.end_time >= datetime.now()
            else:
                is_active_val = session.is_active

            response_data = {
                'id': session.id,
                'session_name': session.session_name,
                'course_name': session.course.course_name if session.course else None,
                'class_id': session.class_group.class_id if session.class_group else None,
                'class_name': session.class_group.class_name if session.class_group else None,
                'participant_count': participant_count,
                'description': session.class_group.description if session.class_group else None,
                'start_time': session.start_time.strftime('%Y-%m-%d %H:%M:%S') if session.start_time else None,
                'end_time': session.end_time.strftime('%Y-%m-%d %H:%M:%S') if session.end_time else None,
                'is_active': is_active_val,
            }
            all_attendance_data.append(response_data)
        return success_response(data=all_attendance_data, message="考勤信息查询成功")
    except Exception as e:
        return error_response(message=f"查询失败: {str(e)}", code=500)


# 考勤新增接口（创建考勤会话）
@api_view(['POST'])
@custom_auth_required(roles=['teacher','admin'])
def attendance_add_api(request):
    try:
        user_id, user_type = get_token_data(request)
        class_id = request.data.get('class_id')
        course_id = request.data.get('course_id')
        end_time_str = request.data.get('end_time')
        session_name = request.data.get('session_name')
        
        if not all([class_id, course_id, session_name]):
            return error_response(message='class_id、course_id、session_name为必填', code=400)
        
        class_group = ClassGroup.objects.filter(class_id=class_id).first()
        if not class_group:
            return error_response(message='班级不存在', code=400)
        
        # 兼容前端传入的course_id可能是CourseStudentTeacher.id的情况
        course = Course.objects.filter(course_id=course_id).first()
        cst_via_id = None
        if not course:
            cst_via_id = CourseStudentTeacher.objects.filter(id=course_id, class_group=class_group).first()
            if cst_via_id:
                course = cst_via_id.course
            else:
                return error_response(message='课程不存在', code=400)
        
        # 解析结束时间（允许为空）
        end_time = None
        if end_time_str:
            try:
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
            except Exception:
                return error_response(message='end_time格式应为YYYY-MM-DD HH:MM:SS', code=400)
        
        # 根据用户类型确定可操作权限与教师归属
        if user_type == 'teacher':
            teacher = Teacher.objects.filter(user_id=user_id).first()
            if not teacher:
                return error_response(message='教师不存在', code=404)
            
            has_relation = CourseStudentTeacher.objects.filter(
                course=course,
                class_group=class_group,
                teacher=teacher
            ).exists()
            if not has_relation:
                return error_response(message='无权为该班级或课程新增考勤会话', code=403)
        elif user_type == 'admin':
            # 如果通过cst_via_id解析到课程，则直接使用该记录的教师；否则查找该课程-班级对应的教师
            if cst_via_id and cst_via_id.teacher:
                teacher = cst_via_id.teacher
            else:
                cst = CourseStudentTeacher.objects.filter(course=course, class_group=class_group).first()
                if not cst or not cst.teacher:
                    return error_response(message='该班级课程未分配教师，无法创建考勤会话', code=400)
                teacher = cst.teacher
        else:
            return error_response(message='无效的用户类型', code=400)
        
        # 前置条件：检查是否存在未完成的考勤会话（end_time为空或未到期）
        has_unfinished = AttendanceSession.objects.filter(
            course=course,
            class_group=class_group
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=datetime.now())
        ).exists()
        if has_unfinished:
            return error_response(message='该课程班级存在未完成的考勤会话，禁止新增', code=400)
        
        session = AttendanceSession.objects.create(
            session_name=session_name,
            course=course,
            class_group=class_group,
            teacher=teacher,
            start_time=None,
            end_time=end_time,
            is_active=False
        )
        
        return success_response(data={'id': session.id}, message='考勤会话新增成功')
    except Exception as e:
        return error_response(message=f'考勤新增失败: {str(e)}', code=500)


# 学生查询自己活跃考勤会话接口
@api_view(['GET'])
@custom_auth_required(roles=['student'])
def student_active_attendance_sessions_api(request):
    try:
        token_data = get_token_from_request(request)
        user_type = token_data.get('user_type')
        user_id = token_data.get('user_id')

        if user_type != 'student':
            return error_response(message="只有学生可以查询考勤会话", code=403)

        student = StudentUser.objects.filter(student_users_id=user_id).first()
        # 如果学生不存在或未分配班级，返回空列表
        if not student or not student.class_id:
            return success_response(data=[], message="活跃考勤会话查询成功")

        now = datetime.now()
        # 仅根据时间窗口与班级过滤：正在考勤（未到期或无结束时间），不再强依赖 is_active
        active_sessions = (
            AttendanceSession.objects
            .filter(class_group_id=student.class_id)
            .filter(Q(end_time__isnull=True) | Q(end_time__gte=now))
        )
        
        session_data = []
        for session in active_sessions:
            is_closed_by_time = bool(session.end_time is not None and session.end_time < now)
            # 增加：是否已签到（当前学生在该会话是否已有签到记录）
            signed_in = StudentAttendance.objects.filter(
                student_users_id=student,
                attendance_session_id=session,
                check_in_time__isnull=False
            ).exists()

            session_data.append({
                'session_id': session.id,
                'session_name': session.session_name,
                'course_name': session.course.course_name if session.course else None,
                'class_name': session.class_group.class_name if session.class_group else None,
                'teacher_name': session.teacher.username if session.teacher else None,
                'participant_count': StudentUser.objects.filter(class_id=session.class_group_id).count(),
                'start_time': session.start_time.strftime('%Y-%m-%d %H:%M:%S') if session.start_time else None,
                'end_time': session.end_time.strftime('%Y-%m-%d %H:%M:%S') if session.end_time else None,
                'signed_in': signed_in,               # 是否已签到
                'is_active': session.is_active        # 新增字段：考勤是否开启
            })

        return success_response(data=session_data, message="活跃考勤会话查询成功")
    except Exception as e:
        return error_response(message=f"查询失败: {str(e)}", code=500)


# 考勤修改接口
@api_view(['PUT'])
@custom_auth_required(roles=['teacher','admin'])
def attendance_update_api(request):
    try:
        user_id, user_type = get_token_data(request)
        session_id = request.data.get('id')
        is_active = request.data.get('is_active')
        end_time_str = request.data.get('end_time')

        if not session_id:
            return error_response(message='缺少会话ID', code=400)

        session = AttendanceSession.objects.filter(id=session_id).first()
        if not session:
            return error_response(message='会话不存在', code=404)

        # 权限：教师只能操作自己创建或负责的会话；管理员不限
        if user_type == 'teacher':
            teacher = Teacher.objects.filter(user_id=user_id).first()
            if not teacher or session.teacher_id != teacher.user_id:
                return error_response(message='无权操作该会话', code=403)

        # 统一处理 is_active 为布尔
        if is_active is not None:
            is_active = True if is_active in [True, 'true', 'True', 1, '1'] else False

        if end_time_str is not None:
            if end_time_str == '':
                if is_active is False:
                    session.end_time = datetime.now()
                else:
                    session.end_time = None
            else:
                try:
                    session.end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
                except Exception:
                    return error_response(message='end_time格式应为YYYY-MM-DD HH:MM:SS', code=400)

        was_active = session.is_active
        if is_active is not None:
            session.is_active = is_active

        # 首次从关闭切换到开启时写入开始时间，之后保持不变
        if is_active is True and not was_active and session.start_time is None:
            session.start_time = datetime.now()

        session.save()
        return success_response(message='会话更新成功')
    except Exception as e:
        return error_response(message=f'会话更新失败: {str(e)}', code=500)


@api_view(['DELETE'])
@custom_auth_required(roles=['teacher','admin'])
def attendance_del_api(request):
    try:
        user_id, user_type = get_token_data(request)
        session_id = request.data.get('id')
        if not session_id:
            return error_response(message='缺少会话ID', code=400)

        session = AttendanceSession.objects.filter(id=session_id).first()
        if not session:
            return error_response(message='会话不存在', code=404)

        if user_type == 'teacher':
            teacher = Teacher.objects.filter(user_id=user_id).first()
            if not teacher or session.teacher_id != teacher.user_id:
                return error_response(message='无权删除该会话', code=403)

        session.delete()
        return success_response(message='会话删除成功')
    except Exception as e:
        return error_response(message=f'会话删除失败: {str(e)}', code=500)


# 统计当前班级学生考勤情况（详情：是否签到 + 当前请假）
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin'])
def student_info_api(request):
    try:
        user_id, user_type = get_token_data(request)
        class_id = request.GET.get('class_id')
        if not class_id:
            return error_response(message='缺少班级ID', code=400)

        # 可选的考勤会话ID，用于基于会话时间窗计算状态
        attendance_id = request.GET.get('attendance_id')

        students = StudentUser.objects.filter(class_id=class_id)
        if not students:
            return error_response(message='班级不存在或无学生', code=404)

        now = datetime.now()
        today = now.date()

        # 若提供了考勤会话ID，取出会话并校验班级一致性
        session = None
        if attendance_id:
            session = AttendanceSession.objects.filter(id=attendance_id).first()
            if not session:
                return error_response(message='会话不存在', code=404)
            if str(session.class_group.class_id) != str(class_id):
                return error_response(message='会话与班级不匹配', code=400)

        student_data = []
        for student in students:
            # 基于是否提供会话ID，分别计算签到与状态
            if session:
                has_checkin = StudentAttendance.objects.filter(
                    student_users_id=student,
                    attendance_session_id=session,
                    check_in_time__isnull=False
                ).exists()

                if has_checkin:
                    status = '已签到'
                else:
                    on_leave = LeaveRequest.objects.filter(
                        student=student,
                        start_time__lte=now,
                        end_time__gte=now,
                        status='approved' 
                    ).exists()
                    if on_leave:
                        status = '请假'
                    else:
                        if session.end_time and now > session.end_time:
                            status = '缺勤'
                        else:
                            status = '未签到'
            else:
                has_checkin = StudentAttendance.objects.filter(
                    student_users_id=student,
                    date=today,
                    attendance_session_id__class_group__class_id=class_id,
                    check_in_time__isnull=False
                ).exists()

                if has_checkin:
                    status = '已签到'
                else:
                    on_leave = LeaveRequest.objects.filter(
                        student=student,
                        start_time__lte=now,
                        end_time__gte=now,
                        status='approved'  # 只有已审批通过的请假才视为有效请假
                    ).exists()
                    status = '请假' if on_leave else '未签到'

            student_data.append({
                'student_users_id': student.student_users_id,
                'student_id': student.student_id,
                'student_name': student.student_name,
                'gender': student.gender,
                'status': status
            })

        return success_response(data=student_data, message='班级学生考勤详情查询成功')
    except Exception as e:
        return error_response(message=f'查询失败: {str(e)}', code=500)
