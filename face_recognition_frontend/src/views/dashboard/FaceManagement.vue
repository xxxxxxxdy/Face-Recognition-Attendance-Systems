<template>
    <div class="face-management-container">
        <!-- 顶部标题栏 -->
        <div class="top-bar">
            <h2>人脸管理</h2>
            <el-button type="primary" @click="handleAddFace">添加人脸</el-button>
        </div>

        <!-- 功能操作区 -->
        <div class="action-bar">
            <div class="search-area">
                <el-input v-model="searchKeyword" placeholder="搜索学生姓名或学号" clearable style="width: 300px;"
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
                <el-button @click="handleBatchDelete" :disabled="selectedRows.length === 0" type="danger"
                    v-if="userStore.user_type !== 'student'">
                    批量删除 ({{ selectedRows.length }})
                </el-button>
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
            <el-table :data="filteredFaceData" style="width: 100%" border stripe
                @selection-change="handleSelectionChange">
                <el-table-column type="selection" width="70" align="center" />
                <el-table-column type="index" label="序号" width="100" align="center" />
                <el-table-column prop="studentId" label="学号" width="240" align="center" />
                <el-table-column prop="studentName" label="学生姓名" width="150" align="center" />
                <el-table-column prop="className" label="班级" width="150" align="center" />
                <el-table-column prop="uploadTime" label="上传时间" width="280" align="center" />
                <el-table-column label="人脸照片" width="200" align="center">
                    <template #default="scope">
                        <el-image v-if="scope.row.faceImage" :src="scope.row.faceImage" fit="cover"
                            style="width: 60px; height: 60px; border-radius: 8px; cursor: pointer;"
                            @click="handleImagePreview(scope.row.faceImage)" />
                        <span v-else style="color: var(--muted);">未上传</span>
                    </template>
                </el-table-column>

                <el-table-column prop="status" label="状态" width="150" align="center">
                    <template #default="scope">
                        <el-tag :type="scope.row.faceImage ? 'success' : 'info'" size="small">
                            {{ scope.row.faceImage ? '已录入' : '未录入' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作" align="center" fixed="right">
                    <template #default="scope">
                        <el-button size="small" @click="handleView(scope.row)">查看</el-button>
                        <el-button
                            v-if="userStore.user_type !== 'student' || scope.row.studentId === studentSelfUser?.student_id"
                            size="small" type="primary" @click="handleUpdate(scope.row)">更新</el-button>
                        <el-button size="small" type="danger" @click="handleDelete(scope.row)"
                            v-if="userStore.user_type !== 'student'">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <!-- 添加/更新人脸对话框 -->
        <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" @close="handleDialogClose">
            <el-form :model="faceForm" :rules="rules" ref="faceFormRef" label-width="100px">
                <el-form-item label="学生姓名" prop="studentName">
                    <el-input v-model="faceForm.studentName" placeholder="请输入学生姓名"></el-input>
                </el-form-item>
                <el-form-item label="学号" prop="studentId">
                    <el-input v-model="faceForm.studentId" placeholder="请输入学号" @blur="handleStudentIdBlur"></el-input>
                </el-form-item>
                <el-form-item label="班级" prop="className">
                    <el-input v-model="faceForm.className" placeholder="输入姓名与学号后自动选择班级" disabled></el-input>
                </el-form-item>
                <el-form-item label="录入方式" prop="captureMethod">
                    <el-tabs v-model="captureMethod" class="capture-tabs">
                        <el-tab-pane label="上传图片" name="upload">
                            <div class="upload-area">
                                <el-upload class="face-uploader" :auto-upload="false" :show-file-list="false"
                                    :on-change="handleFileChange" accept="image/*" drag>
                                    <el-image v-if="previewImage" :src="previewImage" fit="cover"
                                        class="preview-image" />
                                    <div v-else class="upload-placeholder">
                                        <el-icon class="upload-icon">
                                            <Upload />
                                        </el-icon>
                                        <div class="upload-text">拖拽图片到此处或点击上传</div>
                                        <div class="upload-hint">支持 jpg、png 格式，建议正面免冠照片</div>
                                    </div>
                                </el-upload>
                            </div>
                        </el-tab-pane>
                        <el-tab-pane label="摄像头拍摄" name="camera">
                            <div class="camera-area">
                                <div class="camera-container">
                                    <video v-show="!capturedImage && cameraActive" ref="videoRef" class="camera-video"
                                        autoplay></video>
                                    <el-image v-if="capturedImage" :src="capturedImage" fit="cover"
                                        class="captured-image" />
                                    <div v-if="!cameraActive && !capturedImage" class="camera-placeholder">
                                        <el-icon class="camera-icon">
                                            <Camera />
                                        </el-icon>
                                        <p>点击下方按钮启动摄像头</p>
                                    </div>
                                    <canvas ref="canvasRef" style="display: none;"></canvas>
                                </div>
                                <div class="camera-controls">
                                    <el-button v-if="!cameraActive" type="primary" @click="startCamera">
                                        <el-icon>
                                            <VideoCamera />
                                        </el-icon>
                                        启动摄像头
                                    </el-button>
                                    <template v-else>
                                        <el-button type="success" @click="capturePhoto" :disabled="!!capturedImage">
                                            <el-icon>
                                                <Camera />
                                            </el-icon>
                                            拍照
                                        </el-button>
                                        <el-button v-if="capturedImage" @click="retakePhoto">
                                            <el-icon>
                                                <RefreshRight />
                                            </el-icon>
                                            重拍
                                        </el-button>
                                        <el-button type="danger" @click="handleStopCameraAndMessage">
                                            <el-icon>
                                                <Close />
                                            </el-icon>
                                            关闭摄像头
                                        </el-button>
                                    </template>
                                </div>
                            </div>
                        </el-tab-pane>
                    </el-tabs>
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
        <el-dialog v-model="viewDialogVisible" title="人脸详情" width="600px">
            <div class="detail-container" v-if="currentFace">
                <div class="detail-image-section">
                    <el-image v-if="currentFace.faceImage" :src="currentFace.faceImage"
                        :preview-src-list="[currentFace.faceImage]" fit="cover" class="detail-face-image" />
                </div>
                <div class="detail-info-section">
                    <div class="detail-row">
                        <span class="detail-label">学生姓名：</span>
                        <span class="detail-value">{{ currentFace.studentName }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">学号：</span>
                        <span class="detail-value">{{ currentFace.studentId }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">班级：</span>
                        <span class="detail-value">{{ currentFace.className }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">上传时间：</span>
                        <span class="detail-value">{{ currentFace.uploadTime }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">状态：</span>
                        <el-tag :type="currentFace.faceImage ? 'success' : 'info'" size="small">
                            {{ currentFace.faceImage ? '已录入' : '未录入' }}
                        </el-tag>
                    </div>
                </div>
            </div>
            <template #footer>
                <el-button type="primary" @click="viewDialogVisible = false">关闭</el-button>
            </template>
        </el-dialog>

        <!-- 全屏图片预览对话框 -->
        <el-dialog v-model="imagePreviewDialogVisible" title="图片预览" width="500px" class="image-preview-dialog">
            <div class="image-preview-content">
                <el-image :src="currentPreviewImage" fit="contain" class="full-screen-image" />
            </div>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onBeforeUnmount, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Upload, Camera, VideoCamera, RefreshRight, Close } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import { faceAddApi, classGroupsStudentIdApi, faceQueryApi, faceUpdateApi, studentSelfUserApi } from '@/utils/api'
import { useUserStore } from '@/stores/user'

interface FaceRecord {
    id: number
    studentName: string
    studentId: string
    className: string
    faceImage: string
    faceCount: number
    uploadTime: string
    status: 'active' | 'inactive'
}

// 人脸数据
const mockFaceData = ref<FaceRecord[]>([])

// 登录的学生信息
const studentSelfUser = ref<any>({})

const searchKeyword = ref('')
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const imagePreviewDialogVisible = ref(false)
const currentPreviewImage = ref('')
const dialogTitle = ref('添加人脸')
const faceFormRef = ref<any>(null)
const currentFace = ref<FaceRecord | null>(null)
const selectedRows = ref<FaceRecord[]>([])
const captureMethod = ref('upload')
const previewImage = ref('')
const capturedImage = ref('')
const cameraActive = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const userStore = useUserStore() // 实例化 userStore
const canvasRef = ref<HTMLCanvasElement | null>(null)
const mediaStream = ref<MediaStream | null>(null)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const faceForm = reactive({
    studentName: '',
    studentId: '',
    className: ''
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
    ]
})

// 过滤后的数据
const filteredFaceData = computed(() => {
    let data = mockFaceData.value

    if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        data = data.filter(item =>
            item.studentName.toLowerCase().includes(keyword) ||
            item.studentId.toLowerCase().includes(keyword)
        )
    }

    return data
})

// 处理选择变化
const handleSelectionChange = (selection: FaceRecord[]) => {
    selectedRows.value = selection
}

// 添加人脸
const handleAddFace = () => {
    dialogTitle.value = '添加人脸'
    isEditing.value = false
    editingId.value = null
    dialogVisible.value = true
    captureMethod.value = 'upload'
    previewImage.value = ''
    capturedImage.value = ''
    if (faceFormRef.value) {
        faceFormRef.value.resetFields()
    }
    Object.assign(faceForm, {
        studentName: '',
        studentId: '',
        className: ''
    })
}

// 更新人脸
const handleUpdate = (row: FaceRecord) => {
    dialogTitle.value = '更新人脸'
    isEditing.value = true
    editingId.value = row.id
    dialogVisible.value = true
    captureMethod.value = 'upload'
    previewImage.value = row.faceImage
    capturedImage.value = ''
    Object.assign(faceForm, {
        studentName: row.studentName,
        studentId: row.studentId,
        className: row.className
    })
}

// 获取登录的学生信息
const getStudentSelfUser = async () => {
    try {
        const res = await studentSelfUserApi()
        if (res.code === 200) {
            studentSelfUser.value = res.data
        } else {
            ElMessage.error(res.message || '获取学生信息失败')
        }
    } catch (error) {
        ElMessage.error('获取学生信息失败')
    }
}

// 处理文件选择
const handleFileChange = (file: UploadFile) => {
    if (file.raw) {
        const reader = new FileReader()
        reader.onload = (e) => {
            previewImage.value = e.target?.result as string
        }
        reader.readAsDataURL(file.raw)
    }
}

// 启动摄像头
const startCamera = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        })
        mediaStream.value = stream
        if (videoRef.value) {
            videoRef.value.srcObject = stream
        }
        cameraActive.value = true
        capturedImage.value = ''
        ElMessage.success('摄像头已启动')
    } catch (error) {
        ElMessage.error('无法访问摄像头，请检查权限设置')
        console.error('Camera error:', error)
    }
}

// 停止摄像头
const stopCamera = () => {
    if (mediaStream.value) {
        mediaStream.value.getTracks().forEach(track => track.stop())
        mediaStream.value = null
    }
    cameraActive.value = false
    capturedImage.value = ''
}

// 拍照
const capturePhoto = () => {
    if (videoRef.value && canvasRef.value) {
        const video = videoRef.value
        const canvas = canvasRef.value
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        const ctx = canvas.getContext('2d')
        if (ctx) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
            capturedImage.value = canvas.toDataURL('image/png')
            ElMessage.success('拍照成功')
        }
    }
}

// 重拍
const retakePhoto = () => {
    capturedImage.value = ''
}

// 学号输入框失去焦点时查询班级
const handleStudentIdBlur = async () => {
    if (!faceForm.studentId || !faceForm.studentName) {
        return
    }

    try {
        const response = await classGroupsStudentIdApi({
            student_id: faceForm.studentId,
            student_name: faceForm.studentName
        })

        if (response && response.data && response.data.class_name) {
            faceForm.className = response.data.class_name
        } else {
            faceForm.className = ''
            ElMessage.error('该学生不存在')
        }
    } catch (error: any) {
        faceForm.className = ''
        if (error.response && error.response.data && error.response.data.message) {
            ElMessage.error(error.response.data.message)
        } else {
            ElMessage.error('查询班级信息失败')
        }
    }
}

// 对话框关闭时清理
const handleDialogClose = () => {
    stopCamera()
    previewImage.value = ''
    capturedImage.value = ''
    faceForm.className = ''
}

// 提交表单
const submitForm = () => {
    if (!faceFormRef.value) return

    faceFormRef.value.validate((valid: boolean) => {
        if (valid) {
            // 检查是否有人脸图片
            const faceImage = captureMethod.value === 'upload' ? previewImage.value : capturedImage.value

            if (!faceImage) {
                ElMessage.error('请上传人脸图片或拍摄人脸照片')
                return
            }

            const payload = {
                student_name: faceForm.studentName,
                student_id: faceForm.studentId,
                face_image: faceImage
            }

            if (isEditing.value && editingId.value !== null) {
                // 更新模式
                faceUpdateApi({ ...payload, id: editingId.value })
                    .then(() => {
                        ElMessage.success('人脸信息更新成功')
                        dialogVisible.value = false
                        fetchFaceData()
                    })
                    .catch((error) => {
                        if (error.response && error.response.data && error.response.data.message) {
                            ElMessage.error(error.response.data.message)
                        } else {
                            ElMessage.error(`更新失败: ${error.message}`)
                        }
                    })
            } else {
                // 添加模式
                faceAddApi(payload)
                    .then(() => {
                        ElMessage.success('人脸信息上传成功')
                        dialogVisible.value = false
                        fetchFaceData()
                    })
                    .catch((error) => {
                        if (error.response && error.response.data && error.response.data.message) {
                            ElMessage.error(error.response.data.message)
                        } else {
                            ElMessage.error(`上传失败: ${error.message}`)
                        }
                    })
            }
        }
    })
}

// 查看详情
const handleView = (row: FaceRecord) => {
    currentFace.value = row
    viewDialogVisible.value = true
}

// 删除单个
const handleDelete = (row: FaceRecord) => {
    ElMessageBox.confirm('确定删除此人脸记录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        const index = mockFaceData.value.findIndex(item => item.id === row.id)
        if (index !== -1) {
            mockFaceData.value.splice(index, 1)
            ElMessage.success('删除成功')
        }
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}

// 批量删除
const handleBatchDelete = () => {
    ElMessageBox.confirm(`确定删除选中的 ${selectedRows.value.length} 条记录吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        const selectedIds = selectedRows.value.map(row => row.id)
        mockFaceData.value = mockFaceData.value.filter(item => !selectedIds.includes(item.id))
        selectedRows.value = []
        ElMessage.success('批量删除成功')
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
    selectedRows.value = []
    ElMessage.success('刷新成功')
}

const handleStopCameraAndMessage = () => {
    stopCamera()
    ElMessage.info('摄像头已关闭')
}

// 获取人脸数据
const fetchFaceData = async () => {
    try {
        const response = await faceQueryApi()
        if (response && response.data) {
            mockFaceData.value = response.data.map((item: any) => ({
                id: item.id,
                studentName: item.student_name,
                studentId: item.student_id,
                className: item.class_name,
                faceImage: item.face_image ? `http://localhost:8000${item.face_image}` : null,
                faceCount: 1,
                uploadTime: item.capture_time,
                status: 'active'
            }))
        }
    } catch (error: any) {
        console.error('获取人脸数据失败:', error)
        ElMessage.error('获取人脸数据失败，请刷新页面重试')
    }
}

// 组件挂载时获取数据
onMounted(() => {
    fetchFaceData()
    if (userStore.user_type === 'student') {
        getStudentSelfUser()
    }
})

// 组件卸载时清理摄像头
onBeforeUnmount(() => {
    stopCamera()
})
// 处理图片预览
const handleImagePreview = (imageUrl: string) => {
    currentPreviewImage.value = imageUrl
    imagePreviewDialogVisible.value = true
}
</script>

<style scoped>
.face-management-container {
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
    gap: var(--space-md);
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

.capture-tabs {
    margin-top: var(--space-md);
}

.upload-area {
    padding: var(--space-lg) 0;
}

.face-uploader :deep(.el-upload) {
    width: 100%;
}

.face-uploader :deep(.el-upload-dragger) {
    width: 100%;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-card);
    border: 2px dashed var(--primary-200);
    background: var(--primary-50);
    transition: all 0.3s ease;
}

.face-uploader :deep(.el-upload-dragger:hover) {
    border-color: var(--primary);
    background: var(--primary-100);
}

.upload-placeholder {
    text-align: center;
}

.upload-icon {
    font-size: 64px;
    color: var(--primary-300);
    margin-bottom: var(--space-lg);
}

.upload-text {
    font-size: 16px;
    color: var(--text);
    margin-bottom: var(--space-sm);
}

.upload-hint {
    font-size: 14px;
    color: var(--muted);
}

.preview-image,
.captured-image {
    width: 100%;
    height: 300px;
    border-radius: var(--radius-card);
}

.camera-area {
    padding: var(--space-lg) 0;
}

.camera-container {
    width: 100%;
    height: 360px;
    background: #000;
    border-radius: var(--radius-card);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--space-lg);
}

.camera-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.camera-placeholder {
    text-align: center;
    color: #fff;
}

.camera-icon {
    font-size: 64px;
    margin-bottom: var(--space-lg);
}

.camera-placeholder p {
    font-size: 16px;
    margin: 0;
}

.camera-controls {
    display: flex;
    justify-content: center;
    gap: var(--space-md);
    flex-wrap: wrap;
}

.detail-container {
    padding: var(--space-lg);
}

.detail-image-section {
    text-align: center;
    margin-bottom: var(--space-xl);
}

.detail-face-image {
    width: 200px;
    height: 200px;
    border-radius: var(--radius-card);
    box-shadow: var(--shadow-1);
    cursor: pointer;
}

.detail-info-section {
    padding: var(--space-lg);
    background: var(--primary-50);
    border-radius: var(--radius-card);
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

.content-area :deep(.el-avatar) {
    border: 2px solid var(--divider);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    background-color: transparent !important;
}

.image-preview-dialog .el-dialog__body {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.image-preview-dialog .full-screen-image {
    max-width: 100%;
    max-height: 80vh;
    /* 限制最大高度，避免图片过大 */
    object-fit: contain;
}
</style>
