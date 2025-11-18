<template>
  <div class="teacher-account-management-container">
    <div class="top-bar">
      <h2>教师账号管理</h2>
      <el-button type="primary" @click="handleAddTeacher">新增教师</el-button>
    </div>

    <!-- 功能操作区 -->
    <div class="action-bar">
      <div class="search-area">
        <el-input v-model="searchKeyword" placeholder="搜索教师姓名或手机号" clearable style="width: 300px;"
          @clear="handleSearch">
          <template #prefix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input>
        <el-button @click="handleSearch" style="margin-left: 12px;">搜索</el-button>
      </div>
      <div class="action-buttons">
        <el-button @click="handleRefresh">
          <el-icon>
            <Refresh />
          </el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="content-area">
      <el-empty v-if="error" :description="error" />
      <el-empty v-else-if="teacherData.length === 0" description="暂无数据" />
      <el-table v-else :data="filteredTeacherData" style="width: 100%" border stripe highlight-current-row
        :row-style="{ height: '60px' }">
        <el-table-column type="index" label="序号" width="100" align="center" />
        <el-table-column prop="teacher_name" label="姓名" width="120" align="center" />
        <el-table-column label="头像" width="120" align="center">
          <template #default="scope">
            <el-avatar :src="getAvatarUrl(scope.row.avatar)" :size="40" style=" border-radius: 4px;" />
          </template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" width="120" align="center" />
        <el-table-column prop="phone" label="手机号" width="150" align="center" />
        <el-table-column prop="login_time" label="上次登录时间" width="250" align="center">
          <template #default="scope">
            {{ formatLoginTime(scope.row.login_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(scope.row)" style="margin: 0 8px;">修改</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增教师弹窗 -->
    <el-dialog v-model="dialogVisible" title="新增教师" width="500px">
      <el-form :model="newTeacherForm" ref="newTeacherFormRef" :rules="rules" label-width="90px">
        <el-form-item prop="teacher_name">
          <template #label>
            姓名
          </template>
          <el-input v-model="newTeacherForm.teacher_name" placeholder="请输入2-10位姓名" />
        </el-form-item>
        <el-form-item prop="gender">
          <template #label>
            性别
          </template>
          <el-radio-group v-model="newTeacherForm.gender">
            <el-radio label="男" style="margin-right: 24px;">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item prop="phone_number">
          <template #label>
            手机号
          </template>
          <el-input v-model="newTeacherForm.phone_number" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item prop="password">
          <template #label>
            密码
          </template>
          <el-input v-model="newTeacherForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <template #label>
            确认密码
          </template>
          <el-input v-model="newTeacherForm.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看教师详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="教师详细信息" width="500px" :close-on-click-modal="false">
      <div class="teacher-detail">
        <div class="detail-item">
          <label>姓名：</label>
          <span>{{ viewTeacherData.teacher_name }}</span>
        </div>
        <div class="detail-item">
          <label>性别：</label>
          <span>{{ viewTeacherData.gender }}</span>
        </div>
        <div class="detail-item">
          <label>手机号：</label>
          <span>{{ viewTeacherData.phone }}</span>
        </div>
        <div class="detail-item">
          <label>上次登录：</label>
          <span>{{ formatLoginTime(viewTeacherData.login_time) }}</span>
        </div>
        <div class="detail-item">
          <label>头像：</label>
          <el-avatar :src="getAvatarUrl(viewTeacherData.avatar)" :size="80" fit="cover" />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="viewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑教师弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑教师信息" width="500px" :close-on-click-modal="false"
      @close="handleEditClose">
      <el-form ref="editTeacherFormRef" :model="editTeacherForm" :rules="editRules" label-width="90px">
        <el-form-item label="姓名" prop="teacher_name">
          <el-input v-model="editTeacherForm.teacher_name" placeholder="请输入教师姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="editTeacherForm.gender">
            <el-radio label="男" style="margin-right: 24px;">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="手机号" prop="phone_number">
          <el-input v-model="editTeacherForm.phone_number" placeholder="请输入手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleEditClose">取消</el-button>
          <el-button type="primary" @click="submitEditForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { ElTable, ElTableColumn, ElEmpty, ElButton, ElAvatar, ElDialog, ElForm, ElFormItem, ElInput, ElRadioGroup, ElRadio, ElSelect, ElOption, ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { teachersApi, teacherAddApi, teacherUpdateApi, teacherDelApi } from '@/utils/api'
import avatar from '@/assets/icons/avatar.png'
const teacherData = ref<any[]>([]);
const error = ref<string | null>(null);
const dialogVisible = ref(false);
const newTeacherFormRef = ref<FormInstance>();
const searchKeyword = ref('');

const newTeacherForm = reactive({
  teacher_name: '',
  gender: '男',
  phone_number: '',
  password: '',
  confirmPassword: '',
});

const validatePass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== newTeacherForm.password) {
    callback(new Error('两次输入的密码不一致!'));
  } else {
    callback();
  }
};

const rules = reactive({
  teacher_name: [
    { required: true, message: '请输入教师姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'blur' },
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' },
  ],
  phone_number: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, validator: validatePass, trigger: 'blur' },
  ],
});

// 过滤后的数据
const filteredTeacherData = computed(() => {
  let data = teacherData.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter((item: any) =>
      item.teacher_name?.toLowerCase().includes(keyword) ||
      item.phone?.includes(keyword)
    )
  }

  return data
})

// 搜索
const handleSearch = () => {
  // 搜索逻辑已在computed中实现
}

// 刷新
const handleRefresh = async () => {
  searchKeyword.value = ''
  await fetchTeacherData()
  ElMessage.success('刷新成功')
}

// 查看教师详情弹窗
const viewDialogVisible = ref(false)
const viewTeacherData = ref({})

// 编辑教师弹窗
const editDialogVisible = ref(false)
const editTeacherFormRef = ref<FormInstance>()
const editTeacherForm = reactive({
  teacher_id: '',
  teacher_name: '',
  gender: '男',
  phone_number: ''
})

const handleView = (row: any) => {
  viewTeacherData.value = { ...row }
  viewDialogVisible.value = true
};

const handleEdit = (row: any) => {
  // 填充编辑表单
  editTeacherForm.teacher_id = row.teacher_id
  editTeacherForm.teacher_name = row.teacher_name
  editTeacherForm.gender = row.gender
  // 修复：后端返回的字段名是 phone，不是 phone_number
  editTeacherForm.phone_number = row.phone

  editDialogVisible.value = true
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除教师 "${row.teacher_name}" (手机号: ${row.phone}) 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    const response = await teacherDelApi({ teacher_id: row.teacher_id })
    if (response.code === 200) {
      ElMessage.success('教师删除成功')
      await fetchTeacherData()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      const backendMsg = error?.response?.data?.message || error?.response?.data?.detail || error.message;
      ElMessage.error('删除失败: ' + backendMsg)
      console.error('删除教师失败:', error)
    }
  }
};

// 提交编辑表单
const submitEditForm = async () => {
  if (!editTeacherFormRef.value) return
  editTeacherFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        const response = await teacherUpdateApi({
          teacher_id: editTeacherForm.teacher_id,
          teacher_name: editTeacherForm.teacher_name,
          gender: editTeacherForm.gender,
          phone: editTeacherForm.phone_number
        })

        if (response.code === 200) {
          ElMessage.success('教师信息更新成功')
          editDialogVisible.value = false
          await fetchTeacherData()
        } else {
          const backendMsg = response?.response?.data?.message || response?.response?.data?.detail || response.message;
          ElMessage.error('更新失败: ' + backendMsg)
          console.error('更新教师失败:', response)
        }
      } catch (error) {
        const backendMsg = error?.response?.data?.message || error?.response?.data?.detail || error.message;
        ElMessage.error('更新失败: ' + backendMsg)
        console.error('更新教师失败:', error)
      }
    }
  })
}

// 关闭编辑弹窗
const handleEditClose = () => {
  editDialogVisible.value = false
  // 重置表单
  Object.assign(editTeacherForm, {
    teacher_id: '',
    teacher_name: '',
    gender: '男',
    phone_number: ''
  })
}

// 编辑表单验证规则
const editRules = reactive({
  teacher_name: [
    { required: true, message: '请输入教师姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'blur' },
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' },
  ],
  phone_number: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
})

const handleAddTeacher = () => {
  dialogVisible.value = true;
  if (newTeacherFormRef.value) {
    newTeacherFormRef.value.resetFields();
  }
  // 重置所有表单字段
  newTeacherForm.teacher_name = '';
  newTeacherForm.gender = '男';
  newTeacherForm.phone_number = '';
  newTeacherForm.password = '';
  newTeacherForm.confirmPassword = '';
};

const submitForm = async () => {
  if (!newTeacherFormRef.value) return;
  newTeacherFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        const response = await teacherAddApi(newTeacherForm);
        if (response.code === 200) {
          ElMessage.success('教师添加成功');
          dialogVisible.value = false;
          await fetchTeacherData();
        } else {
          const backendMsg = response?.response?.data?.message || response?.response?.data?.detail || response.message;
          ElMessage.error('教师添加失败: ' + backendMsg);
          console.error('添加教师失败:', err);
        }
      } catch (err: any) {
        const backendMsg = err?.response?.data?.message || err?.response?.data?.detail || err.message;
        ElMessage.error('教师添加失败: ' + backendMsg);
        console.error('添加教师失败:', err);
      }
    } else {
      console.log('表单验证失败');
    }
  });
};

// 格式化登录时间
const formatLoginTime = (loginTime: string | null) => {
  if (!loginTime) {
    return '从未登录';
  }
  try {
    const date = new Date(loginTime);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch (error) {
    return '时间格式错误';
  }
};

// 获取头像URL
const getAvatarUrl = (avatarPath: string | null) => {
  if (!avatarPath) {
    return avatar; // 返回默认头像
  }
  // 如果是完整的URL，直接返回
  if (avatarPath.startsWith('http://') || avatarPath.startsWith('https://')) {
    return avatarPath;
  }
  // 如果是相对路径，拼接后端服务器地址
  return `http://localhost:8000/media/${avatarPath.startsWith('/') ? '' : '/'}${avatarPath}`;
};

const fetchTeacherData = async () => {
  try {
    const response = await teachersApi();
    if (response.code === 200) {
      // 确保 response.data 是一个数组，如果不是则设置为空数组
      teacherData.value = Array.isArray(response.data) ? response.data : [];
    } else {
      error.value = response.message || '查询失败';
      teacherData.value = [];
    }
  } catch (err: any) {
    error.value = '请求失败: ' + backendMsg;
    teacherData.value = [];
    console.error('查询教师数据失败:', err);
  }
};

onMounted(async () => {
  await fetchTeacherData();
});
</script>

<style scoped>
.teacher-account-management-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--space-xl);
}

.top-bar {
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  padding: var(--space-xl);
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.top-bar h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-strong);
}

.action-bar {
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  padding: var(--space-lg) var(--space-xl);
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-md);
}

.search-area {
  display: flex;
  align-items: center;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.content-area {
  flex-grow: 1;
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-1);
  padding: var(--space-xl);
}

.content-area :deep(.el-table) {
  background: transparent;
}

.content-area :deep(.el-table th) {
  background: var(--table-header);
  font-weight: 600;
  color: var(--text);
}

.content-area :deep(.el-avatar) {
  border: 2px solid var(--divider);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  background-color: transparent !important;
}

.teacher-detail {
  padding: 20px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item label {
  font-weight: 600;
  color: #606266;
  width: 90px;
  flex-shrink: 0;
}

.detail-item span {
  color: #303133;
  font-size: 14px;
}
</style>