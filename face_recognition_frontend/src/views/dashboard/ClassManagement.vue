<template>
  <div class="class-management-container">
    <div class="top-bar">
      <h2>班级管理</h2>
      <el-button type="primary" @click="handleAddClass">新增班级</el-button>
    </div>

    <!-- 功能操作区 -->
    <div class="action-bar">
      <div class="search-area">
        <el-input v-model="searchKeyword" placeholder="搜索班级名称" clearable style="width: 300px;" @clear="handleSearch">
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
      <el-empty v-else-if="classData === null" description="加载中..." />
      <el-table v-else :data="filteredClassData" style="width: 100%" border stripe>
        <el-table-column type="index" label="序号" width="80" align="center" />
        <el-table-column prop="class_name" label="班级名称" width="180" align="center" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="student_count" label="学生人数" width="120" align="center" />
        <el-table-column label="操作" width="220" align="center">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(scope.row)">修改</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增班级对话框 -->
    <el-dialog v-model="dialogVisible" title="新增班级" width="500px">
      <el-form :model="newClassForm" :rules="rules" ref="newClassFormRef" label-width="100px">
        <el-form-item label="班级名称" prop="class_name">
          <el-input v-model="newClassForm.class_name" placeholder="请输入班级名称"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="newClassForm.description" type="textarea" rows="4" placeholder="请输入班级描述"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看班级详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="班级详情" width="500px">
      <div v-if="selectedClass" class="class-detail">
        <div class="detail-item">
          <label>班级名称：</label>
          <span>{{ selectedClass.class_name }}</span>
        </div>
        <div class="detail-item">
          <label>描述：</label>
          <span>{{ selectedClass.description || '暂无描述' }}</span>
        </div>
        <div class="detail-item">
          <label>学生人数：</label>
          <span>{{ selectedClass.student_count || 0 }} 人</span>
        </div>
        <div class="detail-item">
          <label>班级ID：</label>
          <span>{{ selectedClass.class_id }}</span>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="viewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 修改班级对话框 -->
    <el-dialog v-model="editDialogVisible" title="修改班级" width="500px">
      <el-form :model="editClassForm" :rules="rules" ref="editClassFormRef" label-width="100px">
        <el-form-item label="班级名称" prop="class_name">
          <el-input v-model="editClassForm.class_name" placeholder="请输入班级名称"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editClassForm.description" type="textarea" rows="4" placeholder="请输入班级描述"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEditForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import request from '../../utils/http'
import { ElTable, ElTableColumn, ElEmpty, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { classGroupsApi, classGroupsUpdateApi, classGroupsDelApi } from '../../utils/api'

const classData = ref(null);
const error = ref(null);
const dialogVisible = ref(false);
const viewDialogVisible = ref(false);
const editDialogVisible = ref(false);
const newClassFormRef = ref(null);
const editClassFormRef = ref(null);
const searchKeyword = ref('');
const selectedClass = ref(null);

const newClassForm = reactive({
  class_name: '',
  description: '',
});

const editClassForm = reactive({
  class_id: '',
  class_name: '',
  description: '',
});

const rules = reactive({
  class_name: [
    { required: true, message: '请输入班级名称', trigger: 'blur' },
    { min: 2, max: 16, message: '长度在 2 到 16 个字符', trigger: 'blur' },
  ],
  description: [
    { max: 150, message: '长度最大为 150 个字符', trigger: 'blur' },
  ],
});

// 过滤后的数据
const filteredClassData = computed(() => {
  if (!classData.value) return []

  let data = classData.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter((item: any) =>
      item.class_name?.toLowerCase().includes(keyword)
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
  await fetchClassData()
  ElMessage.success('刷新成功')
}

const handleView = (row: any) => {
  selectedClass.value = row;
  viewDialogVisible.value = true;
};

const handleEdit = (row: any) => {
  selectedClass.value = row;
  editClassForm.class_id = row.class_id;
  editClassForm.class_name = row.class_name;
  editClassForm.description = row.description || '';
  editDialogVisible.value = true;
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除班级 "${row.class_name}" 吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    const response = await classGroupsDelApi({ class_id: row.class_id });
    if (response.code === 200) {
      ElMessage.success('班级删除成功');
      await fetchClassData();
    } else {
      ElMessage.error(response.message || '班级删除失败');
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除班级失败: ' + error.message);
      console.error('删除班级失败:', error);
    }
  }
};

const handleAddClass = () => {
  dialogVisible.value = true;
  if (newClassFormRef.value) {
    newClassFormRef.value.resetFields();
  }
  newClassForm.class_name = '';
  newClassForm.description = '';
};

const submitForm = async () => {
  if (!newClassFormRef.value) return;
  newClassFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        const response = await request.post('/class/add', newClassForm);
        if (response.data.code === 200) {
          ElMessage.success('班级新增成功');
          dialogVisible.value = false;
          await fetchClassData();
        } else {
          ElMessage.error(response.data.message || '班级新增失败');
        }
      } catch (err) {
        ElMessage.error('请求新增班级失败: ' + err.message);
        console.error('新增班级失败:', err);
      }
    } else {
      console.log('表单验证失败');
      return false;
    }
  });
};

const submitEditForm = async () => {
  if (!editClassFormRef.value) return;
  editClassFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        const response = await classGroupsUpdateApi(editClassForm);
        if (response.code === 200) {
          ElMessage.success('班级修改成功');
          editDialogVisible.value = false;
          await fetchClassData();
        } else {
          ElMessage.error(response.message || '班级修改失败');
        }
      } catch (err) {
        ElMessage.error('请求修改班级失败: ' + err.message);
        console.error('修改班级失败:', err);
      }
    } else {
      console.log('表单验证失败');
      return false;
    }
  });
};

const fetchClassData = async () => {
  try {
    const response = await classGroupsApi();
    if (response.code === 200) {
      classData.value = response.data;
    } else {
      error.value = response.message || '查询失败';
      classData.value = [];
    }
  } catch (err) {
    error.value = '请求失败: ' + err.message;
    classData.value = [];
    console.error('查询班级数据失败:', err);
  }
};

onMounted(async () => {
  await fetchClassData();
});
</script>

<style scoped>
.class-management-container {
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

.content-area :deep(.el-table) {
  background: transparent;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
}

.class-detail {
  padding: var(--space-md) 0;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: var(--space-md);
  padding: var(--space-sm) 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-strong);
  min-width: 100px;
  margin-right: var(--space-md);
}

.detail-item span {
  color: var(--text);
  flex: 1;
  word-break: break-word;
}
</style>