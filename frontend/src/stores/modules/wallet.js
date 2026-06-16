import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { walletApi } from '@/api'

// Pinia store managing wallet state (balance, transactions)
export const useWalletStore = defineStore('wallet', () => {
  // The user's wallet object
  const wallet = ref(null)
  // List of wallet transactions
  const transactions = ref([])

  // Computed wallet balance (0 if no wallet)
  const balance = computed(() => wallet.value?.balance || 0)
  // Whether the user has a wallet
  const hasWallet = computed(() => !!wallet.value)

  // Fetch the user's wallet details from the API
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

  // Recharge the wallet with a specified amount
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

  // Fetch the wallet transaction history
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

  // Pay for an order using the wallet balance
  async function pay(orderId) {
    try {
      const response = await walletApi.pay(orderId)
      wallet.value = response.wallet || response
      
      // Update transaction records
      if (response.transaction) {
        transactions.value.unshift(response.transaction)
      }
      
      return response
    } catch (error) {
      console.error('Failed to pay:', error)
      throw error
    }
  }

  // Settle earnings for a completed order
  async function settle(orderId) {
    try {
      const response = await walletApi.settle(orderId)
      wallet.value = response.wallet || response
      
      // Update transaction records
      if (response.transaction) {
        transactions.value.unshift(response.transaction)
      }
      
      return response
    } catch (error) {
      console.error('Failed to settle:', error)
      throw error
    }
  }

  // Reset wallet and transactions state (e.g. on logout)
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
