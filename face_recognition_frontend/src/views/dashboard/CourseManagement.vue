<template>
  <div class="course-management-container">
    <div class="top-bar">
      <h2>课程管理</h2>
      <el-button v-if="userStore.user_type !== 'student'" type="primary" @click="handleAddCourse">新增课程</el-button>
    </div>

    <!-- 功能操作区 -->
    <div class="action-bar">
      <div class="search-area">
        <el-input v-model="searchKeyword" placeholder="搜索课程名称或教师名" clearable style="width: 300px;"
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
      <el-empty v-else-if="courseData.length === 0" description="暂无数据" />
      <el-table v-else :data="filteredCourseData" style="width: 100%" border stripe>
        <el-table-column label="序号" width="80" align="center">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="course_name" label="课程名" width="200" align="center" />
        <el-table-column prop="username" label="指导老师" width="150" align="center" />
        <el-table-column prop="class_name" label="班级名称" />
        <el-table-column label="操作" width="250" align="center" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button v-if="userStore.user_type !== 'student'" size="small" type="warning"
              @click="handleEdit(scope.row)">修改</el-button>
            <el-button v-if="userStore.user_type !== 'student'" size="small" type="danger"
              @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增课程对话框 -->
    <el-dialog v-model="isAddCourseDialogVisible" title="新增课程" width="500px">
      <el-form :model="newCourseForm" :rules="newCourseRules" ref="newCourseFormRef" label-width="100px">
        <el-form-item label="课程名" prop="course_name">
          <el-input v-model="newCourseForm.course_name"></el-input>
        </el-form-item>
        <el-form-item label="选择老师" prop="teacher_id">
          <el-select v-model="newCourseForm.teacher_id" placeholder="请选择老师">
            <el-option v-for="teacher in teachers" :key="teacher.teacher_id" :label="teacher.teacher_name"
              :value="teacher.teacher_id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="选择班级" prop="class_ids">
          <el-select v-model="newCourseForm.class_ids" multiple placeholder="请选择班级">
            <el-option v-for="classGroup in classGroups" :key="classGroup.class_id" :label="classGroup.class_name"
              :value="classGroup.class_id"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleCancelAddCourse">取消</el-button>
          <el-button type="primary" @click="submitAddCourseForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 修改课程对话框 -->
    <el-dialog v-model="isEditCourseDialogVisible" title="修改课程" width="500px">
      <el-form :model="editCourseForm" :rules="editCourseRules" ref="editCourseFormRef" label-width="100px">
        <el-form-item label="课程名" prop="course_name">
          <el-input v-model="editCourseForm.course_name"></el-input>
        </el-form-item>
        <el-form-item label="选择老师" prop="teacher_id">
          <el-select v-model="editCourseForm.teacher_id" placeholder="请选择老师">
            <el-option v-for="teacher in teachers" :key="teacher.teacher_id" :label="teacher.teacher_name"
              :value="teacher.teacher_id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="选择班级" prop="class_ids">
          <el-select v-model="editCourseForm.class_ids" multiple placeholder="请选择班级">
            <el-option v-for="classGroup in classGroups" :key="classGroup.class_id" :label="classGroup.class_name"
              :value="classGroup.class_id"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleCancelEditCourse">取消</el-button>
          <el-button type="primary" @click="submitEditCourseForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 课程详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="课程详情" width="600px">
      <div v-if="currentCourse" class="course-details">
        <div class="detail-row">
          <span class="detail-label">课程ID：</span>
          <span class="detail-value">{{ currentCourse.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">课程名称：</span>
          <span class="detail-value">{{ currentCourse.course_name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">指导老师：</span>
          <span class="detail-value">{{ currentCourse.username }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">班级名称：</span>
          <span class="detail-value">{{ currentCourse.class_name }}</span>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, computed } from 'vue'
import request from '../../utils/http'
import { ElTable, ElTableColumn, ElEmpty, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { teachersApi, classGroupsApi, courseQueryApi, courseAddApi } from '@/utils/api'
import { courseUpdateApi, courseDelApi } from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const courseData = ref<any[]>([])
const error = ref<string | null>(null)
const searchKeyword = ref('')
const isAddCourseDialogVisible = ref(false) // 控制新增课程对话框的显示
const isEditCourseDialogVisible = ref(false) // 控制修改课程对话框的显示
const viewDialogVisible = ref(false) // 控制查看详情对话框的显示
const currentCourse = ref<any>(null) // 当前查看的课程
const newCourseFormRef = ref<FormInstance>() // 表单实例引用
const editCourseFormRef = ref<FormInstance>() // 修改表单实例引用
const newCourseForm = ref({
  course_name: '',
  teacher_id: null,
  class_ids: [],
})
const editCourseForm = ref({
  id: null,
  course_name: '',
  teacher_id: null,
  class_ids: [],
})

// 表单验证规则
const newCourseRules = {
  course_name: [
    { required: true, message: '请输入课程名', trigger: 'blur' },
  ],
  teacher_id: [
    { required: true, message: '请选择老师', trigger: 'change' },
  ],
  class_ids: [
    { type: 'array' as const, required: true, message: '请选择班级', trigger: 'change' },
  ],
}

const editCourseRules = {
  course_name: [
    { required: true, message: '请输入课程名', trigger: 'blur' },
  ],
  teacher_id: [
    { required: true, message: '请选择老师', trigger: 'change' },
  ],
  class_ids: [
    { type: 'array' as const, required: true, message: '请选择班级', trigger: 'change' },
  ],
}

const teachers = ref<any[]>([])
const classGroups = ref<any[]>([])

// 过滤后的数据
const filteredCourseData = computed(() => {
  let data = courseData.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter((item: any) =>
      item.course_name?.toLowerCase().includes(keyword) ||
      item.username?.toLowerCase().includes(keyword)
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
  await fetchCourseData()
  ElMessage.success('刷新成功')
}

const handleAddCourse = () => {
  // 重置表单
  resetForm()
  isAddCourseDialogVisible.value = true
  fetchTeachersAndClassGroups()
}

// 重置表单
const resetForm = () => {
  newCourseForm.value = {
    course_name: '',
    teacher_id: null,
    class_ids: [],
  }
  if (newCourseFormRef.value) {
    newCourseFormRef.value.clearValidate()
  }
}

// 取消新增课程
const handleCancelAddCourse = () => {
  resetForm()
  isAddCourseDialogVisible.value = false
}

const submitAddCourseForm = async () => {
  if (!newCourseFormRef.value) return
  newCourseFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const response = await courseAddApi(newCourseForm.value)
        if (response.code === 200) {
          ElMessage.success('课程新增成功')
          resetForm()
          isAddCourseDialogVisible.value = false
          fetchCourseData()
        } else {
          ElMessage.error(response.message || '课程新增失败')
        }
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '请求失败')
        console.error('新增课程失败:', error)
      }
    } else {
      ElMessage.error('请填写完整信息')
    }
  })
}

const fetchCourseData = async () => {
  try {
    const response = await courseQueryApi()
    if (response.code === 200) {
      courseData.value = response.data
    } else {
      ElMessage.error(response.message || '查询失败')
      courseData.value = []
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '请求失败')
    courseData.value = []
    console.error('查询课程数据失败:', error)
  }
}

const fetchTeachersAndClassGroups = async () => {
  try {
    const teachersResponse = await teachersApi()
    if (teachersResponse.code === 200) {
      if (Array.isArray(teachersResponse.data)) {
        teachers.value = teachersResponse.data
      } else {
        teachers.value = [teachersResponse.data]
      }
      console.log('教师数据:', teachers.value)
    } else {
      ElMessage.error(teachersResponse.message || '获取老师列表失败')
    }

    const classGroupsResponse = await classGroupsApi()
    if (classGroupsResponse.code === 200) {
      classGroups.value = classGroupsResponse.data
    } else {
      ElMessage.error(classGroupsResponse.message || '获取班级列表失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || '获取老师或班级列表失败')
    console.error('获取老师或班级列表失败:', error)
  }
}

// 查看课程详情
const handleView = (row: any) => {
  currentCourse.value = row
  viewDialogVisible.value = true
  console.log('查看课程详情:', row)
}

// 编辑课程
const handleEdit = (row: any) => {
  // 填充编辑表单数据
  editCourseForm.value = {
    id: row.id,
    course_name: row.course_name,
    teacher_id: row.teacher_id,
    class_ids: row.class_ids || []
  }
  isEditCourseDialogVisible.value = true
  console.log('编辑课程:', row)
}

// 提交修改课程表单
const submitEditCourseForm = async () => {
  if (!editCourseFormRef.value) return

  try {
    await editCourseFormRef.value.validate()

    const response = await courseUpdateApi(editCourseForm.value)
    if (response.code === 200) {
      ElMessage.success('修改课程成功')
      resetEditForm()
      isEditCourseDialogVisible.value = false
      await fetchCourseData()
    } else {
      ElMessage.error(response.message || '修改课程失败')
    }
  } catch (error: any) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      console.error('修改课程失败:', error)
    }
  }
}

// 取消修改课程
const handleCancelEditCourse = () => {
  resetEditForm()
  isEditCourseDialogVisible.value = false
}

// 重置修改表单
const resetEditForm = () => {
  editCourseForm.value = {
    id: null,
    course_name: '',
    teacher_id: null,
    class_ids: []
  }
  if (editCourseFormRef.value) {
    editCourseFormRef.value.clearValidate()
  }
}

// 删除课程
const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定删除课程"${row.course_name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const response = await courseDelApi({ id: row.id })
      if (response.code === 200) {
        ElMessage.success(response.message || '删除成功')
        await fetchCourseData()
      } else {
        ElMessage.error(response.message || '删除失败')
      }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '删除失败')
      console.error('删除课程失败:', error)
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

onMounted(async () => {
  await fetchCourseData()
  // 只有教师和管理员需要获取教师和班级数据
  if (userStore.user_type !== 'student') {
    await fetchTeachersAndClassGroups()
  }
})
</script>

<style scoped>
.course-management-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--space-xl);
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.top-bar h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-area {
  display: flex;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.content-area {
  /* flex-grow: 1; */
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border-radius: var(--radius-card);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-1);
  padding: var(--space-xl);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 课程详情样式 */
.course-details {
  padding: 20px;
}

.detail-row {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.detail-label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
  margin-right: 16px;
}

.detail-value {
  color: #333;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .search-area {
    justify-content: center;
  }

  .action-buttons {
    justify-content: center;
  }

  .top-bar {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
}
</style>