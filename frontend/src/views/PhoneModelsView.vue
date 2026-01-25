<template>
  <div class="phone-models-view animated-page">
    <div class="page-header">
      <h1> Phone Models</h1>
      <button class="btn btn-primary add-phone-model-btn" @click="showAddModal = true">
         Add Phone Model
      </button>
    </div>

    <div v-if="loading" class="loading">Loading phone models...</div>

    <div v-else>
      <!-- Group by brand -->
      <div v-for="(models, brand) in groupedModels" :key="brand" class="brand-section">
        <h2 class="brand-header">{{ brand }}</h2>
        <div class="models-grid">
          <div 
            v-for="model in models" 
            :key="model.id" 
            class="model-card"
            :class="{ inactive: !model.is_active }"
          >
            <div class="model-info">
              <h3>{{ model.model }}</h3>
              <p class="slug">{{ model.slug }}</p>
            </div>
            <div class="model-actions">
              <button 
                class="btn btn-sm" 
                :class="model.is_active ? 'btn-secondary' : 'btn-primary'"
                @click="toggleActive(model)"
              >
                {{ model.is_active ? '🔴' : '🟢' }}
              </button>
              <button 
                class="btn btn-sm btn-danger" 
                @click="confirmDelete(model)"
                title="Delete phone model"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>Add Phone Model</h2>
        <form @submit.prevent="saveModel">
          <div class="form-group">
            <label>Brand</label>
            <input v-model="formData.brand" type="text" required placeholder="e.g., Apple, Samsung" />
          </div>
          <div class="form-group">
            <label>Model Name</label>
            <input v-model="formData.model" type="text" required placeholder="e.g., iPhone 12/12 Pro" />
          </div>
          <div class="form-group">
            <label>Slug</label>
            <input v-model="formData.slug" type="text" required placeholder="e.g., iphone-12-12-pro" />
            <small>Used for search matching (lowercase, hyphens)</small>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary">Add Model</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal delete-modal">
        <h2>⚠️ Delete Phone Model</h2>
        <p>Are you sure you want to delete <strong>{{ modelToDelete?.brand }} {{ modelToDelete?.model }}</strong>?</p>
        <p class="warning-text">This will also remove all stock entries associated with this phone model.</p>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closeDeleteModal">Cancel</button>
          <button type="button" class="btn btn-danger" @click="deleteModel">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'

export default {
  name: 'PhoneModelsView',
  data() {
    return {
      models: [],
      loading: true,
      showAddModal: false,
      showDeleteModal: false,
      modelToDelete: null,
      formData: {
        brand: '',
        model: '',
        slug: ''
      }
    }
  },
  computed: {
    groupedModels() {
      return this.models.reduce((acc, model) => {
        if (!acc[model.brand]) acc[model.brand] = []
        acc[model.brand].push(model)
        return acc
      }, {})
    }
  },
  async mounted() {
    await this.loadModels()
  },
  watch: {
    'formData.model'(val) {
      if (val && this.formData.brand) {
        const brand = this.formData.brand.toLowerCase()
        const model = val.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
        this.formData.slug = brand === 'apple' ? model : `${brand}-${model}`.replace(/--+/g, '-')
      }
    }
  },
  methods: {
    async loadModels() {
      this.loading = true
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/phone-models`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.models = data.phone_models
        }
      } catch (err) {
        console.error('Failed to load models:', err)
      } finally {
        this.loading = false
      }
    },
    closeModal() {
      this.showAddModal = false
      this.formData = { brand: '', model: '', slug: '' }
    },
    async saveModel() {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/phone-models`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.formData)
        })
        
        if (res.ok) {
          await this.loadModels()
          this.closeModal()
        } else {
          const err = await res.json()
          alert(err.detail || 'Failed to add model')
        }
      } catch (err) {
        console.error('Failed to save model:', err)
        alert('Error adding phone model')
      }
    },
    async toggleActive(model) {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/phone-models/${model.id}/toggle`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          model.is_active = !model.is_active
        }
      } catch (err) {
        console.error('Failed to toggle model:', err)
      }
    },
    confirmDelete(model) {
      this.modelToDelete = model
      this.showDeleteModal = true
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.modelToDelete = null
    },
    async deleteModel() {
      if (!this.modelToDelete) return
      
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/phone-models/${this.modelToDelete.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (res.ok) {
          // Remove from local list
          this.models = this.models.filter(m => m.id !== this.modelToDelete.id)
          this.closeDeleteModal()
        } else {
          const err = await res.json()
          alert(err.detail || 'Failed to delete phone model')
        }
      } catch (err) {
        console.error('Failed to delete model:', err)
        alert('Error deleting phone model')
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

.brand-section {
  margin-bottom: 3.5rem;
}

.brand-header {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  padding: 0;
  border: none;
  background: none;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
  filter: drop-shadow(0 2px 4px rgba(168, 85, 247, 0.3));
  display: inline-block;
  width: fit-content;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.model-card {
  background: hsl(var(--card));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid hsl(var(--border) / 0.4);
  border-radius: 1rem;
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
  box-shadow: 0 4px 12px -2px rgb(0 0 0 / 0.05);
}

.model-card:hover {
  transform: translateY(-2px);
  border-color: hsl(var(--primary) / 0.4);
  box-shadow: 0 12px 24px -10px hsl(var(--primary) / 0.15);
}

.model-card.inactive {
  opacity: 0.5;
}

.model-info h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: hsl(var(--foreground));
}

.slug {
  color: var(--primary);
  font-size: 0.75rem;
  font-family: monospace;
  margin: 0.25rem 0 0;
}

.model-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-danger {
  background: hsl(var(--destructive));
  color: white;
  border: none;
  transition: all 0.3s ease;
}

.btn-danger:hover {
  background: hsl(var(--destructive) / 0.9);
  transform: translateY(-1px);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
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
  max-width: 400px;
  width: 90%;
  backdrop-filter: blur(10px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.modal h2 {
  margin: 0 0 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid rgba(168, 85, 247, 0.5);
  border-radius: 8px;
  background: transparent;
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.form-group input:focus {
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

.delete-modal {
  border-color: rgba(239, 68, 68, 0.5);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.15));
}

.delete-modal h2 {
  color: #ef4444;
}

.warning-text {
  color: #fbbf24;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  font-style: italic;
}

.page-header .btn-primary,
.add-phone-model-btn {
  color: #ffffff !important;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1.25rem;
  }

  .add-phone-model-btn {
    width: 100%;
    padding: 0.875rem !important;
  }

  .brand-header {
    font-size: 1.25rem;
  }

  .models-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .model-card {
    padding: 1rem;
  }

  .modal {
    max-width: 95%;
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.25rem;
  }

  .brand-header {
    font-size: 1.125rem;
  }

  .modal {
    padding: 1rem;
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
