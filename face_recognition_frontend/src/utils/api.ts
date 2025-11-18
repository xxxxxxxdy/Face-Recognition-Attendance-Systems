import http from './http';

// 登录查询
export const login = (data: any) => {
    return http.post('/login', data).then(res => res.data);
};
// 首页查询
export const homeApi = () => http.get('/home').then(res => res.data);
// 获取当前角色的个人信息
export const profileApi = () => http.get('/profile').then(res => res.data);
// 修改个人信息接口
export const profileUpdateApi = (data: any) => http.put('/profile/update', data).then(res => res.data);
// 考勤查询
export const AttendanceQueryApi = () => http.get('/attendance/query').then(res => res.data);
// 教师查询
export const teachersApi = () => http.get('/teacher/query').then(res => res.data);
// 教师新增
export const teacherAddApi = (data: any) => http.post('/teacher/add', data).then(res => res.data);
// 教师编辑
export const teacherUpdateApi = (data: any) => http.put('/teacher/update', data).then(res => res.data);
// 教师删除
export const teacherDelApi = (data: any) => http.delete('/teacher/del', { data }).then(res => res.data);
// 学生查询
export const studentsApi = () => http.get('/student/query').then(res => res.data);
// 学生新增
export const studentAddApi = (data: any) => http.post('/student/add', data).then(res => res.data);
// 学生编辑
export const studentUpdateApi = (data: any) => http.put('/student/update', data).then(res => res.data);
// 学生删除
export const studentDelApi = (data: any) => http.delete('/student/del', { data }).then(res => res.data);
// 查询当前登录学生信息
export const studentSelfUserApi = () => http.get('/student/selfUser').then(res => res.data);
// 班级查询
export const classGroupsApi = () => http.get('/class/query').then(res => res.data);
// 获取所有班级列表（用于批量导入验证）
export const classListApi = () => http.get('/class/list').then(res => res.data);
// 班级更新
export const classGroupsUpdateApi = (data: any) => http.put('/class/update', data).then(res => res.data);
// 班级删除
export const classGroupsDelApi = (data: any) => http.delete('/class/del', { data }).then(res => res.data);
// 通过学号+姓名查询班级
export const classGroupsStudentIdApi = (data: any) => http.get('/class/query/student', { params: data }).then(res => res.data);
// 课程查询
export const courseQueryApi = () => http.get('/course/query').then(res => res.data);
// 课程新增
export const courseAddApi = (data: any) => http.post('/course/add', data).then(res => res.data);
// 课程修改
export const courseUpdateApi = (data: any) => http.put('/course/update', data).then(res => res.data);
// 课程删除
export const courseDelApi = (data: any) => http.delete('/course/del', { data }).then(res => res.data);
// 学生考勤查询 
export const studentActiveQueryApi = () => http.get('/attendance/student-active-sessions').then(res => res.data);
// 考勤新增
export const attendanceAddApi = (data: any) => http.post('/attendance/add', data).then(res => res.data);
// 考勤编辑
export const attendanceUpdateApi = (data: any) => http.put('/attendance/update', data).then(res => res.data);
// 考勤删除
export const attendanceDelApi = (data: any) => http.delete('/attendance/del', { data }).then(res => res.data);
// 考勤详情
export const attendanceDetailApi = (data: any) => http.get('/attendance/detail', { params: data }).then(res => res.data);
// 考勤学生信息内容
export const attendanceStudentInfoApi = (data: any) => http.get('/attendance/student-info', { params: data }).then(res => res.data);
// 新增学生人脸
export const faceAddApi = (data: any) => http.post('/face/add', data).then(res => res.data);
// 查询学生人脸
export const faceQueryApi = () => http.get('/face/query',).then(res => res.data);
// 更新学生人脸
export const faceUpdateApi = (data: any) => http.put('/face/update', data).then(res => res.data);
// 打卡验证
export const faceCheckApi = (data: any) => http.post('/face/check', data, { timeout: 10000 }).then(res => res.data);
// 查询请假
export const leaveQueryApi = () => http.get('/leave/query').then(res => res.data);
// 新增请假
export const leaveAddApi = (data: any) => http.post('/leave/add', data).then(res => res.data);
// 修改请假
export const leaveUpdateApi = (data: any) => http.put('/leave/update', data).then(res => res.data);
// 删除请假
export const leaveDelApi = (data: any) => http.delete('/leave/del', { data }).then(res => res.data);
// 请假批准接口
export const leaveApproveApi = (data: any) => http.post('/leave/approve', data).then(res => res.data);
