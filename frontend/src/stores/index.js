import { useUserStore } from './user'
import { useNotificationStore } from './modules/notification'
import { useWalletStore } from './modules/wallet'

// Re-export all Pinia stores for convenient imports
export {
  useUserStore,
  useNotificationStore,
  useWalletStore
}
