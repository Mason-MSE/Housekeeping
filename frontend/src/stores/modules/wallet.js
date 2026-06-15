import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { walletApi } from '@/api'

export const useWalletStore = defineStore('wallet', () => {
  const wallet = ref(null)
  const transactions = ref([])

  const balance = computed(() => wallet.value?.balance || 0)
  const hasWallet = computed(() => !!wallet.value)

  async function fetchWallet() {
    try {
      const response = await walletApi.get()
      wallet.value = response
      return response
    } catch (error) {
      console.error('Failed to fetch wallet:', error)
      throw error
    }
  }

  async function recharge(amount) {
    try {
      const response = await walletApi.recharge({ amount })
      wallet.value = response.wallet || response
      return response
    } catch (error) {
      console.error('Failed to recharge wallet:', error)
      throw error
    }
  }

  async function fetchTransactions() {
    try {
      const response = await walletApi.transactions()
      transactions.value = response.items || response
      return response
    } catch (error) {
      console.error('Failed to fetch transactions:', error)
      throw error
    }
  }

  async function pay(orderId) {
    try {
      const response = await walletApi.pay(orderId)
      wallet.value = response.wallet || response
      
      // 更新交易记录
      if (response.transaction) {
        transactions.value.unshift(response.transaction)
      }
      
      return response
    } catch (error) {
      console.error('Failed to pay:', error)
      throw error
    }
  }

  async function settle(orderId) {
    try {
      const response = await walletApi.settle(orderId)
      wallet.value = response.wallet || response
      
      // 更新交易记录
      if (response.transaction) {
        transactions.value.unshift(response.transaction)
      }
      
      return response
    } catch (error) {
      console.error('Failed to settle:', error)
      throw error
    }
  }

  function clearWallet() {
    wallet.value = null
    transactions.value = []
  }

  return {
    wallet,
    transactions,
    balance,
    hasWallet,
    fetchWallet,
    recharge,
    fetchTransactions,
    pay,
    settle,
    clearWallet
  }
})