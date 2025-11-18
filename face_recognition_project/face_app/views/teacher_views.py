from django.http import JsonResponse
from django.utils import timezone
from ..models import Teacher
from ..utils import success_response, error_response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password
from ..decorators import custom_auth_required, get_token_from_request

# 教师查询接口
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin'])
def teacher_query_api(request):
    all_teachers = []
    try:
        token_data = get_token_from_request(request)
        user_type = token_data.get('user_type')
        user_id = token_data.get('user_id')
        
        if user_type == 'teacher':
            # 教师只能查询自己的信息
            teacher = Teacher.objects.filter(user_id=user_id).first()
            if teacher:
                teacher_data = {
                    'teacher_id': teacher.pk,
                    'teacher_name': teacher.username,
                }
                return success_response(data=teacher_data, message="教师信息查询成功")
            else:
                return error_response(message="无权限查询教师信息", code=403)
        elif user_type == 'admin':
            # 管理员可以查询所有教师信息
            teachers = Teacher.objects.all()
            all_teachers = []
            for teacher in teachers:
                all_teachers.append({
                    'teacher_id': teacher.pk,
                    'teacher_name': teacher.username,
                    'gender': teacher.gender,
                    'phone': teacher.phone,
                    'login_time': teacher.login_time,
                    'avatar': teacher.avatar,
                })
            return success_response(data=all_teachers, message="教师信息查询成功")
        else:
            return error_response(message="无权限查询教师信息", code=403)
    except Exception as e:
        return error_response(message=f"查询失败: {str(e)}", code=500)


# 教师更新接口
@api_view(['PUT'])
@custom_auth_required(roles=['admin'])
def teacher_update_api(request):
    try:
        token_data = get_token_from_request(request)
        user_type = token_data.get('user_type')
        
        if user_type != 'admin':
            return error_response(message="无权限更新教师信息", code=403)

        teacher_id = request.data.get('teacher_id')
        teacher_name = request.data.get('teacher_name')
        gender = request.data.get('gender')
        phone = request.data.get('phone')

        if not all([teacher_id, teacher_name, gender, phone]):
            return error_response(message='所有字段都为必填项', code=400)

        # 查找要更新的教师
        try:
            teacher = Teacher.objects.get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return error_response(message='教师不存在', code=404)

        # 更新教师信息
        teacher.username = teacher_name
        teacher.gender = gender
        teacher.phone = phone
        teacher.update_time = timezone.now()
        teacher.save()

        return success_response(message='教师信息更新成功')
    except Exception as e:
        return error_response(message=f'教师信息更新失败: {str(e)}', code=500)


# 教师删除接口
@api_view(['DELETE'])
@custom_auth_required(roles=['admin'])
def teacher_delete_api(request):
    try:
        token_data = get_token_from_request(request)
        user_type = token_data.get('user_type')
        
        if user_type != 'admin':
            return error_response(message="无权限删除教师", code=403)

        teacher_id = request.data.get('teacher_id')

        if not teacher_id:
            return error_response(message='教师ID为必填项', code=400)

        # 查找要删除的教师
        try:
            teacher = Teacher.objects.get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return error_response(message='教师不存在', code=404)

        # 删除教师
        teacher.delete()

        return success_response(message='教师删除成功')
    except Exception as e:
        return error_response(message=f'教师删除失败: {str(e)}', code=500)


# 教师新增接口
@api_view(['POST'])
@custom_auth_required(roles=['admin','teacher'])
def teacher_add_api(request):
    try:
        token_data = get_token_from_request(request)
        user_type = token_data.get('user_type')
        
        if user_type not in ['admin', 'teacher']:
            return error_response(message="无权限新增教师", code=403)

        teacher_name = request.data.get('teacher_name')
        gender = request.data.get('gender')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password', '123456')  # 使用前端传递的密码，默认为123456

        if not all([teacher_name, gender, phone_number]):
            return error_response(message='姓名、性别和手机号为必填项', code=400)

        if Teacher.objects.filter(username=teacher_name).exists():
            return error_response(message='教师姓名已存在', code=400)

        # 直接创建 Teacher 对象
        Teacher.objects.create(
            username=teacher_name,
            password=make_password(password),
            gender=gender,
            phone=phone_number,
        )
        return success_response(message='教师新增成功')
    except Exception as e:
        return error_response(message=f'教师新增失败: {str(e)}', code=500)