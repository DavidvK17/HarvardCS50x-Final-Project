<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import type { AssetFundamentals } from '../types'
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
import { Bar, Line } from 'vue-chartjs'

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

const props = defineProps<{
    assetId: number
}>()

const history = ref<AssetFundamentals[]>([])
const isLoading = ref<boolean>(true)
const errorMessage = ref<string | null>(null)

const fetchFundamentals = async () => {
    try {
        isLoading.value = true
        errorMessage.value = null
        const response = await fetch(`http://localhost:8000/api/fundamentals/${props.assetId}`)

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('No historical financial records found for this equity.')
            }
            throw new Error(`Server returned status code ${response.status}`)
        }

        const data = await response.json()
        history.value = data
    } catch (error) {
        errorMessage.value = error instanceof Error ? error.message : 'An unexpected network error occurred.'
        console.error('Failed fetching core analytics metrics:', error)
    } finally {
        isLoading.value = false
    }
}

onMounted(() => fetchFundamentals())
watch(() => props.assetId, () => fetchFundamentals())

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

const chartLabels = computed(() => history.value.map(record => record.fiscal_year))

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
         <div v-if="isLoading" class="chart-view__status">
            <div class="chart-view__spinner"></div>
            <p>Parsing corporate SEC financial package data streams...</p>
         </div>

         <!-- State 2: Error Alert Frame-->
         <div v-else-if="errorMessage" class="chart-view__status chart-view__status--error">
            <p>⚠️ Ingestion Error: {{ errorMessage }}</p>
         </div>

         <!-- State 3: The 4-Chart Visualization Matrix -->
         <div v-else class="chart-view__grid">

            <!-- Chart A: Top-line Revenue (Bar) -->
             <div class="chart-view__card">
                <div class="chart-view__card-header">
                    <h4 class="chart-view__card-title">Annual Revenue</h4>
                    <span class="chart-view__unit-badge">USD Billions ($B)</span>
                </div>
                <div class="chart-view__canvas-container">
                    <Bar :data="revenueChartData" :options="chartOptions" />
                </div>
             </div>

             <!-- Chart B: Core Operational Earnings (Bar) -->
             <div class="chart-view__card">
                <div class="chart-view__card-header">
                    <h4 class="chart-view__card-title">Operating Income</h4>
                    <span class="chart-view__unit-badge">USD Billions ($B)</span>
                </div>
                <div class="chart-view__canvas-container">
                    <Bar :data="operatingIncomeChartData" :options="chartOptions" />
                </div>
             </div>

            <!-- Chart C: Revenue Velocity Trajectory (Line) -->
             <div class="chart-view__card">
                <div class="chart-view__card-header">
                    <h4 class="chart-view__card-title">Revenue Growth Yoy</h4>
                    <span class="chart-view__unit-badge chart-view__unit-badge--danger">Percentage (%)</span>
                </div>
                <div class="chart-view__canvas-container">
                    <Line :data="growthChartData" :options="chartOptions" />
                </div>
             </div>

             <!-- Chart D: Operational Profit Margins (Line) -->
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