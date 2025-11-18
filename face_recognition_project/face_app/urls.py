from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.my_auth_views import custom_login
from .views.class_views import class_add_api, class_query_api, class_query_student_api, class_update_api, class_del_api
from .views.student_views import student_query_api, student_add_api, student_batch_add_api, student_template_download_api, student_selfUser_api, class_list_api, student_update_api, student_delete_api
from .views.teacher_views import teacher_query_api, teacher_add_api, teacher_update_api, teacher_delete_api
from .views.course_views import course_query_api, course_add_api, course_update_api, course_del_api
from .views.attendance_views import attendance_query_api, attendance_add_api, student_info_api, attendance_update_api, attendance_del_api, student_active_attendance_sessions_api
from .views.face_view import face_add_api, face_query_api, face_check_api, face_update_api
from .views.leave_view import leave_query_api, leave_add_api, leave_update_api, leave_del_api, leaveApproveApi
from .views.home_views import home_api, profile_api, profile_update_api
router = DefaultRouter()


urlpatterns = [
    path('login', custom_login, name='auth_login_api'),
    path('home', home_api, name='home_api'),
    path('profile', profile_api, name='profile_api'),
    path('profile/update', profile_update_api, name='profile_update_api'),
    path('student/query', student_query_api, name='student_query_api'),
    path('student/selfUser', student_selfUser_api, name='student_selfUser_api'),
    path('student/add', student_add_api, name='student_add_api'),
    path('student/update', student_update_api, name='student_update_api'),
    path('student/del', student_delete_api, name='student_delete_api'),
    path('student/batch-add', student_batch_add_api, name='student_batch_add_api'),
    path('student/template-download', student_template_download_api, name='student_template_download_api'),
    path('class/list', class_list_api, name='class_list_api'),
    path('teacher/query', teacher_query_api, name='teacher_query_api'),
    path('teacher/add', teacher_add_api, name='teacher_add_api'),
    path('teacher/update', teacher_update_api, name='teacher_update_api'),
    path('teacher/del', teacher_delete_api, name='teacher_delete_api'),
    path('class/query', class_query_api, name='class_query_api'),
    path('class/add', class_add_api, name='class_add_api'),
    path('class/update', class_update_api, name='class_update_api'),
    path('class/del', class_del_api, name='class_del_api'),
    path('class/query/student', class_query_student_api, name='class_query_student_api'),
    path('course/query', course_query_api, name='course_query_api'),
    path('course/add', course_add_api, name='course_add_api'),
    path('course/update', course_update_api, name='course_update_api'),
    path('course/del', course_del_api, name='course_del_api'),
    path('attendance/query', attendance_query_api, name='attendance_query_api'),
    path('attendance/add', attendance_add_api, name='attendance_session_add_api'),
    path('attendance/update', attendance_update_api, name='attendance_update_api'),
    path('attendance/del', attendance_del_api, name='attendance_del_api'),
    path('attendance/student-active-sessions', student_active_attendance_sessions_api, name='student_active_attendance_sessions_api'),
    path('attendance/student-info', student_info_api, name='student_info_api'),
    path('face/add', face_add_api, name='face_add_api'),
    path('face/query', face_query_api, name='face_query_api'),
    path('face/check', face_check_api, name='face_check_api'),
    path('face/update', face_update_api, name='face_update_api'),
    path('leave/query', leave_query_api, name='leave_query_api'),
    path('leave/add', leave_add_api, name='leave_add_api'),
    path('leave/update', leave_update_api, name='leave_update_api'),
    path('leave/del', leave_del_api, name='leave_del_api'),
    path('leave/approve', leaveApproveApi, name='leave_approve_api'),
]