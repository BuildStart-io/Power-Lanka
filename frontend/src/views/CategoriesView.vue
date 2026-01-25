<template>
  <div class="categories-view animated-page">
    <div class="page-header">
      <h1>📁 Product Categories</h1>
      <button class="btn btn-primary add-category-btn" @click="showAddModal = true">
        ➕ Add Category
      </button>
    </div>

    <div v-if="loading" class="loading">Loading categories...</div>

    <div v-else class="categories-grid">
      <div 
        v-for="category in categories" 
        :key="category.id" 
        class="category-card"
        :class="{ inactive: !category.is_active }"
      >
        <div class="category-image">
          <img 
            v-if="category.image_path" 
            :src="`${API_BASE.replace('/api', '')}/images/${category.image_path}`" 
            :alt="category.name"
          />
          <div v-else class="no-image">📁</div>
        </div>
        <div class="category-info">
          <h3>{{ category.name }}</h3>
          <p class="name-translations" v-if="category.name_si || category.name_ta">
            <span v-if="category.name_si">🇱🇰 {{ category.name_si }}</span>
            <span v-if="category.name_ta">🇮🇳 {{ category.name_ta }}</span>
          </p>
          <div class="product-count">
            👕 {{ category.product_count || 0 }} products
          </div>
          <div class="display-order">
            📊 Order: {{ category.display_order || 0 }}
          </div>
        </div>
        <div class="category-actions">
          <button 
            class="btn btn-sm" 
            :class="category.is_active ? 'btn-success' : 'btn-secondary'"
            @click="toggleActive(category)"
          >
            {{ category.is_active ? '✅ Active' : '❌ Inactive' }}
          </button>
          <button class="btn btn-sm btn-secondary" @click="editCategory(category)">
            ✏️ Edit
          </button>
          <button 
            class="btn btn-sm btn-danger" 
            @click="deleteCategory(category)"
            :disabled="category.product_count > 0"
            :title="category.product_count > 0 ? 'Cannot delete: has products' : 'Delete category'"
          >
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>

    <div v-if="!loading && categories.length === 0" class="no-data">
      No categories found. Add a category to organize your T-shirts!
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal || editingCategory" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ editingCategory ? 'Edit Category' : 'Add New Category' }}</h2>
        <form @submit.prevent="saveCategory">
          <div class="form-group">
            <label>Name (English) *</label>
            <input v-model="formData.name" type="text" required placeholder="e.g., Casual T-Shirts" />
          </div>
          <div class="form-group">
            <label>Name (Sinhala)</label>
            <input v-model="formData.name_si" type="text" placeholder="e.g., සාමාන්‍ය ටී-ෂර්ට්" />
          </div>
          <div class="form-group">
            <label>Name (Tamil)</label>
            <input v-model="formData.name_ta" type="text" placeholder="e.g., சாதாரண டி-ஷர்ட்" />
          </div>
          <div class="form-group">
            <label>Image Path</label>
            <input v-model="formData.image_path" type="text" placeholder="e.g., categories/casual.jpg" />
            <small>Path relative to /images/ folder</small>
          </div>
          <div class="form-group">
            <label>Display Order</label>
            <input v-model.number="formData.display_order" type="number" min="0" placeholder="0" />
            <small>Lower numbers appear first</small>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary">
              {{ editingCategory ? 'Save Changes' : 'Create Category' }}
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
  name: 'CategoriesView',
  data() {
    return {
      API_BASE,
      categories: [],
      loading: true,
      showAddModal: false,
      editingCategory: null,
      formData: {
        name: '',
        name_si: '',
        name_ta: '',
        image_path: '',
        display_order: 0
      }
    }
  },
  async mounted() {
    await this.loadCategories()
  },
  methods: {
    async loadCategories() {
      this.loading = true
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
      } finally {
        this.loading = false
      }
    },
    editCategory(category) {
      this.editingCategory = category
      this.formData = {
        name: category.name,
        name_si: category.name_si || '',
        name_ta: category.name_ta || '',
        image_path: category.image_path || '',
        display_order: category.display_order || 0
      }
    },
    closeModal() {
      this.showAddModal = false
      this.editingCategory = null
      this.formData = { name: '', name_si: '', name_ta: '', image_path: '', display_order: 0 }
    },
    async saveCategory() {
      try {
        const token = localStorage.getItem('admin_token')
        let url = `${API_BASE}/admin/categories`
        let method = 'POST'
        
        if (this.editingCategory) {
          url = `${API_BASE}/admin/categories/${this.editingCategory.id}`
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
          await this.loadCategories()
          this.closeModal()
        } else {
          alert('Failed to save category')
        }
      } catch (err) {
        console.error('Failed to save category:', err)
        alert('Error saving category')
      }
    },
    async toggleActive(category) {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/categories/${category.id}/toggle`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          category.is_active = data.is_active
        }
      } catch (err) {
        console.error('Failed to toggle category:', err)
      }
    },
    async deleteCategory(category) {
      if (category.product_count > 0) {
        alert('Cannot delete category with products. Remove or reassign products first.')
        return
      }
      
      if (!confirm(`Are you sure you want to delete "${category.name}"?`)) {
        return
      }
      
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/categories/${category.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          await this.loadCategories()
        } else {
          alert('Failed to delete category')
        }
      } catch (err) {
        console.error('Failed to delete category:', err)
        alert('Error deleting category')
      }
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

.page-header h1 {
  color: hsl(var(--foreground));
  margin: 0;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.category-card {
  background: hsl(var(--card));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid hsl(var(--border) / 0.4);
  border-radius: 1.25rem;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
  box-shadow: 0 10px 25px -10px rgb(0 0 0 / 0.05);
}

.category-card:hover {
  transform: translateY(-4px);
  border-color: hsl(var(--primary) / 0.4);
  box-shadow: 0 20px 40px -15px hsl(var(--primary) / 0.1);
}

.category-card.inactive {
  opacity: 0.6;
}

.category-image {
  height: 150px;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  font-size: 3rem;
  opacity: 0.5;
}

.category-info {
  padding: 1rem;
}

.category-info h3 {
  margin: 0 0 0.5rem;
  color: hsl(var(--foreground));
  font-weight: 700;
  font-size: 1.15rem;
}

.name-translations {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0 0 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.product-count, .display-order {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.category-actions {
  padding: 1.25rem;
  border-top: 1px solid hsl(var(--border) / 0.4);
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* Modal styles */
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
  backdrop-filter: blur(10px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
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
  font-weight: 500;
  color: white;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid rgba(168, 85, 247, 0.5);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
}

.form-group small {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-success {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  color: #10b981;
}

.btn-danger {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  color: #ef4444;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-data {
  text-align: center;
  color: var(--text-secondary);
  padding: 2rem;
  background: rgba(168, 85, 247, 0.1);
  border-radius: 12px;
}

.add-category-btn {
  color: #ffffff !important;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1.25rem;
  }

  .add-category-btn {
    width: 100%;
  }

  .categories-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }

  .category-actions {
    flex-direction: column;
  }

  .category-actions .btn {
    width: 100%;
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.5rem;
  }

  .category-image {
    height: 180px;
  }
}

.animated-page {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
