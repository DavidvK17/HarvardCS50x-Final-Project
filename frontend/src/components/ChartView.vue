<!--
This component, ChartView.vue, acts as the analytical core of my user interface. Its primary purpose 
is to accept a unique asset tracking key, execute asynchronous data fetches to collect raw fundamental numbers 
linked to that asset, map and normalize those raw entries into individual data series, and register 
third-party charting layers (Chart.js / vue-chartjs) to construct a clean, four-quadrant, responsive graphical 
dashboard tracking corporate performance.
-->

<script setup lang="ts">
// Import core architectural reactive variables and structural lifecycle hooks out of the Vue core engine.
import { ref, onMounted, watch, computed } from 'vue'
import type { AssetFundamentals } from '../types'

// Explicitly import and deconstruct the core underlying elements required by the Chart.js visualization engine.
// Registering these elements ensures my compiled software bundle includes only the exact calculation metrics, 
// scales, shapes, and tooltip items I use, keeping the app optimized and lightweight.
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement
} from 'chart.js'

// Import the specific component wrapper modules exposed by the vue-chartjs abstraction bridge.
import { Bar, Line } from 'vue-chartjs'

// Invoke my Chart.js configuration method to mount the imported charting structures directly into the library registry.
ChartJS.register(
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement
)

// Define my properties interface, requiring an incoming assetId identifier number from App.vue.
const props = defineProps<{
    assetId: number
}>()

// State Containers Architecture:
// Initialize an array structure to store rows of fundamental metrics fetched from my local SQLite storage.
const history = ref<AssetFundamentals[]>([])
const isLoading = ref<boolean>(true)
const errorMessage = ref<string | null>(null)

const fetchFundamentals = async () => {
    /*
    Asynchronously queries my FastAPI server to load the complete historical fundamental data package.
    */
    try {
        isLoading.value = true
        errorMessage.value = null

        // Dispatch the HTTP request tracking the specific corporate asset integer id parameter.
        const response = await fetch(`http://localhost:8000/api/fundamentals/${props.assetId}`)

        if (!response.ok) {
            // If the backend returns a 404 status, it means the table returned empty records for that specific company.
            if (response.status === 404) {
                throw new Error('No historical financial records found for this equity.')
            }
            throw new Error(`Server returned status code ${response.status}`)
        }

        const data = await response.json()
        // Save the chronologically ordered array data maps into my history reactive buffer.
        history.value = data
    } catch (error) {
        errorMessage.value = error instanceof Error ? error.message : 'An unexpected network error occurred.'
        console.error('Failed fetching core analytics metrics:', error)
    } finally {
        isLoading.value = false
    }
}

// Bootstrapping Strategy: Initialize the data connection instantly upon component load.
onMounted(() => fetchFundamentals())

// Watcher Pattern: If a user clicks a new stock widget while browsing inside the detail view, 
// the 'assetId' prop changes, causing this watcher to trigger an immediate background reload.
watch(() => props.assetId, () => fetchFundamentals())

// Design Configuration Configuration Object:
// Sets global UI options matching my custom style definitions (suppressing legends, overriding grid canvas 
// colors to match my slate colors, and setting font properties across the charts).
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false }
    },
    scales: {
        x: {
            grid: { display: false },
            ticks: { color: '#94a3b8', font: { family: 'system-ui'} }
        },
        y: {
            grid: { color: 'rgba(30, 38, 61, 0.4)' },
            ticks: { color: '#94a3b8', font: { family: 'system-ui'} }
        }
    }
}

// Computed Axis Labels Map: Uses high-performance JavaScript .map array operators to cleanly 
// pull the unique corporate 'fiscal_year' integers out of my data records, forming the shared X-axis labels array.
const chartLabels = computed(() => history.value.map(record => record.fiscal_year))

// Computed Datasets Maps:
// The follow four blocks transform raw data arrays into standardized JSON payloads required by Chart.js.
// Notice that for absolute corporate currencies (Revenue and Operating Income), I divide values by 1e9 (1 Billion) 
// to avoid overflowing the interface canvas with long integer values, scaling the axes cleanly down to Billions.
const revenueChartData = computed(() => ({
    labels: chartLabels.value,
    datasets: [{
        data: history.value.map(record => record.revenue ? record.revenue / 1e9 : 0),
        backgroundColor: '#38bdf8',
        borderRadius: 4
    }]
}))

const operatingIncomeChartData = computed(() => ({
    labels: chartLabels.value,
    datasets: [{
        data: history.value.map(record => record.operating_income ? record.operating_income / 1e9 : 0),
        backgroundColor: '#22c55e',
        borderRadius: 4
    }]
}))

const marginChartData = computed(() => ({
    labels: chartLabels.value,
    datasets: [{
        data: history.value.map(record => record.operating_margin),
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        borderWidth: 3,
        tension: 0.2,
        pointBackgroundColor: '#38bdf8'
    }]
}))

const growthChartData = computed(() => ({
    labels: chartLabels.value,
    datasets: [{
        data: history.value.map(record => record.revenue_growth),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 3,
        tension: 0.2,
        pointBackgroundColor: '#ef4444'
    }]
}))
</script>

<template>
    <div class="chart-view">
        <!-- State 1: Loading State Box -->
         <!-- Vue Logic: If loading states are active, hold chart rendering and inject my global spinner. -->
         <div v-if="isLoading" class="chart-view__status">
            <div class="chart-view__spinner"></div>
            <p>Parsing corporate SEC financial package data streams...</p>
         </div>

         <!-- State 2: Error Alert Frame-->
          <!-- Vue Logic: Capture and present standard pipeline structural exception warnings here. -->
         <div v-else-if="errorMessage" class="chart-view__status chart-view__status--error">
            <p>⚠️ Ingestion Error: {{ errorMessage }}</p>
         </div>

         <!-- State 3: The 4-Chart Visualization Matrix -->
          <!-- Vue Logic: The Primary Dashboard Grid Layer mounted once data loading settles cleanly. -->
         <div v-else class="chart-view__grid">

            <!-- Chart Card A: Top-line revenue metrics bar chart setup -->
             <div class="chart-view__card">
                <div class="chart-view__card-header">
                    <h4 class="chart-view__card-title">Annual Revenue</h4>
                    <span class="chart-view__unit-badge">USD Billions ($B)</span>
                </div>
                <div class="chart-view__canvas-container">
                    <!-- 
                      Vue Logic: Mount the custom `<Bar>` chart abstract class component. 
                      I use dynamic property binding syntax (`:data` and `:options`) to pass 
                      my computed data maps down into the library code.
                    -->
                    <Bar :data="revenueChartData" :options="chartOptions" />
                </div>
             </div>

             <!-- Chart Card B: Core Operational Earnings bar chart setup -->
             <div class="chart-view__card">
                <div class="chart-view__card-header">
                    <h4 class="chart-view__card-title">Operating Income</h4>
                    <span class="chart-view__unit-badge">USD Billions ($B)</span>
                </div>
                <div class="chart-view__canvas-container">
                    <Bar :data="operatingIncomeChartData" :options="chartOptions" />
                </div>
             </div>

            <!-- Chart Card C: Revenue Velocity Trajectory line chart setup -->
             <div class="chart-view__card">
                <div class="chart-view__card-header">
                    <h4 class="chart-view__card-title">Revenue Growth Yoy</h4>
                    <span class="chart-view__unit-badge chart-view__unit-badge--danger">Percentage (%)</span>
                </div>
                <div class="chart-view__canvas-container">
                    <!-- Vue Logic: Mount the `<Line>` chart component, passing my reactive line options. -->
                    <Line :data="growthChartData" :options="chartOptions" />
                </div>
             </div>

            <!-- Chart Card D: Operational Margins line chart setup -->
             <div class="chart-view__card">
                <div class="chart-view__card-header">
                    <h4 class="chart-view__card-title">Operating Margin</h4>
                    <span class="chart-view__unit-badge chart-view__unit-badge--success">Percentage (%)</span>
                </div>
                <div class="chart-view__canvas-container">
                    <Line :data="marginChartData" :options="chartOptions" />
                </div>
             </div>

         </div>
    </div>
</template>

<style lang="scss" scoped>
.chart-view {
    width: 100%;

    &__grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
        gap: calc((var(--spacing-base) * 4));
    }

    &__card {
        background-color: var(--c-bg-surface);
        border: 1px solid var(--c-bg-elevated);
        border-radius: 8px;
        padding: calc(var(--spacing-base) * 3);
        display: flex;
        flex-direction: column;
        gap: calc(var(--spacing-base) * 2);
    }

    &__card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    &__card-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--c-text-main);
    }

    &__unit-badge {
        font-size: 0.75rem;
        font-weight: 600;
        background-color: rgba(56, 189, 248, 0.08);
        color: var(--c-brand-primary);
        padding: calc(var(--spacing-base) * 0.4) calc(var(--spacing-base) * 1);
        border-radius: 4px;

        &--success {
            background-color: rgba(34, 197, 94, 0.08);
            color: var(--c-brand-success);
        }

        &--danger {
            background-color: rgba(239, 68, 68, 0.08);
            color: #ef4444;
        }
    }

    &__canvas-container {
        position: relative;
        height: 260px;
        width: 100%;
    }

    &__status {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: calc(var(--spacing-base) * 15) 0;
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
        animation: chart-spin 0.8s linear infinite;
    }

    @keyframes chart-spin {
        to {
            transform: rotate(360deg);
        }
    }

    @media (max-width: 550px) {
        &__grid {
            grid-template-columns: 1fr;
        }
        &__canvas-container {
            height: 220px;
        }
    }
}
</style>