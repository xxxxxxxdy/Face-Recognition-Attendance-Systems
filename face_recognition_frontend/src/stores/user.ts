import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  persist: true,
  state: () => ({
    user_type: ''
  }),
  actions: {
    setUserType(type: string) {
      this.user_type = type
    }
  }
})