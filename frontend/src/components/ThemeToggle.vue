<template>
  <button @click="toggleTheme" class="theme-toggle glass" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
    <span class="theme-icon">{{ isDark ? '🌞' : '🌙' }}</span>
  </button>
</template>

<script>
import { useTheme } from '../composables/useTheme'

export default {
  name: 'ThemeToggle',
  setup() {
    const { isDark, toggleTheme } = useTheme()
    return {
      isDark,
      toggleTheme
    }
  }
}
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: calc(var(--radius) * 0.5);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  color: hsl(var(--foreground));
}

.theme-toggle:hover {
  background: hsl(var(--muted) / 0.1);
  color: hsl(var(--primary));
  transform: translateY(-1px);
}

.theme-icon {
  font-size: 1.25rem;
}
</style>
