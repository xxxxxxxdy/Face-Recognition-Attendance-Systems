<template>
  <div class="home-container">
    <div class="welcome-card">
      <div class="welcome-header">
        <h1 class="welcome-title">欢迎来到课堂考勤系统</h1>
        <p class="welcome-subtitle">Welcome to Face Recognition Attendance System</p>
      </div>
      <div class="welcome-content">
        <p class="welcome-text">欢迎您，{{ userData?.data?.name }}！</p>
      </div>
    </div>

    <!-- 教师功能卡片 -->
    <div v-if="userStore.user_type === 'teacher'" class="features-grid">
      <div class="feature-card" @click="navigateTo('/dashboard/course')">
        <div class="feature-icon">
          <el-icon>
            <Reading />
          </el-icon>
        </div>
        <h3 class="feature-title">课程管理</h3>
        <p class="feature-desc">查看课程处理数据</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/account/student')">
        <div class="feature-icon">
          <el-icon>
            <User />
          </el-icon>
        </div>
        <h3 class="feature-title">学生管理</h3>
        <p class="feature-desc">学生信息数据管理</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/attendance')">
        <div class="feature-icon">
          <el-icon>
            <CircleCheck />
          </el-icon>
        </div>
        <h3 class="feature-title">考勤统计</h3>
        <p class="feature-desc">查看考勤数据分析</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/face-import')">
        <div class="feature-icon">
          <el-icon>
            <Camera />
          </el-icon>
        </div>
        <h3 class="feature-title">人脸导入</h3>
        <p class="feature-desc">进行人脸数据管理</p>
      </div>
    </div>

    <!-- 学生功能卡片 -->
    <div v-else-if="userStore.user_type === 'student'" class="features-grid">
      <div class="feature-card" @click="navigateTo('/dashboard/course')">
        <div class="feature-icon">
          <el-icon>
            <Reading />
          </el-icon>
        </div>
        <h3 class="feature-title">课程管理</h3>
        <p class="feature-desc">查看课程信息</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/leave')">
        <div class="feature-icon">
          <el-icon>
            <Document />
          </el-icon>
        </div>
        <h3 class="feature-title">请假管理</h3>
        <p class="feature-desc">申请和查看请假记录</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/face-import')">
        <div class="feature-icon">
          <el-icon>
            <Camera />
          </el-icon>
        </div>
        <h3 class="feature-title">人脸导入</h3>
        <p class="feature-desc">管理个人人脸数据</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/student-attendance')">
        <div class="feature-icon">
          <el-icon>
            <CircleCheck />
          </el-icon>
        </div>
        <h3 class="feature-title">学生考勤</h3>
        <p class="feature-desc">查看个人考勤记录</p>
      </div>
    </div>

    <!-- 其他身份（管理员等）功能卡片 -->
    <div v-else class="features-grid">
      <div class="feature-card" @click="navigateTo('/dashboard/course')">
        <div class="feature-icon">
          <el-icon>
            <Reading />
          </el-icon>
        </div>
        <h3 class="feature-title">课程管理</h3>
        <p class="feature-desc">查看课程处理数据</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/account/student')">
        <div class="feature-icon">
          <el-icon>
            <User />
          </el-icon>
        </div>
        <h3 class="feature-title">学生管理</h3>
        <p class="feature-desc">学生信息数据管理</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/attendance')">
        <div class="feature-icon">
          <el-icon>
            <CircleCheck />
          </el-icon>
        </div>
        <h3 class="feature-title">考勤统计</h3>
        <p class="feature-desc">查看考勤数据分析</p>
      </div>
      <div class="feature-card" @click="navigateTo('/dashboard/face-import')">
        <div class="feature-icon">
          <el-icon>
            <Camera />
          </el-icon>
        </div>
        <h3 class="feature-title">人脸导入</h3>
        <p class="feature-desc">管理个人人脸数据</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Reading, User, CircleCheck, Camera, Document } from '@element-plus/icons-vue'
import { homeApi } from '@/utils/api';
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

const userData = ref('')
const userStore = useUserStore()
const router = useRouter()

// 路由导航函数
const navigateTo = (path: string) => {
  router.push(path)
}

onMounted(async () => {
  userData.value = await homeApi()
})
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.welcome-card {
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-accent);
  padding: 3rem;
  text-align: center;
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-header {
  margin-bottom: 2rem;
}

.welcome-title {
  font-size: 36px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 var(--space-md) 0;
}

.welcome-subtitle {
  font-size: 18px;
  color: var(--muted);
  font-weight: 500;
  margin: 0;
}

.welcome-content {
  padding-top: var(--space-lg);
  border-top: 1px solid var(--divider);
}

.welcome-text {
  font-size: 16px;
  color: var(--text);
  margin: 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-xl);
  animation: fadeIn 0.8s ease-out 0.2s both;
}

.feature-card {
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-1);
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-accent);
  border-color: rgba(37, 99, 235, 0.2);
}

.feature-icon {
  margin-bottom: var(--space-lg);
  filter: drop-shadow(0 4px 8px rgba(37, 99, 235, 0.2));
}

.feature-icon :deep(.el-icon) {
  font-size: 48px;
  color: var(--primary);
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-strong);
  margin: 0 0 var(--space-md) 0;
}

.feature-desc {
  font-size: 14px;
  color: var(--muted);
  margin: 0;
  line-height: 1.6;
}
</style>