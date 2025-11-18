import { House, Notebook, Calendar, Document, User, Camera, Grid } from '@element-plus/icons-vue'

export const menuConfig = [
  {
    index: '1',
    title: '首页',
    icon: House,
    path: '/dashboard/home',
    permission: ['student', 'teacher', 'admin']
  },
  {
    index: '2',
    title: '课程管理',
    icon: Notebook,
    path: '/dashboard/course',
    permission: ['student', 'teacher', 'admin']
  },
  {
    index: '3',
    title: '考勤管理',
    icon: Calendar,
    path: '/dashboard/attendance',
    permission: ['teacher', 'admin']
  },
  {
    index: '4',
    title: '请假管理',
    icon: Document,
    path: '/dashboard/leave',
    permission: ['student', 'teacher', 'admin']
  },
  {
    index: '5',
    title: '班级管理',
    icon: Grid,
    path: '/dashboard/class',
    permission: ['teacher', 'admin']
  },
  {
    index: '6',
    title: '账号管理',
    icon: User,
    children: [
      { index: '5-1', title: '学生账号管理', path: '/dashboard/account/student', permission: ['teacher', 'admin'] },
      { index: '5-2', title: '教师账号管理', path: '/dashboard/account/teacher', permission: ['admin'] }
    ],
    permission: ['teacher', 'admin']
  },
  {
    index: '7',
    title: '人脸导入',
    icon: Camera,
    path: '/dashboard/face-import',
    permission: ['student', 'teacher', 'admin']
  },
  {
    index: '8',
    title: '学生考勤',
    icon: Calendar,
    path: '/dashboard/student-attendance',
    permission: ['student']
  }
]