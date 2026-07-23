<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Asset } from '../types'
import StockCard from './StockCard.vue';

const emit = defineEmits<{
    'select-asset': [asset: Asset]
}>()

// ref: reactive wrapper box, Asset[]: only thing allowd, ([]) we start wih empty arr
const assets = ref<Asset[]>([])
const isLoading = ref<boolean>(true)
const errorMessage = ref<string | null>(null)

const fetchAssets = async () => {
    try {
        isLoading.value = true
        errorMessage.value = null

        const response = await fetch('http://localhost:8000/api/assets')

        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`)
        }

        const data = await response.json()
        assets.value = data
    } catch (error) {
        errorMessage.value = error instanceof Error ? error.message : 'An unexpected network error occurred.'
        console.error('Failed fetching equities grid data:', error)
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    fetchAssets()
})
</script>

<template>
    <div class="stock-grid">
        <!-- State 1: Loading Feedback Shell -->
         <div v-if="isLoading" class="stock-grid__status">
            <div class="stock-grid__spinner"></div>
            <p>Loading portfolio assets from local database...</p>
         </div>
         <!-- State 2: Expception/Error aLert Board-->
          <div v-else-if="errorMessage" class="stock-grid__status stock-grid__status--error">
            <p>⚠️ Connection Failure: {{ errorMessage }}</p>
            <button class="stock-grid__retry-btn" @click="fetchAssets">
                Retry Network Request
            </button>
          </div>
          <!-- State 3: The Primary Responsive Grid View -->
          <div v-else class="stock-grid__content">
            <StockCard
            v-for="asset in assets"
            :key="asset.id"
            :asset="asset"
            @select="emit('select-asset', asset)"
            />
          </div>
    </div>
</template>

<style lang="scss" scoped>
.stock-grid {
    width: 100%;

    &__content {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: calc(var(--spacing-base) * 4);
    }

    &__status {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: calc(var(--spacing-base) * 10) 0;
        color: var(--c-text-muted);
        font-size: 0.95rem;

        &--error {
            color: #ef4444;
            background-color: rgba(239, 68, 68, 0.05);
            border: 1px dashed rgba(239, 68, 68, 0.2);
            border-radius: 8px;
            padding: calc(var(--spacing-base) * 6);
        }
    }

    &__spinner {
        width: 32px;
        height: 32px;
        border: 3px solid var(--c-bg-elevated);
        border-top-color: var(--c-brand-primary);
        border-radius: 50%;
        margin-bottom: calc(var(--spacing-base) * 3);
        animation: grid-spin 0.8s linear infinite;
    }

    &__retry-btn {
        margin-top: calc(var(--spacing-base) * 3);
        background-color: #ef4444;
        color: #fff;
        border: none;
        padding: calc(var(--spacing-base) * 1.5) calc(var(--spacing-base) * 3);
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        cursor: pointer;
        transition: background-color 0.2s ease;

        &:hover {
            background-color: #dc2626;
        }
    }
}

@keyframes grid-spin {
    to {
        transform: rotate(360deg);
    }
}
</style>