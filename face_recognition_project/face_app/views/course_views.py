from django.http import JsonResponse

from face_app.decorators import custom_auth_required,get_token_from_request
from ..models import Course, CourseStudentTeacher, ClassGroup, Teacher, StudentUser
from ..utils import success_response, error_response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# 课程查询接口
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin', 'student'])
def course_query_api(request):
    all_course_student_teachers = []
    try:
        token = get_token_from_request(request)
        user_type = token.get('user_type')
        user_id = token.get('user_id')
        course_student_teachers = []
        if user_type == 'teacher':
            course_student_teachers = CourseStudentTeacher.objects.filter(teacher=user_id)
        elif user_type == 'admin':
            course_student_teachers = CourseStudentTeacher.objects.all()
        elif user_type == 'student':
            student = StudentUser.objects.get(student_users_id=user_id)
            course_student_teachers = CourseStudentTeacher.objects.filter(class_group=student.class_id)
           
        for cst in course_student_teachers:
            # 获取该课程的所有班级ID
            course_class_ids = list(CourseStudentTeacher.objects.filter(
                course=cst.course, teacher=cst.teacher
            ).values_list('class_group__class_id', flat=True))
            
            all_course_student_teachers.append({
                'id': cst.id,
                'course_name': cst.course.course_name,
                'class_name': cst.class_group.class_name,
                'username': cst.teacher.username,
                'teacher_id': cst.teacher.user_id,
                'class_ids': course_class_ids,
            })
        return success_response(data=all_course_student_teachers, message="课程信息查询成功")
    except Exception as e:
        return error_response(message=f"查询失败: {str(e)}", code=500)

# 课程新增接口
@api_view(['POST'])
@custom_auth_required(roles=['teacher','admin'])
def course_add_api(request):
    try:
        token = get_token_from_request(request)
        user_type = token.get('user_type')
        user_id = token.get('user_id')
        data = request.data
        course_name = data.get('course_name')
        class_ids = data.get('class_ids')  
        teacher_id = data.get('teacher_id')
        
        if not course_name or not class_ids or not teacher_id:
            return error_response(message="课程名称、班级ID和教师ID不能为空", code=400)
        
        # 权限验证：老师只能新增自己的课程
        if user_type == 'teacher':
            # 获取当前登录教师的信息
            current_teacher = Teacher.objects.get(user_id=user_id)
            # 检查提交的teacher_id是否为当前登录教师的ID
            if str(teacher_id) != str(current_teacher.user_id):
                return error_response(message="教师只能新增自己的课程", code=403)
        
        # 验证教师是否存在
        try:
            teacher = Teacher.objects.get(user_id=teacher_id)
        except Teacher.DoesNotExist:
            return error_response(message="指定的教师不存在", code=400)
        
        # 验证同一个老师是否已经有相同的课程名
        existing_course = CourseStudentTeacher.objects.filter(
            teacher=teacher,
            course__course_name=course_name
        ).first()
        
        if existing_course:
            return error_response(message=f"该教师已经有名为'{course_name}'的课程，请使用不同的课程名", code=400)
        
        # 创建课程
        course = Course.objects.create(course_name=course_name)
        
        # 为每个班级创建课程关联记录
        created_relations = []
        for class_id in class_ids:
            try:
                class_group = ClassGroup.objects.get(class_id=class_id)
                # 检查是否已存在相同的课程-教师-班级组合
                existing = CourseStudentTeacher.objects.filter(
                    course=course,
                    class_group=class_group,
                    teacher=teacher
                ).exists()
                
                if not existing:
                    relation = CourseStudentTeacher.objects.create(
                        course=course,
                        class_group=class_group,
                        teacher=teacher
                    )
                    created_relations.append(relation)
            except ClassGroup.DoesNotExist:
                return error_response(message=f"班级ID {class_id} 不存在", code=400)
        
        return success_response(message=f"课程新增成功，关联了 {len(created_relations)} 个班级")
    except Exception as e:
        return error_response(message=f"新增失败: {str(e)}", code=500)

# 课程修改接口
@api_view(['PUT'])
@custom_auth_required(roles=['teacher','admin'])
def course_update_api(request):
    try:
        token = get_token_from_request(request)
        user_type = token.get('user_type')
        user_id = token.get('user_id')
        data = request.data
        
        course_id = data.get('id')
        course_name = data.get('course_name')
        class_ids = data.get('class_ids')
        teacher_id = data.get('teacher_id')
        
        if not course_id or not course_name or not class_ids or not teacher_id:
            return error_response(message="课程ID、课程名称、班级ID和教师ID不能为空", code=400)
        
        # 获取要修改的课程关联记录
        try:
            course_relation = CourseStudentTeacher.objects.get(id=course_id)
            course = course_relation.course
        except CourseStudentTeacher.DoesNotExist:
            return error_response(message="课程不存在", code=404)
        
        # 权限验证：老师只能修改自己的课程
        if user_type == 'teacher':
            current_teacher = Teacher.objects.get(user_id=user_id)
            if str(course_relation.teacher.user_id) != str(current_teacher.user_id):
                return error_response(message="教师只能修改自己的课程", code=403)
        
        # 验证新的教师是否存在
        try:
            new_teacher = Teacher.objects.get(user_id=teacher_id)
        except Teacher.DoesNotExist:
            return error_response(message="指定的教师不存在", code=400)
        
        # 验证同一个老师是否已经有相同的课程名（排除当前正在修改的课程）
        existing_course = CourseStudentTeacher.objects.filter(
            teacher=new_teacher,
            course__course_name=course_name
        ).exclude(course=course).first()
        
        if existing_course:
            return error_response(message=f"该教师已经有名为'{course_name}'的课程，请使用不同的课程名", code=400)
        
        # 更新课程名称
        course.course_name = course_name
        course.save()
        
        # 删除该课程的所有现有关联记录
        CourseStudentTeacher.objects.filter(course=course).delete()
        
        # 为每个班级创建新的课程关联记录
        created_relations = []
        for class_id in class_ids:
            try:
                class_group = ClassGroup.objects.get(class_id=class_id)
                relation = CourseStudentTeacher.objects.create(
                    course=course,
                    class_group=class_group,
                    teacher=new_teacher
                )
                created_relations.append(relation)
            except ClassGroup.DoesNotExist:
                return error_response(message=f"班级ID {class_id} 不存在", code=400)
        
        return success_response(message=f"课程修改成功")
    except Exception as e:
        return error_response(message=f"修改失败: {str(e)}", code=500)

# 课程删除接口
@api_view(['DELETE'])
@custom_auth_required(roles=['teacher','admin'])
def course_del_api(request):
    try:
        token = get_token_from_request(request)
        user_type = token.get('user_type')
        user_id = token.get('user_id')
        data = request.data
        
        course_id = data.get('id')
        
        if not course_id:
            return error_response(message="课程ID不能为空", code=400)
        
        # 获取要删除的课程关联记录
        try:
            course_relation = CourseStudentTeacher.objects.get(id=course_id)
            course = course_relation.course
        except CourseStudentTeacher.DoesNotExist:
            return error_response(message="课程不存在", code=404)
        
        # 权限验证：老师只能删除自己的课程
        if user_type == 'teacher':
            current_teacher = Teacher.objects.get(user_id=user_id)
            if str(course_relation.teacher.user_id) != str(current_teacher.user_id):
                return error_response(message="教师只能删除自己的课程", code=403)
        
        # 获取课程名称用于返回消息
        course_name = course.course_name
        
        # 删除该课程的所有关联记录
        deleted_relations_count = CourseStudentTeacher.objects.filter(course=course).count()
        CourseStudentTeacher.objects.filter(course=course).delete()
        
        # 删除课程本身
        course.delete()
        
        return success_response(message=f"课程'{course_name}'删除成功")
    except Exception as e:
        return error_response(message=f"删除失败: {str(e)}", code=500)

