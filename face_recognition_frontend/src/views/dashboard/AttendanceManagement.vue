<template>
    <div class="attendance-management-container">
        <!-- 顶部标题栏 -->
        <div class="top-bar">
            <h2>考勤管理</h2>
            <el-button style="margin-left: 70%;" type="primary" @click="handleAdd">新增考勤会话</el-button>
            <el-button type="primary" @click="handleExport">考勤导出</el-button>
        </div>

        <!-- 功能操作区 -->
        <div class="action-bar">
            <div class="search-area">
                <el-input v-model="searchKeyword" placeholder="搜索课程或班级名称" clearable style="width: 300px;"
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
                <el-select v-model="statusFilter" placeholder="考勤状态" style="width: 140px; margin-right: 12px;"
                    @change="handleFilterChange" clearable>
                    <el-option label="全部状态" value=""></el-option>
                    <el-option label="考勤中" value="active"></el-option>
                    <el-option label="已结束" value="closed"></el-option>
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
            <el-table :data="filteredAttendanceData" style="width: 100%;" border stripe>
                <el-table-column type="index" label="序号" width="80"></el-table-column>
                <el-table-column prop="course_name" label="课程名称"></el-table-column>
                <el-table-column prop="class_name" label="班级名称"></el-table-column>
                <el-table-column prop="participant_count" label="参与人数"></el-table-column>
                <el-table-column prop="session_name" label="备注"></el-table-column>
                <el-table-column prop="start_time" label="开始时间"></el-table-column>
                <el-table-column prop="end_time" label="结束时间"></el-table-column>
                <el-table-column label="考勤状态">
                    <template #default="scope">
                        <!-- 根据结束时间与当前时间比较显示状态；无结束时间时根据is_active显示 -->
                        <el-tag :type="getStatusType(scope.row)">
                            {{ getStatusLabel(scope.row) }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="280">
                    <template #default="scope">
                        <el-button size="small" type="primary" @click="showAttendanceDetail(scope.row)">详情</el-button>

                        <!-- 考勤中：仅显示关闭 -->
                        <template v-if="isOngoing(scope.row)">
                            <el-button size="small" type="warning" @click="handleClose(scope.row.id)">关闭</el-button>
                        </template>

                        <!-- 未开启：只显示开启；已结束：不显示按钮 -->
                        <template v-else>
                            <el-button v-if="getStatusLabel(scope.row) === '未开启'" size="small" type="success"
                                @click="handleOpen(scope.row)">开启</el-button>
                        </template>

                        <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                        <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <!-- 考勤导出弹窗 -->
        <el-dialog v-model="exportDialogVisible" title="考勤导出" width="80%">
            <div class="export-container">
                <!-- 左侧：考勤记录选择 -->
                <div class="export-left">
                    <h3>选择考勤记录</h3>
                    <el-table 
                        :data="filteredAttendanceData" 
                        style="width: 100%;" 
                        border 
                        stripe
                        @selection-change="handleSelectionChange"
                        ref="exportTableRef">
                        <el-table-column type="selection" width="55"></el-table-column>
                        <el-table-column type="index" label="序号" width="80"></el-table-column>
                        <el-table-column prop="course_name" label="课程名称"></el-table-column>
                        <el-table-column prop="class_name" label="班级名称"></el-table-column>
                        <el-table-column prop="session_name" label="备注"></el-table-column>
                        <el-table-column label="考勤状态">
                            <template #default="scope">
                                <el-tag :type="getStatusType(scope.row)">
                                    {{ getStatusLabel(scope.row) }}
                                </el-tag>
                            </template>
                        </el-table-column>
                    </el-table>
                    
                    <div class="export-actions" style="margin-top: 20px;">
                        <el-button @click="selectAll">全选</el-button>
                        <el-button @click="clearSelection">清空选择</el-button>
                        <el-button 
                            type="primary" 
                            @click="generateExport" 
                            :disabled="selectedAttendanceRecords.length === 0"
                            :loading="exportLoading">
                            生成导出数据
                        </el-button>
                    </div>
                </div>
                
                <!-- 右侧：导出预览和饼图 -->
                <div class="export-right" v-if="exportData.length > 0">
                    <h3>导出预览</h3>
                    
                    <!-- 饼图展示 -->
                    <div class="chart-container">
                        <h4>考勤情况统计</h4>
                        <v-chart 
                            class="chart" 
                            :option="chartOption" 
                            style="height: 300px; width: 100%;">
                        </v-chart>
                    </div>
                    
                    <!-- 数据预览表格 -->
                    <div class="preview-table">
                        <h4>数据预览 (共 {{ exportData.length }} 条记录)</h4>
                        <el-table 
                            :data="exportData.slice(0, 10)" 
                            style="width: 100%;" 
                            border 
                            stripe
                            max-height="300">
                            <el-table-column prop="序号" label="序号" width="80"></el-table-column>
                            <el-table-column prop="姓名" label="姓名"></el-table-column>
                            <el-table-column prop="学号" label="学号"></el-table-column>
                            <el-table-column prop="性别" label="性别"></el-table-column>
                            <el-table-column prop="考勤状态" label="考勤状态">
                                <template #default="scope">
                                    <el-tag :type="getExportStatusType(scope.row.考勤状态)">
                                        {{ scope.row.考勤状态 }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="课程名称" label="课程名称"></el-table-column>
                            <el-table-column prop="班级名称" label="班级名称"></el-table-column>
                            <el-table-column prop="考勤会话" label="考勤会话"></el-table-column>
                        </el-table>
                        <p v-if="exportData.length > 10" style="color: #909399; margin-top: 10px;">
                            仅显示前10条记录，完整数据将在Excel中分工作表导出
                        </p>
                    </div>
                    
                    <!-- 导出按钮 -->
                    <div class="export-final-actions" style="margin-top: 20px;">
                        <el-button 
                            type="success" 
                            @click="downloadExcel"
                            :loading="downloadLoading">
                            <el-icon><Download /></el-icon>
                            下载Excel文件
                        </el-button>
                    </div>
                </div>
            </div>
        </el-dialog>

        <!-- 考勤详情弹窗 -->
        <el-dialog v-model="detailDialogVisible" title="考勤详情" width="70%">
            <!-- 出勤率统计区域 -->
            <div class="attendance-statistics" style="margin-bottom: 20px; padding: 16px; background-color: #f5f7fa; border-radius: 8px;">
                <h3 style="margin: 0 0 12px 0; color: #303133;">出勤统计</h3>
                <el-row :gutter="20">
                    <el-col :span="4">
                        <div class="stat-item">
                            <div class="stat-label">总人数</div>
                            <div class="stat-value" style="color: #409EFF;">{{ attendanceStats.totalCount }}</div>
                        </div>
                    </el-col>
                    <el-col :span="4">
                        <div class="stat-item">
                            <div class="stat-label">出勤人数</div>
                            <div class="stat-value" style="color: #67C23A;">{{ attendanceStats.presentCount }}</div>
                        </div>
                    </el-col>
                    <el-col :span="4">
                        <div class="stat-item">
                            <div class="stat-label">请假人数</div>
                            <div class="stat-value" style="color: #E6A23C;">{{ attendanceStats.leaveCount }}</div>
                        </div>
                    </el-col>
                    <el-col :span="4">
                        <div class="stat-item">
                            <div class="stat-label">缺勤人数</div>
                            <div class="stat-value" style="color: #F56C6C;">{{ attendanceStats.absentCount }}</div>
                        </div>
                    </el-col>
                    <el-col :span="8">
                        <div class="stat-item">
                            <div class="stat-label">出勤率</div>
                            <div class="stat-value" style="color: #409EFF; font-size: 18px; font-weight: bold;">
                                {{ attendanceStats.attendanceRate }}%
                            </div>
                        </div>
                    </el-col>
                </el-row>
            </div>
            
            <el-table :data="currentAttendanceDetails" style="width: 100%;" border stripe>
                <el-table-column type="index" label="序号" width="80"></el-table-column>
                <el-table-column prop="student_name" label="姓名"></el-table-column>
                <el-table-column prop="student_id" label="学号"></el-table-column>
                <el-table-column prop="gender" label="性别">
                    <template #default="scope">
                        <span v-if="scope.row.gender">
                            {{ scope.row.gender === 'male' ? '男' : scope.row.gender === 'female' ? '女' : scope.row.gender }}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column label="考勤状态">
                    <template #default="scope">
                        <el-tag :type="statusTagType(scope.row.status)">
                            {{ scope.row.status || '未签到' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <!-- 移除请假状态列，统一在考勤状态显示 -->
            </el-table>
        </el-dialog>

        <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑考勤会话' : '新增考勤会话'" width="50%">
            <el-form :model="currentSession" :rules="rules" ref="formRef" label-width="120px">
                <el-form-item label="课程" prop="course_id">
                    <el-select v-model="currentSession.course_id" placeholder="请选择课程" @change="handleCourseChange">
                        <el-option v-for="course in courses" :key="course.id" :label="course.course_name"
                            :value="Number(course.id)"></el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="班级" prop="class_id">
                    <el-select v-model="currentSession.class_id" placeholder="请选择班级">
                        <el-option v-for="classGroup in classGroups" :key="classGroup.class_id"
                            :label="classGroup.class_name" :value="Number(classGroup.class_id)"></el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="备注" prop="session_name">
                    <el-input v-model="currentSession.session_name" placeholder="请输入备注"></el-input>
                </el-form-item>

                <el-form-item label="结束时间" prop="end_time">
                    <el-date-picker v-model="currentSession.end_time" type="datetime" placeholder="请选择结束时间"
                        format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
                </el-form-item>

                <el-form-item label="教师姓名" v-if="currentSession.teacher_name">
                    <el-input v-model="currentSession.teacher_name" :disabled="true"></el-input>
                </el-form-item>

                <el-form-item label="是否开启" v-if="isEdit">
                    <el-switch v-model="currentSession.is_active" @change="handleActiveToggle"></el-switch>
                </el-form-item>
            </el-form>

            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="handleSubmit">提交</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import http from '../../utils/http';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Refresh, Download } from '@element-plus/icons-vue';
import { AttendanceQueryApi, classGroupsApi, courseQueryApi, attendanceAddApi, attendanceUpdateApi, attendanceDelApi, attendanceStudentInfoApi } from '@/utils/api';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

// 注册ECharts组件
use([
    CanvasRenderer,
    PieChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent
]);
interface AttendanceSession {
    id?: number;
    session_name: string;
    course_id: number | null;
    class_id: number | null;
    teacher_id: number | null;
    start_time: string;
    end_time: string;
    is_active: boolean;
    course_name?: string;
    class_name?: string;
    teacher_name?: string;
    participant_count?: number;
    details?: AttendanceDetail[];
}

interface AttendanceDetail {
    student_users_id?: number;
    student_id: string;
    student_name: string;
    gender: string | null;
    status: string;
}

interface Course {
    id: number;
    course_name: string;
    teacher_info: { id: number; teacher_name: string };
    class_info: { class_id: number; class_name: string }[];
}

interface ClassGroup {
    class_id: number;
    class_name: string;
}

const attendanceSessions = ref<AttendanceSession[]>([]);
const courses = ref<Course[]>([]);
const classGroups = ref<ClassGroup[]>([]);
const dialogVisible = ref(false);
const detailDialogVisible = ref(false);
const currentAttendanceDetails = ref<AttendanceDetail[]>([]);
const isEdit = ref(false);
const formRef = ref<any>(null);
const searchKeyword = ref('');
const statusFilter = ref('');
const currentSession = ref<AttendanceSession>({
    session_name: '',
    course_id: null,
    class_id: null,
    teacher_id: null,
    start_time: '',
    end_time: '',
    is_active: true,
});

// 导出相关的响应式变量
const exportDialogVisible = ref(false);
const selectedAttendanceRecords = ref<AttendanceSession[]>([]);
const exportData = ref<any[]>([]);
const exportLoading = ref(false);
const downloadLoading = ref(false);
const exportTableRef = ref<any>(null);

// 饼图配置
const chartOption = computed(() => {
    if (exportData.value.length === 0) return {};
    
    // 统计考勤状态
    const statusCount: Record<string, number> = {};
    exportData.value.forEach(item => {
        const status = item.考勤状态 || '未签到';
        statusCount[status] = (statusCount[status] || 0) + 1;
    });
    
    const data = Object.entries(statusCount).map(([name, value]) => ({
        name,
        value
    }));
    
    return {
        title: {
            text: '考勤状态分布',
            left: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left'
        },
        series: [
            {
                name: '考勤状态',
                type: 'pie',
                radius: '50%',
                data: data,
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                itemStyle: {
                    color: function(params: any) {
                        const colors: Record<string, string> = {
                            '已签到': '#67C23A',
                            '请假': '#E6A23C',
                            '缺勤': '#F56C6C',
                            '未签到': '#909399'
                        };
                        return colors[params.name] || '#409EFF';
                    }
                }
            }
        ]
    };
});

const rules = ref({
    course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
    class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
    session_name: [{ required: true, message: '请输入备注', trigger: 'blur' }],
    // end_time可为空，后端允许手动设置，移除必填
});

// 过滤后的数据
const filteredAttendanceData = computed(() => {
    let data = attendanceSessions.value

    // 按状态过滤
    if (statusFilter.value) {
        if (statusFilter.value === 'active') {
            // 考勤中：未设置结束时间且 is_active 为真
            data = data.filter(item => !item.end_time && item.is_active)
        } else if (statusFilter.value === 'closed') {
            // 已结束：有结束时间
            data = data.filter(item => !!item.end_time)
        }
    }

    // 按搜索关键词过滤
    if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        data = data.filter(item =>
            item.course_name?.toLowerCase().includes(keyword) ||
            item.class_name?.toLowerCase().includes(keyword)
        )
    }

    return data
})

// 根据结束时间与当前时间比较返回状态标签与类型
const parseDate = (s: string) => {
    // 兼容 YYYY-MM-DD HH:mm:ss 在不同浏览器的解析
    return new Date(s.replace(/-/g, '/'))
}
const isEndedByTime = (end: string | undefined) => {
    if (!end) return false
    const endDate = parseDate(end)
    return endDate.getTime() < Date.now()
}
const getStatusLabel = (row: AttendanceSession) => {
    if (row.end_time) {
        return isEndedByTime(row.end_time) ? '已结束' : '考勤中'
    }
    return row.is_active ? '考勤中' : '未开启'
}
const getStatusType = (row: AttendanceSession) => {
    if (row.end_time) {
        return isEndedByTime(row.end_time) ? 'danger' : 'success'
    }
    return row.is_active ? 'success' : 'info'
}

// 详情行状态标签类型映射
const statusTagType = (status: string | undefined) => {
    const typeMap: Record<string, string> = {
        '已签到': 'success',
        '请假': 'warning',
        '缺勤': 'danger',
        '未签到': 'info'
    }
    if (!status) return 'info'
    return typeMap[status] || 'info'
}

// 出勤率统计计算
const attendanceStats = computed(() => {
    const details = currentAttendanceDetails.value
    const totalCount = details.length
    
    if (totalCount === 0) {
        return {
            totalCount: 0,
            presentCount: 0,
            leaveCount: 0,
            absentCount: 0,
            attendanceRate: '0.00'
        }
    }
    
    let presentCount = 0  // 已签到
    let leaveCount = 0    // 请假
    let absentCount = 0   // 缺勤/未签到
    
    details.forEach(detail => {
        const status = detail.status || '未签到'
        if (status === '已签到') {
            presentCount++
        } else if (status === '请假') {
            leaveCount++
        } else {
            // 未签到、缺勤等都算作缺勤
            absentCount++
        }
    })
    
    // 出勤率 = (已签到人数 + 请假人数) / 总人数 * 100
    // 或者只计算实际出勤率 = 已签到人数 / 总人数 * 100
    // 这里采用实际出勤率（不包括请假）
    const attendanceRate = totalCount > 0 ? ((presentCount / totalCount) * 100).toFixed(2) : '0.00'
    
    return {
        totalCount,
        presentCount,
        leaveCount,
        absentCount,
        attendanceRate
    }
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
    statusFilter.value = ''
    await fetchAttendanceSessions()
    ElMessage.success('刷新成功')
}

const fetchAttendanceSessions = async () => {
    try {
        const response = await AttendanceQueryApi();
        attendanceSessions.value = response.data;
    } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '获取考勤信息失败');
    }
};

const fetchCourses = async () => {
    try {
        const response = await courseQueryApi();
        courses.value = response.data;
    } catch (error) {
        ElMessage.error('获取课程失败');
    }
};

const fetchClassGroups = async () => {
    try {
        const response = await classGroupsApi();
        classGroups.value = response.data;
    } catch (error) {
        ElMessage.error('获取班级失败');
    }
};

const handleAdd = () => {
    isEdit.value = false;
    currentSession.value = {
        session_name: '',
        course_id: null,
        class_id: null,
        teacher_id: null,
        start_time: '',
        end_time: '',
        is_active: false,
    };
    dialogVisible.value = true;
    fetchCourses();
    fetchClassGroups();
};

const handleEdit = async (row: any) => {
    // 确保课程与班级数据加载完成后再填充表单
    await Promise.all([fetchCourses(), fetchClassGroups()]);
    isEdit.value = true;

    // 复制行数据到当前会话
    currentSession.value = { ...row };

    // 优先使用后端返回的 id（若存在），否则按名称匹配
    const courseIdFromRow = row.course_id ? Number(row.course_id) : null;
    const classIdFromRow = row.class_id ? Number(row.class_id) : null;

    const selectedCourse = courseIdFromRow
        ? courses.value.find(c => Number(c.id) === courseIdFromRow)
        : courses.value.find(c => c.course_name === row.course_name);

    const selectedClassGroup = classIdFromRow
        ? classGroups.value.find(cg => Number(cg.class_id) === classIdFromRow)
        : classGroups.value.find(cg => cg.class_name === row.class_name);

    currentSession.value.course_id = selectedCourse ? Number(selectedCourse.id) : null;
    currentSession.value.class_id = selectedClassGroup ? Number(selectedClassGroup.class_id) : null;

    // 教师信息
    if (selectedCourse && selectedCourse.teacher_info) {
        currentSession.value.teacher_id = Number(selectedCourse.teacher_info.id);
        currentSession.value.teacher_name = selectedCourse.teacher_info.teacher_name;
    } else {
        currentSession.value.teacher_id = row.teacher_id ? Number(row.teacher_id) : null;
        currentSession.value.teacher_name = row.teacher_name || '';
    }

    dialogVisible.value = true;
};

const handleCourseChange = (courseId: number) => {
    const selectedCourse = courses.value.find(course => course.id === courseId);
    if (selectedCourse && selectedCourse.teacher_info) {
        currentSession.value.teacher_id = selectedCourse.teacher_info.id;
        currentSession.value.teacher_name = selectedCourse.teacher_info.teacher_name;
    } else {
        currentSession.value.teacher_id = null;
        currentSession.value.teacher_name = '';
    }
};

const handleActiveToggle = (val: boolean) => {
    // 切换开启/关闭时，结束时间提交为空字符串
    currentSession.value.end_time = ''
}

const handleSubmit = async () => {
    if (!formRef.value) return;
    formRef.value.validate(async (valid: boolean) => {
        if (valid) {
            try {
                if (isEdit.value) {
                    const payload = {
                        id: currentSession.value.id,
                        is_active: currentSession.value.is_active,
                        end_time: currentSession.value.end_time || ''
                    }
                    const response = await attendanceUpdateApi(payload);
                    if (response.code === 200) {
                        ElMessage.success(response.message || '考勤信息更新成功');
                    } else {
                        ElMessage.error(response.message || '更新失败');
                    }
                } else {
                    // 仅传递后端所需字段
                    const payload = {
                        class_id: currentSession.value.class_id,
                        course_id: currentSession.value.course_id,
                        end_time: currentSession.value.end_time || '',
                        session_name: currentSession.value.session_name,
                    };
                    const response = await attendanceAddApi(payload);
                    if (response.code === 200) {
                        ElMessage.success(response.message || '考勤信息添加成功');
                    } else {
                        ElMessage.error(response.message || '添加失败');
                    }
                }
                dialogVisible.value = false;
                fetchAttendanceSessions();
            } catch (error: any) {
                ElMessage.error(error.response?.data?.message || '操作失败');
            }
        } else {
            ElMessage.error('请填写完整信息');
            return false;
        }
    });
};

const handleDelete = async (id: number) => {
    ElMessageBox.confirm('确定删除此考勤信息吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
        .then(async () => {
            try {
                const response = await attendanceDelApi({ id });
                if (response.code === 200) {
                    ElMessage.success(response.message || '考勤信息删除成功');
                    fetchAttendanceSessions();
                } else {
                    ElMessage.error(response.message || '删除失败');
                }
            } catch (error: any) {
                ElMessage.error(error.response?.data?.message || '删除失败');
            }
        })
        .catch(() => {
            ElMessage.info('已取消删除');
        });
};

const handleClose = async (id: number) => {
    ElMessageBox.confirm('确定关闭此考勤信息吗？关闭后将在编辑中继续开启', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
        .then(async () => {
            try {
                const response = await attendanceUpdateApi({ id, is_active: false, end_time: '' });
                if (response.code === 200) {
                    ElMessage.success(response.message || '考勤会话已关闭');
                    fetchAttendanceSessions();
                } else {
                    ElMessage.error(response.message || '关闭失败');
                }
            } catch (error: any) {
                ElMessage.error(error.response?.data?.message || '关闭失败');
            }
        })
        .catch(() => {
            ElMessage.info('已取消关闭');
        });
};

const isOngoing = (row: AttendanceSession) => {
    if (row.end_time) {
        return !isEndedByTime(row.end_time)
    }
    return !!row.is_active
}

const handleOpen = async (row: AttendanceSession) => {
    ElMessageBox.confirm('确定开启此考勤会话吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
        .then(async () => {
            try {
                const payload: any = { id: row.id, is_active: true }
                // 仅当当前记录未设置结束时间时才清空，以避免误清空未来的结束时间
                if (!row.end_time) {
                    payload.end_time = ''
                }
                const response = await attendanceUpdateApi(payload);
                if (response.code === 200) {
                    ElMessage.success(response.message || '考勤会话已开启');
                    fetchAttendanceSessions();
                } else {
                    ElMessage.error(response.message || '开启失败');
                }
            } catch (error: any) {
                ElMessage.error(error.response?.data?.message || '开启失败');
            }
        })
        .catch(() => {
            ElMessage.info('已取消开启');
        });
};

// 导出相关函数
const handleExport = () => {
    exportDialogVisible.value = true;
    // 清空之前的选择和数据
    selectedAttendanceRecords.value = [];
    exportData.value = [];
    if (exportTableRef.value) {
        exportTableRef.value.clearSelection();
    }
};

const handleSelectionChange = (selection: AttendanceSession[]) => {
    selectedAttendanceRecords.value = selection;
};

const selectAll = () => {
    if (exportTableRef.value) {
        exportTableRef.value.toggleAllSelection();
    }
};

const clearSelection = () => {
    if (exportTableRef.value) {
        exportTableRef.value.clearSelection();
    }
};

const generateExport = async () => {
    if (selectedAttendanceRecords.value.length === 0) {
        ElMessage.warning('请先选择要导出的考勤记录');
        return;
    }
    
    exportLoading.value = true;
    exportData.value = [];
    
    try {
        const allStudentData: any[] = [];
        const recordsData: any[] = []; // 存储每个考勤记录的数据
        
        // 为每个选中的考勤记录获取学生数据
        for (const record of selectedAttendanceRecords.value) {
            try {
                const response = await attendanceStudentInfoApi({
                    attendance_id: record.id,
                    class_id: record.class_id
                });
                
                if (response.code === 200) {
                    const now = new Date();
                    const endTime = record.end_time ? parseDate(record.end_time) : null;
                    
                    const students = (response.data || []).map((item: any, index: number) => {
                        // 计算考勤状态
                        let status = item.status;
                        if (!status) {
                            if (item.has_checkin) {
                                status = '已签到';
                            } else if (item.leave) {
                                status = '请假';
                            } else if (endTime && now > endTime) {
                                status = '缺勤';
                            } else {
                                status = '未签到';
                            }
                        }
                        
                        return {
                            序号: index + 1,
                            姓名: item.student_name || '',
                            学号: item.student_id || '',
                            性别: item.gender === 'male' ? '男' : item.gender === 'female' ? '女' : (item.gender || ''),
                            考勤状态: status,
                            课程名称: record.course_name || '',
                            班级名称: record.class_name || '',
                            考勤会话: record.session_name || ''
                        };
                    });
                    
                    // 存储每个考勤记录的数据
                    recordsData.push({
                        record: record,
                        students: students
                    });
                    
                    allStudentData.push(...students);
                }
            } catch (error) {
                console.error(`获取考勤记录 ${record.id} 的学生数据失败:`, error);
            }
        }
        
        // 重新排序序号（用于预览）
        allStudentData.forEach((item, index) => {
            item.序号 = index + 1;
        });
        
        exportData.value = allStudentData;
        // 存储记录数据供导出使用
        (exportData as any).recordsData = recordsData;
        
        if (allStudentData.length === 0) {
            ElMessage.warning('选中的考勤记录中没有学生数据');
        } else {
            ElMessage.success(`成功生成 ${allStudentData.length} 条考勤记录`);
        }
    } catch (error: any) {
        ElMessage.error('生成导出数据失败: ' + (error.message || '未知错误'));
    } finally {
        exportLoading.value = false;
    }
};

const downloadExcel = () => {
    if (exportData.value.length === 0) {
        ElMessage.warning('没有可导出的数据');
        return;
    }
    
    downloadLoading.value = true;
    
    try {
        // 创建工作簿
        const wb = XLSX.utils.book_new();
        const recordsData = (exportData as any).recordsData || [];
        
        // 创建汇总工作表
        if (recordsData.length > 1) {
            const summaryData = [
                ['考勤汇总统计'],
                [''],
                ['课程名称', '班级名称', '考勤会话', '总人数', '已签到', '请假', '缺勤', '未签到', '出勤率']
            ];
            
            recordsData.forEach((recordData: any) => {
                const students = recordData.students;
                const total = students.length;
                const checkedIn = students.filter((s: any) => s.考勤状态 === '已签到').length;
                const leave = students.filter((s: any) => s.考勤状态 === '请假').length;
                const absent = students.filter((s: any) => s.考勤状态 === '缺勤').length;
                const notChecked = students.filter((s: any) => s.考勤状态 === '未签到').length;
                const attendanceRate = total > 0 ? ((checkedIn / total) * 100).toFixed(1) + '%' : '0%';
                
                summaryData.push([
                    recordData.record.course_name || '',
                    recordData.record.class_name || '',
                    recordData.record.session_name || '',
                    total,
                    checkedIn,
                    leave,
                    absent,
                    notChecked,
                    attendanceRate
                ]);
            });
            
            const summaryWs = XLSX.utils.aoa_to_sheet(summaryData);
            
            // 设置汇总表样式
            summaryWs['!cols'] = [
                { wch: 20 }, // 课程名称
                { wch: 15 }, // 班级名称
                { wch: 20 }, // 考勤会话
                { wch: 10 }, // 总人数
                { wch: 10 }, // 已签到
                { wch: 8 },  // 请假
                { wch: 8 },  // 缺勤
                { wch: 10 }, // 未签到
                { wch: 10 }  // 出勤率
            ];
            
            // 合并标题单元格
            summaryWs['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: 8 } }];
            
            XLSX.utils.book_append_sheet(wb, summaryWs, '汇总统计');
        }
        
        // 为每个考勤记录创建独立的工作表
        recordsData.forEach((recordData: any, index: number) => {
            const record = recordData.record;
            const students = recordData.students;
            
            // 计算统计数据
            const total = students.length;
            const checkedIn = students.filter((s: any) => s.考勤状态 === '已签到').length;
            const leave = students.filter((s: any) => s.考勤状态 === '请假').length;
            const absent = students.filter((s: any) => s.考勤状态 === '缺勤').length;
            const notChecked = students.filter((s: any) => s.考勤状态 === '未签到').length;
            const attendanceRate = total > 0 ? ((checkedIn / total) * 100).toFixed(1) + '%' : '0%';
            
            // 创建工作表数据
            const wsData = [
                [`${record.course_name || ''} - ${record.class_name || ''}`],
                [`考勤会话：${record.session_name || ''}`],
                [''],
                ['考勤统计'],
                ['总人数', '已签到', '请假', '缺勤', '未签到', '出勤率'],
                [total, checkedIn, leave, absent, notChecked, attendanceRate],
                [''],
                ['详细名单'],
                ['序号', '姓名', '学号', '性别', '考勤状态'],
                ...students.map((item: any) => [
                    item.序号,
                    item.姓名,
                    item.学号,
                    item.性别,
                    item.考勤状态
                ])
            ];
            
            // 创建工作表
            const ws = XLSX.utils.aoa_to_sheet(wsData);
            
            // 设置列宽
            ws['!cols'] = [
                { wch: 8 },  // 序号
                { wch: 12 }, // 姓名
                { wch: 15 }, // 学号
                { wch: 8 },  // 性别
                { wch: 12 }  // 考勤状态
            ];
            
            // 设置合并单元格
            ws['!merges'] = [
                { s: { r: 0, c: 0 }, e: { r: 0, c: 4 } }, // 标题
                { s: { r: 1, c: 0 }, e: { r: 1, c: 4 } }, // 考勤会话
                { s: { r: 3, c: 0 }, e: { r: 3, c: 4 } }, // 考勤统计标题
                { s: { r: 7, c: 0 }, e: { r: 7, c: 4 } }  // 详细名单标题
            ];
            
            // 生成工作表名称
            let sheetName = `${record.course_name || '课程'}${index + 1}`;
            if (sheetName.length > 31) {
                sheetName = sheetName.substring(0, 28) + '...';
            }
            
            // 添加工作表到工作簿
            XLSX.utils.book_append_sheet(wb, ws, sheetName);
        });
        
        // 如果只有一个考勤记录，也创建一个简单的汇总
        if (recordsData.length === 1) {
            const recordData = recordsData[0];
            const students = recordData.students;
            
            // 创建图表数据工作表
            const chartData = [
                ['考勤状态统计图表数据'],
                [''],
                ['状态', '人数', '百分比'],
                ['已签到', students.filter((s: any) => s.考勤状态 === '已签到').length, 
                 ((students.filter((s: any) => s.考勤状态 === '已签到').length / students.length) * 100).toFixed(1) + '%'],
                ['请假', students.filter((s: any) => s.考勤状态 === '请假').length,
                 ((students.filter((s: any) => s.考勤状态 === '请假').length / students.length) * 100).toFixed(1) + '%'],
                ['缺勤', students.filter((s: any) => s.考勤状态 === '缺勤').length,
                 ((students.filter((s: any) => s.考勤状态 === '缺勤').length / students.length) * 100).toFixed(1) + '%'],
                ['未签到', students.filter((s: any) => s.考勤状态 === '未签到').length,
                 ((students.filter((s: any) => s.考勤状态 === '未签到').length / students.length) * 100).toFixed(1) + '%']
            ];
            
            const chartWs = XLSX.utils.aoa_to_sheet(chartData);
            chartWs['!cols'] = [{ wch: 15 }, { wch: 10 }, { wch: 12 }];
            chartWs['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: 2 } }];
            
            XLSX.utils.book_append_sheet(wb, chartWs, '统计图表');
        }
        
        // 生成Excel文件
        const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        
        // 生成文件名
        const now = new Date();
        const timestamp = now.getFullYear() + 
                         String(now.getMonth() + 1).padStart(2, '0') + 
                         String(now.getDate()).padStart(2, '0') + '_' +
                         String(now.getHours()).padStart(2, '0') + 
                         String(now.getMinutes()).padStart(2, '0');
        const filename = `考勤记录_${timestamp}.xlsx`;
        
        // 下载文件
        saveAs(blob, filename);
        
        ElMessage.success('Excel文件下载成功');
    } catch (error: any) {
        ElMessage.error('Excel文件生成失败: ' + (error.message || '未知错误'));
    } finally {
        downloadLoading.value = false;
    }
};

const getExportStatusType = (status: string) => {
    const typeMap: Record<string, string> = {
        '已签到': 'success',
        '请假': 'warning',
        '缺勤': 'danger',
        '未签到': 'info'
    };
    return typeMap[status] || 'info';
};

onMounted(() => {
    fetchAttendanceSessions();

});

// 显示考勤详情
const showAttendanceDetail = async (row: AttendanceSession) => {
    try {
        const response = await attendanceStudentInfoApi({
            attendance_id: row.id,
            class_id: row.class_id
        });

        if (response.code === 200) {
            const now = new Date();
            const endTime = row.end_time ? parseDate(row.end_time) : null;
            const details = (response.data || []).map((item: any) => {
                // 若后端未返回status，按旧字段兜底计算
                if (!item.status) {
                    let computedStatus = '未签到';
                    if (item.has_checkin) {
                        computedStatus = '已签到';
                    } else if (item.leave) {
                        computedStatus = '请假';
                    } else if (endTime && now > endTime) {
                        computedStatus = '缺勤';
                    }
                    item.status = computedStatus;
                }
                return item;
            });
            currentAttendanceDetails.value = details;
            detailDialogVisible.value = true;
        } else {
            ElMessage.error(response.message || '获取考勤详情失败');
        }
    } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '获取考勤详情失败');
        currentAttendanceDetails.value = [];
        detailDialogVisible.value = true;
    }
};
</script>

<style scoped>
.attendance-management-container {
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

.content-area :deep(.el-tag) {
    border-radius: var(--radius-sm);
    font-weight: 500;
}

.dialog-footer button:first-child {
    margin-right: var(--space-md);
}

/* 出勤统计样式 */
.attendance-statistics {
    border: 1px solid #e4e7ed;
}

.stat-item {
    text-align: center;
    padding: 8px;
}

.stat-label {
    font-size: 14px;
    color: #909399;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 16px;
    font-weight: 600;
    line-height: 1.2;
}

/* 导出弹窗样式 */
.export-container {
    display: flex;
    gap: 20px;
    min-height: 500px;
}

.export-left {
    flex: 1;
    min-width: 0;
}

.export-right {
    flex: 1;
    min-width: 0;
    border-left: 1px solid #e4e7ed;
    padding-left: 20px;
}

.export-actions {
    display: flex;
    gap: 10px;
    align-items: center;
}

.chart-container {
    margin-bottom: 20px;
    padding: 16px;
    background-color: #f5f7fa;
    border-radius: 8px;
}

.chart-container h4 {
    margin: 0 0 16px 0;
    color: #303133;
}

.preview-table h4 {
    margin: 0 0 12px 0;
    color: #303133;
}

.export-final-actions {
    display: flex;
    justify-content: center;
}

.chart {
    width: 100%;
    height: 300px;
}
</style>
