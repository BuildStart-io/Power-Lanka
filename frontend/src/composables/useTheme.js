import { ref, watchEffect } from 'vue'

const isDark = ref(localStorage.getItem('theme') === 'dark')

export function useTheme() {
    const toggleTheme = () => {
        isDark.value = !isDark.value
    }

    const initTheme = () => {
        // Only set initial state, watchEffect handles the class application
    }

    watchEffect(() => {
        if (isDark.value) {
            document.documentElement.classList.add('dark')
            localStorage.setItem('theme', 'dark')
        } else {
            document.documentElement.classList.remove('dark')
            localStorage.setItem('theme', 'light')
        }
    })

    return {
        isDark,
        toggleTheme,
        initTheme
    }
}
