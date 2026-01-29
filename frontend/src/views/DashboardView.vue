<template>
  <div class="dashboard animated-page">
    <h1>Dashboard</h1>
    
    <div v-if="loading" class="loading">Loading...</div>
    
    <div v-else class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <Package :size="28" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_orders }}</div>
          <div class="stat-label">Total Orders</div>
        </div>
      </div>
      
      <div class="stat-card highlight">
        <div class="stat-icon">
          <Clock :size="28" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending_orders }}</div>
          <div class="stat-label">Pending Orders</div>
        </div>
      </div>
      
      <div class="stat-card success">
        <div class="stat-icon">
          <DollarSign :size="28" />
        </div>
        <div class="stat-info">
          <div class="stat-value">Rs. {{ formatNumber(stats.total_revenue) }}</div>
          <div class="stat-label">Total Revenue</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <Users :size="28" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_customers }}</div>
          <div class="stat-label">Customers</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <ShoppingBag :size="28" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_items_sold || 0 }}</div>
          <div class="stat-label">Items Sold</div>
        </div>
      </div>
    </div>
    
    <!-- Product and Quick Actions Container -->
    <div class="content-grid">
      <!-- Product Section -->
      <div class="product-section">
        <div class="section-header">
          <h2>Product</h2>
        </div>
        
        <div v-if="productLoading" class="loading">Loading product...</div>
        
        <div v-else-if="product" class="product-card">
          <div class="product-info">
            <div class="product-header">
              <h3>{{ product.name }}</h3>
              <span class="product-price">Rs. {{ formatNumber(product.price) }}</span>
            </div>
            <p class="product-name-si">{{ product.name_si }}</p>
            <p class="delivery-info">🚚 Delivery: Rs. {{ deliveryCharge }}</p>
          </div>
          
          <!-- Images Gallery -->
          <div class="images-section">
            <h4>Product Images ({{ productImages.length }})</h4>
            
            <div class="images-gallery" v-if="productImages.length > 0">
              <div v-for="(img, index) in productImages" :key="index" class="image-item">
                <img :src="`${API_BASE}/media/${img}`" :alt="`Product image ${index + 1}`" />
                <button class="delete-btn" @click="deleteImage(img)" title="Delete image">
                  <Trash2 :size="16" />
                </button>
              </div>
            </div>
            
            <div v-else class="no-images">
              <p>No images uploaded yet</p>
            </div>
            
            <!-- Upload Form -->
            <div class="upload-form">
              <input 
                type="file" 
                ref="fileInput" 
                accept="image/*" 
                @change="handleFileSelect"
              />
              <button 
                class="btn btn-primary btn-dashboard" 
                :disabled="!selectedFile || uploading"
                @click="uploadImage"
              >
                {{ uploading ? 'Uploading...' : 'Upload Image' }}
              </button>
            </div>
            <p class="upload-hint">Max file size: 1MB</p>
          </div>
        </div>
      </div>
      
      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="action-buttons">
          <router-link to="/orders" class="action-card">
            <div class="action-icon">
              <ShoppingBag :size="28" />
            </div>
            <div class="action-content">
              <div class="action-title">View Orders</div>
              <div class="action-description">Manage and track all customer orders</div>
            </div>
          </router-link>
          <router-link to="/customers" class="action-card">
            <div class="action-icon">
              <Users :size="28" />
            </div>
            <div class="action-content">
              <div class="action-title">View Customers</div>
              <div class="action-description">Browse customer list and details</div>
            </div>
          </router-link>
          <router-link to="/whatsapp" class="action-card">
            <div class="action-icon">
              <Smartphone :size="28" />
            </div>
            <div class="action-content">
              <div class="action-title">WhatsApp</div>
              <div class="action-description">Check WhatsApp connection status</div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'
import { 
  Package, 
  Clock, 
  DollarSign, 
  Users, 
  ShoppingBag, 
  Trash2, 
  Smartphone 
} from 'lucide-vue-next'

export default {
  name: 'DashboardView',
  components: {
    Package,
    Clock,
    DollarSign,
    Users,
    ShoppingBag,
    Trash2,
    Smartphone
  },
  data() {
    return {
      API_BASE,
      stats: {
        total_orders: 0,
        pending_orders: 0,
        total_revenue: 0,
        total_customers: 0,
        total_items_sold: 0
      },
      loading: true,
      product: null,
      productLoading: true,
      deliveryCharge: 350,
      selectedFile: null,
      uploading: false
    }
  },
  computed: {
    productImages() {
      if (!this.product || !this.product.image_paths) return []
      return this.product.image_paths.split(',').map(p => p.trim()).filter(p => p)
    }
  },
  async mounted() {
    await Promise.all([this.loadStats(), this.loadProduct()])
  },
  methods: {
    async loadStats() {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          this.stats = await res.json()
        }
      } catch (err) {
        console.error('Failed to load stats:', err)
      } finally {
        this.loading = false
      }
    },
    async loadProduct() {
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/product`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.product = data.product
          this.deliveryCharge = data.delivery_charge || 350
        }
      } catch (err) {
        console.error('Failed to load product:', err)
      } finally {
        this.productLoading = false
      }
    },
    handleFileSelect(e) {
      const file = e.target.files[0]
      if (!file) {
        this.selectedFile = null
        return
      }
      
      // Check file size (1MB limit)
      if (file.size > 1 * 1024 * 1024) {
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2)
        alert(`File size (${sizeMB}MB) exceeds 1MB limit.`)
        this.selectedFile = null
        this.$refs.fileInput.value = ''
        return
      }
      
      this.selectedFile = file
    },
    async uploadImage() {
      if (!this.selectedFile) return
      
      this.uploading = true
      try {
        const token = localStorage.getItem('admin_token')
        const formData = new FormData()
        formData.append('file', this.selectedFile)
        
        const res = await fetch(`${API_BASE}/admin/product/images`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })
        
        if (res.ok) {
          await this.loadProduct()
          this.selectedFile = null
          this.$refs.fileInput.value = ''
        } else {
          const error = await res.json()
          alert(error.detail || 'Failed to upload image')
        }
      } catch (err) {
        console.error('Failed to upload:', err)
        alert('Error uploading image')
      } finally {
        this.uploading = false
      }
    },
    async deleteImage(imagePath) {
      if (!confirm('Delete this image?')) return
      
      // Extract filename from path (e.g., "products/file.jpg" -> "file.jpg")
      const filename = imagePath.split('/').pop()
      
      try {
        const token = localStorage.getItem('admin_token')
        const res = await fetch(`${API_BASE}/admin/product/images/${filename}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (res.ok) {
          await this.loadProduct()
        } else {
          alert('Failed to delete image')
        }
      } catch (err) {
        console.error('Failed to delete:', err)
        alert('Error deleting image')
      }
    },
    formatNumber(num) {
      return num ? num.toLocaleString() : '0'
    }
  }
}
</script>

<style scoped>
.dashboard {
  width: 100%;
  overflow-x: hidden;
  padding-bottom: 2rem;
}

.dashboard h1 {
  margin: 0;
  color: hsl(var(--foreground));
  margin-bottom: 2rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  font-size: 1.75rem;
  animation: slideDownFade 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2.5rem;
  width: 100%;
}

.stat-card {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 1.5rem;
  background: hsl(var(--glass-bg));
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid hsl(var(--glass-border));
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 25px 30px -5px hsl(var(--primary) / 0.12), 0 12px 15px -6px hsl(var(--primary) / 0.1);
  border-color: hsl(var(--primary) / 0.4);
}

/* Premium Gradient Orbs */
.stat-card::before {
  content: '';
  position: absolute;
  top: -25%;
  right: -25%;
  width: 160px;
  height: 160px;
  background: radial-gradient(circle, hsl(var(--primary) / 0.18), transparent 70%);
  border-radius: 50%;
  transition: all 0.6s ease;
  pointer-events: none;
  z-index: 0;
}

.stat-card:hover::before {
  transform: scale(2.2);
  background: radial-gradient(circle, hsl(var(--primary) / 0.28), transparent 70%);
}

.stat-icon {
  position: relative;
  font-size: 1.75rem;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s ease;
  z-index: 1;
  border: none;
}

.monochrome-emoji {
  filter: grayscale(100%) brightness(0.6) sepia(100%) hue-rotate(190deg) saturate(500%);
  opacity: 0.9;
}

.stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(6deg);
}

.stat-info {
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1;
  color: hsl(var(--foreground));
  letter-spacing: -0.05em;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: hsl(var(--muted-foreground));
  margin-top: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Content Grid Layout */
.content-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 3rem;
  width: 100%;
}

/* Glass Section Unified Style */
.product-section, .quick-actions {
  background: hsl(var(--glass-bg));
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid hsl(var(--glass-border));
  border-radius: 1.5rem;
  padding: 1.5rem;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05);
  transition: all 0.3s ease;
}

.product-section:hover, .quick-actions:hover {
  border-color: hsl(var(--primary) / 0.3);
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.05);
}

.product-section {
  width: 100%;
}

.quick-actions {
  width: 100%;
}

.section-header h2, .quick-actions h2 {
  margin: 0 0 1.25rem;
  font-size: 1.25rem;
  color: hsl(var(--foreground));
  font-weight: 800;
  letter-spacing: -0.03em;
}

.product-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
}

.product-info {
  position: relative;
  padding: 1.5rem;
  background: hsl(var(--muted) / 0.15);
  border-radius: 1.25rem;
  border: 1px solid hsl(var(--border) / 0.4);
}

.product-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: hsl(var(--foreground));
  font-weight: 800;
  letter-spacing: -0.03em;
}

.product-price {
  font-size: 1.1rem;
  font-weight: 800;
  color: hsl(var(--primary));
  filter: drop-shadow(0 0 8px hsl(var(--primary) / 0.25));
}

.product-name-si {
  margin: 0.25rem 0 0;
  color: hsl(var(--muted-foreground));
  font-size: 0.9rem;
  font-weight: 500;
}

.delivery-info {
  margin: 1rem 0 0;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.875rem;
  background: hsl(var(--warning) / 0.08);
  color: hsl(var(--warning));
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  border: 1px solid hsl(var(--warning) / 0.15);
}

.images-section {
  padding: 1.5rem;
  background: hsl(var(--muted) / 0.08);
  border-radius: 1.5rem;
  border: 1px solid hsl(var(--border) / 0.25);
}

.images-section h4 {
  margin: 0 0 1.25rem;
  font-size: 1.1rem;
  font-weight: 700;
  color: hsl(var(--foreground));
}

.images-gallery {
  display: flex;
  overflow-x: auto;
  gap: 1.5rem;
  padding-bottom: 1.25rem;
  margin-bottom: 2rem;
  scrollbar-width: thin;
  scrollbar-color: hsl(var(--primary) / 0.2) transparent;
}

.images-gallery::-webkit-scrollbar {
  height: 6px;
}

.images-gallery::-webkit-scrollbar-thumb {
  background: hsl(var(--primary) / 0.25);
  border-radius: 10px;
}

.image-item {
  position: relative;
  flex: 0 0 140px;
  aspect-ratio: 1;
  border-radius: 1.25rem;
  overflow: hidden;
  background: hsl(var(--muted) / 0.2);
  border: 1px solid hsl(var(--border) / 0.4);
  transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
  color: hsl(var(--foreground));
  font-size: 0.7rem;
}

.image-item:hover {
  transform: scale(1.06) rotate(1.5deg);
  box-shadow: 0 20px 40px -15px rgb(0 0 0 / 0.2);
}

.delete-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: hsl(var(--destructive));
  color: white;
  border: none;
  border-radius: 0.875rem;
  width: 36px;
  height: 36px;
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateY(-10px);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgb(0 0 0 / 0.25);
}

.image-item:hover .delete-btn {
  opacity: 1;
  transform: translateY(0);
}

.upload-form {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  max-width: 480px;
}

.upload-form input[type="file"] {
  flex: 1;
  padding: 0.5rem;
  background: hsl(var(--primary) / 0.03);
  border: 1px solid hsl(var(--primary) / 0.4);
  border-radius: 0.75rem;
  font-size: 0.8125rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-form input[type="file"]::file-selector-button {
  background: hsl(var(--primary));
  color: white;
  border: none;
  padding: 0.4rem 0.75rem;
  border-radius: 0.5rem;
  margin-right: 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-form input[type="file"]::file-selector-button:hover {
  background: hsl(var(--primary) / 0.9);
  transform: translateY(-1px);
}

.upload-form input[type="file"]:focus {
  border-color: hsl(var(--primary));
  box-shadow: 0 0 0 3px hsl(var(--primary) / 0.1);
  outline: none;
}

.btn-dashboard {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
}

.upload-hint {
  font-size: 0.7rem;
  color: hsl(var(--muted-foreground));
  margin-top: 0.5rem;
  font-weight: 500;
}

/* Quick Action Cards */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, hsl(var(--primary) / 0.1), hsl(var(--primary) / 0.05));
  border: 1px solid hsl(var(--primary) / 0.3);
  border-radius: 1.5rem;
  text-decoration: none;
  transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 25px -10px rgb(0 0 0 / 0.05);
}

.dark .action-card {
  background: transparent;
  border: 1.5px solid hsl(var(--primary) / 0.4);
}

.dark .action-card:hover {
  background: hsl(var(--primary) / 0.1);
  border-color: hsl(var(--primary));
}

.action-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, hsl(var(--primary) / 0.1), transparent);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.action-card:hover {
  transform: translateX(12px);
  border-color: hsl(var(--primary) / 0.4);
  box-shadow: 0 20px 35px -12px hsl(var(--primary) / 0.15);
}

.action-card:hover::after {
  opacity: 1;
}

.action-icon {
  font-size: 1.75rem;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
  z-index: 1;
}

.action-card:hover .action-icon {
  transform: scale(1.15) rotate(-3deg);
}

.action-content {
  flex: 1;
  z-index: 1;
}

.action-title {
  font-size: 1.125rem;
  font-weight: 800;
  color: hsl(var(--foreground));
  margin-bottom: 0.25rem;
  letter-spacing: -0.02em;
}

.dark .action-title {
  color: white;
}

.action-description {
  font-size: 0.875rem;
  color: hsl(var(--muted-foreground));
  line-height: 1.4;
  font-weight: 500;
}

.dark .action-description {
  color: hsl(215 20% 85%);
}

@media (max-width: 1024px) {
  .content-grid {
    flex-direction: column;
    gap: 2rem;
  }
}

@media (max-width: 768px) {
  .dashboard h1 {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .stat-card {
    padding: 1.25rem;
    min-height: auto;
  }

  .stat-value {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .product-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .product-price {
    font-size: 1.25rem;
  }

  .image-item {
    flex: 0 0 120px;
  }

  .action-card {
    padding: 1rem;
    gap: 1rem;
  }

  .action-icon {
    font-size: 1.5rem;
  }

  .action-title {
    font-size: 1rem;
  }
  .images-section {
    padding: 0.75rem;
  }

  .images-section h4 {
    font-size: 0.9375rem;
    margin-bottom: 0.75rem;
  }

  .upload-form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 1rem;
    width: 100%;
  }

  .upload-form input[type="file"],
  .btn-dashboard {
    width: 100%;
    max-width: none;
  }

  .upload-form input[type="file"] {
    padding: 0.25rem;
    font-size: 0.7rem;
    border-radius: 0.5rem;
  }

  .upload-form input[type="file"]::file-selector-button {
    padding: 0.2rem 0.4rem;
    font-size: 0.65rem;
    margin-right: 0.35rem;
    border-radius: 0.375rem;
  }

  .btn-dashboard {
    padding: 0.3rem 0.6rem;
    font-size: 0.7rem;
    border-radius: 0.5rem;
  }

  .upload-hint {
    font-size: 0.65rem;
    margin-top: 0.35rem;
  }
}

.animated-page {
  animation: slideUpFade 1s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes slideUpFade {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDownFade {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
