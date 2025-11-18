from django.db import models
class StudentUser(models.Model):
    student_users_id = models.AutoField(primary_key=True,)
    student_id = models.CharField(max_length=64, unique=True)
    student_name = models.CharField(max_length=64)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=64, null=True, blank=True)
    class_id = models.CharField(max_length=64, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    email = models.CharField(max_length=255, null=True) 
    avatar = models.CharField(max_length=255, null=True) 
    phone = models.CharField(max_length=11, null=True) 
    login_time = models.DateTimeField(null=True) 

    @property
    def id(self):
        return self.student_users_id

    class Meta:
        db_table = 'student_users'

class Teacher(models.Model):
    user_id = models.AutoField(primary_key=True)
    login_time = models.DateTimeField(null=True, blank=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    username = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=64, null=True, blank=True)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=64, null=True, blank=True)

    @property
    def id(self):
        return self.pk

    class Meta:
        db_table = 'teacher'

class Administrators(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    login_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'administrators'

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=64)

    class Meta:
        db_table = 'course'

class ClassGroup(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=16)
    description = models.CharField(max_length=255, null=True)
    source_id = models.CharField(max_length=64)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'class_group'

class CourseStudentTeacher(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, db_column='teacher_id')

    class Meta:
        db_table = 'course_student_teacher'
        unique_together = (('course', 'teacher', 'class_group'),)


class AttendanceSession(models.Model):
    id = models.AutoField(primary_key=True)
    session_name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_session'

# 学生考勤
class StudentAttendance(models.Model):
    id = models.AutoField(primary_key=True)
    student_users_id = models.ForeignKey(StudentUser, on_delete=models.CASCADE, db_column='student_users_id')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    attendance_session_id = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, db_column='attendance_session_id')
    date = models.DateField()
    status = models.CharField(max_length=50)
    check_in_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'student_attendance'


class FaceInfo(models.Model):
    face_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(StudentUser, on_delete=models.CASCADE, db_column='user_id')
    face_img = models.ImageField(upload_to='face_images/', blank=True, null=True)
    capture_time = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = 'face_info'


class LeaveRequest(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey('StudentUser',on_delete=models.CASCADE,to_field='student_users_id', verbose_name="学生")
    start_time = models.DateTimeField(verbose_name="请假开始时间")
    end_time = models.DateTimeField(verbose_name="请假结束时间")
    reason = models.TextField(verbose_name="请假原因")
    leave_type = models.IntegerField(verbose_name="请假类型", choices=[(1, '病假'), (2, '事假')])
    status = models.CharField(max_length=20, default='pending', verbose_name="审批状态")
    approver_id = models.IntegerField(null=True, blank=True, verbose_name="审批人")
    approval_time = models.DateTimeField(null=True, blank=True, verbose_name="审批时间")
    comments = models.TextField(null=True, blank=True, verbose_name="审批意见")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'leave_request'