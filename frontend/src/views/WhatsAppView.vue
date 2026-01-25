<template>
  <div class="whatsapp-view">
    <h1 class="page-title">WhatsApp Connection</h1>
    
    <div class="status-card" :class="statusClass">
      <div class="status-header">
        <div class="status-badge-icon" :class="qrData.status"></div>
        <div class="status-text">
          <h2>{{ statusTitle }}</h2>
          <p>{{ statusMessage }}</p>
        </div>
      </div>
    </div>

    <div v-if="qrData.status === 'waiting_for_scan'" class="qr-card">
      <div class="qr-header">
        <h2>Scan QR Code</h2>
        <p>Open WhatsApp on your phone and scan this QR code to connect</p>
      </div>
      
      <div class="qr-container">
        <div v-if="loading" class="loading-spinner">
          <div class="spinner"></div>
          <p>Loading QR Code...</p>
        </div>
        <div v-else-if="qrData.qr && !isQrExpired" class="qr-code-wrapper">
          <canvas ref="qrCanvas" class="qr-canvas"></canvas>
        </div>
        <div v-else class="qr-placeholder">
          <p v-if="isQrExpired">QR Code expired. Click refresh to get a new one.</p>
          <p v-else>QR Code not available</p>
        </div>
      </div>

      <div v-if="qrData.timestamp" class="qr-timestamp">
        <p>Last updated: {{ formatTimestamp(qrData.timestamp) }} <span v-if="isQrExpired" class="expired-badge">EXPIRED</span></p>
      </div>

      <div class="qr-instructions">
        <h3>How to connect:</h3>
        <ol>
          <li>Open WhatsApp on your phone</li>
          <li>Tap Menu (⋮) or Settings</li>
          <li>Tap <span class="highlight-blue">"Linked Devices"</span></li>
          <li>Tap <span class="highlight-blue">"Link a Device"</span></li>
          <li>Scan the QR code above</li>
        </ol>
      </div>

      <button @click="refreshQR" class="btn btn-secondary" :disabled="loading">
        <span v-if="!loading">Refresh QR Code</span>
        <span v-else>Loading...</span>
      </button>
    </div>

    <div v-else-if="qrData.status === 'authenticated'" class="connected-card">
      <div class="connected-content">
        <div class="success-icon">✓</div>
        <h2>WhatsApp Connected</h2>
        <p>Your WhatsApp is successfully connected and ready to receive messages</p>
        <div class="connected-info">
          <p><strong>Connected since:</strong> {{ formatTimestamp(qrData.timestamp) }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="qrData.status === 'not_initialized'" class="info-card">
      <div class="info-content">
        <div class="info-icon">ℹ️</div>
        <h2>WhatsApp Service Not Started</h2>
        <p>The WhatsApp service is not running. Please start the service to connect.</p>
      </div>
    </div>

    <div class="auto-refresh-notice">
      <small>Auto-refreshing every 3 seconds when waiting for scan</small>
    </div>
  </div>
</template>

<script>
import QRCode from 'qrcode'
import { API_BASE } from '../config'

export default {
  name: 'WhatsAppView',
  data() {
    return {
      qrData: {
        status: 'loading',
        qr: null,
        timestamp: null,
        message: 'Loading...'
      },
      loading: true,
      refreshInterval: null,
      now: Date.now()
    }
  },
  computed: {
    isQrExpired() {
      if (!this.qrData.timestamp) return true
      const qrTime = new Date(this.qrData.timestamp).getTime()
      const oneMinuteAgo = this.now - (60 * 1000)
      return qrTime < oneMinuteAgo
    },
    statusClass() {
      return {
        'status-waiting': this.qrData.status === 'waiting_for_scan',
        'status-connected': this.qrData.status === 'authenticated',
        'status-error': this.qrData.status === 'not_initialized' || this.qrData.status === 'disconnected'
      }
    },
    statusIcon() {
      if (this.qrData.status === 'authenticated') return '✅'
      if (this.qrData.status === 'waiting_for_scan') return '⏳'
      if (this.qrData.status === 'disconnected') return '📴'
      if (this.qrData.status === 'not_initialized') return '⚠️'
      return '📱'
    },
    statusTitle() {
      if (this.qrData.status === 'authenticated') return 'Connected'
      if (this.qrData.status === 'waiting_for_scan') return 'Waiting for Connection'
      if (this.qrData.status === 'disconnected') return 'Disconnected'
      if (this.qrData.status === 'not_initialized') return 'Service Not Running'
      return 'Loading...'
    },
    statusMessage() {
      if (this.qrData.status === 'authenticated') return 'WhatsApp is connected and ready'
      if (this.qrData.status === 'waiting_for_scan') return 'Please scan the QR code with WhatsApp'
      if (this.qrData.status === 'disconnected') return 'WhatsApp was disconnected. Restart the service to reconnect.'
      if (this.qrData.status === 'not_initialized') return 'WhatsApp service needs to be started'
      return 'Checking status...'
    }
  },
  methods: {
    async fetchQRCode() {
      try {
        const token = localStorage.getItem('admin_token')
        const response = await fetch(`${API_BASE}/admin/whatsapp/qr`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!response.ok) {
          throw new Error('Failed to fetch QR code')
        }

        const data = await response.json()
        this.qrData = data
        
        // Generate QR code canvas if QR data is available
        if (data.qr && this.$refs.qrCanvas) {
          await this.$nextTick()
          await QRCode.toCanvas(this.$refs.qrCanvas, data.qr, {
            width: 300,
            margin: 2,
            color: {
              dark: '#000000',
              light: '#FFFFFF'
            }
          })
        }
        
        this.loading = false
      } catch (error) {
        console.error('Error fetching QR code:', error)
        this.qrData = {
          status: 'error',
          message: error.message
        }
        this.loading = false
      }
    },
    async refreshQR() {
      this.loading = true
      await this.fetchQRCode()
    },
    formatTimestamp(timestamp) {
      if (!timestamp) return 'Unknown'
      const date = new Date(timestamp)
      return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
      })
    },
    startAutoRefresh() {
      // Auto-refresh every 3 seconds when waiting for scan
      this.refreshInterval = setInterval(async () => {
        // Update 'now' to recalculate expiration
        this.now = Date.now()
        if (this.qrData.status === 'waiting_for_scan') {
          await this.fetchQRCode()
        } else {
          // Clear interval if not waiting anymore
          this.stopAutoRefresh()
        }
      }, 3000)
    },
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    }
  },
  async mounted() {
    await this.fetchQRCode()
    this.startAutoRefresh()
  },
  beforeUnmount() {
    this.stopAutoRefresh()
  },
  watch: {
    'qrData.qr': async function(newVal) {
      if (newVal && this.$refs.qrCanvas) {
        await this.$nextTick()
        await QRCode.toCanvas(this.$refs.qrCanvas, newVal, {
          width: 300,
          margin: 2,
          color: {
            dark: '#000000',
            light: '#FFFFFF'
          }
        })
      }
    }
  }
}
</script>

<style scoped>
.whatsapp-view {
  width: 100%;
  padding-top: 1rem;
  padding-bottom: 2rem;
}

.page-title {
  color: hsl(var(--foreground));
  margin-bottom: 2rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  font-size: 1.75rem;
  animation: slideDownFade 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.status-card {
  background: hsl(var(--glass-bg));
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid hsl(var(--glass-border));
  border-radius: 1.5rem;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.03);
  animation: slideUpFade 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.status-badge-icon {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: hsl(var(--muted-foreground));
  position: relative;
}

.status-badge-icon::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid currentColor;
  opacity: 0.2;
}

.status-badge-icon.authenticated { background: hsl(var(--success)); color: hsl(var(--success)); }
.status-badge-icon.waiting_for_scan { background: hsl(var(--warning)); color: hsl(var(--warning)); animation: pulse 2s infinite; }
.status-badge-icon.error, .status-badge-icon.disconnected { background: hsl(var(--destructive)); color: hsl(var(--destructive)); }

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.5; }
  100% { transform: scale(1); opacity: 1; }
}

.status-text h2 {
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0 0 0.25rem 0;
  color: hsl(var(--primary));
  letter-spacing: -0.02em;
}

.status-text p {
  margin: 0;
  color: hsl(var(--muted-foreground));
  font-size: 0.9375rem;
  font-weight: 500;
}

.qr-card {
  background: hsl(var(--glass-bg));
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid hsl(var(--glass-border));
  border-radius: 1.5rem;
  padding: 2.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.03);
  animation: slideUpFade 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.qr-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.qr-header h2 {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.75rem;
  color: hsl(var(--primary));
  letter-spacing: -0.03em;
}

.qr-header p {
  color: hsl(var(--muted-foreground));
  font-weight: 500;
  font-size: 0.9375rem;
}

.qr-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 320px;
  margin-bottom: 2.5rem;
}

.highlight-blue {
  color: hsl(var(--primary));
  font-weight: 700;
}

.qr-code-wrapper {
  background: white;
  padding: 1.25rem;
  border-radius: 1.25rem;
  border: 1px solid hsl(var(--border) / 0.6);
  box-shadow: 0 10px 25px -10px rgb(0 0 0 / 0.1);
}

.qr-timestamp {
  text-align: center;
  margin-bottom: 1.5rem;
  padding: 0.75rem 1.25rem;
  background: hsl(var(--muted) / 0.1);
  border: 1px solid hsl(var(--border) / 0.4);
  border-radius: 1rem;
}

.qr-timestamp p {
  margin: 0;
  color: hsl(var(--muted-foreground));
  font-size: 0.8125rem;
  font-weight: 600;
}

.expired-badge {
  background: hsl(var(--destructive));
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.6875rem;
  font-weight: 800;
  margin-left: 0.5rem;
}

.qr-instructions {
  background: hsl(var(--primary) / 0.03);
  border: 1px solid hsl(var(--primary) / 0.1);
  border-radius: 1.25rem;
  padding: 1.75rem;
  margin-bottom: 2rem;
}

.qr-instructions h3 {
  font-size: 1rem;
  font-weight: 800;
  margin: 0 0 1.25rem 0;
  color: hsl(var(--foreground));
  letter-spacing: -0.01em;
}

.qr-instructions ol {
  margin: 0;
  padding-left: 1.25rem;
  color: hsl(var(--muted-foreground));
  font-weight: 500;
}

.qr-instructions li {
  margin-bottom: 0.75rem;
  font-size: 0.9375rem;
}

.qr-instructions li:last-child {
  margin-bottom: 0;
}

.connected-card, .info-card {
  background: hsl(var(--glass-bg));
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid hsl(var(--glass-border));
  border-radius: 2rem;
  padding: 4rem 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.03);
  animation: slideUpFade 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.connected-content h2, .info-content h2 {
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: 1rem;
  color: hsl(var(--foreground));
  letter-spacing: -0.04em;
}

.connected-content p, .info-content p {
  color: hsl(var(--muted-foreground));
  font-size: 1.0625rem;
  font-weight: 500;
  margin-bottom: 2rem;
}

.connected-info {
  background: hsl(var(--success) / 0.05);
  border: 1px solid hsl(var(--success) / 0.1);
  border-radius: 1.25rem;
  padding: 1.25rem;
  display: inline-block;
}

.connected-info p {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: hsl(var(--success));
}

.auto-refresh-notice {
  text-align: center;
  color: hsl(var(--muted-foreground));
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.6;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.875rem 1.75rem;
  border: none;
  border-radius: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.9375rem;
  width: 100%;
}

.btn-secondary {
  background: hsl(217 91% 20%);
  color: white;
  border: 1px solid hsl(var(--primary) / 0.3);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.btn-secondary:hover:not(:disabled) {
  background: hsl(var(--muted) / 0.1);
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.08);
}

@media (max-width: 768px) {
  .page-title { 
    font-size: 1.5rem; 
    margin-bottom: 1.5rem;
  }
  
  .status-card {
    padding: 1.25rem;
  }

  .status-header {
    gap: 1rem;
  }

  .status-text h2 {
    font-size: 1.125rem;
  }

  .qr-card { 
    padding: 1.5rem; 
  }

  .qr-header h2 {
    font-size: 1.25rem;
  }

  .qr-container {
    min-height: 280px;
    margin-bottom: 1.5rem;
  }

  .qr-code-wrapper {
    padding: 0.75rem;
    max-width: 100%;
  }

  .qr-code-wrapper canvas {
    max-width: 100% !important;
    height: auto !important;
  }

  .connected-card, .info-card {
    padding: 3rem 1.5rem;
  }

  .connected-content h2, .info-content h2 {
    font-size: 1.5rem;
  }

  .qr-instructions {
    padding: 1.25rem;
  }

  .btn {
    padding: 0.75rem 1.5rem;
  }
}

@media (max-width: 480px) {
  .status-badge-icon {
    width: 10px;
    height: 10px;
  }

  .status-text p {
    font-size: 0.8125rem;
  }

  .qr-header p {
    font-size: 0.8125rem;
  }

  .qr-instructions li {
    font-size: 0.8125rem;
  }
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
