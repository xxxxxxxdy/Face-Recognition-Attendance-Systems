<template>
  <div class="profile-center">

    <div class="profile-content">
      <h2 style="text-align: center;">个人中心</h2>
      <!-- 头像上传区域 -->
      <div class="avatar-section" v-if="currentUserType !== 'admin'">
        <div class="avatar-container">
          <div class="avatar-wrapper">
            <!-- 显示头像或默认图标 -->
            <img v-if="avatarUrl" :src="getFullAvatarUrl(avatarUrl)" alt="头像" class="avatar-image" />
            <div v-else class="avatar-placeholder">
              <el-icon :size="60" color="#c0c4cc">
                <User />
              </el-icon>
            </div>

            <!-- 上传按钮覆盖层 -->
            <div class="avatar-overlay">
              <el-upload ref="uploadRef" :show-file-list="false" :before-upload="beforeAvatarUpload" action="#"
                :http-request="customUpload" accept="image/*">
                <el-button type="primary" size="small" :loading="uploading">
                  {{ uploading ? '上传中...' : (avatarUrl ? '更换头像' : '上传头像') }}
                </el-button>
              </el-upload>
            </div>
          </div>
        </div>
      </div>

      <!-- 个人信息表单 -->
      <el-form :model="formData" :rules="formRules" ref="profileForm" label-width="120px" class="profile-form">
        <!-- 学生信息字段 -->
        <template v-if="currentUserType === 'student'">
          <el-form-item label="姓名" prop="student_name">
            <el-input v-model="formData.student_name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="性别" prop="gender">
            <el-select v-model="formData.gender" placeholder="请选择性别">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="formData.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="formData.phone" placeholder="请输入手机号" />
          </el-form-item>
        </template>

        <!-- 教师信息字段 -->
        <template v-if="currentUserType === 'teacher'">
          <el-form-item label="姓名" prop="username">
            <el-input v-model="formData.username" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="性别" prop="gender">
            <el-select v-model="formData.gender" placeholder="请选择性别">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="formData.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="formData.email" placeholder="请输入邮箱" />
          </el-form-item>
        </template>

        <!-- 管理员信息字段 -->
        <template v-if="currentUserType === 'admin'">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="formData.username" placeholder="请输入用户名" />
          </el-form-item>
        </template>

        <!-- 密码修改字段 -->
        <div class="password-section">
          <el-form-item label="当前密码" prop="old_password">
            <el-input v-model="formData.old_password" type="password" placeholder="请输入当前密码（如需修改密码）" show-password />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input v-model="formData.new_password" type="password" placeholder="请输入新密码（如需修改密码）" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input v-model="formData.confirm_password" type="password" placeholder="请再次输入新密码（如需修改密码）"
              show-password />
          </el-form-item>
        </div>

        <el-form-item>
          <el-button type="primary" @click="updateProfile" :loading="updating">
            更新信息
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { homeApi, profileApi, profileUpdateApi } from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userInfo = ref<any>({})
const updating = ref(false)
const uploading = ref(false)
const profileForm = ref()
const uploadRef = ref()

// 头像URL
const avatarUrl = ref<string>('')

// 将相对路径转换为完整URL
const getFullAvatarUrl = (relativePath: string) => {
  if (!relativePath) return ''

  // 如果是base64数据URL（上传预览时），直接返回
  if (relativePath.startsWith('data:')) {
    return relativePath
  }

  // 如果已经是完整URL，直接返回
  if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
    return relativePath
  }

  // 如果是相对路径，拼接完整URL
  return `http://localhost:8000/media/${relativePath}`
}

// 表单数据（包含密码字段）
const formData = reactive<any>({
  // 密码字段
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 从Pinia store获取当前用户类型
const currentUserType = computed(() => {
  return userStore.user_type || 'student' // 默认为student
})

// 表单验证规则 - 所有字段都可以为空，只做格式验证
const formRules = computed(() => {
  const rules: any = {}

  // 邮箱格式验证（非必填）
  rules.email = [{
    type: 'email',
    message: '请输入正确的邮箱格式',
    trigger: 'blur',
    required: false
  }]

  // 手机号格式验证（非必填）
  rules.phone = [{
    pattern: /^1[3-9]\d{9}$/,
    message: '请输入正确的手机号',
    trigger: 'blur',
    required: false
  }]

  // 密码验证规则（只在输入时验证格式和一致性）
  if (formData.new_password || formData.confirm_password) {
    if (formData.new_password) {
      rules.old_password = [{ required: true, message: '修改密码时请输入当前密码', trigger: 'blur' }]
      rules.new_password = [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ]
    }
    if (formData.confirm_password) {
      rules.confirm_password = [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        {
          validator: (rule: any, value: string, callback: Function) => {
            if (value !== formData.new_password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
  }

  return rules
})



// 上传前验证
const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
    return false
  }
  return true
}

// 自定义上传函数
const customUpload = (options: any) => {
  const { file } = options
  uploading.value = true

  // 创建 FileReader 来预览图片
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarUrl.value = e.target?.result as string
    uploading.value = false
  }
  reader.readAsDataURL(file)
}

// 获取用户信息
const getUserInfo = async () => {
  try {
    // 首先获取用户类型
    const homeResponse = await homeApi()
    if (homeResponse.code === 200) {
      // 同步用户类型到Pinia store
      if (homeResponse.data.user_type) {
        userStore.setUserType(homeResponse.data.user_type)
      }
    }

    // 然后获取详细的个人信息
    const response = await profileApi()
    if (response.code === 200) {
      userInfo.value = response.data

      // 设置头像URL（保存相对路径，显示时转换为完整URL）
      avatarUrl.value = userInfo.value.avatar || ''

      // 根据用户类型初始化表单数据
      if (currentUserType.value === 'student') {
        Object.assign(formData, {
          student_name: userInfo.value.student_name || userInfo.value.name || '',
          gender: userInfo.value.gender || '',
          email: userInfo.value.email || '',
          phone: userInfo.value.phone || ''
        })
      } else if (currentUserType.value === 'teacher') {
        Object.assign(formData, {
          username: userInfo.value.name || '',
          gender: userInfo.value.gender || '',
          phone: userInfo.value.phone || '',
          email: userInfo.value.email || ''
        })
      } else if (currentUserType.value === 'admin') {
        Object.assign(formData, {
          username: userInfo.value.name || ''
        })
      }
    }
  } catch (error) {
    ElMessage.error('获取用户信息失败')
    console.error('获取用户信息错误:', error)
  }
}

// 检查是否有任何字段有值
const hasAnyValue = (data: any) => {
  const fieldsToCheck = [
    'student_name', 'username', 'email', 'phone', 'gender', 'age', 'major', 'class_name',
    'old_password', 'new_password'  // 不包括confirm_password，因为它只是前端校验用的
  ]

  // 检查头像是否有值
  if (avatarUrl.value && avatarUrl.value.trim() !== '') {
    return true
  }

  // 检查表单字段是否有值
  return fieldsToCheck.some(field => {
    const value = data[field]
    return value !== undefined && value !== null && value !== ''
  })
}

// 更新个人信息（包含头像）
const updateProfile = async () => {
  if (!profileForm.value) return

  try {
    console.log('开始表单验证...')
    await profileForm.value.validate()
    console.log('表单验证通过')

    // 检查是否有任何字段有值
    if (!hasAnyValue(formData)) {
      ElMessage.warning('请至少填写一个字段后再提交')
      return
    }

    updating.value = true

    // 准备提交的数据 - 包含页面中的所有数据
    const submitData = {
      ...formData,
      avatar: avatarUrl.value, // 将头像URL包含在个人信息中
      user_type: currentUserType.value // 添加用户类型信息
    }

    // 密码处理：只传递旧密码和新密码，不传递确认密码
    if (submitData.confirm_password !== undefined) {
      delete submitData.confirm_password
    }

    // 确保密码字段始终存在，即使为空
    if (!submitData.old_password) {
      submitData.old_password = ''
    }
    if (!submitData.new_password) {
      submitData.new_password = ''
    }

    console.log('提交的数据:', submitData)
    console.log('开始调用更新接口...')

    // 调用真实更新接口
    const res = await profileUpdateApi(submitData)
    console.log('接口返回结果:', res)
    if (res && res.code === 200) {
      ElMessage.success('信息更新成功')

      // 如果修改了密码，清空密码字段
      if (formData.old_password || formData.new_password || formData.confirm_password) {
        formData.old_password = ''
        formData.new_password = ''
        formData.confirm_password = ''
      }

      // 更新成功后刷新用户信息
      await getUserInfo()

      // 刷新页面
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } else {
      ElMessage.error(res?.message || '更新失败')
    }

    updating.value = false


  } catch (error) {
    console.error('更新信息失败:', error)
    console.log('错误详情:', error)
    if (error && typeof error === 'object' && 'message' in error) {
      ElMessage.error(`验证失败: ${error.message}`)
    } else {
      ElMessage.error('表单验证失败，请检查输入信息')
    }
    updating.value = false
  }
}



onMounted(() => {
  getUserInfo()
})
</script>

<style scoped>
.profile-center {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.profile-header {
  text-align: center;
  margin-bottom: 32px;
}

.profile-header h2 {
  color: #303133;
  margin-bottom: 8px;
}

.profile-header p {
  color: #909399;
  margin: 0;
}

.profile-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.avatar-section {
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
}

.avatar-container {
  position: relative;
  display: inline-block;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.avatar-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f0f0f0;
  display: block;
}

.avatar-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: #f5f7fa;
  border: 4px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-overlay {
  margin-top: 16px;
}

.profile-form {
  max-width: 500px;
  margin: 0 auto;
}

.password-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.password-section h3 {
  color: #303133;
  margin-bottom: 24px;
  text-align: center;
}

.password-form {
  max-width: 500px;
  margin: 0 auto;
}

.el-form-item {
  margin-bottom: 24px;
}

.el-button {
  width: 100%;
}
</style>