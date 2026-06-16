import { createRouter, createWebHistory } from 'vue-router'

// Define all application routes with lazy-loaded components and metadata
const routes = [
  {
    path: '/',
    name: 'Portal',
    component: () => import('@/views/Portal.vue'),
    meta: { title: 'CleanPro - Professional Cleaning Services' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'Login' }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Home', requiresAuth: true }
  },
  {
    path: '/cleaner-requirements',
    name: 'CleanerMyRequirements',
    component: () => import('@/views/CleanerMyRequirements.vue'),
    meta: { title: 'Cleaner: Applications & assignments', requiresAuth: true }
  },
  {
    path: '/guest-requirements',
    redirect: '/my-requirements'
  },
  {
    path: '/my-orders',
    name: 'MyOrders',
    component: () => import('@/views/MyOrdersEntry.vue'),
    meta: { title: 'My Orders', requiresAuth: true }
  },
  {
    path: '/my-tasks',
    name: 'MyTasks',
    component: () => import('@/views/MyTasks.vue'),
    meta: { title: 'My Tasks', requiresAuth: true }
  },
  {
    path: '/cleaner-tasks',
    name: 'CleanerTasks',
    component: () => import('@/views/CleanerTasks.vue'),
    meta: { title: 'My Tasks', requiresAuth: true }
  },
  {
    path: '/my-requirements',
    name: 'CustomerMyRequirements',
    component: () => import('@/views/CustomerMyRequirements.vue'),
    meta: { title: 'Customer: My posted requirements', requiresAuth: true }
  },
  {
    path: '/customer-requirements',
    redirect: '/my-requirements'
  },
  {
    path: '/my-bookings',
    name: 'CustomerBookings',
    component: () => import('@/views/CustomerBookings.vue'),
    meta: { title: 'My Bookings', requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'TaskManagement',
    component: () => import('@/views/TaskManagement.vue'),
    meta: { title: 'Task Management', requiresAuth: true }
  },
  {
    path: '/admin-requirements',
    name: 'AdminRequirements',
    component: () => import('@/views/AdminRequirements.vue'),
    meta: { title: 'Requirements Management', requiresAuth: true }
  },
  {
    path: '/admin-cleaning-services',
    name: 'AdminCleaningServices',
    component: () => import('@/views/AdminCleaningServices.vue'),
    meta: { title: 'Cleaning Services', requiresAuth: true }
  },
  {
    path: '/admin-tasks',
    name: 'AdminTasks',
    component: () => import('@/views/AdminTasks.vue'),
    meta: { title: 'Task Management', requiresAuth: true }
  },
  {
    path: '/admin-complaints',
    name: 'AdminComplaints',
    component: () => import('@/views/AdminComplaints.vue'),
    meta: { title: 'Complaints', requiresAuth: true }
  },
  {
    path: '/api-management',
    name: 'ApiManagement',
    component: () => import('@/views/ApiManagement.vue'),
    meta: { title: 'API Management', requiresAuth: true }
  },
  {
    path: '/requirements',
    name: 'RequirementsManagement',
    component: () => import('@/views/RequirementsManagement.vue'),
    meta: { title: 'Requirements', requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/UserManagement.vue'),
    meta: { title: 'User Management', requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/views/MyOrdersEntry.vue'),
    meta: { title: 'Order Management', requiresAuth: true }
  },
  {
    path: '/staff',
    name: 'Staff',
    component: () => import('@/views/Staff.vue'),
    meta: { title: 'Staff Management', requiresAuth: true }
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: () => import('@/views/Inventory.vue'),
    meta: { title: 'Inventory Management', requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports.vue'),
    meta: { title: 'Reports', requiresAuth: true }
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('@/views/Wallet.vue'),
    meta: { title: 'My Wallet', requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/Notifications.vue'),
    meta: { title: 'Notifications', requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: () => import('@/views/UserManagement.vue'),
    meta: { title: 'User Management', requiresAuth: true }
  },
  {
    path: '/roles',
    name: 'RoleManagement',
    component: () => import('@/views/RoleManagement.vue'),
    meta: { title: 'Role Management', requiresAuth: true }
  },
  {
    path: '/menu-management',
    name: 'MenuManagement',
    component: () => import('@/views/MenuManagement.vue'),
    meta: { title: 'Menu Management', requiresAuth: true }
  },
  {
    path: '/permission-management',
    name: 'PermissionManagement',
    component: () => import('@/views/PermissionManagement.vue'),
    meta: { title: 'Permission Management', requiresAuth: true }
  },
  {
    path: '/resources',
    name: 'ResourceManagement',
    component: () => import('@/views/ResourceManagement.vue'),
    meta: { title: 'Resource Management', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: 'Settings', requiresAuth: true }
  },
  {
    path: '/docs',
    name: 'Docs',
    component: () => import('@/views/DocsView.vue'),
    meta: { title: 'API Documentation', requiresAuth: true }
  }
]

// Create the router instance with HTML5 history mode
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard: redirect logged-in users away from /login, and require auth on protected routes
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path === '/login' && token) {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const userRoles = userInfo.roles || [userInfo.role || 'guest']
    const userRole = userRoles[0]
    
    if (userRole === 'admin' || userRole === 'manager') {
      next('/home')
    } else if (['staff', 'cleaner', 'employee'].includes(userRole)) {
      next('/cleaner-tasks')
    } else if (userRole === 'guest') {
      next('/my-requirements')
    } else {
      next('/')
    }
  } else if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
