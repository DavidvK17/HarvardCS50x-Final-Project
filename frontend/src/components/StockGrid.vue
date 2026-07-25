<!--
This component, StockGrid.vue, manages the layout grid and network requests for my asset dashboard. 
Its primary purpose is to listen to index selections passed down by its parent, programmatically pull 
the relevant corporate equities list from my FastAPI backend using asynchronous operations, evaluate 
in-memory string search queries to filter down corporate results in real time, handle structural state 
feedback loops (Loading, Error, and Empty results), and loop over individual data objects to render 
reusable child components.
-->
<script setup lang="ts">
// Import lifecycle hooks and reactive primitives out of the Vue framework engine.
// 'watch' is brought in so I can observe state adjustments on input properties over time.
// 'onMounted' handles the exact moment this component injects into the browser DOM tree.
import { ref, onMounted, computed, watch } from 'vue'
import type { Asset } from '../types'
import StockCard from './StockCard.vue';

// Declare my input parameters using compile-time generic types. 
// This macro creates a read-only 'props' proxy object that maps variables passed down by App.vue.
const props = defineProps<{
    selectedIndex: string
    searchFilter: string
}>()

// Configure my custom component custom events. This provides a type-safe interface for 
// transmitting individual Asset data payloads backward up the component hierarchy.
const emit = defineEmits<{
    'select-asset': [asset: Asset]
}>()

// State Management Allocation:
// Initialize 'assets' as a reactive array using ref, explicitly binding it to accept 
// only my Asset data structures. It starts as an empty array placeholder: ([]).
const assets = ref<Asset[]>([])
const isLoading = ref<boolean>(true)
const errorMessage = ref<string | null>(null)

const fetchAssets = async () => {
    /*
    Executes an asynchronous, non-blocking HTTP fetch pipeline targeting the backend API.
    Handles loading states, networking flags, and populates the reactive assets storage box.
    */
    try {
        // Raise flags: set loading state to true and reset previous errors to clear out the viewport.
        isLoading.value = true
        errorMessage.value = null

        // Make an explicit network call utilizing a template literal string that pipes 
        // my index query argument directly to the backend URL parameter (?index=...).
        const response = await fetch(`http://localhost:8000/api/assets?index=${props.selectedIndex}`)

        // If the browser networking connection completes but returns a failure response code (e.g., 500 or 400),
        // raise a custom Error exception object to redirect program execution to the catch block.
        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`)
        }

        // Await the asynchronous transformation of the incoming raw network stream into clean JSON matrices.
        const data = await response.json()

        // Populate the inner value of my reactive array reference with the fetched assets collection.
        assets.value = data
    } catch (error) {
        // Intercept failure modes safely: isolate the error message string and update the error variable 
        // to present structural warning message updates directly inside the UI layout.
        errorMessage.value = error instanceof Error ? error.message : 'An unexpected network error occurred.'
        console.error('Failed fetching equities grid data:', error)
    } finally {
        // Complete the request loop lifecycle by turning down the loading flag, dropping spinner visuals.
        isLoading.value = false
    }
}

// Watch Pattern: Tell Vue to keep a constant look out on the 'selectedIndex' property. 
// If the user clicks a tab button on the homepage, changing the target index string, 
// this watcher fires, immediately re-executing fetchAssets() to load the fresh group.
watch(() => props.selectedIndex, () => {
    fetchAssets()
})

// Computed Text Filter Optimization:
// This computes a sub-selected, trimmed asset list without performing slow secondary API queries.
const filteredAssets = computed(() => {
    // Standardize user input data by stripping edge whitespace characters and forcing letters to lowercase.
    const query = props.searchFilter.toLowerCase().trim()
    // If the search string is clear or empty, pass through the unfiltered master assets array instantly.
    if (!query) return assets.value

    // Apply a high-performance array filter operation. It checks every asset, comparing the sanitized 
    // search query against both the corporate ticker and full company name fields.
    return assets.value.filter(asset => 
        asset.ticker.toLowerCase().includes(query) ||
        asset.name.toLowerCase().includes(query)
    )
})

// Lifecycle Registry: Execute my core API data collection mechanism exactly once as soon as 
// this grid component safely boots onto the screen canvas.
onMounted(() => fetchAssets())
</script>

<template>
    <div class="stock-grid">
        <!-- State 1: Loading Feedback Shell -->
         <!-- 
           Vue Logic: Conditional Loading State Block.
           If 'isLoading' stands true, mount this markup node instantly, displaying my global 
           shared spinner class and feedback message text.
         -->
         <div v-if="isLoading" class="stock-grid__status">
            <div class="stock-grid__spinner"></div>
            <p>Loading portfolio assets from local database...</p>
         </div>

         <!-- State 2: Exception/Error aLert Board-->
          <!-- 
           Vue Logic: 'v-else-if' handles alternative branching conditions. 
           If the loading stage passes but a network failure string populates my state, mount 
           this error block container. The button includes a click listener to trigger a manual retry.
         -->
          <div v-else-if="errorMessage" class="stock-grid__status stock-grid__status--error">
            <p>⚠️ Connection Failure: {{ errorMessage }}</p>
            <button class="stock-grid__retry-btn" @click="fetchAssets">
                Retry Network Request
            </button>
          </div>

          <!-- State 3: The Primary Responsive Grid View -->
           <!-- 
            Vue Logic: Main Layout Branching Core.
            If the application successfully breaks out of both loading and error bounds, render this block.
          -->
           <div v-else>
            <!-- 
              Vue Logic: Check if my internal computed list calculation resolves to 0 entries. 
              If the search query yields no matches, present explicit feedback inside the dashboard.
            -->
            <div v-if="filteredAssets.length === 0" class="stock-grid__empty-search">
                <p>No corporate entities found matching "{{ props.searchFilter }}".</p>
            </div>
            <!-- 
              Vue Logic: Primary Data Render Node.
              If matching elements populate my computed list, initialize my multi-column CSS grid engine.
            -->
            <div v-else class="stock-grid__content">
                <!-- 
                  Vue Logic: The 'v-for' directive handles list operations by looping dynamically.
                  - ':key="asset.id"' assigns a strict, unique identifier tracking index value to each node. 
                    This is a critical performance engine that allows Vue to target adjustments to individual 
                    elements inside the virtual DOM instead of destroying the entire grid array on updates.
                  - ':asset="asset"' feeds the looping asset object instance forward down into the child props interface.
                  - '@select' intercept emissions from the child card, instantly redirecting that signal to my 
                    parent app layer using the syntax emit('select-asset', asset).
                -->
                <StockCard
                    v-for="asset in filteredAssets"
                    :key="asset.id"
                    :asset="asset"
                    @select="emit('select-asset', asset)"
                />
          </div>
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

    &__empty-search {
        text-align: center;
        padding: calc(var(--spacing-base) * 8);
        background-color: var(--c-bg-elevated);
        border: 1px solid var(--c-bg-elevated);
        border-radius: 8px;
        color: var(--c-text-muted);
        font-size: 0.95rem;
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