<template>
  <div class="student-account-management-container">
    <div class="top-bar">
      <h2>学生账号管理</h2>
      <div class="top-bar-buttons">
        <el-button type="success" @click="downloadTemplate" size="medium">下载模板</el-button>
        <el-button type="warning" @click="handleBatchImport" size="medium">批量导入</el-button>
        <el-button type="primary" @click="handleAddStudent" size="medium">新增学生</el-button>
      </div>
    </div>

    <!-- 功能操作区 -->
    <div class="action-bar">
      <div class="search-area">
        <el-input v-model="searchKeyword" placeholder="搜索学生姓名或学号" clearable style="width: 300px;" @clear="handleSearch">
          <template #prefix>
            <el-icon>
              <Search />
            </el-icon>
          </template>
        </el-input>
        <el-button @click="handleSearch" style="margin-left: 12px;">搜索</el-button>
      </div>
      <div class="action-buttons">
        <el-select v-model="classFilter" placeholder="筛选班级" style="width: 140px; margin-right: 12px;"
          @change="handleFilterChange" clearable>
          <el-option label="全部班级" value=""></el-option>
          <el-option v-for="cls in uniqueClasses" :key="cls" :label="cls" :value="cls"></el-option>
        </el-select>
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
      <el-empty v-else-if="studentData === null" description="加载中..." />
      <el-table v-else :data="filteredStudentData" style="width: 100%" border stripe highlight-current-row
        :row-style="{ height: '60px' }">
        <el-table-column type="index" label="序号" width="80" align="center" />
        <el-table-column prop="student_id" label="学号" width="140" align="center" />
        <el-table-column prop="student_name" label="学生姓名" width="160" align="center" />
        <el-table-column label="头像" width="120" align="center">
          <template #default="scope">
            <div v-if="scope.row.avatar && scope.row.avatar.trim() !== ''">
              <el-avatar :src="getFullAvatarUrl(scope.row.avatar)" size="40"
                style="border: 1px solid #e5e7eb; border-radius: 4px;" />
            </div>
            <div v-else style="color: #999; font-size: 12px;">
              暂无头像信息
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" width="80" align="center" />
        <el-table-column prop="class_name" label="班级" align="center" />
        <el-table-column label="操作" width="220" align="center">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(scope.row)" style="margin: 0 8px;">修改</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 批量导入弹窗 -->
    <el-dialog v-model="batchImportVisible" title="批量导入学生" width="600px" :before-close="handleBatchImportClose">
      <div class="batch-import-content">
        <div class="import-steps">
          <h4>导入步骤：</h4>
          <ol>
            <li>点击"下载模板"按钮下载Excel模板文件</li>
            <li>按照模板格式填写学生信息</li>
            <li>上传填写好的Excel文件</li>
            <li>点击"开始导入"完成批量添加</li>
          </ol>
        </div>

        <div class="file-upload-area">
          <el-upload ref="uploadRef" :auto-upload="false" :show-file-list="true" :limit="1" accept=".xlsx,.xls"
            :on-change="handleFileChange" :on-remove="handleFileRemove" drag>
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将Excel文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 .xlsx/.xls 文件，且不超过 10MB
              </div>
            </template>
          </el-upload>
        </div>

        <div v-if="importPreviewData.length > 0" class="preview-area">
          <h4>数据预览（前5条）：</h4>
          <el-table :data="importPreviewData.slice(0, 5)" border size="small">
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="student_name" label="姓名" width="100" />
            <el-table-column prop="gender" label="性别" width="80" />
            <el-table-column prop="class_name" label="班级" />
          </el-table>
          <p class="preview-info">共 {{ importPreviewData.length }} 条数据</p>

          <!-- 验证错误显示 -->
          <div v-if="validationErrors.length > 0" class="validation-errors">
            <h4 style="color: #f56c6c; margin-bottom: 10px;">
              <i class="el-icon-warning"></i> 数据验证失败（{{ validationErrors.length }} 个错误）：
            </h4>
            <div class="error-list">
              <div v-for="(error, index) in validationErrors" :key="index" class="error-item">
                {{ error }}
              </div>
            </div>
            <p style="color: #f56c6c; margin-top: 10px; font-size: 14px;">
              请修正以上错误后重新上传文件
            </p>
          </div>

          <div v-else-if="importPreviewData.length > 0" class="validation-success">
            <p style="color: #67c23a; margin-top: 10px; font-size: 14px;">
              <i class="el-icon-success"></i> 数据验证通过，可以开始导入
            </p>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button size="medium" @click="batchImportVisible = false">取消</el-button>
          <el-button type="success" size="medium" @click="downloadTemplate">下载模板</el-button>
          <el-button type="primary" size="medium" @click="submitBatchImport"
            :disabled="importPreviewData.length === 0 || validationErrors.length > 0" :loading="importing">
            {{ importing ? '导入中...' : '开始导入' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 新增学生弹窗 -->
    <el-dialog v-model="dialogVisible" title="新增学生" width="500px" :before-close="handleClose">
      <el-form :model="newStudentForm" ref="newStudentFormRef" :rules="rules" label-width="90px">
        <el-form-item prop="student_id">
          <template #label>
            学号
          </template>
          <el-input v-model="newStudentForm.student_id" placeholder="请输入6-18位学号" size="medium" />
        </el-form-item>
        <el-form-item prop="student_name">
          <template #label>
            姓名
          </template>
          <el-input v-model="newStudentForm.student_name" placeholder="请输入2-10位姓名" size="medium" />
        </el-form-item>
        <el-form-item prop="gender">
          <template #label>
            性别
          </template>
          <el-radio-group v-model="newStudentForm.gender" size="medium">
            <el-radio label="男" style="margin-right: 24px;">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item prop="class_id">
          <template #label>
            班级
          </template>
          <el-select v-model="newStudentForm.class_id" placeholder="请选择班级" size="medium" style="width: 100%;">
            <el-option v-for="item in classOptions" :key="item.class_id" :label="item.class_name"
              :value="item.class_id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button size="medium" @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" size="medium" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看学生详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="学生详细信息" width="500px" :close-on-click-modal="false">
      <div class="student-detail">
        <div class="detail-item">
          <label>学号：</label>
          <span>{{ viewStudentData.student_id }}</span>
        </div>
        <div class="detail-item">
          <label>姓名：</label>
          <span>{{ viewStudentData.student_name }}</span>
        </div>
        <div class="detail-item">
          <label>性别：</label>
          <span>{{ viewStudentData.gender }}</span>
        </div>
        <div class="detail-item">
          <label>班级：</label>
          <span>{{ viewStudentData.class_name }}</span>
        </div>
        <div class="detail-item">
          <label>头像：</label>
          <el-avatar v-if="viewStudentData.avatar && viewStudentData.avatar.trim() !== ''" :src="getFullAvatarUrl(viewStudentData.avatar)" :size="80"
            fit="cover" />
          <span v-else style="color: #999; font-size: 14px;">暂无头像信息</span>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="viewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑学生弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑学生信息" width="500px" :close-on-click-modal="false"
      @close="handleEditClose">
      <el-form ref="editStudentFormRef" :model="editStudentForm" :rules="rules" label-width="80px">
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="editStudentForm.student_id" placeholder="请输入学生学号" />
        </el-form-item>
        <el-form-item label="姓名" prop="student_name">
          <el-input v-model="editStudentForm.student_name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="editStudentForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="editStudentForm.class_id" placeholder="请选择班级" style="width: 100%">
            <el-option v-for="classItem in classOptions" :key="classItem.class_id" :label="classItem.class_name"
              :value="classItem.class_id" />
          </el-select>
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
import { onMounted, ref, reactive, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import request from '@/utils/http'
import { ElTable, ElTableColumn, ElEmpty, ElButton, ElAvatar, ElDialog, ElForm, ElFormItem, ElInput, ElRadioGroup, ElRadio, ElSelect, ElOption } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { studentsApi, studentAddApi, classGroupsApi, classListApi, studentUpdateApi, studentDelApi } from '@/utils/api'
import StudentImg from '@/assets/icons/b4b58d7d-e033-41e9-b9fa-1a89df753781.jpg'

const studentData = ref(null);
const error = ref(null);
const dialogVisible = ref(false);
const newStudentFormRef = ref(null);
const classOptions = ref([]);
const searchKeyword = ref('');
const classFilter = ref('');

// 查看学生详情弹窗
const viewDialogVisible = ref(false)
const viewStudentData = ref({})

// 编辑学生弹窗
const editDialogVisible = ref(false)
const editStudentFormRef = ref(null)
const editStudentForm = reactive({
  student_id: '',
  student_name: '',
  gender: '男',
  class_id: null,
  original_student_id: '' // 保存原始学号，用于更新
})

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

const newStudentForm = reactive({
  student_id: '',
  student_name: '',
  gender: '男',
  class_id: null,
});

// 批量导入相关
const batchImportVisible = ref(false)
const importing = ref(false)
const importPreviewData = ref([])
const uploadRef = ref(null)
const validClassNames = ref([]) // 有效的班级名称列表
const validationErrors = ref([]) // 验证错误列表

const rules = reactive({
  student_id: [
    { required: true, message: '请输入学生学号', trigger: 'blur' },
    { min: 5, max: 20, message: '长度在 5 到 20 个字符', trigger: 'blur' },
  ],
  student_name: [
    { required: true, message: '请输入学生姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'blur' },
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' },
  ],
  class_id: [
    { required: true, message: '请选择班级', trigger: 'change' },
  ],
});

// 获取唯一的班级列表
const uniqueClasses = computed(() => {
  if (!studentData.value) return []
  const classes = new Set(studentData.value.map((item: any) => item.class_name).filter(Boolean))
  return Array.from(classes)
})

// 过滤后的数据
const filteredStudentData = computed(() => {
  if (!studentData.value) return []

  let data = studentData.value

  // 按班级过滤
  if (classFilter.value) {
    data = data.filter((item: any) => item.class_name === classFilter.value)
  }

  // 按搜索关键词过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter((item: any) =>
      item.student_name?.toLowerCase().includes(keyword) ||
      item.student_id?.toLowerCase().includes(keyword)
    )
  }

  return data
})

// 搜索
const handleSearch = () => {
  // 搜索逻辑已在computed中实现
}

// 筛选变更
const handleFilterChange = () => {
  // 过滤逻辑已在computed中实现
}

// 刷新
const handleRefresh = async () => {
  searchKeyword.value = ''
  classFilter.value = ''
  await fetchStudentData()
  ElMessage.success('刷新成功')
}

const handleView = (row: any) => {
  viewStudentData.value = { ...row }
  viewDialogVisible.value = true
}

const handleEdit = async (row: any) => {
  // 先获取班级选项
  await fetchClassOptions()
  
  // 打开弹窗
  editDialogVisible.value = true
  
  // 使用 nextTick 确保 DOM 更新完成后再设置表单值
  await nextTick()
  
  // 然后填充编辑表单
  editStudentForm.student_id = row.student_id
  editStudentForm.student_name = row.student_name
  editStudentForm.gender = row.gender
  // 将字符串类型的class_id转换为数字类型，以匹配班级选项中的class_id
  editStudentForm.class_id = row.class_id ? parseInt(row.class_id) : null
  editStudentForm.original_student_id = row.student_id
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学生 "${row.student_name}" (学号: ${row.student_id}) 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    const response = await studentDelApi({ student_id: row.student_id })
    if (response.code === 200) {
      ElMessage.success('学生删除成功')
      await fetchStudentData()
    } else {
      ElMessage.error(response.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      // 处理axios错误响应
      let errorMessage = '删除失败'
      
      if (error.response && error.response.data) {
        // 后端返回的错误信息
        errorMessage = error.response.data.message || error.response.data.error || '删除失败'
      } else if (error.message) {
        // 网络错误或其他错误
        errorMessage = error.message
      }
      
      ElMessage.error(errorMessage)
      console.error('删除学生失败:', error)
    }
  }
}

// 提交编辑表单
const submitEditForm = async () => {
  if (!editStudentFormRef.value) return
  editStudentFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        const response = await studentUpdateApi({
          original_student_id: editStudentForm.original_student_id,
          student_id: editStudentForm.student_id,
          student_name: editStudentForm.student_name,
          gender: editStudentForm.gender,
          // 将数字类型的class_id转换为字符串类型发送给后端
          class_id: editStudentForm.class_id ? editStudentForm.class_id.toString() : null
        })

        if (response.code === 200) {
          ElMessage.success('学生信息更新成功')
          editDialogVisible.value = false
          await fetchStudentData()
        } else {
          ElMessage.error(response.message || '更新失败')
        }
      } catch (error) {
        ElMessage.error('更新失败: ' + error.message)
        console.error('更新学生失败:', error)
      }
    }
  })
}

// 关闭编辑弹窗
const handleEditClose = () => {
  editDialogVisible.value = false
  // 重置表单
  Object.assign(editStudentForm, {
    student_id: '',
    student_name: '',
    gender: '男',
    class_id: null,
    original_student_id: ''
  })
}
const fetchClassOptions = async () => {
  try {
    const response = await classGroupsApi();
    if (response.code === 200) {
      classOptions.value = response.data;
    } else {
      ElMessage.error(response.message || '获取班级列表失败');
    }
  } catch (err) {
    ElMessage.error('请求班级列表失败: ' + err.message);
    console.error('获取班级列表失败:', err);
  }
};

// 获取所有班级名称列表（用于批量导入验证）
const fetchValidClassNames = async () => {
  try {
    const response = await classListApi();
    if (response.code === 200) {
      validClassNames.value = response.data.classes.map(cls => cls.class_name);
    } else {
      ElMessage.error(response.message || '获取班级列表失败');
    }
  } catch (err) {
    ElMessage.error('请求班级列表失败: ' + err.message);
    console.error('获取班级列表失败:', err);
  }
};

const handleAddStudent = () => {
  dialogVisible.value = true;
  if (newStudentFormRef.value) {
    newStudentFormRef.value.resetFields();
  }
  newStudentForm.student_id = '';
  newStudentForm.student_name = '';
  newStudentForm.gender = '男';
  newStudentForm.class_id = null;
  fetchClassOptions();
};

const submitForm = async () => {
  if (!newStudentFormRef.value) return;
  newStudentFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        const response = await studentAddApi(newStudentForm);
        if (response.code === 200) {
          ElMessage.success('学生添加成功');
          dialogVisible.value = false;
          await fetchStudentData();
        } else {
          ElMessage.error(response.message || '学生添加失败');
        }
      } catch (err) {
        ElMessage.error('请求失败: ' + err.message);
        console.error('添加学生失败:', err);
      }
    } else {
      console.log('表单验证失败');
      return false;
    }
  });
};

const fetchStudentData = async () => {
  try {
    const response = await studentsApi();
    if (response.code === 200) {
      studentData.value = response.data;
    } else {
      error.value = response.message || '查询失败';
      studentData.value = [];
    }
  } catch (err) {
    error.value = '请求失败: ' + err.message;
    studentData.value = [];
    console.error('查询学生数据失败:', err);
  }
};

const handleClose = () => {
  dialogVisible.value = false
  // 重置表单
  Object.assign(newStudentForm, {
    student_id: '',
    student_name: '',
    gender: '男',
    class_id: null
  })
}

// 批量导入相关方法
const handleBatchImport = async () => {
  batchImportVisible.value = true
  await fetchValidClassNames() // 获取班级列表用于验证
}

const handleBatchImportClose = () => {
  batchImportVisible.value = false
  importPreviewData.value = []
  validationErrors.value = []
  validClassNames.value = []
  importing.value = false
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 验证导入数据
const validateImportData = async (data) => {
  const errors = []
  const existingStudentIds = new Set()

  // 获取现有学生学号
  if (studentData.value) {
    studentData.value.forEach(student => {
      existingStudentIds.add(student.student_id)
    })
  }

  // 检查重复学号（当前批次内）
  const currentBatchIds = new Set()

  for (let i = 0; i < data.length; i++) {
    const row = data[i]
    const rowNum = i + 1

    // 检查必填字段
    if (!row.student_id || !row.student_name || !row.gender || !row.class_name) {
      errors.push(`第${rowNum}行：缺少必填字段`)
      continue
    }

    // 检查学号格式
    if (row.student_id.length < 5 || row.student_id.length > 20) {
      errors.push(`第${rowNum}行：学号长度应在5-20个字符之间`)
    }

    // 检查姓名格式
    if (row.student_name.length < 2 || row.student_name.length > 10) {
      errors.push(`第${rowNum}行：姓名长度应在2-10个字符之间`)
    }

    // 检查性别
    if (!['男', '女'].includes(row.gender)) {
      errors.push(`第${rowNum}行：性别只能是'男'或'女'`)
    }

    // 检查班级是否存在
    if (!validClassNames.value.includes(row.class_name)) {
      errors.push(`第${rowNum}行：班级'${row.class_name}'不存在`)
    }

    // 检查学号是否已存在于数据库
    if (existingStudentIds.has(row.student_id)) {
      errors.push(`第${rowNum}行：学号'${row.student_id}'已存在`)
    }

    // 检查当前批次中是否有重复学号
    if (currentBatchIds.has(row.student_id)) {
      errors.push(`第${rowNum}行：学号'${row.student_id}'在导入数据中重复`)
    } else {
      currentBatchIds.add(row.student_id)
    }
  }

  return errors
}

const downloadTemplate = async () => {
  try {
    const response = await request.get('/student/template-download', {
      responseType: 'blob'
    })

    // 创建下载链接
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '学生信息导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败，请重试')
    console.error('模板下载错误:', error)
  }
}

const handleFileChange = async (file) => {
  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const sheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[sheetName]
      const jsonData = XLSX.utils.sheet_to_json(worksheet)

      // 转换数据格式
      const formattedData = jsonData.map(row => ({
        student_id: String(row['学号'] || '').trim(),
        student_name: String(row['姓名'] || '').trim(),
        gender: String(row['性别'] || '').trim(),
        class_name: String(row['班级'] || '').trim()
      })).filter(item => item.student_id && item.student_name)

      if (formattedData.length === 0) {
        ElMessage.error('Excel文件中没有有效的学生数据')
        return
      }

      // 验证数据
      const errors = await validateImportData(formattedData)
      validationErrors.value = errors

      if (errors.length > 0) {
        ElMessage.error(`数据验证失败，发现 ${errors.length} 个错误，请修正后重新上传`)
        importPreviewData.value = formattedData // 仍然显示数据，但不允许导入
      } else {
        importPreviewData.value = formattedData
        ElMessage.success(`成功解析 ${formattedData.length} 条学生数据，数据验证通过`)
      }
    } catch (error) {
      ElMessage.error('Excel文件解析失败，请检查文件格式')
      console.error('Excel解析错误:', error)
    }
  }
  reader.readAsArrayBuffer(file.raw)
}

const handleFileRemove = () => {
  importPreviewData.value = []
}

const submitBatchImport = async () => {
  if (importPreviewData.value.length === 0) {
    ElMessage.error('请先上传Excel文件')
    return
  }

  if (validationErrors.value.length > 0) {
    ElMessage.error('数据验证失败，请修正错误后重新上传文件')
    return
  }

  importing.value = true

  try {
    const response = await request.post('/student/batch-add', {
      students: importPreviewData.value
    })

    if (response.data.code === 200) {
      ElMessage.success(`成功导入 ${importPreviewData.value.length} 名学生`)
      batchImportVisible.value = false
      importPreviewData.value = []
      validationErrors.value = []
      if (uploadRef.value) {
        uploadRef.value.clearFiles()
      }
      // 刷新学生列表
      fetchStudentData()
    } else {
      ElMessage.error(response.data.message || '批量导入失败')
    }
  } catch (error) {
    ElMessage.error('批量导入失败，请重试')
    console.error('批量导入错误:', error)
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  await fetchStudentData();
});
</script>

<style scoped>
.student-account-management-container {
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
}

.top-bar-buttons {
  display: flex;
  gap: 10px;
}

.batch-import-content {
  padding: 10px 0;
}

.import-steps {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.import-steps h4 {
  margin: 0 0 10px 0;
  color: #409eff;
}

.import-steps ol {
  margin: 0;
  padding-left: 20px;
}

.import-steps li {
  margin-bottom: 5px;
  color: #606266;
}

.file-upload-area {
  margin-bottom: 20px;
}

.preview-area {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fafafa;
}

.preview-area h4 {
  margin: 0 0 15px 0;
  color: #409eff;
}

.preview-info {
  margin: 10px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.validation-errors {
  margin-top: 15px;
  padding: 15px;
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 6px;
}

.error-list {
  max-height: 200px;
  overflow-y: auto;
  margin: 10px 0;
}

.error-item {
  padding: 5px 0;
  color: #f56c6c;
  font-size: 14px;
  border-bottom: 1px solid #fbc4c4;
}

.error-item:last-child {
  border-bottom: none;
}

.validation-success {
  margin-top: 15px;
  padding: 10px 15px;
  background-color: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
}

.student-detail {
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
  width: 80px;
  flex-shrink: 0;
}

.detail-item span {
  color: #303133;
  font-size: 14px;
}
</style>