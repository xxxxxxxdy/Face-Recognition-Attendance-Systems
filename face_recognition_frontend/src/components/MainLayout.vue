<template>
    <el-container class="common-layout">
        <el-aside :width="isCollapse ? '64px' : '200px'" class="aside-menu">
            <div class="logo-title">
                <img :src="FaceRecognitionIcon" alt="Face Recognition Icon" class="logo-icon" />
                <span v-if="!isCollapse">课堂考勤系统</span>
            </div>
            <el-menu :default-active="route.path" class="el-menu-vertical-demo" :collapse="isCollapse"
                @open="handleOpen" @close="handleClose">
                <template v-for="menu in filteredMenus" :key="menu.index">
                    <el-sub-menu v-if="menu.children" :index="menu.index">
                        <template #title>
                            <el-icon>
                                <component :is="menu.icon" />
                            </el-icon>
                            <span>{{ menu.title }}</span>
                        </template>
                        <el-menu-item v-for="child in menu.children" :key="child.index" :index="child.path"
                            @click="handleMenuItemClick(child.path)">
                            {{ child.title }}
                        </el-menu-item>
                    </el-sub-menu>
                    <el-menu-item v-else :index="menu.path" @click="handleMenuItemClick(menu.path)">
                        <el-icon>
                            <component :is="menu.icon" />
                        </el-icon>
                        <span>{{ menu.title }}</span>
                    </el-menu-item>
                </template>
            </el-menu>
        </el-aside>
        <el-container>
            <el-header class="header-bar">
                <div class="header-left">
                    <el-icon class="collapse-icon" @click="toggleCollapse">
                        <component :is="isCollapse ? Expand : Fold" />
                    </el-icon>
                    <span class="breadcrumb">{{ breadcrumbTitle }}</span>
                </div>
                <div class="header-right">
                    <el-dropdown>
                        <span class="el-dropdown-link">
                            <el-avatar :size="30" :src="userAvatar" />
                            <span class="username">{{ welcomeText }}</span>
                            <el-icon class="el-icon--right"><arrow-down /></el-icon>
                        </span>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item @click="goToProfile">个人中心</el-dropdown-item>
                                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
            </el-header>
            <el-main class="main-content">
                <router-view></router-view>
            </el-main>
        </el-container>
    </el-container>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { menuConfig } from '@/utils/menuConfig'
import { homeApi } from '@/utils/api'
import {
    Fold,
    Expand,
    ArrowDown
} from '@element-plus/icons-vue'
import FaceRecognitionIcon from '@/assets/icons/face_icon.svg'
import AvatarIcon from '@/assets/icons/avatar.png'

const isCollapse = ref(false)
const userData = ref<any>(null)

const toggleCollapse = () => {
    isCollapse.value = !isCollapse.value
}

const handleOpen = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}

const router = useRouter()
const route = useRoute()
const handleMenuItemClick = (path: string) => {
    router.push(path)
}

const userStore = useUserStore()
const currentRole = computed(() => userStore.user_type)

const filteredMenus = computed(() => {
    const role = currentRole.value;
    // 不要直接修改 menuConfig，返回新数组
    return menuConfig
        .filter(menu => Array.isArray(menu.permission) && menu.permission.includes(role))
        .map(menu => ({
            ...menu,
            children: Array.isArray(menu.children)
                ? menu.children.filter(child => Array.isArray(child.permission) && child.permission.includes(role))
                : undefined
        }))
})

const breadcrumbTitle = computed(() => {
    let title = '首页'
    for (const menu of menuConfig) {
        if (menu.path === route.path) {
            title = menu.title
            break
        }
        if (menu.children) {
            for (const child of menu.children) {
                if (child.path === route.path) {
                    title = `${menu.title} > ${child.title}`
                    break
                }
            }
        }
    }
    return title
})

// 将相对路径转换为完整URL
const getFullAvatarUrl = (relativePath: string) => {
    if (!relativePath) return AvatarIcon
    
    // 如果是base64数据URL，直接返回
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

// 计算用户头像
const userAvatar = computed(() => {
    if (userData.value?.avatar) {
        return getFullAvatarUrl(userData.value.avatar)
    }
    return AvatarIcon // 默认头像
})

// 计算欢迎文本
const welcomeText = computed(() => {
    if (userData.value?.name) {
        const roleText = {
            'student': '同学',
            'teacher': '老师',
            'admin': '管理员'
        }[currentRole.value] || ''
        return `欢迎你，${userData.value.name}${roleText}！`
    }
    return '欢迎你！'
})

// 跳转到个人中心
const goToProfile = () => {
    router.push('/profile')
}

const logout = () => {
    localStorage.removeItem('token')
    userStore.setUserType('')
    router.push('/login')
}

// 获取用户信息
onMounted(async () => {
    try {
        userData.value = await homeApi().then(res => res.data)
    } catch (error) {
        console.error('获取用户信息失败:', error)
    }
})
</script>

<style scoped>
.common-layout {
    height: 100vh;
    background: transparent;
}

.aside-menu {
    background: var(--surface);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    border-right: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
}

.logo-title {
    color: var(--primary);
    font-size: 20px;
    font-weight: 700;
    text-align: center;
    padding: var(--space-xl) 0;
    border-bottom: 1px solid var(--divider);
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-md);
}

.logo-icon {
    width: 2rem;
    height: 2rem;
    filter: drop-shadow(0 2px 4px rgba(37, 99, 235, 0.2));
}

.logo-title span {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.el-menu-vertical-demo {
    height: 100%;
    border-right: none;
    flex-grow: 1;
    overflow-y: auto;
    background: transparent !important;
    padding: var(--space-sm) 0;
}

.el-menu-vertical-demo :deep(.el-menu-item),
.el-menu-vertical-demo :deep(.el-sub-menu__title) {
    color: var(--text);
    border-radius: var(--radius-item);
    margin: 4px var(--space-sm);
    height: 48px;
    line-height: 48px;
}

.el-menu-vertical-demo :deep(.el-menu-item:hover),
.el-menu-vertical-demo :deep(.el-sub-menu__title:hover) {
    background: var(--primary-50);
    color: var(--primary);
}

.el-menu-vertical-demo :deep(.el-menu-item.is-active) {
    background: linear-gradient(135deg, rgba(96, 165, 250, 0.15), rgba(37, 99, 235, 0.15));
    color: var(--primary);
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
}

.el-menu-vertical-demo :deep(.el-sub-menu .el-menu-item) {
    background: transparent;
    min-width: auto;
}

.el-menu-vertical-demo :deep(.el-sub-menu .el-menu-item:hover) {
    background: var(--primary-50);
}

.el-menu-vertical-demo :deep(.el-sub-menu .el-menu-item.is-active) {
    background: linear-gradient(135deg, rgba(96, 165, 250, 0.15), rgba(37, 99, 235, 0.15));
    color: var(--primary);
    font-weight: 600;
}

.header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--surface);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    border-bottom: 1px solid var(--divider);
    padding: 0 var(--space-xl);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-left {
    display: flex;
    align-items: center;
    gap: var(--space-lg);
}

.collapse-icon {
    font-size: 20px;
    cursor: pointer;
    color: var(--text);
    transition: all 0.2s ease;
    padding: var(--space-sm);
    border-radius: var(--radius-sm);
}

.collapse-icon:hover {
    color: var(--primary);
    background: var(--primary-50);
}

.breadcrumb {
    font-size: 16px;
    color: var(--text-strong);
    font-weight: 500;
}

.header-right {
    display: flex;
    align-items: center;
}

.el-dropdown-link {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-item);
    transition: all 0.2s ease;
    gap: var(--space-sm);
}

.el-dropdown-link:hover {
    background: var(--primary-50);
}

.username {
    color: var(--text);
    font-weight: 500;
}

.el-avatar {
    background-color: transparent !important;
}

.main-content {
    background: transparent;
    padding: var(--space-xl);
    overflow-y: auto;
}

/* Collapsed state adjustments */
.el-menu-vertical-demo.el-menu--collapse {
    width: 64px;
}

.el-menu-vertical-demo.el-menu--collapse :deep(.el-menu-item),
.el-menu-vertical-demo.el-menu--collapse :deep(.el-sub-menu__title) {
    padding: 0 !important;
    text-align: center;
}
</style>