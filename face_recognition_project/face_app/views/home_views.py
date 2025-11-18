from django.utils import timezone
from nt import error
import os
from deepface import DeepFace
import matplotlib.pyplot as plt
import base64
import numpy as np
import uuid
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from face_app.decorators import custom_auth_required, get_token_from_request, get_token_data
from ..models import FaceInfo, StudentUser, ClassGroup, AttendanceSession, StudentAttendance, Teacher, Administrators
from ..utils import success_response, error_response
from rest_framework.decorators import api_view
from datetime import datetime
import re
from PIL import Image
from io import BytesIO

def save_avatar_image(avatar_data, user_id, user_type, old_avatar_path=None):
    """
    保存头像图片到本地文件系统，并删除旧头像
    :param avatar_data: base64编码的图片数据
    :param user_id: 用户ID
    :param user_type: 用户类型
    :param old_avatar_path: 旧头像的相对路径
    :return: 相对路径或None
    """
    if not avatar_data:
        return None
    
    try:
        # 处理base64数据，参考face_view.py的save_face_image方法
        if avatar_data.startswith("data:image"):
            avatar_data = avatar_data.split(",")[1]
        
        # 解码base64数据
        avatar_binary = base64.b64decode(avatar_data)
        
        # 确保avatar目录存在
        media_path = os.path.join(settings.MEDIA_ROOT, 'avatar')
        os.makedirs(media_path, exist_ok=True)
        
        # 生成唯一文件名，使用jpg格式保持一致性
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        unique_filename = f'{user_type}_{user_id}_{timestamp}_{unique_id}.jpg'
        file_path = os.path.join(media_path, unique_filename)
        
        # 将图片数据转换为PIL Image对象
        image = Image.open(BytesIO(avatar_binary))
        
        # 如果是RGBA模式，转换为RGB
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # 保存图片
        image.save(file_path, 'JPEG', quality=85)
        
        # 删除旧头像文件
        if old_avatar_path and old_avatar_path.strip():
            try:
                old_file_path = os.path.join(settings.MEDIA_ROOT, old_avatar_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    print(f"已删除旧头像: {old_file_path}")
            except Exception as e:
                print(f"删除旧头像失败: {str(e)}")
                # 不抛出异常，因为新头像已经保存成功
        
        # 返回相对路径
        return f"avatar/{unique_filename}"
        
    except Exception as e:
        print(f"保存头像失败: {str(e)}")
        return None

# 登录后展示个人信息
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin', 'student'])
def home_api(request):
    user = request.user
    user_type = user.get('user_type')
    user_id = user.get('user_id')
    
    try:
        if user_type == 'student':
            student = StudentUser.objects.get(student_users_id=user_id)
            class_name = ClassGroup.objects.get(class_id=student.class_id).class_name
            return success_response({
                'user_id': student.student_users_id,
                'name': student.student_name,
                'avatar': student.avatar,
                'class_group': class_name
            })
        elif user_type == 'teacher':
            teacher = Teacher.objects.get(user_id=user_id)
            return success_response({
                'user_id': teacher.user_id,
                'name': teacher.username,
                'avatar': teacher.avatar
            })
        elif user_type == 'admin':
            admin = Administrators.objects.get(admin_id=user_id)
            return success_response({
                'user_id': admin.admin_id,
                'name': '管理员'
            })
        else:
            return error_response(message="无效的用户类型", code=400)
    except StudentUser.DoesNotExist:
        return error_response(message="学生用户不存在", code=404)
    except Teacher.DoesNotExist:
        return error_response(message="教师用户不存在", code=404)
    except Administrators.DoesNotExist:
        return error_response(message="管理员用户不存在", code=404)
    except Exception as e:
        return error_response(message=f"获取用户信息失败: {str(e)}", code=500)

# 获取当前用户的个人信息
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin', 'student'])
def profile_api(request):
    user_id, user_type = get_token_data(request)
    try:
        if user_type == 'student':
            student = StudentUser.objects.get(student_users_id=user_id)
            class_name = ClassGroup.objects.get(class_id=student.class_id).class_name if student.class_id else None
            return success_response({
                'user_id': student.student_users_id,
                'name': student.student_name,
                'gender': student.gender,
                'email': student.email,
                'avatar': student.avatar,
                'phone': student.phone,
                'class_group': class_name
            })
        elif user_type == 'teacher':
            teacher = Teacher.objects.get(user_id=user_id)
            return success_response({
                'user_id': teacher.user_id,
                'name': teacher.username,
                'gender': teacher.gender,
                'phone': teacher.phone,
                'email': teacher.email,
                'avatar': teacher.avatar
            })
        elif user_type == 'admin':
            admin = Administrators.objects.get(admin_id=user_id)
            return success_response({
                'user_id': admin.admin_id,
                'name': '管理员'
            })
        else:
            return error_response(message="无效的用户类型", code=400)
    except StudentUser.DoesNotExist:
        return error_response(message="学生用户不存在", code=404)
    except Teacher.DoesNotExist:
        return error_response(message="教师用户不存在", code=404)
    except Administrators.DoesNotExist:
        return error_response(message="管理员用户不存在", code=404)

@api_view(['PUT'])
@custom_auth_required(roles=['teacher','admin', 'student'])
def profile_update_api(request):
    user_id, user_type = get_token_data(request)
    data = request.data
    
    try:
        if user_type == 'student':
            student = StudentUser.objects.get(student_users_id=user_id)
            
            # 处理头像上传 - 只有当avatar_data不为空时才处理
            avatar_data = data.get('avatar')
            avatar_path = None
            if avatar_data and avatar_data.strip():  # 确保不是空字符串
                # 获取旧头像路径
                old_avatar_path = student.avatar if hasattr(student, 'avatar') else None
                avatar_path = save_avatar_image(avatar_data, user_id, user_type, old_avatar_path)
            
            # 更新字段 - 只有当字段值不为空时才更新
            username = data.get('username')
            if username and username.strip():
                student.student_name = username
                
            gender = data.get('gender')
            if gender and gender.strip():
                student.gender = gender
                
            email = data.get('email')
            if email and email.strip():
                student.email = email
                
            phone = data.get('phone')
            if phone and phone.strip():
                student.phone = phone
                
            class_group = data.get('class_group')
            if class_group and class_group.strip():
                student.class_id = class_group
                
            if avatar_path:
                student.avatar = avatar_path
                
            # 处理密码更新
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            if old_password and old_password.strip() and new_password and new_password.strip():
                # 验证旧密码
                if not check_password(old_password, student.password):
                    return error_response(message='旧密码错误', code=400)
                
                # 更新新密码
                student.password = make_password(new_password)
                
            student.save()
            return success_response({
                'message': '学生个人信息更新成功'
            })
            
        elif user_type == 'teacher':
            teacher = Teacher.objects.get(user_id=user_id)
            
            # 处理头像上传 - 只有当avatar_data不为空时才处理
            avatar_data = data.get('avatar')
            avatar_path = None
            if avatar_data and avatar_data.strip():  # 确保不是空字符串
                # 获取旧头像路径
                old_avatar_path = teacher.avatar if hasattr(teacher, 'avatar') else None
                avatar_path = save_avatar_image(avatar_data, user_id, user_type, old_avatar_path)
            
            # 更新字段 - 只有当字段值不为空时才更新
            username = data.get('username')
            if username and username.strip():
                teacher.username = username
                
            gender = data.get('gender')
            if gender and gender.strip():
                teacher.gender = gender
                
            email = data.get('email')
            if email and email.strip():
                teacher.email = email
                
            phone = data.get('phone')
            if phone and phone.strip():
                teacher.phone = phone
                
            if avatar_path:
                teacher.avatar = avatar_path
                
            # 处理密码更新
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            if old_password and old_password.strip() and new_password and new_password.strip():
                # 验证旧密码
                if not check_password(old_password, teacher.password):
                    return error_response(message='旧密码错误', code=400)
                
                # 更新新密码
                teacher.password = make_password(new_password)
                
            teacher.save()
            return success_response({
                'message': '教师个人信息更新成功'
            })
            
        elif user_type == 'admin':
            admin = Administrators.objects.get(admin_id=user_id)
            
            # 处理头像上传 - 只有当avatar_data不为空时才处理
            avatar_data = data.get('avatar')
            avatar_path = None
            if avatar_data and avatar_data.strip():  # 确保不是空字符串
                # 获取旧头像路径
                old_avatar_path = admin.avatar if hasattr(admin, 'avatar') else None
                avatar_path = save_avatar_image(avatar_data, user_id, user_type, old_avatar_path)
            
            # 管理员可能只能更新部分信息 - 只有当字段值不为空时才更新
            username = data.get('username')
            if username and username.strip():
                admin.admin_name = username  # 假设管理员有admin_name字段
                
            if avatar_path:
                admin.avatar = avatar_path  # 假设管理员有avatar字段
                
            # 处理密码更新
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            if old_password and old_password.strip() and new_password and new_password.strip():
                # 验证旧密码
                if not check_password(old_password, admin.password):
                    return error_response(message='旧密码错误', code=400)
                
                # 更新新密码
                admin.password = make_password(new_password)
                
            admin.save()
            return success_response({
                'message': '管理员个人信息更新成功'
            })
            
        else:
            return error_response(message="无效的用户类型", code=400)
            
    except StudentUser.DoesNotExist:
        return error_response(message="学生用户不存在", code=404)
    except Teacher.DoesNotExist:
        return error_response(message="教师用户不存在", code=404)
    except Administrators.DoesNotExist:
        return error_response(message="管理员用户不存在", code=404)
    except Exception as e:
        return error_response(message=f"更新个人信息失败: {str(e)}", code=500)