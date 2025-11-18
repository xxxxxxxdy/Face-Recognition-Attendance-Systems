import jwt
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.conf import settings
from face_app.utils import success_response, error_response
from face_app.decorators import generate_token
from face_app.models import StudentUser, Teacher, Administrators
from rest_framework.decorators import api_view
from django.utils import timezone
@csrf_exempt
@api_view(['POST'])
def custom_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user_type = data.get('user_type')
    except json.JSONDecodeError:
        return error_response(message='无效的JSON格式', code=500)
    
    if not username or not password or not user_type:
        return error_response(message='用户名、密码和用户类型不能为空', code=500)
    
    user = None
    # 学生用户登录
    if user_type == 'student':
        user = StudentUser.objects.filter(student_id=username).first()
    # 教师用户登录
    elif user_type == 'teacher':
        user = Teacher.objects.filter(phone=username).first()
    # 管理员用户登录
    elif user_type == 'admin':
        user = Administrators.objects.filter(username=username).first()
    
    if not user:
        return error_response(message='用户名或密码错误', code=500)
    
    if not check_password(password, user.password):
        return error_response(message='用户名或密码错误', code=500)
    
    # 更新最后登录时间
    user.login_time = timezone.now()
    user.save(update_fields=['login_time'])
    
    # 学生用户登录
    if user_type == 'student':
        id = user.student_users_id
    # 教师用户登录
    elif user_type == 'teacher':
        id = user.user_id
    # 管理员用户登录
    elif user_type == 'admin':
        id = user.admin_id

    token = generate_token(id,user_type)

    return success_response(code=200, data={'token': token,'user_type':user_type}, message='登录成功')
