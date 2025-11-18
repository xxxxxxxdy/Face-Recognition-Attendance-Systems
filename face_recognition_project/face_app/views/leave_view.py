from rest_framework.decorators import api_view
from ..utils import  success_response, error_response
from ..decorators import custom_auth_required, get_token_from_request, get_token_data
from ..models import LeaveRequest, StudentUser, CourseStudentTeacher, Teacher, Course, AttendanceSession, ClassGroup 
from datetime import datetime
import json

# 请假查询接口
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin','student'])
def leave_query_api(request):
    try:
        token_data = get_token_from_request(request)
        user_type = token_data.get('user_type')
        user_id = token_data.get('user_id')

        leave_requests_queryset = LeaveRequest.objects.all()
        # 学生请假查询处理
        if user_type == 'student':
            leave_requests_queryset = leave_requests_queryset.filter(student=user_id)
           
        # 教师查询处理
        elif user_type == 'teacher':
            teacher_managed_class_ids = CourseStudentTeacher.objects.filter(
                teacher__user_id=user_id
            ).values_list('class_group_id', flat=True)

            students_in_managed_classes_ids = StudentUser.objects.filter(
                class_id__in=teacher_managed_class_ids
            ).values_list('student_users_id', flat=True)

            print(students_in_managed_classes_ids)
            leave_requests_queryset = leave_requests_queryset.filter(student__student_users_id__in=students_in_managed_classes_ids)
          
        elif user_type == 'admin':
            pass 
        leave_requests_queryset = leave_requests_queryset.select_related('student')
        

        result_data = []
        for lr in leave_requests_queryset:
            student_of_lr = lr.student 
            class_of_lr = ClassGroup.objects.filter(class_id=student_of_lr.class_id).first() if student_of_lr else None
        
            student_name_for_lr = student_of_lr.student_name if student_of_lr else None
            class_name_for_lr = class_of_lr.class_name if class_of_lr else None
        
            teacher_name = None
            if lr.approver_id:
                approver_teacher = Teacher.objects.filter(user_id=lr.approver_id).first()
                if approver_teacher:
                    teacher_name = approver_teacher.username
        
            result_data.append({
                'id': lr.id,
                'student_id': lr.student.student_id,
                'student_username': student_name_for_lr,
                'class_name': class_name_for_lr,
                'start_time': lr.start_time.isoformat() if lr.start_time else None,
                'end_time': lr.end_time.isoformat() if lr.end_time else None,
                'leave_type': lr.leave_type,
                'reason': lr.reason,
                'status': lr.status,
                'approver_id': teacher_name,
                'approval_time': lr.approval_time.isoformat() if lr.approval_time else None,
                'comments': lr.comments,
                'submitted_at': lr.submitted_at.isoformat() if lr.submitted_at else None,
                'updated_at': lr.updated_at.isoformat() if lr.updated_at else None,
            })
        return success_response(data=result_data, message="请假信息查询成功")
    except Exception as e:
        return error_response(message=f"查询失败: {str(e)}", code=500)

# 请假新增
@api_view(['POST'])
@custom_auth_required(roles=['student','teacher','admin'])
def leave_add_api(request):
    try:
        user_id, user_type = get_token_data(request)
        
        # 获取前端传入的数据
        data = json.loads(request.body) if request.body else {}
        
        # 验证必要字段
        required_fields = ['student_id', 'student_username', 'class_name', 'start_time', 'end_time', 'reason', 'leave_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return error_response(message=f"缺少必要字段: {field}", code=400)
        
        if user_type == 'student':
            current_student = StudentUser.objects.filter(student_users_id=user_id).first()
            if not current_student:
                return error_response(message="学生用户不存在", code=400)
            
            # 验证前端传入的学号和姓名是否与当前登录学生一致
            if (current_student.student_id != data['student_id'] or 
                current_student.student_name != data['student_username']):
                return error_response(message="只能新增自己的请假信息", code=403)
            
            student_for_leave = current_student
        else:
            # 根据学号查找学生
            student_for_leave = StudentUser.objects.filter(student_id=data['student_id']).first()
            if not student_for_leave:
                return error_response(message="学生不存在", code=400)
            
            # 验证学生姓名是否匹配
            if student_for_leave.student_name != data['student_username']:
                return error_response(message="学生账号信息不存在", code=400)
        
        # 检查该学生是否已有请假记录
        existing_leave = LeaveRequest.objects.filter(student=student_for_leave).first()
        if existing_leave:
            return error_response(message="该学生已有请假记录，不可重复请假", code=400)
        
        # 解析时间字符串
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        except ValueError:
            try:
                start_time = datetime.strptime(data['start_time'], '%Y-%m-%d')
                end_time = datetime.strptime(data['end_time'], '%Y-%m-%d')
            except ValueError:
                return error_response(message="时间格式错误，请使用 YYYY-MM-DD 格式", code=400)
        
        # 验证时间逻辑
        if start_time >= end_time:
            return error_response(message="开始时间必须早于结束时间", code=400)
        
        # 验证请假类型
        valid_leave_types = [1, 2, 3]  # 1: 病假, 2: 事假 3: 其他
        if data['leave_type'] not in valid_leave_types:
            return error_response(message="无效的请假类型", code=400)
        
        # 创建请假记录
        leave_request = LeaveRequest.objects.create(
            student=student_for_leave,
            start_time=start_time,
            end_time=end_time,
            reason=data['reason'],
            leave_type=data['leave_type'],
            status='pending'  # 默认状态为待审批
        )
        
        return success_response(
            data={'id': leave_request.id}, 
            message="请假申请提交成功"
        )
        
    except json.JSONDecodeError:
        return error_response(message="请求数据格式错误", code=400)
    except Exception as e:
        return error_response(message=f"请假申请提交失败: {str(e)}", code=500)


# 修改请假
@api_view(['PUT'])
@custom_auth_required(roles=['student','teacher','admin'])
def leave_update_api(request):
    try:
        user_id, user_type = get_token_data(request)
        
        # 获取前端传入的数据
        data = json.loads(request.body) if request.body else {}
        
        # 验证必要字段
        required_fields = ['id']
        for field in required_fields:
            if field not in data:
                return error_response(message=f"缺少必要字段: {field}", code=400)
        
        # 查找请假记录
        leave_request = LeaveRequest.objects.filter(id=data['id']).first()
        if not leave_request:
            return error_response(message="请假记录不存在", code=400)
        
        # 验证用户权限
        if user_type == 'student' and leave_request.student.student_users_id != user_id:
            return error_response(message="只能修改自己的请假记录", code=403)
        
        # 如果是学生角色，验证学号和姓名是否匹配
        if user_type == 'student':
            if 'student_id' in data and data['student_id'] != leave_request.student.student_id:
                return error_response(message="学号不匹配，无法修改", code=403)
            if 'student_username' in data and data['student_username'] != leave_request.student.student_name:
                return error_response(message="姓名不匹配，无法修改", code=403)
        
        # 更新请假记录字段
        if 'student_id' in data and user_type in ['teacher', 'admin']:
            # 只有教师和管理员可以修改学号
            student = StudentUser.objects.filter(student_id=data['student_id']).first()
            if not student:
                return error_response(message="学生不存在", code=400)
            leave_request.student = student
        
        if 'class_name' in data:
            leave_request.class_name = data['class_name']
        
        if 'leave_type' in data:
            if data['leave_type'] not in [1, 2, 3]:
                return error_response(message="请假类型无效", code=400)
            leave_request.leave_type = data['leave_type']
        
        if 'reason' in data:
            if not data['reason'].strip():
                return error_response(message="请假原因不能为空", code=400)
            leave_request.reason = data['reason']
        
        if 'start_time' in data:
            try:
                start_time = datetime.strptime(data['start_time'], '%Y-%m-%d').date()
                leave_request.start_time = start_time
            except ValueError:
                return error_response(message="开始时间格式错误，请使用 YYYY-MM-DD 格式", code=400)
        
        if 'end_time' in data:
            try:
                end_time = datetime.strptime(data['end_time'], '%Y-%m-%d').date()
                leave_request.end_time = end_time
            except ValueError:
                return error_response(message="结束时间格式错误，请使用 YYYY-MM-DD 格式", code=400)
        
        # 验证时间逻辑
        if leave_request.start_time and leave_request.end_time:
            if leave_request.start_time > leave_request.end_time:
                return error_response(message="开始时间不能晚于结束时间", code=400)
        
        # 保存修改
        leave_request.save()
        
        return success_response(
            message="请假申请修改成功",
            data={
                "id": leave_request.id,
                "student_id": leave_request.student.student_id,
                "student_username": leave_request.student.student_name,
                "class_name": leave_request.class_name,
                "leave_type": leave_request.leave_type,
                "reason": leave_request.reason,
                "start_time": leave_request.start_time.strftime('%Y-%m-%d') if leave_request.start_time else None,
                "end_time": leave_request.end_time.strftime('%Y-%m-%d') if leave_request.end_time else None,
                "status": leave_request.status
            }
        )
        
    except json.JSONDecodeError:
        return error_response(message="请求数据格式错误", code=400)
    except Exception as e:
        return error_response(message=f"请假申请修改失败: {str(e)}", code=500)

# 删除请假记录
@api_view(['DELETE'])
@custom_auth_required(roles=['student','admin'])
def leave_del_api(request):
    try:
        user_id, user_type = get_token_data(request)
            
        # 获取前端传入的数据
        data = json.loads(request.body) if request.body else {}
            
        # 验证必要字段
        required_fields = ['id']
        for field in required_fields:
            if field not in data:
                return error_response(message=f"缺少必要字段: {field}", code=400)
            
        # 查找请假记录
        leave_request = LeaveRequest.objects.filter(id=data['id']).first()
        if not leave_request:
            return error_response(message="请假记录不存在", code=400)
            
        # 学生权限验证
        if user_type == 'student':
            # 学生只能删除自己的请假记录
            if leave_request.student.student_users_id != user_id:
                return error_response(message="只能删除自己的请假记录", code=403)
            # 学生只能删除待审批的请假记录
            if leave_request.status != 'pending':
                return error_response(message="只能删除未处理的请假记录", code=403)
        
        # 管理员可以删除任何请假记录，无需额外验证
            
        # 删除请假记录
        leave_request.delete()
            
        return success_response(data={
            "id": data['id']
        }, message="请假申请删除成功")
        
    except json.JSONDecodeError:
        return error_response(message="请求数据格式错误", code=400)
    except Exception as e:
        return error_response(message=f"请假申请删除失败: {str(e)}", code=500)

# 请假审批
@api_view(['POST'])
@custom_auth_required(roles=['teacher','admin'])
def leaveApproveApi(request):
        user_id, user_type = get_token_data(request)
            
        # 获取前端传入的数据
        data = json.loads(request.body) if request.body else {}
            
        # 验证必要字段
        required_fields = ['id', 'approve_status']
        for field in required_fields:
            if field not in data:
                return error_response(message=f"缺少必要字段: {field}", code=400)
            
        # 验证审批状态值
        if data['approve_status'] not in ['approved', 'rejected']:
            return error_response(message="审批状态只能是 approved 或 rejected", code=400)
            
        # 查找请假记录
        leave_request = LeaveRequest.objects.filter(id=data['id']).first()
        if not leave_request:
            return error_response(message="请假记录不存在", code=400)
            
        # 检查请假记录状态 - 只有待处理状态才能审批
        if leave_request.status != 'pending':
            return error_response(message="只能审批未处理的请假记录", code=403)
            
        # 教师权限验证：只能审批自己班级的学生
        if user_type == 'teacher':
            # 获取请假学生的班级ID
            student_class_id = leave_request.student.class_id
            
            # 直接查询教师是否管理该学生所在的班级
            teacher_manages_class = CourseStudentTeacher.objects.filter(
                teacher__user_id=user_id,
                class_group_id=student_class_id
            ).exists()
            
            # 添加调试信息
            print(f"教师ID: {user_id}")
            print(f"学生班级ID: {student_class_id}")
            print(f"学生信息: {leave_request.student.student_name} (ID: {leave_request.student.student_id})")
            print(f"教师是否管理该班级: {teacher_manages_class}")
            
            if not teacher_manages_class:
                print(f"权限验证失败 - 教师 {user_id} 不管理班级 {student_class_id}")
                return error_response(message="您只能审批自己班级学生的请假申请", code=403)
            
        # 更新审批状态和相关信息
        leave_request.status = data['approve_status']
        leave_request.approver_id = user_id  
        leave_request.approval_time = datetime.now()  
        
        # 如果有审批备注，保存到 comments 字段
        if 'comments' in data and data['comments']:
            leave_request.comments = data['comments']
        elif data['approve_status'] == 'approved':
            leave_request.comments = '同意请假'
        else:
            leave_request.comments = '拒绝请假'
            
        leave_request.save()

        return success_response(
            message="请假审批成功",
            data={
                "id": leave_request.id,
            }
        )


