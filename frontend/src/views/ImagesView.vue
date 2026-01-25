<template>
  <div class="images-view animated-page">
    <div class="page-header">
      <h1>🖼️ Category Images</h1>
      <div class="image-count-badge" :class="{ 'near-limit': images.length >= 40, 'at-limit': images.length >= 50 }">
        {{ images.length }} / 50 images
      </div>
    </div>

    <div class="filters">
      <select v-model="categoryFilter" @change="loadImages">
        <option value="">All Categories</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.name }}
        </option>
      </select>
    </div>

    <!-- Upload Section -->
    <div class="upload-section" v-if="categoryFilter">
      <h3>Upload Image to {{ selectedCategoryName }}</h3>
      <p class="upload-hint">📁 Max file size: 1MB | Total limit: 50 images</p>
      <div class="upload-form">
        <input 
          type="file" 
          ref="fileInput" 
          accept="image/*" 
          @change="handleFileSelect"
        />
        <label>
          <input type="checkbox" v-model="isPrimary" /> Set as primary image
        </label>
        <button 
          class="btn btn-primary" 
          :disabled="!selectedFile || uploading || images.length >= 50"
          @click="uploadImage"
        >
          {{ uploading ? 'Uploading...' : (images.length >= 50 ? '🚫 Limit Reached' : '📤 Upload') }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading images...</div>

    <div v-else-if="images.length === 0" class="empty-state">
      <div class="empty-icon">🖼️</div>
      <p>No images found. Upload your first image!</p>
    </div>

    <div v-else class="images-grid">
      <div 
        v-for="image in images" 
        :key="image.id" 
        class="image-card"
        :class="{ primary: image.is_primary }"
      >
        <div class="image-preview">
          <img :src="`${API_BASE}/images/${image.image_path}`" :alt="image.category_name" />
          <span v-if="image.is_primary" class="primary-badge">⭐ Primary</span>
        </div>
        <div class="image-info">
          <p class="category">{{ image.category_name }}</p>
          <p class="path">{{ image.image_path }}</p>
        </div>
        <div class="image-actions">
          <button class="btn btn-sm btn-danger" @click="deleteImage(image)">
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'

export default {
  name: 'ImagesView',
  data() {
    return {
      API_BASE,
      images: [],
      categories: [],
      loading: true,
      categoryFilter: '',
      selectedFile: null,
      isPrimary: false,
      uploading: false
    }
  },
  computed: {
    selectedCategoryName() {
      const cat = this.categories.find(c => c.id === parseInt(this.categoryFilter))
      return cat ? cat.name : ''
    }
  },
  async mounted() {
    // Check for category query param
    const urlParams = new URLSearchParams(window.location.search)
    const categoryId = urlParams.get('category')
    if (categoryId) {
      this.categoryFilter = parseInt(categoryId)
    }
    
    await this.loadCategories()
    await this.loadImages()
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
          this.categories = data.categories
        }
      } catch (err) {
        console.error('Failed to load categories:', err)
      }
    },
    async loadImages() {
      this.loading = true
      try {
        const token = localStorage.getItem('admin_token')
        let url = `${API_BASE}/admin/images`
        if (this.categoryFilter) {
          url += `?category_id=${this.categoryFilter}`
        }
        const res = await fetch(url, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.images = data.images
        }
      } catch (err) {
        console.error('Failed to load images:', err)
      } finally {
        this.loading = false
      }
    },
    handleFileSelect(e) {
      const file = e.target.files[0]
      if (!file) {
        this.selectedFile = null
        return
      }
      
      // Check file size (1MB = 1,048,576 bytes)
      const maxSize = 1 * 1024 * 1024 // 1MB
      if (file.size > maxSize) {
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2)
        alert(`File size (${fileSizeMB}MB) exceeds 1MB limit. Please choose a smaller image.`)
        this.selectedFile = null
        this.$refs.fileInput.value = ''
        return
      }
      
      this.selectedFile = file
    },
    async uploadImage() {
      if (!this.selectedFile || !this.categoryFilter) return
      
      // Check total image count (50 max)
      if (this.images.length >= 50) {
        alert('Maximum of 50 images allowed. Please delete some images first.')
        return
      }
      
      this.uploading = true
      try {
        const token = localStorage.getItem('admin_token')
        const formData = new FormData()
        formData.append('file', this.selectedFile)
        formData.append('category_id', this.categoryFilter)
        formData.append('is_primary', this.isPrimary)
        
        const res = await fetch(`${API_BASE}/admin/images`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })
        
        if (res.ok) {
          await this.loadImages()
          this.selectedFile = null
          this.isPrimary = false
          this.$refs.fileInput.value = ''
          alert('Image uploaded successfully! ✅')
        } else {
          const error = await res.json()
          alert(error.detail || 'Failed to upload image')
        }
      } catch (err) {
        console.error('Failed to upload image:', err)
        alert('Error uploading image')
      } finally {
        this.uploading = false
      }
    },
    async deleteImage(image) {
      if (!confirm('Are you sure you want to delete this image?')) return
      
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/images/${image.id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (res.ok) {
          await this.loadImages()
        } else {
          alert('Failed to delete image')
        }
      } catch (err) {
        console.error('Failed to delete image:', err)
        alert('Error deleting image')
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
  flex-wrap: wrap;
  gap: 1rem;
}

.image-count-badge {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.2));
  border: 2px solid rgba(34, 197, 94, 0.5);
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.875rem;
  color: #22c55e;
}

.image-count-badge.near-limit {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.2));
  border-color: rgba(251, 191, 36, 0.5);
  color: #fbbf24;
}

.image-count-badge.at-limit {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.2));
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
}

.filters {
  margin-bottom: 1rem;
}

.filters select {
  padding: 0.75rem 1rem;
  border: 2px solid rgba(168, 85, 247, 0.5);
  border-radius: 8px;
  background: transparent;
  color: var(--text-primary);
  min-width: 200px;
  font-weight: 500;
  transition: border-color 0.2s;
}

.filters select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
}

.upload-section {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.upload-section h3 {
  margin: 0 0 1rem;
}

.upload-hint {
  margin: 0 0 1rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-style: italic;
}

.upload-form {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.upload-form .btn-primary {
  color: #ffffff !important;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
}

.upload-form input[type="file"] {
  padding: 0.75rem 1rem;
  border: 2px solid rgba(168, 85, 247, 0.5);
  border-radius: 8px;
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.upload-form input[type="file"]:hover {
  border-color: var(--primary);
  background: rgba(168, 85, 247, 0.1);
}

.upload-form input[type="file"]::file-selector-button {
  padding: 0.625rem 1.25rem;
  margin-right: 1rem;
  border: 2px solid rgba(168, 85, 247, 0.7);
  border-radius: 6px;
  background: rgba(168, 85, 247, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.upload-form input[type="file"]::file-selector-button:hover {
  background: rgba(168, 85, 247, 0.35);
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.4);
}

.upload-form label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: var(--text-primary);
  font-weight: 500;
}

.upload-form input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--primary);
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.image-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.image-card.primary {
  border-color: #f59e0b;
}

.image-preview {
  position: relative;
  height: 180px;
  background: #1a1a2e;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.primary-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #f59e0b;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.image-info {
  padding: 1rem;
}

.image-info .category {
  font-weight: 600;
  margin: 0 0 0.25rem;
}

.image-info .path {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-family: monospace;
  margin: 0;
  word-break: break-all;
}

.image-actions {
  padding: 0 1rem 1rem;
}

.btn-danger {
  background: #dc2626;
  color: white;
}

.btn-danger:hover {
  background: #b91c1c;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.5rem;
  }

  .filters select {
    width: 100%;
  }

  .upload-section {
    padding: 1rem;
  }

  .upload-form {
    flex-direction: column;
    align-items: stretch;
  }

  .upload-form input[type="file"] {
    width: 100%;
  }

  .upload-form .btn-primary {
    width: 100%;
  }

  .images-grid {
    grid-template-columns: 1fr;
  }

  .image-preview {
    height: 200px;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.25rem;
  }

  .upload-section h3 {
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
