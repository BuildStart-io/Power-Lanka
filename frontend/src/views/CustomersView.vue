<template>
  <div class="customers-view animated-page">
    <div class="page-header">
      <h1>Customers</h1>
    </div>

    <div v-if="loading" class="loading">Loading customers...</div>

    <div v-else-if="customers.length === 0" class="empty-state">
      <div class="empty-icon">Group</div>
      <p>No customers yet</p>
    </div>

    <div v-else class="customers-table-wrapper">
      <table class="customers-table">
        <thead>
          <tr>
            <th>Phone</th>
            <th>Name</th>
            <th>Gender</th>
            <th>Address</th>
            <th>District</th>
            <th>Orders</th>
            <th>Messages</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in customers" :key="customer.id">
            <td class="phone">{{ customer.phone }}</td>
            <td>{{ customer.name || '-' }}</td>
            <td>
              <span v-if="customer.gender === 'male'">Male</span>
              <span v-else-if="customer.gender === 'female'">Female</span>
              <span v-else class="text-muted">-</span>
            </td>
            <td>{{ customer.address || '-' }}</td>
            <td>{{ customer.city || '-' }}</td>
            <td>{{ customer.order_count }}</td>
            <td>{{ customer.message_count }}</td>
            <td>{{ formatDate(customer.created_at) }}</td>
            <td>
              <router-link :to="`/chat/${customer.phone}`" class="btn btn-sm btn-secondary">
                Chat
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'

export default {
  name: 'CustomersView',
  data() {
    return {
      customers: [],
      loading: true
    }
  },
  async mounted() {
    await this.loadCustomers()
  },
  methods: {
    async loadCustomers() {
      this.loading = true
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/customers`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.customers = data.customers
        }
      } catch (err) {
        console.error('Failed to load customers:', err)
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.customers-view {
  width: 100%;
  overflow-x: hidden;
  padding-top: 1rem;
  padding-bottom: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  color: hsl(var(--foreground));
  font-weight: 800;
  letter-spacing: -0.04em;
  font-size: 1.75rem;
  animation: slideDownFade 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.customers-table-wrapper {
  background: hsl(var(--glass-bg));
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid hsl(var(--glass-border));
  border-radius: 1.5rem;
  overflow: hidden;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.03);
  margin-bottom: 2rem;
  animation: slideUpFade 1s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.customers-table {
  width: 100%;
  border-collapse: collapse;
}

.customers-table th {
  padding: 1.25rem 1.5rem;
  text-align: left;
  background: hsl(var(--muted) / 0.15);
  font-weight: 800;
  color: hsl(var(--primary));
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-bottom: 1px solid hsl(var(--border) / 0.4);
}

.customers-table td {
  padding: 1.125rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid hsl(var(--border) / 0.4);
  color: hsl(var(--foreground));
  font-size: 0.9375rem;
  font-weight: 500;
}

.customers-table tr:last-child td {
  border-bottom: none;
}

.customers-table tr:hover {
  background: hsl(var(--primary) / 0.02);
}

.phone {
  font-weight: 700;
  color: hsl(var(--primary));
  letter-spacing: 0.02em;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 700;
  border-radius: 0.75rem;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: hsl(var(--glass-bg));
  border-radius: 2rem;
  border: 1px dashed hsl(var(--glass-border));
  animation: slideUpFade 1s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
  color: hsl(var(--muted-foreground));
}

@media (max-width: 1024px) {
  .customers-table-wrapper {
    overflow-x: auto;
    margin: 0 -1rem 2rem;
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
}

@media (max-width: 768px) {
  .page-header h1 { font-size: 1.5rem; }
  
  .customers-table th, .customers-table td {
    padding: 0.875rem 1rem;
    font-size: 0.8125rem;
  }
  
  .customers-table th:first-child, .customers-table td:first-child {
    padding-left: 1.5rem;
  }
  
  .customers-table th:last-child, .customers-table td:last-child {
    padding-right: 1.5rem;
  }
}

@media (max-width: 480px) {
  .phone {
    font-size: 0.75rem;
  }
}

.animated-page {
  animation: slideUpFade 1s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes slideUpFade {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideDownFade {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
