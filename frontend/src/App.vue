<script setup lang="ts">
import { ref } from 'vue';
import type { Asset } from './types'
import StockGrid from './components/StockGrid.vue';
import ChartView from './components/ChartView.vue';

const selectedAsset = ref<Asset | null>(null)
const searchQuery = ref<string>('')

const handleSelectedAsset = (asset: Asset) => {
  selectedAsset.value = asset
}
const handleBacktoHome = () => {
  selectedAsset.value = null
  searchQuery.value = ''
}
</script>

<template>
    <div class="portfolio-app">
      <!-- Header Block -->
       <header class="portfolio-app__header">
          <div class="portfolio-app__header-inner">
            <h1 class="portfolio-app__brand" @click="handleBacktoHome">
              Homepage <span class="portfolio-app__brand-pill">SEC Portal</span>
            </h1>

            <button
              v-if="selectedAsset"
              class="portfolio-app__back-button"
              @click="handleBacktoHome"
            >
              ← Back to Homepage
            </button>
          </div>
       </header>

       <main class="portfolio-app__main">
        <!-- View 1: The Homepage 8-Widget Grid-->
         <section v-if="!selectedAsset" class="portfolio-app__view-container">
          <div class="portfolio-app__view-header">
            <h2>Portfolio Equities</h2>
            <p>Select a company widget below to analyze its 5-year SEC fundamental trends.</p>

            <div class="portfolio-app__search-container">
              <input
              v-model="searchQuery"
              type="text"
              placeholder="🔍 Search equities by ticker symbol or company name..."
              class="portfolio-app__search-input"
              />
            </div>
          </div> 

           <StockGrid :search-filter="searchQuery" @select-asset="handleSelectedAsset"/>
         </section>

         <!-- VIEW 2: Asynchronous 4-Chart Detail View-->
          <section v-else class="portfolio-app__view-container">
            <div class="portfolio-app__company-banner">
              <div class="portfolio-app__meta-row">
                <span class="portfolio-app__ticker-badge">{{ selectedAsset.ticker }}</span>
                <span class="portfolio-app__cik-info">CIK: {{ selectedAsset.cik }}</span>
              </div>
              <h2>{{ selectedAsset.name }}</h2>
            </div>

            <ChartView :asset-id="selectedAsset.id"/>
          </section>
       </main>

    </div>
</template>

<style lang="scss" scoped>
.portfolio-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--c-bg-main);
  color: var(--c-text-main);

  &__header {
    background-color: var(--c-bg-surface);
    border-bottom: 1px solid var(--c-bg-elevated);
    padding: calc(var(--spacing-base) * 2) calc(var(--spacing-base) * 4);

    &-inner {
      max-width: 1300px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  &__brand {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    cursor: pointer;
    user-select: none;

    &-pill {
      font-size: 0.75rem;
      background-color: rgba(56, 189, 248, 0.1);
      color: var(--c-brand-primary);
      padding: calc(var(--spacing-base) * 0.3) calc(var(--spacing-base) * 1);
      border-radius: 4px;
      margin-left: var(--spacing-base);
    }
  }

  &__back-button {
    background-color: var(--c-bg-elevated);
    color: var(--c-text-main);
    border: 1px solid var(--c-bg-surface);
    padding: calc(var(--spacing-base) * 1) calc((var(--spacing-base) * 2));
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background-color: var(--c-brand-primary);
      color: var(--c-bg-main);
    }
  }

  &__main {
    flex: 1;
    width: 100%;
    max-width: 1300px;
    margin: 0 auto;
    padding: calc(var(--spacing-base) * 4);
  }

  &__view-header {
    h2 {
      margin-bottom: calc(var(--spacing-base) * 0.5);
      font-size: 1.5rem;
    }

    p {
      margin-bottom: calc(var(--spacing-base) * 4);
      color: var(--c-text-muted);
    }
  }

  &__search-container {
    margin-bottom: calc(var(--spacing-base) * 4);
    max-width: 500px;
  }

  &__search-input {
    width: 100%;
    padding: calc(var(--spacing-base) * 2) calc(var(--spacing-base) * 3);
    background-color: var(--c-bg-surface);
    border: 1px solid var(--c-bg-elevated);
    border-radius: 8px;
    color: var(--c-text-main);
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s ease;

      &:focus {
        border-color: var(--c-brand-primary);
      }
  }

  &__company-banner {
    background: linear-gradient(135deg, var(--c-bg-surface) 0%, var(--c-bg-elevated) 100%);
    border: 1px solid var(--c-bg-elevated);
    border-radius: 8px;
    padding: calc(var(--spacing-base) * 3);
    margin-bottom: calc(var(--spacing-base) * 4);

    h2 {
      margin-top: var(--spacing-base);
      font-size: 1.75rem;
    }
  }

  &__meta-row {
    display: flex;
    align-items: center;
    gap: calc(var(--spacing-base) * 2);
  }

  &__ticker-badge {
    background-color: var(--c-brand-primary);
    color: var(--c-bg-main);
    font-weight: 700;
    padding: calc(var(--spacing-base) * 0.4) calc(var(--spacing-base) * 1);
    border-radius: 4px;
    font-size: 0.85rem;
  }

  &__cik-info {
    color: var(--c-text-muted);
    font-family: monospace;
    font-size: 0.85rem;
  }
}
</style>