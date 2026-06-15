<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { walletApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const walletInfo = ref({ balance: 0, frozen_balance: 0 })
const transactions = ref([])
const rechargeDialogVisible = ref(false)
const rechargeAmount = ref(100)

const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
const canRecharge = computed(() => userRoles.value.some(r => ['admin', 'guest'].includes(r)))

const fetchWallet = async () => {
  loading.value = true
  try {
    const [walletRes, transRes] = await Promise.all([
      walletApi.get(),
      walletApi.transactions()
    ])
    walletInfo.value = walletRes
    transactions.value = transRes || []
  } catch (error) {
    console.error('Failed to fetch wallet:', error)
  } finally {
    loading.value = false
  }
}

const handleRecharge = async () => {
  if (rechargeAmount.value <= 0) {
    ElMessage.warning('Please enter valid amount')
    return
  }
  
  try {
    await walletApi.recharge({ amount: rechargeAmount.value })
    ElMessage.success('Recharge successful')
    rechargeDialogVisible.value = false
    fetchWallet()
  } catch (error) {
    ElMessage.error('Recharge failed')
  }
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('en-US')
}

const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    recharge: 'Recharge',
    payment: 'Payment',
    income: 'Income',
    earning: 'Earning',
    settlement: 'Settlement',
    refund: 'Refund',
    refund_clawback: 'Refund adjustment'
  }
  return map[type] || type
}

const getTypeColor = (type: string) => {
  const map: Record<string, string> = {
    recharge: 'success',
    payment: 'danger',
    income: 'success',
    earning: 'success',
    settlement: 'success',
    refund: 'success',
    refund_clawback: 'danger'
  }
  return map[type] || 'info'
}

/** Types that reduce wallet balance (show − and red). */
const isWalletDebitType = (type: string) => {
  const t = (type || '').toLowerCase()
  return t === 'payment' || t === 'refund_clawback'
}

const formatTxAmount = (row: { type: string; amount?: number }) => {
  const raw = Number(row.amount)
  const fixed = Number.isFinite(raw) ? raw.toFixed(2) : '0.00'
  const debit = isWalletDebitType(row.type)
  return {
    cls: debit ? 'amount-negative' : 'amount-positive',
    prefix: debit ? '-' : '+',
    fixed
  }
}

onMounted(() => {
  fetchWallet()
})
</script>

<template>
  <div class="wallet-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="wallet-card">
          <div class="wallet-header">
            <div class="wallet-info">
              <el-icon class="wallet-icon"><Wallet /></el-icon>
              <div>
                <div class="wallet-label">Account Balance</div>
                <div class="wallet-balance">¥{{ walletInfo.balance?.toFixed(2) || '0.00' }}</div>
              </div>
            </div>
            <el-button v-if="canRecharge" type="primary" size="large" @click="rechargeDialogVisible = true">
              <el-icon><Plus /></el-icon>
              Recharge
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Transaction History</span>
            </div>
          </template>
          
          <el-table :data="transactions" v-loading="loading" style="width: 100%">
            <el-table-column prop="type" label="Type" width="100">
              <template #default="{ row }">
                <el-tag :type="getTypeColor(row.type)">
                  {{ getTypeLabel(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="Amount" width="120">
              <template #default="{ row }">
                <template v-for="cell in [formatTxAmount(row)]" :key="`${row.id ?? ''}-${cell.fixed}`">
                  <span :class="cell.cls">{{ cell.prefix }}¥{{ cell.fixed }}</span>
                </template>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
                  {{ row.status === 'completed' ? 'Success' : 'Processing' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="Time" width="180">
              <template #default="{ row }">
                {{ formatDate(row.create_time) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="rechargeDialogVisible" title="Recharge" width="400px">
      <el-form label-width="80px">
        <el-form-item label="Amount">
          <el-input-number v-model="rechargeAmount" :min="1" :max="10000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Quick">
          <el-button-group>
            <el-button @click="rechargeAmount = 100">100</el-button>
            <el-button @click="rechargeAmount = 200">200</el-button>
            <el-button @click="rechargeAmount = 500">500</el-button>
            <el-button @click="rechargeAmount = 1000">1000</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rechargeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleRecharge">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.wallet-card {
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  border: none;
}
.wallet-card :deep(.el-card__body) { padding: 30px; }
.wallet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
}
.wallet-info {
  display: flex;
  align-items: center;
  gap: 16px;
}
.wallet-icon { font-size: 48px; }
.wallet-label { font-size: 14px; opacity: 0.9; }
.wallet-balance { font-size: 32px; font-weight: 600; }
.card-header { font-weight: 600; }
.amount-positive { color: #67c23a; font-weight: 600; }
.amount-negative { color: #f56c6c; font-weight: 600; }
</style>
