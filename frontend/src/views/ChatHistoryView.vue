<template>
  <div class="animated-page">
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
      <router-link to="/customers" class="btn btn-secondary btn-sm">← Back</router-link>
      <h1>💬 Chat History: {{ phone }}</h1>
    </div>
    
    <div v-if="customer" class="card" style="margin-bottom: 1.5rem;">
      <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
        <div><strong>Name:</strong> {{ customer.name || 'N/A' }}</div>
        <div><strong>Phone:</strong> {{ customer.phone }}</div>
        <div><strong>Address:</strong> {{ customer.address || 'N/A' }}</div>
        <div><strong>District:</strong> {{ customer.city || 'N/A' }}</div>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    
    <div v-else class="card">
      <div class="chat-container">
        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          :class="['chat-message', msg.role]"
        >
          <div class="chat-content">{{ msg.content }}</div>
          <div class="chat-time">{{ formatTime(msg.time) }}</div>
        </div>
        
        <div v-if="messages.length === 0" style="text-align: center; color: var(--text-secondary); padding: 2rem;">
          No messages yet
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE } from '../config'

export default {
  name: 'ChatHistoryView',
  data() {
    return {
      loading: true,
      phone: '',
      customer: null,
      messages: []
    }
  },
  async mounted() {
    this.phone = this.$route.params.phone
    await this.fetchChatHistory()
  },
  methods: {
    async fetchChatHistory() {
      const token = localStorage.getItem('admin_token')
      
      try {
        const response = await fetch(`${API_BASE}/admin/chat-history/${this.phone}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.customer = data.customer
          this.messages = data.messages
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (err) {
        console.error('Error fetching chat history:', err)
      } finally {
        this.loading = false
      }
    },
    formatTime(timeStr) {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 1.5rem;
}

.page-header h1 {
  color: hsl(var(--foreground));
  background: linear-gradient(135deg, hsl(var(--gradient-start)), hsl(var(--gradient-end)));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card {
  background: hsl(var(--card));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: 0 20px 25px -5px hsl(var(--primary) / 0.05), 0 10px 10px -5px hsl(var(--primary) / 0.02);
}

.chat-container {
  max-height: 60vh;
  overflow-y: auto;
  padding: 1rem;
}

.chat-message {
  max-width: 80%;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.chat-message.user {
  background: hsl(var(--primary) / 0.2);
  border: 1px solid hsl(var(--primary) / 0.3);
  margin-left: auto;
  border-bottom-right-radius: 4px;
  color: hsl(var(--foreground));
}

.chat-message.assistant {
  background: hsl(var(--muted) / 0.5);
  border: 1px solid hsl(var(--border));
  margin-right: auto;
  border-bottom-left-radius: 4px;
  color: hsl(var(--foreground));
}

.chat-content {
  white-space: pre-wrap;
  word-break: break-word;
  color: hsl(var(--foreground));
}

.chat-time {
  font-size: 0.75rem;
  color: hsl(var(--muted-foreground));
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.25rem;
  }

  .chat-container {
    max-height: calc(100vh - 280px);
    padding: 0.5rem;
  }

  .chat-message {
    max-width: 92%;
    padding: 0.875rem;
    font-size: 0.8125rem;
  }

  .card {
    padding: 1rem;
    border-radius: 1rem;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.25rem;
  }

  .chat-message {
    max-width: 90%;
    padding: 0.625rem;
    font-size: 0.875rem;
  }

  .card {
    padding: 0.75rem;
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
