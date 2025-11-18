<template>
    <div class="leave-management-container">
        <!-- 顶部标题栏 -->
        <div class="top-bar">
            <h2>请假管理</h2>
            <el-button type="primary" @click="handleAddLeave">新增请假</el-button>
        </div>

        <!-- 功能操作区 -->
        <div class="action-bar">
            <div class="search-area">
                <el-input v-model="searchKeyword" placeholder="搜索学生姓名或请假原因" clearable style="width: 300px;"
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
                <el-select v-model="statusFilter" placeholder="请假状态" style="width: 140px; margin-right: 12px;"
                    @change="handleFilterChange">
                    <el-option label="全部状态" value="all"></el-option>
                    <el-option label="待审批" value="pending"></el-option>
                    <el-option label="已批准" value="approved"></el-option>
                    <el-option label="已拒绝" value="rejected"></el-option>
                </el-select>
                <el-button @click="handleRefresh">
                    <el-icon>
                        <Refresh />
                    </el-icon>
                    刷新
                </el-button>
            </div>
        </div>

        <!-- 表格展示区 -->
        <div class="content-area">
            <el-table :data="filteredLeaveData" style="width: 100%" border stripe>
                <el-table-column type="index" label="序号" width="80" align="center" />
                <el-table-column prop="studentId" label="学号" width="180" align="center" />
                <el-table-column prop="studentName" label="学生姓名" width="120" align="center" />
                <el-table-column prop="className" label="班级" width="120" align="center" />
                <el-table-column prop="reason" label="请假原因" min-width="150" show-overflow-tooltip />
                <el-table-column prop="leaveType" label="请假类型" width="100" align="center">
                    <template #default="scope">
                        <el-tag :type="getLeaveTypeTag(scope.row.leaveType)" size="small">
                            {{ scope.row.leaveType }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="days" label="请假天数" width="100" align="center" />
                <el-table-column prop="startDate" label="开始日期" width="120" align="center" />
                <el-table-column prop="endDate" label="结束日期" width="120" align="center" />
                <el-table-column prop="status" label="审批状态" width="100" align="center">
                    <template #default="scope">
                        <el-tag :type="getStatusTag(scope.row.status)" size="small">
                            {{ getStatusText(scope.row.status) }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="280" align="center" fixed="right">
                    <template #default="scope">
                        <el-button size="small" @click="handleView(scope.row)">查看</el-button>
                        <el-button v-if="userStore.user_type === 'student' && scope.row.status === 'pending'"
                            size="small" type="success" @click="handleEdit(scope.row)">修改</el-button>

                        <el-button v-if="scope.row.status === 'pending' && userStore.user_type !== 'student'"
                            size="small" type="success" @click="handleApprove(scope.row)">
                            批准
                        </el-button>
                        <el-button v-if="scope.row.status === 'pending' && userStore.user_type !== 'student'"
                            size="small" type="warning" @click="handleReject(scope.row)">
                            拒绝
                        </el-button>
                        <el-button v-if="canDeleteLeave(scope.row)"
                            size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <!-- 新增/编辑请假对话框 -->
        <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
            <el-form :model="leaveForm" :rules="rules" ref="leaveFormRef" label-width="100px">
                <el-form-item label="学生姓名" prop="studentName">
                    <el-input v-model="leaveForm.studentName" placeholder="请输入学生姓名" :disabled="isEditing"></el-input>
                </el-form-item>
                <el-form-item label="学号" prop="studentId">
                    <el-input v-model="leaveForm.studentId" placeholder="请输入学号" @blur="handleStudentIdBlur"
                        :disabled="isEditing"></el-input>
                </el-form-item>
                <el-form-item label="班级" prop="className">
                    <el-input v-model="leaveForm.className" placeholder="输入姓名与学号后自动选择班级" disabled></el-input>
                </el-form-item>
                <el-form-item label="请假类型" prop="leaveType">
                    <el-select v-model="leaveForm.leaveType" placeholder="请选择请假类型" style="width: 100%;">
                        <el-option label="事假" value="事假"></el-option>
                        <el-option label="病假" value="病假"></el-option>
                        <el-option label="其他" value="其他"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="开始日期" prop="startDate">
                    <el-date-picker v-model="leaveForm.startDate" type="date" placeholder="选择开始日期" style="width: 100%;"
                        format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
                </el-form-item>
                <el-form-item label="结束日期" prop="endDate">
                    <el-date-picker v-model="leaveForm.endDate" type="date" placeholder="选择结束日期" style="width: 100%;"
                        format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
                </el-form-item>
                <el-form-item label="请假原因" prop="reason">
                    <el-input v-model="leaveForm.reason" type="textarea" rows="4" placeholder="请输入请假原因"></el-input>
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="submitForm">确定</el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 查看详情对话框 -->
        <el-dialog v-model="viewDialogVisible" title="请假详情" width="600px" top="5vh">
            <div class="detail-container" v-if="currentLeave">
                <div class="detail-row">
                    <span class="detail-label">学生姓名：</span>
                    <span class="detail-value">{{ currentLeave.studentName }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">学号：</span>
                    <span class="detail-value">{{ currentLeave.studentId }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">班级：</span>
                    <span class="detail-value">{{ currentLeave.className }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">请假类型：</span>
                    <el-tag :type="getLeaveTypeTag(currentLeave.leaveType)" size="small">
                        {{ currentLeave.leaveType }}
                    </el-tag>
                </div>
                <div class="detail-row">
                    <span class="detail-label">开始日期：</span>
                    <span class="detail-value">{{ currentLeave.startDate }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">结束日期：</span>
                    <span class="detail-value">{{ currentLeave.endDate }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">请假天数：</span>
                    <span class="detail-value">{{ currentLeave.days }} 天</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">审批状态：</span>
                    <el-tag :type="getStatusTag(currentLeave.status)" size="small">
                        {{ getStatusText(currentLeave.status) }}
                    </el-tag>
                </div>
                <div class="detail-row">
                    <span class="detail-label">请假原因：</span>
                    <span class="detail-value">{{ currentLeave.reason }}</span>
                </div>
                <div class="detail-row" v-if="currentLeave.approveNote">
                    <span class="detail-label">审批备注：</span>
                    <span class="detail-value">{{ currentLeave.approveNote }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">提交时间：</span>
                    <span class="detail-value">{{ currentLeave.submittedAt }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">审批时间：</span>
                    <span class="detail-value">{{ currentLeave.approvalTime || '未审批' }}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">审批人：</span>
                    <span class="detail-value">{{ currentLeave.approverId || '无' }}</span>
                </div>
            </div>
            <template #footer>
                <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
            </template>
        </el-dialog>
    </div>
</template>


<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { leaveQueryApi, classGroupsStudentIdApi } from '@/utils/api'
import { leaveAddApi, leaveUpdateApi, leaveDelApi, leaveApproveApi } from '@/utils/api'
import { useUserStore } from '../../stores/user'

interface LeaveRecord {
    id: number
    studentName: string
    studentId: string
    className: string
    leaveType: string
    reason: string
    startDate: string
    endDate: string
    days: number
    status: 'pending' | 'approved' | 'rejected'
    approveNote?: string
    approvalTime?: string
    approverId?: number
    comments?: string
    submittedAt?: string
    updatedAt?: string
}

// 模拟数据
const mockLeaveData = ref<LeaveRecord[]>([])

const userStore = useUserStore()

const searchKeyword = ref('')
const statusFilter = ref('all')
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('新增请假')
const isEditing = ref(false)
const editingLeaveId = ref<number | null>(null)
const leaveFormRef = ref<any>(null)
const currentLeave = ref<LeaveRecord | null>(null)

const leaveForm = reactive({
    id: undefined as number | undefined,
    studentName: '',
    studentId: '',
    className: '',
    leaveType: '',
    reason: '',
    startDate: '',
    endDate: ''
})

const rules = reactive({
    studentName: [
        { required: true, message: '请输入学生姓名', trigger: 'blur' }
    ],
    studentId: [
        { required: true, message: '请输入学号', trigger: 'blur' }
    ],
    className: [
        { required: true, message: '请输入班级', trigger: 'blur' }
    ],
    leaveType: [
        { required: true, message: '请选择请假类型', trigger: 'change' }
    ],
    startDate: [
        { required: true, message: '请选择开始日期', trigger: 'change' }
    ],
    endDate: [
        { required: true, message: '请选择结束日期', trigger: 'change' }
    ],
    reason: [
        { required: true, message: '请输入请假原因', trigger: 'blur' }
    ]
})

// 过滤后的数据
const filteredLeaveData = computed(() => {
    let data = mockLeaveData.value

    // 按状态过滤
    if (statusFilter.value !== 'all') {
        data = data.filter(item => item.status === statusFilter.value)
    }

    // 按搜索关键词过滤
    if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        data = data.filter(item =>
            item.studentName.toLowerCase().includes(keyword) ||
            item.reason.toLowerCase().includes(keyword)
        )
    }

    return data
})

// 获取请假类型标签颜色
const getLeaveTypeTag = (type: string) => {
    const tagMap: Record<string, string> = {
        '病假': 'warning',
        '事假': 'info',
        '其他': 'success'
    }
    return tagMap[type] || 'info'
}

// 获取状态标签颜色
const getStatusTag = (status: string) => {
    const tagMap: Record<string, string> = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger'
    }
    return tagMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
    const textMap: Record<string, string> = {
        'pending': '待审批',
        'approved': '已批准',
        'rejected': '已拒绝'
    }
    return textMap[status] || status
}

// 判断是否可以删除请假记录
const canDeleteLeave = (row: LeaveRecord) => {
    // 学生用户：只能删除待审批的自己的请假记录
    if (userStore.user_type === 'student') {
        return row.status === 'pending'
    }
    
    // 教师用户：不能删除任何请假记录，只能审批
    if (userStore.user_type === 'teacher') {
        return false
    }
    
    // 管理员：可以删除所有请假记录
    if (userStore.user_type === 'admin') {
        return true
    }
    
    // 其他情况不允许删除
    return false
}

// 格式化日期
const formatDate = (dateString: string) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${year}-${month}-${day}`
}

// 计算请假天数
const calculateDays = (startDateString: string, endDateString: string) => {
    if (!startDateString || !endDateString) return 0
    const start = new Date(startDateString)
    const end = new Date(endDateString)

    // 将日期调整到各自的零点，以便只比较日期部分
    start.setHours(0, 0, 0, 0)
    end.setHours(0, 0, 0, 0)

    const diffTime = Math.abs(end.getTime() - start.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    return diffDays
}

// 新增请假
const handleAddLeave = () => {
    dialogTitle.value = '新增请假'
    isEditing.value = false
    editingLeaveId.value = null
    dialogVisible.value = true
    if (leaveFormRef.value) {
        leaveFormRef.value.resetFields()
    }
    Object.assign(leaveForm, {
        id: undefined,
        studentName: '',
        studentId: '',
        className: '',
        leaveType: '',
        reason: '',
        startDate: '',
        endDate: ''
    })
}

// 学号输入框失去焦点时查询班级
const handleStudentIdBlur = async () => {
    if (!leaveForm.studentId || !leaveForm.studentName) {
        return
    }

    try {
        const response = await classGroupsStudentIdApi({
            student_id: leaveForm.studentId,
            student_name: leaveForm.studentName
        })

        if (response && response.data && response.data.class_name) {
            leaveForm.className = response.data.class_name
        } else {
            leaveForm.className = ''
            ElMessage.error('该学生不存在')
        }
    } catch (error: any) {
        leaveForm.className = ''
        if (error.response && error.response.data && error.response.data.message) {
            ElMessage.error(error.response.data.message)
        } else {
            ElMessage.error('查询班级信息失败')
        }
    }
}

// 提交表单
const submitForm = async () => {
    if (!leaveFormRef.value) return
    leaveFormRef.value.validate(async (valid: boolean) => {
        if (valid) {
            try {
                const leaveTypeMap: Record<string, number> = {
                    '事假': 1,
                    '病假': 2,
                    '其他': 3
                }
                const payload = {
                    student_id: leaveForm.studentId,
                    class_name: leaveForm.className,
                    leave_type: leaveTypeMap[leaveForm.leaveType],
                    reason: leaveForm.reason,
                    start_time: leaveForm.startDate,
                    end_time: leaveForm.endDate,
                    student_username: leaveForm.studentName
                }

                if (isEditing.value && editingLeaveId.value !== null) {
                    // 编辑模式
                    const response = await leaveUpdateApi({ ...payload, id: editingLeaveId.value })
                    if (response && response.code === 200) {
                        ElMessage.success('请假申请修改成功')
                        dialogVisible.value = false
                        fetchLeaveData()
                    } else {
                        ElMessage.error(response.message || '修改请假申请失败')
                    }
                } else {
                    // 新增模式
                    const response = await leaveAddApi(payload)
                    if (response && response.code === 200) {
                        ElMessage.success('请假申请提交成功')
                        dialogVisible.value = false
                        fetchLeaveData()
                    } else {
                        ElMessage.error(response.message || '提交请假申请失败')
                    }
                }
            } catch (error: any) {
                let errorMessage = '提交请假申请失败，请重试'
                if (error.response && error.response.data) {
                    errorMessage = error.response.data.message || error.response.data.error || errorMessage
                } else if (error.message) {
                    errorMessage = error.message
                }
                ElMessage.error(errorMessage)
            }
        } else {
            ElMessage.error('请填写完整信息')
        }
    })
}

// 查看详情
const handleView = (row: LeaveRecord) => {
    currentLeave.value = row
    viewDialogVisible.value = true
}

// 修改请假
const handleEdit = (row: LeaveRecord) => {
    dialogTitle.value = '修改请假'
    isEditing.value = true
    editingLeaveId.value = row.id
    dialogVisible.value = true

    // 预填充表单数据
    Object.assign(leaveForm, {
        id: row.id,
        studentName: row.studentName,
        studentId: row.studentId,
        className: row.className,
        leaveType: row.leaveType,
        reason: row.reason,
        startDate: row.startDate,
        endDate: row.endDate
    })
}

// 批准请假
const handleApprove = (row: LeaveRecord) => {
    ElMessageBox.prompt('请输入审批备注（可选）', '批准请假', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.*/,
    }).then(async ({ value }) => {
        try {
            const response = await leaveApproveApi({
                id: row.id,
                approve_status: 'approved',
                comments: value || '同意请假'
            })
            
            if (response && response.code === 200) {
                // 更新本地数据
                row.status = 'approved'
                row.approveNote = value || '同意请假'
                row.comments = value || '同意请假'
                row.approvalTime = new Date().toLocaleString()
                ElMessage.success('已批准请假申请')
                // 刷新数据
                fetchLeaveData()
            } else {
                ElMessage.error(response.message || '批准请假申请失败')
            }
        } catch (error: any) {
            console.error('批准请假申请失败:', error)
            const errorMessage = error.response?.data?.message || error.message || '批准请假申请失败，请重试'
            ElMessage.error(errorMessage)
        }
    }).catch(() => {
        ElMessage.info('已取消操作')
    })
}

// 拒绝请假
const handleReject = (row: LeaveRecord) => {
    ElMessageBox.prompt('请输入拒绝原因', '拒绝请假', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.+/,
        inputErrorMessage: '请输入拒绝原因'
    }).then(async ({ value }) => {
        try {
            const response = await leaveApproveApi({
                id: row.id,
                approve_status: 'rejected',
                comments: value
            })
            
            if (response && response.code === 200) {
                // 更新本地数据
                row.status = 'rejected'
                row.approveNote = value
                row.comments = value
                row.approvalTime = new Date().toLocaleString()
                ElMessage.success('已拒绝请假申请')
                // 刷新数据
                fetchLeaveData()
            } else {
                ElMessage.error(response.message || '拒绝请假申请失败')
            }
        } catch (error: any) {
            console.error('拒绝请假申请失败:', error)
            const errorMessage = error.response?.data?.message || error.message || '拒绝请假申请失败，请重试'
            ElMessage.error(errorMessage)
        }
    }).catch(() => {
        ElMessage.info('已取消操作')
    })
}

// 删除请假
const handleDelete = async (row: LeaveRecord) => {
    ElMessageBox.confirm('确定删除此请假记录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(async () => {
        try {
            const response = await leaveDelApi({ id: row.id })
            if (response && response.code === 200) {
                // 从本地数据中移除
                const index = mockLeaveData.value.findIndex(item => item.id === row.id)
                if (index !== -1) {
                    mockLeaveData.value.splice(index, 1)
                }
                ElMessage.success('删除成功')
            } else {
                ElMessage.error(response.message || '删除失败')
            }
        } catch (error: any) {
            console.error('删除请假记录失败:', error)
            const errorMessage = error.response?.data?.message || error.message || '删除失败，请重试'
            ElMessage.error(errorMessage)
        }
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}

// 搜索
const handleSearch = () => {
    // 搜索逻辑已在computed中实现
}

// 刷新
const handleRefresh = () => {
    searchKeyword.value = ''
    statusFilter.value = 'all'
    fetchLeaveData() // 刷新数据
    ElMessage.success('刷新成功')
}

// 状态筛选变更
const handleFilterChange = () => {
    // 过滤逻辑已在computed中实现
}

onMounted(async () => {
    await fetchLeaveData()
})

// 获取请假数据
const fetchLeaveData = async () => {
    try {
        const response = await leaveQueryApi()
        if (response && response.code === 200) {
            mockLeaveData.value = response.data.map((item: any) => ({
                id: item.id,
                studentName: item.student_username,
                studentId: item.student_id.toString(),
                className: item.class_name,
                leaveType: item.leave_type === 1 ? '事假' : item.leave_type === 2 ? '病假' : '其他',
                reason: item.reason,
                startDate: formatDate(item.start_time),
                endDate: formatDate(item.end_time),
                days: calculateDays(item.start_time, item.end_time),
                status: item.status,
                approveNote: item.comments,
                approvalTime: item.approval_time,
                approverId: item.approver_id,
                submittedAt: item.submitted_at,
                updatedAt: item.updated_at
            }))
        } else {
            ElMessage.error(response.message || '获取请假数据失败')
        }
    } catch (error: any) {
        console.error('获取请假数据失败:', error)
        ElMessage.error('获取请假数据失败，请刷新页面重试')
    }
}

</script>


<style scoped>
.leave-management-container {
    display: flex;
    flex-direction: column;
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

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-md);
}

.detail-container {
    padding: var(--space-lg);
}

.detail-row {
    display: flex;
    align-items: center;
    padding: var(--space-md) 0;
    border-bottom: 1px solid var(--divider);
}

.detail-row:last-child {
    border-bottom: none;
}

.detail-label {
    font-weight: 600;
    color: var(--text);
    min-width: 100px;
    flex-shrink: 0;
}

.detail-value {
    color: var(--text-strong);
    flex: 1;
}
</style>