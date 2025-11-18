<template>
    <div class="student-attendance-management-container">
        <h2>学生考勤</h2>

        <el-table :data="activeAttendanceSessions" style="width: 100%; margin-top: 20px;" border>
            <el-table-column type="index" label="序号" width="80"></el-table-column>
            <el-table-column prop="course_name" label="课程名称"></el-table-column>
            <el-table-column prop="teacher_name" label="老师名称"></el-table-column>
            <el-table-column prop="class_name" label="班级"></el-table-column>
            <el-table-column prop="participant_count" label="参与人数"></el-table-column>
            <el-table-column prop="session_name" label="备注"></el-table-column>
            <el-table-column label="操作" width="120">
                <template #default="scope">
                    <el-button size="small" 
                        :type="scope.row.is_closed ? 'info' : (!scope.row.is_active ? 'warning' : (scope.row.signed_in ? 'success' : 'primary'))"
                        @click="handleJoinAttendance(scope.row)"
                        :disabled="scope.row.signed_in || scope.row.is_closed || !scope.row.is_active">
                        {{ scope.row.is_closed ? '已关闭' : (!scope.row.is_active ? '未开启' : (scope.row.signed_in ? '已签到' : '签到')) }}
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import http from '../../utils/http';
import { ElMessage } from 'element-plus';
import { studentActiveQueryApi } from '@/utils/api';
interface ActiveAttendanceSession {
    session_id: number;
    session_name: string;
    course_name: string;
    class_name: string;
    teacher_name: string;
    participant_count: number;
    start_time?: string;
    end_time?: string;
    is_closed: boolean;
    signed_in: boolean;
    is_active: boolean;
}

const activeAttendanceSessions = ref<ActiveAttendanceSession[]>([]);

const fetchActiveAttendanceSessions = async () => {
    try {
        const response = await studentActiveQueryApi();
        activeAttendanceSessions.value = response.data.map((session: any) => ({
            session_id: session.session_id,
            session_name: session.session_name,
            course_name: session.course_name,
            class_name: session.class_name,
            teacher_name: session.teacher_name,
            participant_count: session.participant_count,
            start_time: session.start_time,
            end_time: session.end_time,
            // 兼容后端未返回 is_closed 的情况，按 end_time 推断
            is_closed: session.is_closed !== undefined ? session.is_closed : (session.end_time ? new Date(session.end_time).getTime() < Date.now() : false),
            signed_in: !!session.signed_in,
            is_active: !!session.is_active
        }));
    } catch (error) {
        ElMessage.error('获取考勤会话失败');
    }
};

const router = useRouter();

const handleJoinAttendance = (session: ActiveAttendanceSession) => {
    if (session.is_closed) {
        ElMessage.warning('该考勤会话已关闭，无法签到。');
        return;
    }
    if (!session.is_active) {
        ElMessage.warning('该考勤会话未开启，无法签到。');
        return;
    }
    if (session.signed_in) {
        ElMessage.success('该考勤会话已签到，无需重复签到。');
        return;
    }
    router.push({ name: 'AttendanceCheck', query: { session_id: session.session_id } });
};

onMounted(() => {
    fetchActiveAttendanceSessions();
});
</script>

<style scoped>
.student-attendance-management-container {
    display: flex;
    flex-direction: column;
    gap: var(--space-xl);
}

.student-attendance-management-container h2 {
    margin: 0 0 var(--space-lg) 0;
    font-size: 24px;
    font-weight: 700;
    color: var(--text-strong);
    background: var(--surface);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    padding: var(--space-xl);
    border-radius: var(--radius-card);
    border: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: var(--shadow-1);
}

.student-attendance-management-container :deep(.el-table) {
    background: var(--surface);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    border-radius: var(--radius-card);
    border: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: var(--shadow-1);
}

.student-attendance-management-container :deep(.el-table th) {
    background: var(--table-header);
    font-weight: 600;
    color: var(--text);
}
</style>