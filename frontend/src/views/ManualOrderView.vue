<template>
  <div class="manual-order-view animated-page">
    <div class="page-header">
      <h1> Create Manual Order</h1>
      <router-link to="/orders" class="btn btn-secondary back-link">← Back to Orders</router-link>
    </div>

    <div class="order-form">
      <!-- Customer Info Section -->
      <div class="form-section">
        <h3>Customer Information</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Phone Number *</label>
            <input v-model="customer.phone" type="text" required placeholder="e.g., 0771234567" />
          </div>
          <div class="form-group">
            <label>Customer Name *</label>
            <input v-model="customer.name" type="text" required placeholder="Full name" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Gender</label>
            <select v-model="customer.gender">
              <option value="">Not specified</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
          <div class="form-group">
            <label>City</label>
            <input v-model="customer.city" type="text" placeholder="City" />
          </div>
        </div>
        <div class="form-group">
          <label>Delivery Address *</label>
          <textarea v-model="customer.address" required placeholder="Full delivery address"></textarea>
        </div>
      </div>

      <!-- Order Items Section -->
      <div class="form-section">
        <h3>Order Items</h3>
        
        <!-- Add Item Form -->
        <div class="add-item-form">
          <div class="form-row">
            <div class="form-group">
              <label>Category</label>
              <select v-model="newItem.categoryId" @change="loadCategoryProducts">
                <option value="">Select category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Product</label>
              <select v-model="newItem.productId" @change="selectProduct">
                <option value="">Select product</option>
                <option v-for="prod in categoryProducts" :key="prod.id" :value="prod.id">
                  {{ prod.name }} - Rs. {{ formatNumber(prod.price) }}
                </option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Phone Model</label>
              <select v-model="newItem.phoneModelId">
                <option value="">Select phone model</option>
                <option v-for="stock in productStock" :key="stock.phone_model_id" :value="stock.phone_model_id">
                  {{ stock.brand }} {{ stock.phone_model }} ({{ stock.stock_quantity }} in stock)
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Quantity</label>
              <input v-model.number="newItem.quantity" type="number" min="1" value="1" />
            </div>
            <button type="button" class="btn btn-primary add-btn" @click="addItem" :disabled="!canAddItem">
               Add Item
            </button>
          </div>
        </div>

        <!-- Items List -->
        <div v-if="orderItems.length > 0" class="items-list">
          <div class="item-row" v-for="(item, index) in orderItems" :key="index">
            <div class="item-info">
              <strong>{{ item.productName }}</strong>
              <span class="phone-model">{{ item.phoneModelName }}</span>
            </div>
            <div class="item-qty">× {{ item.quantity }}</div>
            <div class="item-price">Rs. {{ formatNumber(item.price * item.quantity) }}</div>
            <button class="btn btn-sm btn-danger" @click="removeItem(index)">🗑️</button>
          </div>
          <div class="items-total">
            <strong>Total: Rs. {{ formatNumber(totalAmount) }}</strong>
          </div>
        </div>
        <div v-else class="empty-items">
          No items added yet. Use the form above to add products.
        </div>
      </div>

      <!-- Payment Section -->
      <div class="form-section">
        <h3>Payment & Notes</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Payment Method *</label>
            <select v-model="paymentMethod" required>
              <option value="cod"> Cash on Delivery</option>
              <option value="bank"> Bank Transfer</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Special Notes</label>
          <textarea v-model="specialNote" placeholder="Any special instructions..."></textarea>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="form-actions">
        <button 
          type="button" 
          class="btn btn-primary btn-lg" 
          @click="submitOrder"
          :disabled="!canSubmit || submitting"
        >
          {{ submitting ? ' Creating Order...' : ' Create Order' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'

export default {
  name: 'ManualOrderView',
  data() {
    return {
      customer: {
        phone: '',
        name: '',
        gender: '',
        address: '',
        city: ''
      },
      categories: [],
      categoryProducts: [],
      productStock: [],
      selectedProduct: null,
      newItem: {
        categoryId: '',
        productId: '',
        phoneModelId: '',
        quantity: 1
      },
      orderItems: [],
      paymentMethod: 'cod',
      specialNote: '',
      submitting: false
    }
  },
  computed: {
    canAddItem() {
      return this.newItem.productId && this.newItem.phoneModelId && this.newItem.quantity > 0
    },
    totalAmount() {
      return this.orderItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    },
    canSubmit() {
      return this.customer.phone && 
             this.customer.name && 
             this.customer.address && 
             this.orderItems.length > 0
    }
  },
  async mounted() {
    await this.loadCategories()
  },
  methods: {
    async loadCategories() {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/categories`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.categories = data.categories.filter(c => c.is_active)
        }
      } catch (err) {
        console.error('Failed to load categories:', err)
      }
    },
    async loadCategoryProducts() {
      if (!this.newItem.categoryId) {
        this.categoryProducts = []
        return
      }
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/products?category_id=${this.newItem.categoryId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.categoryProducts = data.products.filter(p => p.is_active)
        }
      } catch (err) {
        console.error('Failed to load products:', err)
      }
      this.newItem.productId = ''
      this.productStock = []
    },
    async selectProduct() {
      if (!this.newItem.productId) {
        this.productStock = []
        this.selectedProduct = null
        return
      }
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/products/${this.newItem.productId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const product = await res.json()
          this.selectedProduct = product
          this.productStock = product.phone_stock.filter(s => s.stock_quantity > 0)
        }
      } catch (err) {
        console.error('Failed to load product:', err)
      }
      this.newItem.phoneModelId = ''
    },
    addItem() {
      if (!this.canAddItem) return
      
      const stock = this.productStock.find(s => s.phone_model_id === this.newItem.phoneModelId)
      
      this.orderItems.push({
        productId: this.selectedProduct.id,
        productName: this.selectedProduct.name,
        phoneModelId: this.newItem.phoneModelId,
        phoneModelName: `${stock.brand} ${stock.phone_model}`,
        quantity: this.newItem.quantity,
        price: this.selectedProduct.price
      })
      
      // Reset form
      this.newItem = { categoryId: '', productId: '', phoneModelId: '', quantity: 1 }
      this.categoryProducts = []
      this.productStock = []
      this.selectedProduct = null
    },
    removeItem(index) {
      this.orderItems.splice(index, 1)
    },
    async submitOrder() {
      if (!this.canSubmit) return
      
      this.submitting = true
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/orders/manual`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            phone: this.customer.phone,
            customer_name: this.customer.name,
            delivery_address: this.customer.address,
            delivery_city: this.customer.city,
            gender: this.customer.gender || null,
            items: this.orderItems.map(item => ({
              product_id: item.productId,
              phone_model_id: item.phoneModelId,
              quantity: item.quantity
            })),
            payment_method: this.paymentMethod,
            special_note: this.specialNote || null
          })
        })
        
        if (res.ok) {
          const data = await res.json()
          alert(`✅ Order #${data.order.id} created successfully!`)
          this.$router.push('/orders')
        } else {
          const error = await res.json()
          alert(`❌ Failed to create order: ${error.detail || 'Unknown error'}`)
        }
      } catch (err) {
        console.error('Failed to create order:', err)
        alert('❌ Error creating order')
      } finally {
        this.submitting = false
      }
    },
    formatNumber(num) {
      return num ? num.toLocaleString() : '0'
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.order-form {
  max-width: 800px;
}

.form-section {
  background: hsl(var(--card));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid hsl(var(--border) / 0.4);
  border-radius: 1.25rem;
  padding: 1.75rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 25px -10px rgb(0 0 0 / 0.05);
}

.form-section h3 {
  margin: 0 0 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid hsl(var(--border) / 0.4);
  color: hsl(var(--foreground));
  font-weight: 700;
  font-size: 1.25rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid rgba(168, 85, 247, 0.5);
  border-radius: 8px;
  background: transparent;
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
}

.form-group select {
  background-color: transparent;
  color: var(--text-primary);
}

.form-group select option {
  background-color: var(--bg-card);
  color: var(--text-primary);
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.add-item-form {
  background: rgba(99, 102, 241, 0.05);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.add-btn {
  align-self: flex-end;
  white-space: nowrap;
}

.items-list {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.item-row:last-of-type {
  border-bottom: none;
}

.item-info {
  flex: 1;
}

.item-info strong {
  display: block;
}

.phone-model {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.item-qty {
  color: var(--text-secondary);
}

.item-price {
  font-weight: 600;
  color: #10b981;
  min-width: 100px;
  text-align: right;
}

.items-total {
  padding: 1.25rem;
  background: hsl(var(--primary) / 0.1);
  text-align: right;
  font-size: 1.25rem;
  border-top: 1px solid hsl(var(--primary) / 0.2);
}

.empty-items {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  background: rgba(0,0,0,0.02);
  border-radius: 8px;
}

.form-actions {
  margin-top: 1rem;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.125rem;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.back-link {
  text-decoration: none !important;
}

.page-header .btn,
.page-header a,
.page-header router-link {
  text-decoration: none !important;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1.25rem;
  }

  .back-link {
    width: 100%;
    text-align: center;
    padding: 0.75rem;
  }

  .order-form {
    max-width: 100%;
  }

  .form-section {
    padding: 1.25rem;
    border-radius: 1rem;
    margin-bottom: 1.5rem;
  }

  .form-row {
    flex-direction: column;
    gap: 1rem;
  }

  .add-item-form {
    padding: 1rem;
  }

  .add-btn {
    width: 100%;
    margin-top: 0.5rem;
    padding: 0.875rem;
  }

  .item-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem;
  }

  .item-price {
    text-align: left;
    min-width: auto;
  }

  .form-actions .btn-lg {
    width: 100%;
    padding: 1rem;
    font-size: 1.1rem;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.25rem;
  }

  .form-section h3 {
    font-size: 1rem;
  }
}

.animated-page {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
