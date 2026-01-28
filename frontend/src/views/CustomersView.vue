<template>
  <div class="customers-view animated-page">
    <div class="page-header">
      <h1>👥 Customers (WhatsApp)</h1>
    </div>

    <div v-if="loading" class="loading">Loading customers...</div>

    <div v-else-if="customers.length === 0" class="empty-state">
      <div class="empty-icon">🌱</div>
      <p>No WhatsApp conversations yet.</p>
    </div>

    <div v-else class="customers-table-wrapper">
      <table class="customers-table">
        <thead>
          <tr>
            <th>Phone</th>
            <th>Messages</th>
            <th>Last Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in customers" :key="customer.phone">
            <td class="phone">{{ customer.phone }}</td>
            <td>{{ customer.message_count }}</td>
            <td>{{ formatDate(customer.last_active) }}</td>
            <td>
              <router-link :to="`/chat/${customer.phone}`" class="btn btn-sm btn-secondary">
                💬 Chat History
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
        // No token needed for this demo/local version unless we added auth
        const res = await fetch(`${API_BASE}/admin/customers`)
        if (res.ok) {
          const data = await res.json()
          this.customers = data
        } else {
             console.error("Failed to fetch customers")
        }
      } catch (err) {
        console.error('Failed to load customers:', err)
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style scoped>
.customers-view {
  width: 100%;
  padding-bottom: 2rem;
}

.page-header h1 {
  margin-bottom: 2rem;
  color: hsl(var(--foreground));
  font-weight: 800;
  font-size: 1.75rem;
}

.customers-table-wrapper {
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border) / 0.4);
  border-radius: 1.25rem;
  overflow: hidden;
}

.customers-table {
  width: 100%;
  border-collapse: collapse;
}

.customers-table th {
  padding: 1rem;
  text-align: left;
  background: hsl(var(--muted) / 0.1);
  font-weight: 700;
  color: hsl(var(--primary));
  font-size: 0.85rem;
}

.customers-table td {
  padding: 1rem;
  border-bottom: 1px solid hsl(var(--border) / 0.4);
  color: hsl(var(--foreground));
}

.phone {
  font-weight: 700;
  color: hsl(var(--primary));
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

.empty-state {
  text-align: center;
  padding: 4rem;
  background: hsl(var(--muted)/0.05);
  border-radius: 1rem;
}
.empty-icon { font-size: 3rem; }
</style>
