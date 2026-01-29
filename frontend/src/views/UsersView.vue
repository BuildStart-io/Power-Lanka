<template>
  <div class="users-view animated-page">
    <div class="page-header">
      <h1>👥 User Management</h1>
      <button class="btn btn-primary add-user-btn" @click="openAddModal">
        Add New User
      </button>
    </div>

    <div v-if="loading" class="loading">Loading staff members...</div>

    <div v-else-if="users.length === 0" class="empty-state">
      <div class="empty-icon">👥</div>
      <p>No admins found. Add the first one!</p>
    </div>

    <div v-else class="users-list">
      <div 
        v-for="user in users" 
        :key="user.id" 
        class="user-card"
      >
        <div class="user-header">
          <div class="user-info">
            <div class="user-avatar">👤</div>
            <div>
            <h3>{{ user.full_name || 'Admin User' }}</h3>
              <p class="user-email">
                {{ user.email }}
                <span :class="['role-badge', (user.role || 'admin').toLowerCase()]">
                  {{ (user.role || 'admin').charAt(0).toUpperCase() + (user.role || 'admin').slice(1) }}
                </span>
              </p>
            </div>
          </div>
          <div class="user-date">Joined: {{ formatDate(user.created_at) }}</div>
        </div>
        
        <div class="user-actions">
          <button class="btn btn-sm btn-secondary" @click="openEditModal(user)">
             Edit
          </button>
          <button class="btn btn-sm btn-danger" @click="confirmDelete(user)">
             Remove Access
          </button>
        </div>
      </div>
    </div>

    <!-- Add User Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>Add New Team Member</h2>
        <form @submit.prevent="saveUser">
          <div class="form-group">
            <label>Full Name</label>
            <input 
              v-model="form.full_name" 
              type="text" 
              required 
              placeholder="e.g., John Doe"
            />
          </div>
          <div class="form-group">
            <label>Email Address</label>
            <input 
              v-model="form.email" 
              type="email" 
              required 
              placeholder="e.g., john@power.lk"
            />
          </div>
          <div class="form-group">
            <label>Role</label>
            <select v-model="form.role" required>
              <option value="staff">Staff (Limited Access)</option>
              <option value="admin">Admin (Full Access)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Password</label>
            <input 
              v-model="form.password" 
              type="password" 
              required 
              placeholder="Set a secure password"
            />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Creating...' : 'Create Account' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    <!-- Edit User Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <h2>Manage User: {{ editingUser?.full_name }}</h2>
        <form @submit.prevent="updateUser">
          
          <div class="form-group">
            <label>Role</label>
            <select v-model="editForm.role" required>
              <option value="staff">Staff (Limited Access)</option>
              <option value="admin">Admin (Full Access)</option>
            </select>
          </div>

          <div class="form-group">
            <label>Reset Password</label>
            <input 
              v-model="editForm.password" 
              type="password" 
              placeholder="Leave empty to keep current"
            />
            <small style="color: hsl(var(--muted-foreground)); display: block; margin-top: 0.25rem;">
              Only enter a value if you want to change the password.
            </small>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeEditModal">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Updating...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import { API_BASE } from '../config'

export default {
  name: 'UsersView',
  data() {
    return {
      users: [],
      loading: true,
      saving: false,
      showModal: false,
      showEditModal: false,
      editingUser: null,
      form: {
        full_name: '',
        email: '',
        password: '',
        role: 'staff'
      },
      editForm: {
        role: 'staff',
        password: ''
      }
    }
  },
  async mounted() {
    await this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        const res = await fetch(`${API_BASE}/admin/users`)
        if (res.ok) {
          this.users = await res.json()
        }
      } catch (err) {
        console.error('Failed to load users:', err)
      } finally {
        this.loading = false
      }
    },
    openAddModal() {
      this.form = {
        full_name: '',
        email: '',
        password: '',
        role: 'staff'
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    openEditModal(user) {
      this.editingUser = user
      this.editForm = {
        role: user.role || 'admin', // Default fallbacks
        password: ''
      }
      this.showEditModal = true
    },
    closeEditModal() {
      this.showEditModal = false
      this.editingUser = null
    },
    async saveUser() {
      this.saving = true
      try {
        const res = await fetch(`${API_BASE}/admin/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        })
        
        if (res.ok) {
          await this.loadUsers()
          this.closeModal()
        } else {
          const err = await res.json()
          alert(err.detail || 'Failed to create user')
        }
      } catch (err) {
        console.error('Error saving user:', err)
        alert('Check backend connection')
      } finally {
        this.saving = false
      }
    },
    async updateUser() {
      if (!this.editingUser) return
      this.saving = true
      
      try {
        // 1. Update Role (always sent)
        const roleRes = await fetch(`${API_BASE}/admin/users/${this.editingUser.id}/role`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ role: this.editForm.role })
        })

        if (!roleRes.ok) throw new Error('Failed to update role')

        // 2. Update Password (only if provided)
        if (this.editForm.password) {
          const passRes = await fetch(`${API_BASE}/admin/users/${this.editingUser.id}/password`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: this.editForm.password })
          })
          if (!passRes.ok) throw new Error('Failed to update password')
        }

        await this.loadUsers()
        this.closeEditModal()
        alert('User updated successfully')
        
      } catch (err) {
        console.error('Update failed:', err)
        alert('Failed to update user. See console for details.')
      } finally {
        this.saving = false
      }
    },
    async confirmDelete(user) {
      if (this.users.length <= 1) {
        alert("Cannot delete the last admin account.")
        return
      }
      if (!confirm(`Are you sure you want to revoke access for ${user.email}? This action cannot be undone.`)) return
      
      try {
        const res = await fetch(`${API_BASE}/admin/users/${user.id}`, {
          method: 'DELETE'
        })
        if (res.ok) {
          await this.loadUsers()
        } else {
          alert('Failed to delete user.')
        }
      } catch (err) {
        console.error('Delete failed:', err)
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.user-card {
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border) / 0.4);
  border-radius: 1rem;
  padding: 1.25rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.user-card:hover {
  border-color: hsl(var(--primary) / 0.5);
  box-shadow: 0 4px 20px -10px hsl(var(--primary) / 0.2);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex: 1;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 44px;
  height: 44px;
  background: hsl(var(--primary) / 0.1);
  color: hsl(var(--primary));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.user-info h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.user-email {
  margin: 0;
  font-size: 0.875rem;
  color: hsl(var(--muted-foreground));
}

.user-date {
  font-size: 0.875rem;
  color: hsl(var(--muted-foreground));
}

.user-actions {
  margin-left: 2rem;
  display: flex;
  gap: 0.5rem;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: hsl(var(--card));
  padding: 2rem;
  border-radius: 1.5rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
  border: 1px solid hsl(var(--border));
}

.modal h2 { margin-top: 0; margin-bottom: 1.5rem; }

.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-size: 0.875rem; font-weight: 500; }
.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid hsl(var(--border));
  border-radius: 0.75rem;
  background: hsl(var(--background));
  color: hsl(var(--foreground));
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid hsl(var(--border));
  border-radius: 0.75rem;
  background: hsl(var(--background));
  color: hsl(var(--foreground));
  cursor: pointer;
}

.role-badge {
  display: inline-block;
  font-size: 0.7em;
  padding: 0.2em 0.6em;
  border-radius: 1em;
  text-transform: uppercase;
  font-weight: 700;
  margin-left: 0.5rem;
  letter-spacing: 0.05em;
}

.role-badge.admin {
  background: hsl(var(--primary) / 0.2);
  color: hsl(var(--primary));
  border: 1px solid hsl(var(--primary) / 0.3);
}

.role-badge.staff {
  background: hsl(var(--muted) / 0.3);
  color: hsl(var(--muted-foreground));
  border: 1px solid hsl(var(--border));
}

.loading, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; }

/* Responsive Adjustments */
@media (max-width: 640px) {
  .user-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.25rem;
  }
  
  .user-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .user-actions {
    width: 100%;
    margin-left: 0;
    flex-direction: column;
  }
  
  .user-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
