<!--
This file, App.vue, serves as the orchestrator and root layout engine for my user interface. 
Its primary purpose is to manage the top-level state of the application, dynamically routing the view 
between a comprehensive, filterable multi-company dashboard (the homepage grid) and a granular, asynchronous 
single-asset data visualization dashboard (the chart view). By centralizing states like the currently active 
market index, user search queries, and the selected corporate entity, this file establishes a predictable 
unidirectional data flow—passing down reactive configurations as properties to sub-components and listening 
for interactive data emissions to cleanly update my interface in real time.
-->

<script setup lang="ts">
// Import the core reactivity methods from the Vue core engine.
// 'ref' allows me to declare raw values as reactive, mutable pointer references.
// 'computed' lets me derive read-only caching variables that automatically calculate 
// new values only when their underlying reactive dependencies change.
import { ref, computed } from 'vue';

// Import my custom TypeScript interface definitions to enforce compile-time type safety 
// when passing data objects across my component boundaries.
import type { Asset } from './types'

// Import my child presentation components. App.vue acts as the parent container 
// that mounts and destroys these modules based on the application's runtime state.
import StockGrid from './components/StockGrid.vue';
import ChartView from './components/ChartView.vue'

// Instantiate a reactive reference to track which company the user wants to analyze. 
// It is explicitly typed to contain either a valid Asset object structure or 'null'. 
// Initializing it as 'null' means the user starts by default on the homepage dashboard view.
const selectedAsset = ref<Asset | null>(null)

// Instantiate a reactive string reference to capture the user's keystrokes in the search input field.
const searchQuery = ref<string>('')

// Instantiate a reactive string tracking which market index is currently active. 
// I initialize this to 'SP500', matching one of the indices supported by my FastAPI backend.
const currentIndex = ref<string>('SP500')

// Define a caching computed property to dynamically compute the user-facing header text.
// If 'currentIndex' alters its state, this computed block detects the change, evaluates 
// the matching conditional branch, and pushes the new string down to my HTML layout.
const indexTitle = computed(() => {
  if (currentIndex.value === 'SP500') return 'S&P 500 Index'
  if (currentIndex.value === 'NASDAQ100') return 'Nasdaq-100'
  if (currentIndex.value === 'DOW30') return 'Dow Jones Industrial Average'
  return 'Portfolio Equities'
})

// Define a callback function to handle asset selection. When a child component emits 
// notice that a widget was clicked, this function captures that specific Asset data package 
// and assigns it to my 'selectedAsset' reference, instantly updating the app view layout.
const handleSelectedAsset = (asset: Asset) => {
  selectedAsset.value = asset
}

// Define a state restoration callback function. This function resets my tracking hooks 
// back to baseline values, clearing active search fields and setting the selected company 
// pointer back to 'null' to smoothly transition the layout back to the homepage grid view.
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
            <!--
              Vue Logic: '@click' is syntax representing an event listener (v-on:click). 
              When a user clicks this heading element, it triggers the 'handleBacktoHome' 
              JavaScript method, acting as an intuitive navigation shortcut.
            -->
            <h1 class="portfolio-app__brand" @click="handleBacktoHome">
              Homepage <span class="portfolio-app__brand-pill">SEC Portal</span>
            </h1>

            <!--
              Vue Logic: 'v-if' is a powerful structural directive. If 'selectedAsset' evaluates 
              to a truthy value (meaning an asset is actively being looked at), Vue injects this button 
              element physically into the DOM. If 'null', it is completely stripped from the document.
            -->
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
         <!--
           Vue Logic: 'v-if="!selectedAsset"' means if NO asset has been clicked, display the 
           homepage search and filtering grid dashboard layout.
         -->
         <section v-if="!selectedAsset" class="portfolio-app__view-container">
          <div class="portfolio-app__view-header">
            <!--
              Vue Logic: '{{ indexTitle }}' is text interpolation syntax. It evaluates the string 
              returned by my caching computed property and injects it dynamically into the text node.
            -->
            <h2>{{ indexTitle }} Equities</h2>
            <p>Select a company widget below to analyze its historical fundamental trends.</p>

            <!-- Dynamic Interactive Switch Tags Block -->
             <div class="portfolio-app__index-tabs">
              <!--
                Vue Logic: ':class' (v-bind:class) allows dynamic CSS class evaluation. 
                It injects the modification class 'portfolio-app__tab-btn--active' if and only if 
                the conditional expression inside evaluates to true (currentIndex === 'SP500'). 
                The click event listener updates my underlying reactive state on the fly.
              -->
              <button
                class="portfolio-app__tab-btn"
                :class="{ 'portfolio-app__tab-btn--active': currentIndex === 'SP500'}"
                @click="currentIndex = 'SP500'"
              >S&P 500</button>

              <button
                class="portfolio-app__tab-btn"
                :class="{ 'portfolio-app__tab-btn--active': currentIndex === 'NASDAQ100'}"
                @click="currentIndex = 'NASDAQ100'"
              >Nasdaq-100</button>

              <button
                class="portfolio-app__tab-btn"
                :class="{ 'portfolio-app__tab-btn--active': currentIndex === 'DOW30'}"
                @click="currentIndex = 'DOW30'"
              >Dow Jones 30</button>
             </div>

            <!-- Search Filter Container-->
            <div class="portfolio-app__search-container">
              <!--
                Vue Logic: 'v-model' establishes a seamless two-way data binding pattern. 
                When a user types inside this input box, the 'searchQuery' variable updates instantly 
                in my script block. Conversely, if my script alters 'searchQuery', the input box text 
                refreshes immediately to reflect that value.
              -->
              <input
              v-model="searchQuery"
              type="search"
              placeholder="🔍 Search equities by ticker symbol or company name..."
              class="portfolio-app__search-input"
              />
            </div>
          </div> 

          <!--
             Vue Logic: Here I instantiate my custom '<StockGrid>' component. 
             - ':selectedIndex' and ':search-filter' bind and pass down my reactive parent states 
               as properties ('props') into the child component.
             - '@select-asset' is a custom event listener. When the child component decides to fire 
               an emission named 'select-asset', this parent captures that signal along with its 
               accompanying data payload and passes it straight to 'handleSelectedAsset'.
           -->
           <StockGrid 
            :selectedIndex="currentIndex"
            :search-filter="searchQuery" 
            @select-asset="handleSelectedAsset"/>
         </section>

         <!-- VIEW 2: Asynchronous 4-Chart Detail View-->
          <!--
           Vue Logic: 'v-else' acts as a logical fallback pairing with the 'v-if' directly above it. 
           If 'selectedAsset' is truthy, this alternate view container is mounted instead, rendering 
           the multi-chart analytics breakdown.
         -->
          <section v-else class="portfolio-app__view-container">
            <div class="portfolio-app__company-banner">
              <div class="portfolio-app__meta-row">
                <!-- Interpolate the raw properties nested directly inside my asset state object -->
                <span class="portfolio-app__ticker-badge">{{ selectedAsset.ticker }}</span>
                <span class="portfolio-app__cik-info">CIK: {{ selectedAsset.cik }}</span>
              </div>
              <h2>{{ selectedAsset.name }}</h2>
            </div>

            <!--
              Vue Logic: Instantiate the custom '<ChartView>' component, binding and passing down 
              the database-assigned auto-incrementing tracking ID of the active asset as a prop.
            -->
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
    padding: calc(var(--spacing-base) * 1) calc(var(--spacing-base) * 2);
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

  &__index-tabs {
    display: flex;
    gap: calc(var(--spacing-base) * 2);
    margin-bottom: calc(var(--spacing-base) * 3);
  }

  &__tab-btn {
    background-color: var(--c-bg-surface);
    color: var(--c-text-muted);
    border: 1px solid var(--c-bg-elevated);
    padding: calc(var(--spacing-base) * 1.5) calc(var(--spacing-base) * 3);
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      color: var(--c-text-main);
      border-color: var(--c-text-muted);
    }

    &--active {
      background-color: rgba(56, 189, 248, 0.1);
      color: var(--c-brand-primary);
      border-color: var(--c-brand-primary);
    }
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