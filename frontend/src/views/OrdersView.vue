<template>
  <div class="orders-view animated-page">
    <div class="page-header">
      <h1>Orders</h1>
      <div class="header-right">
        <button @click="showExportPanel = !showExportPanel" class="btn btn-secondary export-toggle-btn">
          Export CSV
        </button>
        <router-link to="/orders/new" class="btn btn-primary new-order-btn">New Order</router-link>
      </div>
    </div>

    <!-- Export Panel -->
    <div v-if="showExportPanel" class="export-panel">
      <h3>Export Orders to CSV</h3>
      <div class="export-filters">
        <div class="filter-group">
          <label>Start Date:</label>
          <input type="date" v-model="exportFilters.startDate" class="date-input">
        </div>
        <div class="filter-group">
          <label>End Date:</label>
          <input type="date" v-model="exportFilters.endDate" class="date-input">
        </div>
        <div class="filter-group">
          <label>Status:</label>
          <select v-model="exportFilters.status" class="status-select">
            <option value="">All Statuses</option>
            <option value="confirmed">Confirmed</option>
            <option value="processing">Processing</option>
            <option value="shipped">Shipped</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div class="filter-group">
          <button @click="downloadCSV" class="btn btn-primary download-btn" :disabled="downloading">
            {{ downloading ? 'Downloading...' : 'Download CSV' }}
          </button>
        </div>
      </div>
    </div>

    <div class="filter-tabs-container">
      <div class="filter-tabs">
        <button 
          v-for="tab in statusTabs" 
          :key="tab.value"
          class="filter-tab"
          :class="{ active: statusFilter === tab.value }"
          @click="statusFilter = tab.value; loadOrders()"
        >
          {{ tab.icon }} {{ tab.label }}
          <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading orders...</div>

    <div v-else-if="orders.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <p>No orders found</p>
    </div>

    <div v-else class="orders-list">
      <div 
        v-for="order in orders" 
        :key="order.id" 
        class="order-card"
        :class="{ expanded: expandedOrder === order.id }"
      >
        <div class="order-header" @click="toggleOrder(order.id)">
          <div class="order-info">
            <span class="order-id">#{{ order.id }}</span>
            <span class="order-phone">{{ order.phone }}</span>
            <span class="order-name" v-if="order.customer_name">{{ order.customer_name }}</span>
          </div>
          <div class="order-meta">
            <span class="order-amount">Rs. {{ formatNumber(order.total_amount) }}</span>
            <span class="order-items">{{ order.item_count }} items</span>
            <span :class="['status-badge', order.status]">{{ order.status }}</span>
          </div>
          <div class="order-date">{{ formatDate(order.created_at) }}</div>
          <span class="expand-icon">{{ expandedOrder === order.id ? '▼' : '▶' }}</span>
        </div>

        <div v-if="expandedOrder === order.id" class="order-details">
          <div class="detail-section" v-if="orderDetails[order.id]">
            <h4>Delivery Details</h4>
            <p v-if="orderDetails[order.id].delivery_address"><strong>Address:</strong> {{ orderDetails[order.id].delivery_address }}</p>
            <p v-if="orderDetails[order.id].delivery_city"><strong>City:</strong> {{ orderDetails[order.id].delivery_city }}</p>
            <p v-if="orderDetails[order.id].payment_method"><strong>Payment:</strong> {{ orderDetails[order.id].payment_method === 'cod' ? 'Cash on Delivery' : 'Bank Transfer' }}</p>
            <p v-if="orderDetails[order.id].special_note"><strong>Note:</strong> {{ orderDetails[order.id].special_note }}</p>
          </div>

          <div class="detail-section" v-if="orderDetails[order.id]">
            <h4>Order Items</h4>
            <ul class="items-list">
              <li v-for="item in orderDetails[order.id].items" :key="item.id">
                {{ item.category_name }} ({{ item.phone_model }}) × {{ item.quantity }}
                <span class="item-price">Rs. {{ formatNumber(item.quantity * item.unit_price) }}</span>
              </li>
            </ul>
            
            <div class="order-total-breakdown">
              <div class="breakdown-row">
                <span>Subtotal:</span>
                <span>Rs. {{ formatNumber(orderDetails[order.id].subtotal || 0) }}</span>
              </div>
              <div class="breakdown-row">
                <span>Delivery Charge:</span>
                <span>Rs. {{ formatNumber(orderDetails[order.id].delivery_charge || 350) }}</span>
              </div>
              <div class="breakdown-row total-row">
                <span><strong>Total:</strong></span>
                <span><strong>Rs. {{ formatNumber(orderDetails[order.id].total_amount) }}</strong></span>
              </div>
            </div>
          </div>

          <div class="order-actions">
            <h4>🔄 Update Status</h4>
            <div class="status-buttons">
              <button 
                v-for="status in availableStatuses" 
                :key="status.value"
                class="btn btn-sm"
                :class="{ 'btn-primary': order.status === status.value, 'btn-secondary': order.status !== status.value }"
                :disabled="order.status === status.value"
                @click="updateStatus(order.id, status.value)"
              >
                {{ status.icon }} {{ status.label }}
              </button>
            </div>
          </div>

          <div class="order-links">
            <router-link :to="`/chat/${order.phone}`" class="btn btn-secondary btn-sm">
              View Chat History
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'

export default {
  name: 'OrdersView',
  data() {
    return {
      orders: [],
      orderDetails: {},
      loading: true,
      statusFilter: '',
      expandedOrder: null,
      showExportPanel: false,
      downloading: false,
      exportFilters: {
        startDate: '',
        endDate: '',
        status: ''
      },
      statusTabs: [
        { value: '', label: 'All', icon: '', count: 0 },
        { value: 'confirmed', label: 'Confirmed', icon: '', count: 0 },
        { value: 'processing', label: 'Processing', icon: '', count: 0 },
        { value: 'shipped', label: 'Shipped', icon: '', count: 0 },
        { value: 'completed', label: 'Completed', icon: '', count: 0 },
        { value: 'cancelled', label: 'Cancelled', icon: '', count: 0 }
      ],
      availableStatuses: [
        { value: 'confirmed', label: 'Confirmed', icon: '' },
        { value: 'processing', label: 'Processing', icon: '' },
        { value: 'shipped', label: 'Shipped', icon: '' },
        { value: 'completed', label: 'Completed', icon: '' },
        { value: 'cancelled', label: 'Cancelled', icon: '' }
      ]
    }
  },
  async mounted() {
    await this.loadOrders()
  },
  methods: {
    async downloadCSV() {
      this.downloading = true
      try {
        const token = localStorage.getItem('admin_token')
        let url = `${API_BASE}/admin/orders/export/csv?`
        
        const params = new URLSearchParams()
        if (this.exportFilters.startDate) {
          params.append('start_date', this.exportFilters.startDate)
        }
        if (this.exportFilters.endDate) {
          params.append('end_date', this.exportFilters.endDate)
        }
        if (this.exportFilters.status) {
          params.append('status', this.exportFilters.status)
        }
        
        url += params.toString()
        
        const res = await fetch(url, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (res.ok) {
          // Get the blob from response
          const blob = await res.blob()
          
          // Create download link
          const downloadUrl = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = downloadUrl
          
          // Get filename from Content-Disposition header or use default
          const contentDisposition = res.headers.get('Content-Disposition')
          let filename = 'orders.csv'
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename=(.+)/)
            if (filenameMatch) {
              filename = filenameMatch[1].replace(/"/g, '')
            }
          }
          
          link.download = filename
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(downloadUrl)
          
          alert('✅ CSV downloaded successfully!')
        } else {
          alert('❌ Failed to download CSV')
        }
      } catch (err) {
        console.error('Failed to download CSV:', err)
        alert('❌ Error downloading CSV')
      } finally {
        this.downloading = false
      }
    },
    async loadOrders() {
      this.loading = true
      try {
        const token = localStorage.getItem('admin_token')
        let url = `${API_BASE}/admin/orders`
        if (this.statusFilter) {
          url += `?status=${this.statusFilter}`
        }
        const res = await fetch(url, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.orders = data.orders
        }
      } catch (err) {
        console.error('Failed to load orders:', err)
      } finally {
        this.loading = false
      }
    },
    async toggleOrder(orderId) {
      if (this.expandedOrder === orderId) {
        this.expandedOrder = null
        return
      }
      
      this.expandedOrder = orderId
      
      // Load order details if not cached
      if (!this.orderDetails[orderId]) {
        try {
          const token = localStorage.getItem('admin_token')
          const res = await fetch(`${API_BASE}/admin/orders/${orderId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          if (res.ok) {
            this.orderDetails[orderId] = await res.json()
          }
        } catch (err) {
          console.error('Failed to load order details:', err)
        }
      }
    },
    async updateStatus(orderId, status) {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/orders/${orderId}/status`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ status })
        })
        if (res.ok) {
          // Update local state
          const order = this.orders.find(o => o.id === orderId)
          if (order) order.status = status
          
          // Refresh if filtering by status
          if (this.statusFilter) {
            await this.loadOrders()
          }
        }
      } catch (err) {
        console.error('Failed to update status:', err)
      }
    },
    formatNumber(num) {
      return num ? num.toLocaleString() : '0'
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  }
}
</script>

<style scoped>
.orders-view {
  width: 100%;
  overflow-x: hidden;
  padding-top: 1rem;
  padding-bottom: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.page-header h1 {
  margin: 0;
  color: hsl(var(--foreground));
  font-weight: 800;
  letter-spacing: -0.04em;
  font-size: 1.75rem;
  animation: slideDownFade 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.export-toggle-btn, .new-order-btn {
  text-decoration: none !important;
  font-weight: 700;
  border-radius: 1rem;
}

/* Export Panel Styles */
.export-panel {
  background: hsl(var(--glass-bg));
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid hsl(var(--glass-border));
  border-radius: 1.5rem;
  padding: 1.75rem;
  margin-bottom: 2.5rem;
  box-shadow: 0 15px 25px -5px rgb(0 0 0 / 0.05);
  animation: slideDownFade 0.5s ease-out;
}

.export-panel h3 {
  margin: 0 0 1.25rem;
  color: hsl(var(--foreground));
  font-size: 1.125rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.export-filters {
  display: flex;
  gap: 1.25rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.75rem;
  font-weight: 700;
  color: hsl(var(--muted-foreground));
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.date-input, .status-select {
  padding: 0.625rem 1rem;
  border: 1px solid hsl(var(--border) / 0.6);
  border-radius: 0.875rem;
  background: hsl(var(--input) / 0.5);
  color: hsl(var(--foreground));
  font-size: 0.875rem;
  min-width: 180px;
  transition: all 0.3s ease;
}

.date-input:focus, .status-select:focus {
  outline: none;
  border-color: hsl(var(--primary));
  box-shadow: 0 0 0 3px hsl(var(--primary) / 0.1);
}

.download-btn {
  border-radius: 0.875rem;
  font-weight: 700;
}

/* Filter Tabs */
.filter-tabs-container {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 2rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  scrollbar-width: none;
}

.filter-tabs-container::-webkit-scrollbar {
  display: none;
}

.filter-tabs {
  display: flex;
  gap: 0.75rem;
  background: hsl(var(--muted) / 0.15);
  padding: 0.5rem;
  border-radius: 1.25rem;
  border: 1px solid hsl(var(--border) / 0.4);
}

.filter-tab {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 0.875rem;
  background: transparent;
  color: hsl(var(--muted-foreground));
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 700;
  font-size: 0.875rem;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-tab:hover {
  color: hsl(var(--foreground));
  background: hsl(var(--muted) / 0.3);
}

.filter-tab.active {
  background: linear-gradient(135deg, hsl(var(--primary) / 0.1), hsl(var(--primary) / 0.05));
  color: hsl(var(--primary));
  border: 1px solid hsl(var(--primary) / 0.3);
  box-shadow: 0 4px 12px hsl(var(--primary) / 0.15);
}

.dark .filter-tab.active {
  background: transparent;
  border: 1.5px solid hsl(var(--primary) / 0.4);
  box-shadow: none;
}

.tab-count {
  background: hsl(var(--primary) / 0.1);
  color: hsl(var(--primary));
  padding: 0.125rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 800;
}

.filter-tab.active .tab-count {
  background: hsl(var(--primary));
  color: white;
}

/* Orders List */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.order-card {
  background: hsl(var(--glass-bg));
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid hsl(var(--glass-border));
  border-radius: 1.5rem;
  overflow: hidden;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.03);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-card:hover {
  border-color: hsl(var(--primary) / 0.3);
  box-shadow: 0 20px 30px -10px rgb(0 0 0 / 0.05);
  transform: translateY(-2px);
}

.order-header {
  padding: 1.25rem 1.75rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  cursor: pointer;
}

.order-info {
  display: flex;
  gap: 1.25rem;
  align-items: center;
  flex: 1;
}

.order-id {
  font-weight: 800;
  color: hsl(var(--primary));
  letter-spacing: -0.02em;
}

.order-phone {
  color: hsl(var(--muted-foreground));
  font-weight: 600;
  font-size: 0.9375rem;
}

.order-name {
  color: hsl(var(--foreground));
  font-weight: 700;
}

.order-meta {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.order-amount {
  font-weight: 800;
  color: hsl(var(--foreground));
  font-size: 1.125rem;
}

.order-items {
  color: hsl(var(--muted-foreground));
  font-size: 0.8125rem;
  font-weight: 500;
}

.status-badge {
  padding: 0.4rem 0.875rem;
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid transparent;
}

.status-badge.confirmed { background: hsl(var(--warning) / 0.08); color: hsl(var(--warning)); border-color: hsl(var(--warning) / 0.15); }
.status-badge.processing { background: hsl(var(--primary) / 0.08); color: hsl(var(--primary)); border-color: hsl(var(--primary) / 0.15); }
.status-badge.shipped { background: hsl(var(--success) / 0.08); color: hsl(var(--success)); border-color: hsl(var(--success) / 0.15); }
.status-badge.completed { background: hsl(var(--success) / 0.12); color: hsl(var(--success)); border-color: hsl(var(--success) / 0.2); }
.status-badge.cancelled { background: hsl(var(--destructive) / 0.08); color: hsl(var(--destructive)); border-color: hsl(var(--destructive) / 0.15); }

.order-date {
  color: hsl(var(--muted-foreground));
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 140px;
}

.order-details {
  padding: 1.75rem;
  border-top: 1px solid hsl(var(--glass-border));
  background: hsl(var(--muted) / 0.1);
  animation: slideDownFade 0.3s ease-out;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  margin-bottom: 1rem;
  color: hsl(var(--foreground));
  font-weight: 800;
  font-size: 1rem;
  letter-spacing: -0.01em;
}

.detail-section p {
  margin: 0.5rem 0;
  color: hsl(var(--muted-foreground));
  font-size: 0.9375rem;
}

.detail-section strong {
  color: hsl(var(--foreground));
  font-weight: 700;
  margin-right: 0.5rem;
}

.items-list {
  list-style: none;
  padding: 0;
  background: white;
  border-radius: 1.25rem;
  border: 1px solid hsl(var(--border) / 0.6);
  overflow: hidden;
}

.items-list li {
  display: flex;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid hsl(var(--border) / 0.4);
}

.items-list li:last-child {
  border-bottom: none;
}

.item-price {
  font-weight: 700;
  color: hsl(var(--foreground));
}

.order-total-breakdown {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: hsl(var(--primary) / 0.03);
  border-radius: 1.25rem;
  border: 1px solid hsl(var(--primary) / 0.1);
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  padding: 0.375rem 0;
  color: hsl(var(--muted-foreground));
  font-weight: 500;
}

.breakdown-row.total-row {
  border-top: 1px solid hsl(var(--primary) / 0.15);
  margin-top: 0.75rem;
  padding-top: 1rem;
  color: hsl(var(--foreground));
  font-size: 1.25rem;
  font-weight: 800;
}

.order-actions {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid hsl(var(--glass-border));
}

.status-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 0.625rem 1.25rem;
  font-size: 0.8125rem;
  font-weight: 700;
  border-radius: 0.875rem;
}

.order-links {
  margin-top: 1.25rem;
  display: flex;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: hsl(var(--glass-bg));
  border-radius: 2rem;
  border: 1px dashed hsl(var(--glass-border));
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

@media (max-width: 1024px) {
  .order-header {
    flex-wrap: wrap;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .page-header h1 { font-size: 1.5rem; }
  
  .export-panel {
    padding: 1.25rem;
  }

  .export-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .date-input, .status-select {
    min-width: 100%;
  }

  .filter-tabs-container { 
    margin: 1rem -1rem 1.5rem; 
    padding: 0 1rem 0.75rem;
  }
  
  .filter-tab {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
  }

  .order-header {
    padding: 1.25rem;
  }

  .order-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    width: 100%;
  }

  .order-meta {
    width: 100%;
    justify-content: space-between;
    padding-top: 0.5rem;
    border-top: 1px solid hsl(var(--border) / 0.3);
  }

  .order-date {
    width: 100%;
    text-align: left;
    margin-top: 0.25rem;
  }

  .order-footer {
    flex-direction: column;
    gap: 1rem;
  }

  .order-total-section {
    width: 100%;
    justify-content: space-between;
  }

  .status-actions {
    width: 100%;
    flex-direction: column;
  }

  .btn-sm {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .order-item {
    gap: 0.75rem;
  }

  .item-img {
    width: 40px;
    height: 40px;
  }

  .item-price {
    font-size: 0.8125rem;
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
