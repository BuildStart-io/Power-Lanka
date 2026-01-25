<template>
  <div class="tshirts-view animated-page">
    <div class="page-header">
      <h1>👕 T-shirts Management</h1>
      <div class="header-actions">
        <select v-model="filterCategory" class="filter-select">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
        <button class="btn btn-primary" @click="showAddModal = true">➕ Add T-shirt</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    
    <div v-else class="tshirts-grid">
      <div v-for="tshirt in filteredTshirts" :key="tshirt.id" class="tshirt-card" :class="{ inactive: !tshirt.is_active }">
        <div class="tshirt-image">
          <img v-if="tshirt.image_path" :src="`${API_BASE.replace('/api', '')}/images/${tshirt.image_path}`" :alt="tshirt.name" />
          <div v-else class="no-image">👕</div>
        </div>
        <div class="tshirt-info">
          <h3>{{ tshirt.name }}</h3>
          <div class="tshirt-price">Rs. {{ formatNumber(tshirt.price) }}</div>
          <div class="tshirt-category" v-if="tshirt.category_name">
            📁 {{ tshirt.category_name }}
          </div>
          <div class="tshirt-category no-category" v-else>
            📁 No Category
          </div>
          <div class="tshirt-description">{{ tshirt.description || 'No description' }}</div>
          
          <div class="stock-info">
            <h4>Stock by Size:</h4>
            <div class="stock-grid">
              <div class="stock-item">
                <span class="size">S</span>
                <span class="qty">{{ tshirt.stock_s }}</span>
              </div>
              <div class="stock-item">
                <span class="size">M</span>
                <span class="qty">{{ tshirt.stock_m }}</span>
              </div>
              <div class="stock-item">
                <span class="size">L</span>
                <span class="qty">{{ tshirt.stock_l }}</span>
              </div>
              <div class="stock-item">
                <span class="size">XL</span>
                <span class="qty">{{ tshirt.stock_xl }}</span>
              </div>
              <div class="stock-item">
                <span class="size">XXL</span>
                <span class="qty">{{ tshirt.stock_xxl }}</span>
              </div>
            </div>
          </div>
          
          <div class="tshirt-actions">
            <button 
              @click="toggleActive(tshirt)" 
              :class="['btn', 'btn-sm', tshirt.is_active ? 'btn-success' : 'btn-secondary']"
            >
              {{ tshirt.is_active ? '✅ Active' : '❌ Inactive' }}
            </button>
            <button class="btn btn-sm btn-secondary" @click="editTshirt(tshirt)">
              ✏️ Edit
            </button>
            <button class="btn btn-sm btn-danger" @click="deleteTshirt(tshirt)">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="!loading && filteredTshirts.length === 0" class="no-data">
      No T-shirts found. Click "Add T-shirt" to create one.
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal || editingTshirt" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ editingTshirt ? 'Edit T-Shirt' : 'Add New T-Shirt' }}</h2>
        <form @submit.prevent="saveTshirt">
          <div class="form-group">
            <label>Name</label>
            <input v-model="formData.name" type="text" required />
          </div>
          <div class="form-group">
            <label>Price (Rs.)</label>
            <input v-model.number="formData.price" type="number" min="0" required />
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="formData.category_id">
              <option :value="null">-- No Category --</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="formData.description" rows="2"></textarea>
          </div>
          <div class="form-group">
            <label>Image Path</label>
            <input v-model="formData.image_path" type="text" placeholder="tshirts/example.jpg" />
          </div>
          <div class="form-row">
            <div class="form-group half">
              <label>Stock S</label>
              <input v-model.number="formData.stock_s" type="number" min="0" />
            </div>
            <div class="form-group half">
              <label>Stock M</label>
              <input v-model.number="formData.stock_m" type="number" min="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group half">
              <label>Stock L</label>
              <input v-model.number="formData.stock_l" type="number" min="0" />
            </div>
            <div class="form-group half">
              <label>Stock XL</label>
              <input v-model.number="formData.stock_xl" type="number" min="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group half">
              <label>Stock XXL</label>
              <input v-model.number="formData.stock_xxl" type="number" min="0" />
            </div>
            <div class="form-group half">
              <label>Display Order</label>
              <input v-model.number="formData.display_order" type="number" min="0" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'

export default {
  name: 'TshirtsView',
  data() {
    return {
      API_BASE,
      tshirts: [],
      categories: [],
      loading: true,
      filterCategory: '',
      showAddModal: false,
      editingTshirt: null,
      formData: {
        name: '',
        price: 1990,
        description: '',
        image_path: '',
        category_id: null,
        display_order: 0,
        stock_s: 10,
        stock_m: 10,
        stock_l: 10,
        stock_xl: 10,
        stock_xxl: 10
      }
    }
  },
  computed: {
    filteredTshirts() {
      if (!this.filterCategory) return this.tshirts
      return this.tshirts.filter(t => t.category_id === this.filterCategory)
    }
  },
  async mounted() {
    await Promise.all([this.loadTshirts(), this.loadCategories()])
  },
  methods: {
    async loadTshirts() {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/tshirts`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.tshirts = data.tshirts || []
        }
      } catch (err) {
        console.error('Failed to load T-shirts:', err)
      } finally {
        this.loading = false
      }
    },
    async loadCategories() {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/categories`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.categories = data.categories || []
        }
      } catch (err) {
        console.error('Failed to load categories:', err)
      }
    },
    async toggleActive(tshirt) {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/tshirts/${tshirt.id}/toggle`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          tshirt.is_active = data.is_active
        }
      } catch (err) {
        console.error('Failed to toggle T-shirt:', err)
      }
    },
    editTshirt(tshirt) {
      this.editingTshirt = tshirt
      this.formData = {
        name: tshirt.name,
        price: tshirt.price,
        description: tshirt.description || '',
        image_path: tshirt.image_path || '',
        category_id: tshirt.category_id || null,
        display_order: tshirt.display_order || 0,
        stock_s: tshirt.stock_s || 0,
        stock_m: tshirt.stock_m || 0,
        stock_l: tshirt.stock_l || 0,
        stock_xl: tshirt.stock_xl || 0,
        stock_xxl: tshirt.stock_xxl || 0
      }
    },
    closeModal() {
      this.editingTshirt = null
      this.showAddModal = false
      this.formData = {
        name: '',
        price: 1990,
        description: '',
        image_path: '',
        category_id: null,
        display_order: 0,
        stock_s: 10,
        stock_m: 10,
        stock_l: 10,
        stock_xl: 10,
        stock_xxl: 10
      }
    },
    async saveTshirt() {
      try {
        const token = localStorage.getItem('admin_token')
        let url = `${API_BASE}/admin/tshirts`
        let method = 'POST'
        
        if (this.editingTshirt) {
          url = `${API_BASE}/admin/tshirts/${this.editingTshirt.id}`
          method = 'PUT'
        }
        
        const res = await fetch(url, {
          method,
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.formData)
        })
        if (res.ok) {
          await this.loadTshirts()
          this.closeModal()
        } else {
          alert('Failed to save T-shirt')
        }
      } catch (err) {
        console.error('Failed to save T-shirt:', err)
        alert('Error saving T-shirt')
      }
    },
    async deleteTshirt(tshirt) {
      if (!confirm(`Are you sure you want to delete "${tshirt.name}"?`)) {
        return
      }
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/tshirts/${tshirt.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          await this.loadTshirts()
        } else {
          const data = await res.json()
          alert(data.detail || 'Failed to delete T-shirt')
        }
      } catch (err) {
        console.error('Failed to delete T-shirt:', err)
        alert('Error deleting T-shirt')
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
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h1 {
  color: white;
  margin: 0;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 2px solid rgba(168, 85, 247, 0.5);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  min-width: 180px;
}

.tshirts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.tshirt-card {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.15));
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.tshirt-card.inactive {
  opacity: 0.6;
}

.tshirt-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(168, 85, 247, 0.3);
}

.tshirt-image {
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
}

.tshirt-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}

.no-image {
  font-size: 4rem;
  opacity: 0.5;
}

.tshirt-info {
  padding: 1rem;
}

.tshirt-info h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: white;
}

.tshirt-price {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #a855f7, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.25rem;
}

.tshirt-category {
  font-size: 0.875rem;
  color: #10b981;
  margin-bottom: 0.5rem;
}

.tshirt-category.no-category {
  color: var(--text-secondary);
}

.tshirt-description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.stock-info h4 {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.stock-grid {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.stock-item {
  background: rgba(168, 85, 247, 0.2);
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 40px;
}

.stock-item .size {
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.stock-item .qty {
  font-weight: 600;
  color: white;
}

.tshirt-actions {
  display: flex;
  gap: 0.5rem;
}

.no-data {
  text-align: center;
  color: var(--text-secondary);
  padding: 2rem;
  background: rgba(168, 85, 247, 0.1);
  border-radius: 12px;
}

.btn-success {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  color: #10b981;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.15));
  border: 2px solid rgba(168, 85, 247, 0.5);
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  backdrop-filter: blur(10px);
}

.modal h2 {
  margin: 0 0 1.5rem;
  color: white;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: white;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid rgba(168, 85, 247, 0.5);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary);
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group.half {
  flex: 1;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.animated-page {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tshirts-grid {
    grid-template-columns: 1fr;
  }
  
  .tshirt-actions {
    flex-direction: column;
  }
  
  .tshirt-actions .btn {
    width: 100%;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>
