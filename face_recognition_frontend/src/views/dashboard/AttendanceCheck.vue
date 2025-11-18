<template>
    <div class="attendance-check-container">
        <el-card class="camera-card">
            <template #header>
                <div class="card-header">
                    <span>人脸签到</span>
                </div>
            </template>
            <div class="camera-area">
                <video ref="videoElement" v-show="cameraActive && !capturedImage" autoplay></video>
                <img v-if="capturedImage" :src="capturedImage" alt="Captured Face" class="captured-image-display" />
                <canvas ref="canvasElement" style="display: none;"></canvas>
            </div>
            <div class="controls">
                <el-button type="primary" @click="capturePhoto"
                    :disabled="!cameraActive || capturedImage">拍照</el-button>
                <el-button type="info" @click="retakePhoto" :disabled="!capturedImage">重拍</el-button>
                <el-button type="danger" @click="submitAttendance" :disabled="!capturedImage">签到</el-button>
                <el-button @click="goBack">返回</el-button>
            </div>
        </el-card>

        <!-- 签到结果弹框 -->
        <el-dialog v-model="resultDialogVisible" title="签到结果" width="400px" center :close-on-click-modal="false"
            :close-on-press-escape="false">
            <div class="result-content">
                <el-result :icon="attendanceStatus === 'success' ? 'success' : 'error'" :title="attendanceMessage">
                    <template #extra v-if="attendanceDetail">
                        <p><strong>姓名:</strong> {{ attendanceDetail.student_name }}</p>
                        <p><strong>学号:</strong> {{ attendanceDetail.student_id }}</p>
                        <p><strong>班级:</strong> {{ attendanceDetail.class_name }}</p>
                        <p><strong>签到时间:</strong> {{ attendanceDetail.check_time }}</p>
                    </template>
                </el-result>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="resultDialogVisible = false">关闭</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { faceCheckApi } from '@/utils/api';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter(); // 获取router实例

const videoElement = ref<HTMLVideoElement | null>(null);
const canvasElement = ref<HTMLCanvasElement | null>(null);
let mediaStream: MediaStream | null = null;
const cameraActive = ref(false);
const capturedImage = ref<string | null>(null);

const resultDialogVisible = ref(false); // 控制签到结果弹框的显示与隐藏
const attendanceStatus = ref<'success' | 'error'>('info');
const attendanceMessage = ref('');
const attendanceDetail = ref<any>(null);

const sessionId = route.query.session_id?.toString() || '';


const startCamera = async () => {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoElement.value) {
            videoElement.value.srcObject = mediaStream;
            videoElement.value.play();
            cameraActive.value = true;
        }
    } catch (error) {
        console.error("Error accessing camera:", error);
        ElMessage.error("无法访问摄像头，请检查权限设置。");
        cameraActive.value = false;
    }
};

const stopCamera = () => {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }
    if (videoElement.value) {
        videoElement.value.srcObject = null;
    }
    cameraActive.value = false;
};

const capturePhoto = async () => {
    if (videoElement.value && canvasElement.value) {
        const video = videoElement.value;
        const canvas = canvasElement.value;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        if (context) {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            capturedImage.value = canvas.toDataURL('image/jpeg');
            stopCamera(); // 拍照后停止摄像头
        }
    }
};

const retakePhoto = async () => {
    capturedImage.value = null;
    await nextTick(); // 等待DOM更新，确保video元素重新渲染
    startCamera(); // 重新启动摄像头
};

const submitAttendance = async () => {
    if (!capturedImage.value) {
        ElMessage.warning("请先拍照！");
        return;
    }

    try {
        const formData = new FormData();
        formData.append('face_image', capturedImage.value);
        formData.append('session_id', sessionId);

        const response = await faceCheckApi(formData);
        if (response.code === 200) {
            attendanceStatus.value = 'success';
            attendanceMessage.value = response.msg || "签到成功！";
            attendanceDetail.value = response.data;
        } else {
            attendanceStatus.value = 'error';
            attendanceMessage.value = response.msg || "签到失败！";
            attendanceDetail.value = null;
        }
    } catch (error) {
        console.error("签到请求失败:", error);
        attendanceStatus.value = 'error';
        attendanceMessage.value = "签到请求失败，请稍后再试。";
        attendanceDetail.value = null;
    } finally {
        resultDialogVisible.value = true; // 显示签到结果弹框
    }
};

const goBack = () => {
    router.back();
};

onMounted(() => {
    startCamera();
});

onUnmounted(() => {
    stopCamera();
});
</script>

<style scoped>
.attendance-check-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
    gap: 20px;
}

.camera-card,
.result-card {
    width: 100%;
    max-width: 600px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
}

.camera-area {
    width: 100%;
    height: 0;
    padding-bottom: 75%;
    /* 4:3 Aspect Ratio */
    position: relative;
    background-color: #000;
    border-radius: 8px;
    overflow: hidden;
}

.camera-area video,
.captured-image-display {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 8px;
}

.controls {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    gap: 10px;
}

.result-content {
    text-align: center;
}

.result-content p {
    margin: 5px 0;
}
</style>