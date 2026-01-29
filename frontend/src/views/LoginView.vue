<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">Power Lanka - <br> Admin Portal</h1>
      
      <div v-if="error" class="error">{{ error }}</div>
      
      <form @submit.prevent="login">
        <div class="form-group">
          <label class="form-label">Username</label>
          <input 
            v-model="email" 
            type="email" 
            class="form-input login-input" 
            placeholder="admin@store.lk"
            required
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">Password</label>
          <input 
            v-model="password" 
            type="password" 
            class="form-input login-input" 
            placeholder="Enter password"
            required
          />
        </div>
        
        <button type="submit" class="btn btn-primary login-btn" style="width: 100%;" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
    <div class="login-footer">
      <div class="powered-by">
        <img src="/photo.png" alt="BuildStart" />
        <div class="powered-by-text">
          <span class="powered-by-label">Powered by</span>
          <span class="powered-by-name">BuildStart</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'
import { useTheme } from '../composables/useTheme'

export default {
  name: 'LoginView',
  data() {
    return {
      email: '',
      password: '',
      error: null,
      loading: false
    }
  },
  created() {
    const { initTheme } = useTheme()
    initTheme()
  },
  methods: {
    async login() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch(`${API_BASE}/admin/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        })
        
          if (response.ok) {
            const data = await response.json()
            localStorage.setItem('admin_token', data.token)
            localStorage.setItem('admin_user', JSON.stringify(data.user))
            
            if (data.user.role === 'staff') {
              this.$router.push('/orders')
            } else {
              this.$router.push('/')
            }
          } else {
          const err = await response.json()
          this.error = err.detail || 'Login failed'
        }
      } catch (err) {
        this.error = 'Network error - check API server'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
}

.login-footer {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 10;
}

.powered-by {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.3rem;
}

.powered-by img {
  height: 40px;
  width: auto;
}

.powered-by-text {
  color: hsl(var(--muted-foreground));
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.2;
}

.powered-by-label {
  font-size: 0.6rem;
}

.powered-by-name {
  font-size: 1.55rem;
  font-weight: 500;
}

.login-input {
  border: 2px solid hsl(var(--border));
  background: hsl(var(--input));
  transition: all 0.3s ease;
}

.login-input:focus {
  outline: none;
  border-color: hsl(var(--ring));
  box-shadow: 0 0 0 3px hsl(var(--ring) / 0.2);
}

.login-card .btn-primary,
.login-btn {
  font-size: 1rem;
  font-weight: 600;
  padding: 0.875rem 1.5rem;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  animation: fadeIn 0.5s ease-in;
}

.login-card {
  animation: slideUp 0.6s ease-out;
  border: 2px solid hsl(var(--primary)) !important;
}

.login-title {
  animation: fadeInDown 0.7s ease-out;
}

.form-group {
  animation: fadeIn 0.8s ease-out;
  animation-fill-mode: both;
}

.form-group:nth-child(1) {
  animation-delay: 0.1s;
}

.form-group:nth-child(2) {
  animation-delay: 0.2s;
}

.login-btn {
  animation: fadeInUp 0.9s ease-out;
}

.login-footer {
  animation: fadeIn 1s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.25rem;
  }

  .form-group {
    margin-bottom: 1.25rem;
  }

  .login-footer {
    bottom: 1rem;
    right: 1rem;
  }

  .powered-by img {
    height: 32px;
  }

  .powered-by-label {
    font-size: 0.5rem;
  }

  .powered-by-name {
    font-size: 1.25rem;
  }
}
</style>