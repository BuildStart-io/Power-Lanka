<template>
  <div id="app">
    <template v-if="isLoggedIn && $route.path !== '/login'">
      <aside class="sidebar" :class="{ open: showMobileMenu }">
        <div class="sidebar-header">
          <div class="logo">
            <span class="logo-power">Power</span><span class="logo-lanka">Lanka</span>
          </div>
          <button class="mobile-menu-close" @click="toggleMobileMenu">✕</button>
        </div>
        <nav>
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }" @click="closeMobileMenuOnClick" v-if="userRole === 'admin'">
            <LayoutDashboard :size="20" />
            <span>Dashboard</span>
          </router-link>
          <router-link to="/orders" class="nav-link" :class="{ active: $route.path === '/orders' }" @click="closeMobileMenuOnClick">
            <ShoppingBag :size="20" />
            <span>Orders</span>
          </router-link>
          <router-link to="/products" class="nav-link" :class="{ active: $route.path === '/products' }" @click="closeMobileMenuOnClick" v-if="userRole === 'admin'">
            <Package :size="20" />
            <span>Products</span>
          </router-link>
          <router-link to="/whatsapp" class="nav-link" :class="{ active: $route.path === '/whatsapp' }" @click="closeMobileMenuOnClick" v-if="userRole === 'admin'">
            <MessageCircle :size="20" />
            <span>WhatsApp</span>
          </router-link>
          <router-link to="/customers" class="nav-link" :class="{ active: $route.path === '/customers' }" @click="closeMobileMenuOnClick" v-if="userRole === 'admin'">
            <Users :size="20" />
            <span>Customers</span>
          </router-link>
          <router-link to="/admins" class="nav-link" :class="{ active: $route.path === '/admins' }" @click="closeMobileMenuOnClick" v-if="userRole === 'admin'">
            <UserCog :size="20" />
            <span>Admins</span>
          </router-link>
        </nav>
        <div style="position: absolute; bottom: 1.5rem; left: 1.5rem; right: 1.5rem;">
          <div style="display: flex; align-items: center; justify-content: center; gap: 0.3rem;">
            <img src="/photo.png" alt="BuildStart" style="height: 40px; width: auto;" />
            <div style="color: var(--text-secondary); text-align: center; display: flex; flex-direction: column; align-items: center; line-height: 1.2;">
              <span style="font-size: 0.6rem;">Powered by</span>
              <span style="font-size: 1.55rem; font-weight: 500;">BuildStart</span>
            </div>
          </div>
        </div>
      </aside>
      <button v-if="!showMobileMenu" class="mobile-menu-toggle" @click="toggleMobileMenu">☰</button>
      <div v-if="showMobileMenu" class="mobile-overlay" @click="toggleMobileMenu"></div>
      <main class="main-content">
        <div class="top-header">
          <ThemeToggle />
          <div class="profile-menu">
            <button @click="toggleProfileMenu" class="profile-button glass">
              <User :size="20" />
              <span class="profile-name">{{ adminName }}</span>
              <span class="dropdown-arrow">▼</span>
            </button>
            <div v-if="showProfileMenu" class="profile-dropdown glass-card">
              <button @click="logout" class="profile-dropdown-item logout-item">
                 <LogOut :size="16" class="mr-2" /> Logout
              </button>
            </div>
          </div>
        </div>
        <router-view />
      </main>
    </template>
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script>
import ThemeToggle from './components/ThemeToggle.vue'
import { useTheme } from './composables/useTheme'
import { 
  LayoutDashboard, 
  ShoppingBag, 
  Package, 
  MessageCircle, 
  Users, 
  UserCog, 
  LogOut, 
  User, 
  Menu, 
  X 
} from 'lucide-vue-next'

export default {
  components: {
    ThemeToggle,
    LayoutDashboard,
    ShoppingBag,
    Package,
    MessageCircle,
    Users,
    UserCog,
    LogOut,
    User,
    Menu,
    X
  },
  name: 'App',
  data() {
    return {
      showProfileMenu: false,
      showMobileMenu: false,
      loginState: !!localStorage.getItem('admin_token')
    }
  },
  computed: {
    isLoggedIn() {
      return this.loginState
    },
    adminName() {
      const user = localStorage.getItem('admin_user')
      return user ? JSON.parse(user).name : 'Admin'
    },
    userRole() {
       const user = localStorage.getItem('admin_user')
       return user ? (JSON.parse(user).role || 'admin') : 'admin'
    }
  },
  watch: {
    // Watch route changes to re-check login state
    '$route'(to, from) {
      this.checkLoginState()
    }
  },
  methods: {
    checkLoginState() {
      this.loginState = !!localStorage.getItem('admin_token')
    },
    logout() {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      this.loginState = false
      this.$router.push('/login')
    },
    toggleProfileMenu() {
      this.showProfileMenu = !this.showProfileMenu
    },
    toggleMobileMenu() {
      this.showMobileMenu = !this.showMobileMenu
    },
    closeMobileMenuOnClick() {
      if (window.innerWidth <= 768) {
        this.showMobileMenu = false
      }
    }
  },
  created() {
    // Check login state on component creation
    this.checkLoginState()
  },
  mounted() {
    // Check login state on mount
    this.checkLoginState()
    // Close profile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.profile-menu')) {
        this.showProfileMenu = false
      }
    })
  }
}
</script>

<style scoped>
.top-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
  margin-bottom: 3.5rem;
  position: relative;
  z-index: 50;
}

.profile-menu {
  position: relative;
}

.profile-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: transparent;
  border: none;
  border-radius: calc(var(--radius) * 0.5);
  color: hsl(var(--foreground));
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9375rem;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  font-weight: 600;
}

.profile-button:hover {
  background: hsl(var(--muted) / 0.1);
  color: hsl(var(--primary));
}

.profile-icon {
  font-size: 1.5rem;
}

.profile-name {
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 0.75rem;
  transition: transform 0.2s;
}

.profile-menu:hover .dropdown-arrow {
  transform: rotate(180deg);
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  border-radius: calc(var(--radius) * 0.5);
  min-width: 200px;
  box-shadow: 0 20px 25px -5px hsl(var(--primary) / 0.1), 0 10px 10px -5px hsl(var(--primary) / 0.04);
  z-index: 1000;
  overflow: hidden;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.profile-dropdown-item {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  text-align: left;
  background: transparent;
  border: none;
  color: hsl(var(--foreground));
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
}

.profile-dropdown-item:hover {
  background: hsl(var(--accent));
}

.profile-info {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.logout-item {
  color: hsl(var(--destructive));
}

.logout-item:hover {
  background: hsl(var(--destructive) / 0.1);
  color: hsl(var(--destructive));
}

.mobile-menu-toggle {
  display: none;
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 1001;
  background: linear-gradient(135deg, hsl(var(--gradient-start)), hsl(var(--gradient-end)));
  color: hsl(var(--primary-foreground));
  border: none;
  border-radius: calc(var(--radius) * 0.5);
  padding: 0.75rem;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 4px 12px hsl(var(--primary) / 0.3);
  transition: all 0.3s ease;
}

.mobile-menu-toggle:hover {
  box-shadow: 0 6px 16px hsl(var(--primary) / 0.4);
  transform: translateY(-1px);
}

.mobile-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 999;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mobile-menu-close {
  display: none;
  background: transparent;
  border: none;
  color: hsl(var(--foreground));
  font-size: 1.5rem;
  padding: 0.5rem;
  cursor: pointer;
  opacity: 0.7;
}

.mobile-menu-close:hover {
  opacity: 1;
}

.logo-power {
  color: #ef4444; /* Red for Power */
}

.logo-lanka {
  color: #16a34a; /* Green for Lanka */
}

@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
  }

  .mobile-menu-close {
    display: block;
  }

  .mobile-overlay {
    display: block;
  }

  .main-content {
    padding: 1rem;
    padding-top: 5rem;
  }

  .sidebar .logo {
    margin: 0;
  }

  .sidebar-header {
    margin-bottom: 2rem;
  }

  .top-header {
    margin-bottom: 1.5rem;
    gap: 0.75rem;
  }

  .profile-button {
    padding: 0.5rem 0.75rem;
    font-size: 0.8125rem;
  }

  .profile-name {
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

@media (max-width: 480px) {
  .mobile-menu-toggle {
    top: 0.5rem;
    left: 0.5rem;
    padding: 0.5rem;
    font-size: 1.25rem;
  }

  .main-content {
    padding-top: 4rem;
  }

  .sidebar .logo {
    margin-top: 3rem;
  }

  .top-header {
    margin-bottom: 0.75rem;
  }
}

/* Add styles for nav icons */
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logout-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
