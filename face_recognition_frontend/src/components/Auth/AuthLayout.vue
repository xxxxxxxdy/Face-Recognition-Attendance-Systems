<template>
  <div class="auth-container">
    <div class="form-wrapper">
      <h2 class="title">登录</h2>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="login-form">
        <el-form-item label="账号：" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码：" prop="password">
          <el-input type="password" v-model="loginForm.password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="登录身份">
          <el-radio-group v-model="selectedUserType">
            <el-radio label="student">学生</el-radio>
            <el-radio label="teacher">教师</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" class="login-button">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { login } from '@/utils/api';
import { useUserStore } from '@/stores/user';

export default defineComponent({
  name: 'AuthLayout',
  setup() {
    const router = useRouter();
    const loginFormRef = ref<any>(null);
    const selectedUserType = ref('student');

    const loginForm = reactive({
      username: '',
      password: '',
      user_type: selectedUserType.value,
    });

    const loginRules = reactive({
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
      ],
    });

    const handleLogin = async () => {
      if (!loginFormRef.value) return;
      loginFormRef.value.validate(async (valid: boolean) => {
        if (valid) {
          try {
            loginForm.user_type = selectedUserType.value;
            const response = await login({
              username: loginForm.username,
              password: loginForm.password,
              user_type: loginForm.user_type,
            });
            console.log(response);
            if (response.code === 200) {
              ElMessage.success(`登录成功！`);

              localStorage.setItem('token', response.data.token);
              localStorage.setItem('user_type', response.data.user_type);
              const userStore = useUserStore();
              userStore.setUserType(response.data.user_type);

              router.push('/dashboard/home');
            } else {
              ElMessage.error(response.message || '登录失败');
            }
          } catch (error: any) {
            ElMessage.error(error.response?.data?.message || error.message || '登录请求失败');
          }
        } else {
          ElMessage.error('请填写完整的登录信息');
          return false;
        }
      });
    };

    return {
      loginForm,
      loginRules,
      loginFormRef,
      handleLogin,
      selectedUserType,
    };
  },
});
</script>

<style scoped>
.auth-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: transparent;
  font-family: inherit;
  position: relative;
  overflow: hidden;
}

.auth-container::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 30%, rgba(96, 165, 250, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(167, 243, 208, 0.15) 0%, transparent 50%);
  z-index: 0;
}

.form-wrapper {
  position: relative;
  width: 24rem;
  padding: 2.5rem;
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-accent);
  display: flex;
  flex-direction: column;
  z-index: 1;
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.title {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-strong);
  font-size: 28px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-form :deep(.el-form-item__label) {
  color: var(--text);
  font-weight: 500;
}

.login-form .el-form-item {
  margin-bottom: var(--space-lg);
}

.login-form .el-radio {
  margin-left: var(--space-lg);
  margin-right: var(--space-sm);
}

.login-form :deep(.el-radio__label) {
  color: var(--text);
  font-weight: 500;
}

.login-form :deep(.el-radio__input.is-checked .el-radio__inner) {
  background: var(--gradient-primary);
  border-color: var(--primary);
}

.login-form :deep(.el-radio__input.is-checked + .el-radio__label) {
  color: var(--primary);
}

.login-button {
  width: 100%;
  margin-top: var(--space-md);
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
</style>