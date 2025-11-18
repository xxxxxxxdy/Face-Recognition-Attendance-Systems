<template>
  <router-view />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import 'element-plus/dist/index.css';

export default defineComponent({
  name: 'App',
});
</script>

<style>
/* Design Tokens - Glassmorphism Style */
:root {
  /* Colors */
  --primary: #2563eb;
  --primary-300: #60a5fa;
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-200: #bfdbfe;
  --text: #374151;
  --text-strong: #1f2937;
  --muted: #6b7280;
  --divider: #eef2ff;
  --table-header: #f8fafc;
  --row-hover: #f9fbff;
  
  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #60a5fa, #2563eb);
  --gradient-bg: linear-gradient(to bottom, rgba(238, 242, 255, 0.5), rgba(224, 242, 254, 0.3));
  
  /* Surfaces/Elevation */
  --surface: rgba(255, 255, 255, 0.9);
  --surface-solid: rgba(255, 255, 255, 0.95);
  --blur: 12px;
  --shadow-1: 0 6px 16px rgba(0, 0, 0, 0.06);
  --shadow-2: 0 8px 24px rgba(0, 0, 0, 0.08);
  --shadow-accent: 0 10px 30px rgba(37, 99, 235, 0.10);
  
  /* Radii */
  --radius-card: 16px;
  --radius-input: 10px;
  --radius-item: 8px;
  --radius-sm: 6px;
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;
}

html,
body,
#app {
  height: 100%;
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Global glassmorphism background */
body {
  background: 
    radial-gradient(circle at 10% 20%, rgba(238, 242, 255, 0.8) 0%, transparent 50%),
    radial-gradient(circle at 90% 80%, rgba(224, 242, 254, 0.6) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(167, 243, 208, 0.3) 0%, transparent 70%),
    linear-gradient(to bottom, #f0f4f8, #e8f0f7);
  background-attachment: fixed;
}

/* Element Plus Overrides for Glassmorphism */
.el-button--primary {
  background: var(--gradient-primary);
  border: none;
  border-radius: var(--radius-input);
  font-weight: 500;
  transition: all 0.3s ease;
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #7bb4fc, #3b75f0);
  transform: translateY(-1px);
  box-shadow: var(--shadow-accent);
}

.el-button--primary:active {
  transform: translateY(0);
}

.el-button {
  border-radius: var(--radius-input);
  font-weight: 500;
  transition: all 0.2s ease;
}

.el-button--default {
  background: var(--primary-50);
  border: 1px solid var(--primary-200);
  color: var(--primary);
}

.el-button--default:hover {
  background: var(--primary-100);
  border-color: var(--primary-300);
}

.el-input__wrapper {
  border-radius: var(--radius-input);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.el-input__wrapper:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1), 0 4px 12px rgba(37, 99, 235, 0.08);
}

.el-select .el-input__wrapper {
  border-radius: var(--radius-input);
}

.el-dialog {
  border-radius: var(--radius-card);
  background: var(--surface-solid);
  backdrop-filter: blur(var(--blur));
  box-shadow: var(--shadow-2);
}

.el-dialog__header {
  border-bottom: 1px solid var(--divider);
  padding: var(--space-xl);
}

.el-dialog__title {
  color: var(--text-strong);
  font-weight: 600;
  font-size: 18px;
}

.el-dialog__body {
  padding: var(--space-xl);
}

.el-table {
  border-radius: var(--radius-card);
  overflow: hidden;
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
}

.el-table th.el-table__cell {
  background: var(--table-header);
  color: var(--text);
  font-weight: 600;
  border-color: var(--divider);
}

.el-table tr {
  transition: background-color 0.2s ease;
}

.el-table tbody tr:hover > td {
  background: var(--row-hover) !important;
}

.el-table td.el-table__cell,
.el-table th.el-table__cell.is-leaf {
  border-color: var(--divider);
}

.el-card {
  border-radius: var(--radius-card);
  background: var(--surface);
  backdrop-filter: blur(var(--blur));
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-1);
}

.el-dropdown-menu {
  border-radius: var(--radius-item);
  background: var(--surface-solid);
  backdrop-filter: blur(var(--blur));
  border: 1px solid var(--divider);
  box-shadow: var(--shadow-2);
}

.el-dropdown-menu__item:hover {
  background: var(--row-hover);
  color: var(--primary);
}

.el-menu {
  border-right: none;
}

.el-menu-item,
.el-sub-menu__title {
  border-radius: var(--radius-item);
  margin: 4px 8px;
  transition: all 0.2s ease;
}

.el-textarea__inner {
  border-radius: var(--radius-input);
  font-family: inherit;
}

.el-select-dropdown {
  border-radius: var(--radius-input);
  background: var(--surface-solid);
  backdrop-filter: blur(var(--blur));
  box-shadow: var(--shadow-2);
}

.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover {
  background: var(--row-hover);
}

.el-select-dropdown__item.selected {
  color: var(--primary);
  font-weight: 600;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  transition: background 0.2s;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.15);
}
</style>
