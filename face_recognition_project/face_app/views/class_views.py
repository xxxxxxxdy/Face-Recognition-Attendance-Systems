from ..models import ClassGroup, StudentUser, Course, CourseStudentTeacher
from ..utils import success_response, error_response
from rest_framework.decorators import api_view
from ..decorators import custom_auth_required, get_token_data, get_token_from_request

# 班级查询接口
@api_view(['GET'])
@custom_auth_required(roles=['student','teacher','admin'])
def class_query_api(request):
    all_classes = []
    try:
        token_data = get_token_from_request(request)
        user_type = token_data.get('user_type')
        user_id = token_data.get('user_id')

        if user_type == 'student':
            # 学生只能查询自己班级的信息
            student_user_profile = StudentUser.objects.filter(student_users_id=user_id).first()
            student_class_id = student_user_profile.class_id
            if student_class_id:
                student_class = ClassGroup.objects.filter(class_id=student_class_id).first()
                if student_class:
                    all_classes.append({
                        'class_id': student_class.class_id,
                        'class_name': student_class.class_name,
                        'description': student_class.description,
                        'student_count': StudentUser.objects.filter(class_id=student_class.class_id).count(),
                        'course_count': CourseStudentTeacher.objects.filter(class_group=student_class).count(),
                    })
        elif user_type == 'teacher' or user_type == 'admin':
            # 教师和管理员可以查询所有班级信息
            classes = ClassGroup.objects.all()
            for class_obj in classes:
                all_classes.append({
                    'class_id': class_obj.class_id,
                    'class_name': class_obj.class_name,
                    'description': class_obj.description,
                    'student_count': StudentUser.objects.filter(class_id=class_obj.class_id).count(),
                    'course_count': CourseStudentTeacher.objects.filter(class_group=class_obj).count(),
                })

        return success_response(data=all_classes, message="班级信息查询成功")
    except Exception as e:
        return error_response(message=f"查询失败: {str(e)}", code=500)


# 班级新增接口
@api_view(['POST'])
def class_add_api(request):
    try:
        class_name = request.data.get('class_name')
        description = request.data.get('description')
        user_id,user_type = get_token_data(request)
        source_id = user_id

        if not all([class_name, source_id]):
            return error_response(message='班级名称为必填项', code=400)

        if ClassGroup.objects.filter(class_name=class_name).exists():
            return error_response(message='班级名称已存在', code=400)

        ClassGroup.objects.create(
            class_name=class_name,
            description=description,
            source_id=source_id,
        )
        return success_response(message='班级新增成功')
    except Exception as e:
        return error_response(message=f'班级新增失败: {str(e)}', code=500)

#通过学号与姓名查询班级
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin','student'])
def class_query_student_api(request):
    student_id = request.GET.get('student_id')
    student_name = request.GET.get('student_name')
    student = StudentUser.objects.filter(student_id=student_id, student_name=student_name).first()
    if not student:
        return error_response(message="学生不存在", code=400)
    class_name = ClassGroup.objects.filter(class_id=student.class_id).first().class_name

    return success_response(data={'class_name':class_name}, message="班级查询成功")

# 班级修改接口
@api_view(['PUT'])
@custom_auth_required(roles=['teacher','admin'])
def class_update_api(request):
    try:
        class_id = request.data.get('class_id')
        class_name = request.data.get('class_name')
        description = request.data.get('description')
        
        if not class_id:
            return error_response(message='班级ID为必填项', code=400)
        
        if not class_name:
            return error_response(message='班级名称为必填项', code=400)
        
        # 检查班级是否存在
        class_obj = ClassGroup.objects.filter(class_id=class_id).first()
        if not class_obj:
            return error_response(message='班级不存在', code=404)
        
        # 检查班级名称是否已被其他班级使用
        existing_class = ClassGroup.objects.filter(class_name=class_name).exclude(class_id=class_id).first()
        if existing_class:
            return error_response(message='班级名称已存在', code=400)
        
        # 更新班级信息
        class_obj.class_name = class_name
        class_obj.description = description or ''
        class_obj.save()
        
        return success_response(message='班级修改成功')
    except Exception as e:
        return error_response(message=f'班级修改失败: {str(e)}', code=500)

# 班级删除接口
@api_view(['DELETE'])
@custom_auth_required(roles=['teacher','admin'])
def class_del_api(request):
    try:
        class_id = request.data.get('class_id')
        
        if not class_id:
            return error_response(message='班级ID为必填项', code=400)
        
        # 检查班级是否存在
        class_obj = ClassGroup.objects.filter(class_id=class_id).first()
        if not class_obj:
            return error_response(message='班级不存在', code=404)
        
        # 检查班级是否有学生
        student_count = StudentUser.objects.filter(class_id=class_id).count()
        if student_count > 0:
            return error_response(message=f'该班级还有{student_count}名学生，无法删除', code=400)
        
        # 检查班级是否有关联的课程
        course_count = CourseStudentTeacher.objects.filter(class_group=class_obj).count()
        if course_count > 0:
            return error_response(message=f'该班级还有{course_count}门课程，无法删除', code=400)
        
        # 删除班级
        class_obj.delete()
        
        return success_response(message='班级删除成功')
    except Exception as e:
        return error_response(message=f'班级删除失败: {str(e)}', code=500)
