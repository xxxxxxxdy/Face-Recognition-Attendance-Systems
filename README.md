# Face Recognition Attendance System

一个基于 B/S 架构的人脸识别考勤系统。后端使用 Django + DRF，前端使用 Vue 3 + Vite + Element Plus，实现学生/教师/管理员多角色的考勤、请假与信息管理，支持人脸签到和 Excel 数据导出。

- 采用内置管理员账号密码admin/admin，内置管理员创建学生与老师。
## 特性

- 人脸签到：摄像头快速识别，防代打卡，签到体验自然
- 多角色权限：学生 / 教师 / 管理员，接口按角色精细授权（JWT + 自定义装饰器）
- 考勤会话：创建、修改、开启/关闭，支持结束时间与状态管理
- 请假流程：提交、审批、拒绝，教师按班级权限操作
- 数据管理：学生、教师、班级、课程的增删改查与关联校验
- 数据导出：按会话导出考勤 Excel，含状态统计与明细
- 安全基础：统一错误响应、CORS/CSRF 中间件、Token 校验、图片格式与大小检查

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Element Plus、ECharts（图表）、xlsx（Excel）
- 后端：Django、Django REST Framework、PyJWT、自定义认证装饰器
- 数据库：MySQL（示例：`face_attendance_db`）
- 人脸识别：基于 CNN（SFace/ArcFace/FaceNet 架构分析与可扩展）、Pillow 图像处理
- 存储：人脸图片存储于 `face_app/media`（`MEDIA_ROOT`）

## 目录结构

```
Face-Recognition-Attendance-System
├── face_recognition_frontend/        # Vue 前端
│   ├── src/views/                    # 页面：考勤、请假、用户中心等
│   ├── src/stores/                   # 状态管理
│   ├── .env.development              # 开发环境 API 地址
│   └── vite.config.ts
└── face_recognition_project/         # Django 后端
    ├── face_app/
    │   ├── views/                    # 业务接口（学生/教师/课程/考勤/人脸/请假）
    │   ├── decorators.py             # 自定义认证与授权（JWT/角色）
    │   ├── models.py                 # 数据模型
    │   ├── utils.py                  # 统一成功/错误响应
    │   └── media/                    # 人脸图片存储
    └── face_recognition_project/
        ├── settings.py               # 项目配置（CORS/DB/REST）
        └── urls.py                   # 路由入口
```

## 快速上手

### 后端（Django）

1) 配置数据库（MySQL）
- 创建数据库：`face_attendance_db`
- 修改 `settings.py` 中的 DB 账号与密码（默认演示为 `root` / `root`，请务必更改）

2) 安装依赖并初始化（Windows）
- 创建并激活虚拟环境：
  ```
  python -m venv venv
  ```
  ```
  .\venv\Scripts\activate
  ```
- 安装依赖（requirements 中不完整）：
  ```
  pip install -r requirements.txt
  ```
- 启动后端：
  ```
  python manage.py runserver
  ```

3) 媒体文件
- `MEDIA_ROOT` 默认在 `face_app/media`，请确保目录存在且服务用户有写权限。

### 前端（Vue 3）

1) 安装与启动
- 进入前端目录：
  ```
  cd face_recognition_frontend
  ```
- 安装依赖：
  ```
  npm install
  ```
- 配置 `.env.development`（示例，默认不需要处理）：
  ```
  VITE_API_BASE_URL=http://localhost:8000
  ```
- 开发启动：
  ```
  npm run dev
  ```

## 功能模块概览

- 登录认证：`POST /api/auth/login`（JWT Token）
- 学生信息：查询/新增/修改/删除，批量导入与模板下载
- 教师与课程：按教师权限管理课程与班级关联
- 考勤会话：创建、更新、开启/关闭、按班级查询
- 人脸管理：学生人脸图片上传与更新；人脸签到接口
- 请假流程：学生提交、教师审批/拒绝；状态与备注记录
- 数据导出：会话维度导出 Excel，包含状态统计与明细

> 具体路由请参考：`face_recognition_project/face_app/urls.py` 与各 `views/*.py`。

## 常见问题

- 启动后端提示依赖缺失  
  建议使用虚拟环境并安装 `requirements.txt`。如依赖版本不兼容，请在本地验证后使用 `pip freeze > requirements.txt` 重新生成并测试。目前本项目依赖文件有所缺失。

- MySQL 连接失败  
  检查数据库是否创建、账号密码是否正确、端口是否放通。Windows 下注意本地服务运行与权限配置。

- 人脸识别失败或准确度不稳定  
  保证人脸平面完整性，避免遮挡、角度异常。

## 研发与扩展

- 人脸识别算法可替换/升级：支持接入 ArcFace/FaceNet/SFace 等多种模型
- 异步任务：高并发签到建议接入任务队列（如 Celery + Redis）
- 日志与监控：建议接入 Sentry/ELK 做错误追踪与审计
- 接口文档：可补充 Swagger/OpenAPI 以利于前后端协作

注：当前 `requirements.txt` 依赖清单不完整，建议在本地环境验证后使用 `pip freeze > requirements.txt` 完整导出依赖并同步到仓库。
