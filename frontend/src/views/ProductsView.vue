<template>
  <div class="products-view animated-page">
    <div class="page-header">
      <h1>📦 Product Management</h1>
      <button class="btn btn-primary add-product-btn" @click="openAddModal">
        Add New Product
      </button>
    </div>

    <div v-if="loading" class="loading">Loading products...</div>

    <div v-else-if="products.length === 0" class="empty-state">
      <div class="empty-icon">🌱</div>
      <p>No products found. Start adding your Power Lanka products!</p>
    </div>

    <div v-else class="products-list">
      <div 
        v-for="product in products" 
        :key="product.id" 
        class="product-card"
        :class="{ inactive: product.available === 'No' }"
      >
        <div class="product-image-container">
            <img 
              v-if="product.image_paths" 
              :src="`${API_BASE}/media/${product.image_paths.split(',')[0]}`" 
              alt="Product Image"
              class="product-thumb"
            />
            <div v-else class="no-image-placeholder">📦</div>
        </div>
        <div class="product-header">
          <div class="product-info">
            <h3>{{ product.product_name }}</h3>
            <span class="variant-badge" v-if="product.variant">{{ product.variant }}</span>
          </div>
          <div class="product-price">Rs. {{ formatNumber(product.price_lkr) }}</div>
        </div>
        
        <div class="product-status">
          <div class="status-indicator">
            <span :class="['dot', product.available === 'Yes' ? 'online' : 'offline']"></span>
            <span class="status-text">{{ product.available === 'Yes' ? 'In Stock' : 'Out of Stock' }}</span>
          </div>
          <label class="switch">
            <input 
              type="checkbox" 
              :checked="product.available === 'Yes'" 
              @change="toggleAvailability(product)"
            >
            <span class="slider round"></span>
          </label>
        </div>

        <div class="product-actions">
          <button class="btn btn-sm btn-secondary" @click="editProduct(product)">
            ✏️ Edit Details
          </button>
          <button class="btn btn-sm btn-danger" @click="confirmDelete(product)">
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Product Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ editingId ? 'Edit Product' : 'Add New Product' }}</h2>
        <form @submit.prevent="saveProduct">
          <div class="form-group">
            <label>Product Name</label>
            <input 
              v-model="form.product_name" 
              type="text" 
              required 
              placeholder="e.g., Power Fly Killer Spray"
            />
          </div>
          <div class="form-group">
            <label>Variant (e.g., 500ml, 4L)</label>
            <input 
              v-model="form.variant" 
              type="text" 
              placeholder="e.g., 500ml"
            />
          </div>
          <div class="form-group">
            <label>Price (LKR)</label>
            <input 
              v-model.number="form.price_lkr" 
              type="number" 
              required 
              min="0" 
              step="1"
            />
          </div>
          <div class="form-group">
            <label>Initial Availability</label>
            <select v-model="form.available">
              <option value="Yes">In Stock</option>
              <option value="No">Out of Stock</option>
            </select>
          </div>
          <div class="form-group">
            <label>Product Image</label>
            <input 
              type="file" 
              accept="image/*"
              @change="handleFileSelect"
            />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Saving...' : (editingId ? 'Save Changes' : 'Create Product') }}
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
  name: 'ProductsView',
  data() {
    return {
      products: [],
      loading: true,
      saving: false,
      showModal: false,
      editingId: null,
      form: {
        product_name: '',
        variant: '',
        price_lkr: 0,
        available: 'Yes'
      },
      selectedFile: null
    }
  },
  async mounted() {
    await this.loadProducts()
  },
  methods: {
    async loadProducts() {
      this.loading = true
      try {
        console.log(`Fetching from: ${API_BASE}/admin/products/`) // Debug log
        const res = await fetch(`${API_BASE}/admin/products/`)
        console.log('Response status:', res.status) // Debug log
        
        if (res.ok) {
          this.products = await res.json()
        } else {
             const text = await res.text()
             console.error('Fetch failed:', text)
             // alert(`Failed to load products: ${res.status} ${text}`) 
        }
      } catch (err) {
        console.error('Failed to load products:', err)
        // alert(`Network Error: ${err.message}`)
      } finally {
        this.loading = false
      }
    },
    openAddModal() {
      this.editingId = null
      this.form = {
        product_name: '',
        variant: '',
        price_lkr: 0,
        available: 'Yes'
      }
      this.selectedFile = null
      this.showModal = true
    },
    editProduct(product) {
      this.editingId = product.id
      this.form = {
        id: product.id,
        product_name: product.product_name,
        variant: product.variant || '',
        price_lkr: product.price_lkr,
        available: product.available
      }
      this.selectedFile = null
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
      this.editingId = null
    },
    handleFileSelect(e) {
      const file = e.target.files[0]
      if (file) {
        this.selectedFile = file
      }
    },
    async saveProduct() {
        this.saving = true
        try {
            const formData = new FormData()
            formData.append('product_name', this.form.product_name)
            formData.append('price_lkr', this.form.price_lkr)
            formData.append('available', this.form.available)
            
            if (this.form.variant) formData.append('variant', this.form.variant)
            if (this.editingId) formData.append('id', this.editingId)
            
            if (this.selectedFile) {
                formData.append('image', this.selectedFile)
            }

            const res = await fetch(`${API_BASE}/admin/products/`, {
                method: 'POST',
                // No Content-Type header needed for FormData; browser sets it with boundary
                body: formData
            })
            
            if (res.ok) {
                await this.loadProducts()
                this.closeModal()
            } else {
                const err = await res.json()
                alert(err.detail || 'Failed to save product')
            }
        } catch (err) {
            console.error('Error saving product:', err)
            alert('Check backend connection')
        } finally {
            this.saving = false
        }
    },
    async toggleAvailability(product) {
      try {
        const res = await fetch(`${API_BASE}/admin/products/${product.id}/availability`, {
          method: 'PATCH'
        })
        if (res.ok) {
          const data = await res.json()
          product.available = data.available
        }
      } catch (err) {
        console.error('Failed to toggle availability:', err)
      }
    },
    async confirmDelete(product) {
      if (!confirm(`Are you sure you want to delete ${product.product_name}?`)) return
      
      try {
        const res = await fetch(`${API_BASE}/admin/products/${product.id}`, {
          method: 'DELETE'
        })
        if (res.ok) {
          await this.loadProducts()
        }
      } catch (err) {
        console.error('Delete failed:', err)
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
  margin-bottom: 2rem;
}

.products-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border) / 0.4);
  border-radius: 1.25rem;
  padding: 1.5rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.product-card:hover {
  border-color: hsl(var(--primary) / 0.5);
  box-shadow: 0 10px 30px -15px hsl(var(--primary) / 0.2);
}

.product-card.inactive {
  opacity: 0.7;
  background: hsl(var(--muted) / 0.05);
}

.product-image-container {
  width: 100%;
  height: 160px;
  background: hsl(var(--muted) / 0.1);
  border-radius: 0.75rem;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.product-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image-placeholder {
  font-size: 3rem;
  opacity: 0.5;
}

.product-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.product-info h3 {
  margin: 0 0 0.5rem;
  font-size: 1.125rem;
  font-weight: 600;
}

.variant-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.625rem;
  background: hsl(var(--primary) / 0.1);
  color: hsl(var(--primary));
  border-radius: 1rem;
  font-weight: 500;
}

.product-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: hsl(var(--primary));
  white-space: nowrap;
}

.product-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: hsl(var(--muted) / 0.1);
  border-radius: 0.875rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.online { background: #10b981; box-shadow: 0 0 10px #10b981; }
.dot.offline { background: #6b7280; }

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.product-actions {
  display: flex;
  gap: 0.75rem;
}

.product-actions .btn {
  flex: 1;
  justify-content: center;
}

/* Switch UI */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 22px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #10b981;
}

input:checked + .slider:before {
  transform: translateX(22px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
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
.form-group input, .form-group select {
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

.loading, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
</style>
