from django.utils import timezone
from nt import error
import os
from deepface import DeepFace
import matplotlib.pyplot as plt
import base64
import numpy as np
import uuid
from django.conf import settings
from face_app.decorators import custom_auth_required, get_token_from_request, get_token_data
from ..models import FaceInfo, StudentUser, ClassGroup, AttendanceSession, StudentAttendance
from ..utils import success_response, error_response
from rest_framework.decorators import api_view
from datetime import datetime

# 查询人脸数据
@api_view(['GET'])
@custom_auth_required(roles=['teacher','admin', 'student'])
def face_query_api(request):
    token = get_token_from_request(request)
    user_id = token.get('user_id')
    user_type = token.get('user_type')

    if user_type == 'student':
        student_obj = StudentUser.objects.filter(student_users_id=user_id).first()
        if not student_obj:
            return error_response(message="学生不存在", code=400)
        
        current_student_class_id = student_obj.class_id
        students_in_same_class = StudentUser.objects.filter(class_id=current_student_class_id)
        
        # 构建返回数据
        student_data = {
            'student_id': student_obj.student_id,
            'student_name': student_obj.student_name,
            'class_id': student_obj.class_id,
            'class_students': []
        }
        class_group_obj = ClassGroup.objects.filter(class_id=current_student_class_id).first()
        class_name_str = class_group_obj.class_name if class_group_obj else None

        for index, s in enumerate(students_in_same_class):
            face_info = FaceInfo.objects.filter(student_id=s).first()
            face_image_url = face_info.face_img.url if face_info and face_info.face_img else None
            capture_time = face_info.capture_time.strftime("%Y-%m-%d %H:%M:%S") if face_info and face_info.capture_time else None

           
            student_data['class_students'].append({
                'id': s.id, 
                'student_id': s.student_id,
                'student_name': s.student_name, 
                'class_name': class_name_str, 
                'gender': s.gender,
                'face_image': face_image_url, 
                'capture_time': capture_time, 
            })
        
        return success_response(data=student_data['class_students'], message="同班学生信息查询成功")
    elif user_type == 'teacher' or user_type == 'admin':
        # 从StudentUser开始查询，这样可以显示所有学生（包括没有人脸的）
        all_students = StudentUser.objects.all()
        result_data = []
        for student in all_students:
            # 查找该学生的人脸信息
            face_info = FaceInfo.objects.filter(student_id=student).first()
            
            # 获取班级名称
            class_name_str = None
            if student.class_id:
                class_group_obj = ClassGroup.objects.filter(class_id=student.class_id).first()
                if class_group_obj:
                    class_name_str = class_group_obj.class_name

            # 人脸信息（如果存在）
            face_image_url = face_info.face_img.url if face_info and face_info.face_img else None
            capture_time = face_info.capture_time.strftime("%Y-%m-%d %H:%M:%S") if face_info and face_info.capture_time else None

            result_data.append({
                'face_id': face_info.face_id if face_info else None,
                'student_id': student.student_id,
                'student_name': student.student_name,
                'class_name': class_name_str,
                'gender': student.gender,
                'face_image': face_image_url,
                'capture_time': capture_time,
            })
        return success_response(data=result_data, message="所有学生信息查询成功")
    else:
        return error_response(message="无效的用户类型", code=400)


# 人脸签到功能
@api_view(['POST'])
@custom_auth_required(roles=['teacher','admin','student'])
def face_check_api(request):
    # 初始化临时文件路径变量
    temp_face_path = None
    extracted_face1_path = None
    extracted_face2_path = None
    
    try:
        face_image_base64 = request.data.get('face_image')
        session_id = request.data.get('session_id')
        token = get_token_from_request(request)
        user_id = token.get('user_id')
        user_type = token.get('user_type')
        # 裁剪图片地址
        cropping_path = os.path.join(settings.MEDIA_ROOT, 'image_cropping')
        # 签到图片地址
        temp_media_path = os.path.join(settings.MEDIA_ROOT, 'temp_face_image')

        if user_type == 'student':
            student_obj = StudentUser.objects.filter(student_users_id=user_id).first()
            if not student_obj:
                return error_response(message="学生不存在", code=400)
            
        else:
            return error_response(message="无效的用户类型", code=400)   

        if not face_image_base64:
            return error_response(message="未提供人脸图片", code=400)
        if not session_id:
            return error_response(message="未提供考勤会话ID", code=400)
        

        # 获取考勤会话
        attendance_session = AttendanceSession.objects.filter(id=session_id).first()
        if not attendance_session:
            return error_response(message="考勤会话不存在", code=400)
        if not attendance_session.is_active:
            return error_response(message="考勤会话已结束", code=400)
        
        # 是否已签到
        student_info = StudentAttendance.objects.filter(attendance_session_id=attendance_session, student_users_id=student_obj).first()
        if student_info:
            return error_response(message="学生已签到", code=400)          

        # 解码并保存人脸
        if face_image_base64.startswith("data:image"):
            face_image_base64 = face_image_base64.split(",")[1]
        face_image_binary = base64.b64decode(face_image_base64)

        # 持久化保存图片
        unique_filename = f'{uuid.uuid4()}.jpg'
        temp_face_path = os.path.join(temp_media_path,unique_filename)
        with open(temp_face_path, 'wb') as f:
            f.write(face_image_binary)
       
        # 获取人脸地址
        face_info = FaceInfo.objects.filter(student_id=student_obj).first()
        if not face_info:
            return error_response(message="未找到学生人脸信息", code=400)
        # 人脸地址
        face_img =  os.path.join(settings.MEDIA_ROOT) + face_info.face_img.name

        extracted_face1_path = extract_and_save_face(temp_face_path, cropping_path)
        extracted_face2_path = extract_and_save_face(face_img, cropping_path)

        if extracted_face1_path and extracted_face2_path:
            result_verify = DeepFace.verify(img1_path=extracted_face1_path,
                                        img2_path=extracted_face2_path,
                                        model_name='SFace',
                                        detector_backend='retinaface')
            
            # 签到处理
            print(result_verify)
            if result_verify['verified']:
                current_time = timezone.now()
                attendance_status = ''
                if attendance_session.end_time and current_time > attendance_session.end_time:
                    attendance_status = '迟到'
                else:
                    attendance_status = '已签到'

                StudentAttendance.objects.create(
                    student_users_id=student_obj,
                    course_id=attendance_session.course,
                    attendance_session_id=attendance_session, 
                    date=current_time.date(),
                    status=attendance_status,
                    check_in_time=current_time,
                )
                return success_response(message="人脸签到成功") 
            else:
                return error_response(message="人脸验证失败", code=500)
        else:
            return error_response(message="未检测到人脸或提取失败", code=400)

    except Exception as e:
        return error_response(message=f"签到失败: {str(e)}", code=500)
    
    finally:
        # 无论成功或异常，都清理临时图片资源
        if temp_face_path and os.path.exists(temp_face_path):
            try:
                os.remove(temp_face_path)
            except:
                pass
        if extracted_face1_path and os.path.exists(extracted_face1_path):
            try:
                os.remove(extracted_face1_path)
            except:
                pass
        if extracted_face2_path and os.path.exists(extracted_face2_path):
            try:
                os.remove(extracted_face2_path)
            except:
                pass
        
# 新增人脸功能
@api_view(['POST'])
@custom_auth_required(roles=['teacher','admin', 'student'])
def face_add_api(request):
    try:
        token = get_token_from_request(request)
        user_id = token.get('user_id')
        user_type = token.get('user_type')

        student_id = request.data.get('student_id')
        face_image = request.data.get('face_image')
        
        # 查询学生
        student = StudentUser.objects.filter(student_id=student_id).first()
        if not student:
            return error_response(message="该学生不存在", code=400)

        # 学生只能新增自己的人脸信息
        if user_type == 'student':  
            if student.student_users_id != user_id:
                return error_response(message="无权限新增其他学生的人脸信息", code=403)

        
        # 检查是否已存在该学生的人脸信息
        existing_face = FaceInfo.objects.filter(student_id__student_id=student_id).first()
        if existing_face:
            return error_response(message="该学生已存在人脸信息", code=400)

        # 保存图片的功能
        is_save = save_face_image(face_image)
        if not is_save:
            return error_response(message="保存图片失败.", code=500)
        # 保存人脸信息到数据库
        face_info = FaceInfo(
            student_id=student,
            face_img=f"\\face_images\\{is_save}",
            capture_time=datetime.now()
        )

        face_info.save()

        return success_response(data=face_info.face_id, message="人脸上传成功")
    except Exception as e:
        return error_response(message=f"查询失败: {str(e)}", code=500)


#修改人脸信息
@api_view(['PUT'])
@custom_auth_required(roles=['teacher','admin', 'student'])
def face_update_api(request):
    user = get_token_data(request) 
    if user:
        face_image_data = request.data.get('face_image')
        student_id_param = request.data.get('student_id')
        student_name_param = request.data.get('student_name')

        if not all([face_image_data, student_id_param, student_name_param]):
            return error_response(message="缺少必要的参数", code=400)
        # 获取学生信息
        try:
            student = StudentUser.objects.get(student_id=student_id_param, student_name=student_name_param)
        except StudentUser.DoesNotExist:
            return error_response(message="未找到匹配的学生信息", code=404)
        except Exception as e:
            return error_response(message=f"查询学生信息失败: {str(e)}", code=500)

        # 持久化存储
        saved_image_name = save_face_image(face_image_data)
        if not saved_image_name:
            return error_response(message="保存图片失败.", code=500)

        face_img_path = f"\\face_images\\{saved_image_name}"

        try:
            # 尝试获取现有的人脸信息，并删除旧图片
            existing_face_info = FaceInfo.objects.filter(student_id=student).first()
            if existing_face_info and existing_face_info.face_img:
                old_image_relative_path = existing_face_info.face_img.name
                old_image_full_path = os.path.join(settings.MEDIA_ROOT)
                old_img_url = (old_image_full_path+old_image_relative_path)
                if os.path.exists(old_img_url):
                    os.remove(old_img_url)

            face_info, created = FaceInfo.objects.update_or_create(
                student_id=student,
                defaults={
                    'face_img': face_img_path,
                    'capture_time': datetime.now()
                }
            )
            if created:
                message = "学生人脸信息新增成功"
            else:
                message = "学生人脸信息更新成功"
            return success_response(message=message, data={'face_info_id': face_info.face_id})

        except Exception as e:
            return error_response(message=f"更新/新增人脸信息失败: {str(e)}", code=500)

# 保存图片到本地
def save_face_image(face_image_base64):
    if face_image_base64.startswith("data:image"):
        face_image_base64 = face_image_base64.split(",")[1]    
    face_image_binary = base64.b64decode(face_image_base64)
    media_path = os.path.join(settings.MEDIA_ROOT, 'face_images')
    os.makedirs(media_path, exist_ok=True)
    
    unique_filename = f'{uuid.uuid4()}.jpg'
    file_path = os.path.join(media_path, unique_filename)
    with open(file_path, 'wb') as f:
        f.write(face_image_binary)
    return unique_filename

# 提高准确率裁剪人脸部分
def extract_and_save_face(image_path, output_dir):
    result = DeepFace.extract_faces(img_path=image_path, align=True)
    if result:
        face_image = result[0]['face']
        original_filename = os.path.basename(image_path)
        output_path = os.path.join(output_dir, original_filename)
        plt.imsave(output_path, face_image)
        return output_path
    return None
