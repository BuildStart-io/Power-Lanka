<template>
  <div class="chat-history-view animated-page">
    <div class="page-header">
       <router-link to="/customers" class="back-link">← Back to Customers</router-link>
       <h1>💬 {{ phone }}</h1>
    </div>

    <div v-if="loading" class="loading">Loading chat...</div>

    <div v-else class="chat-card">
      <div class="chat-container">
        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          :class="['chat-bubble', msg.role]"
        >
          <div class="chat-content">{{ msg.content }}</div>
          <div class="chat-meta">{{ formatTime(msg.time) }}</div>
        </div>
        
        <div v-if="messages.length === 0" class="empty-chat">
          No conversation history found.
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
      messages: []
    }
  },
  async mounted() {
    this.phone = this.$route.params.phone
    await this.fetchChatHistory()
  },
  methods: {
    async fetchChatHistory() {
      try {
        const res = await fetch(`${API_BASE}/admin/chat-history/${this.phone}`)
        if (res.ok) {
          const data = await res.json()
          this.messages = data.messages
        } else {
           console.error("Failed to load history")
        }
      } catch (err) {
        console.error('Error fetching chat history:', err)
      } finally {
        this.loading = false
      }
    },
    formatTime(timeStr) {
      if (!timeStr) return ''
      return new Date(timeStr).toLocaleString()
    }
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.back-link {
    text-decoration: none;
    font-weight: bold;
    color: hsl(var(--primary)); 
    background: hsl(var(--primary)/0.1);
    padding: 0.5rem 1rem;
    border-radius: 2rem;
}

.chat-card {
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border) / 0.4);
  border-radius: 1.5rem;
  height: 70vh;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-bubble {
  max-width: 70%;
  padding: 1rem;
  border-radius: 1rem;
  position: relative;
}

.chat-bubble.user {
  align-self: flex-end;
  background: hsl(var(--primary) / 0.2);
  border-bottom-right-radius: 0.25rem;
  color: hsl(var(--foreground));
}

.chat-bubble.assistant {
  align-self: flex-start;
  background: hsl(var(--muted));
  border-bottom-left-radius: 0.25rem;
  color: hsl(var(--foreground));
}

.chat-meta {
  font-size: 0.7rem;
  margin-top: 0.5rem;
  opacity: 0.7;
  text-align: right;
}

.empty-chat {
    text-align: center;
    color: hsl(var(--muted-foreground));
    margin-top: 2rem;
}
</style>
