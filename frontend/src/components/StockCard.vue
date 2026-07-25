<!--
This component, StockCard.vue, is a highly lightweight presentational component ("dumb component"). 
Its singular responsibility is to accept a decoupled, isolated Asset metadata record package from its 
parent layout container, format its inner string data parameters safely inside a clean corporate widget UI template, 
and capture direct pointing click inputs to notify the master application frame exactly which stock has been chosen.
-->
<script setup lang="ts">
import type { Asset } from '../types'

// Setup macro mapping the structural Asset object constraints required to build this visualization container.
defineProps<{
    asset: Asset
}>()

// Setup macro configuring my programmatic click dispatch emitter logic hook.
const emit = defineEmits<{
    'select': [asset: Asset]
}>()
</script>

<template>
    <!-- 
      Vue Logic: Add a programmatic click event listener directly onto the base root HTML card node wrapper.
      The moment a user selects this item anywhere inside its bounds, the inline method executes, firing 
      the custom event 'select' and passing the active asset variable dictionary up the call stack to the parent grid.
    -->
    <div class="stock-card" @click="emit('select', asset)">
        <div class="stock-card__header">
            <!-- Interpolate standard string tokens using mustache evaluation blocks -->
            <span class="stock-card__ticker">{{ asset.ticker }}</span>
            <span class="stock-card__id-badge">{{ asset.id }}</span>
        </div>

        <!-- 
          Vue Logic: ':title="asset.name"' leverages attribute binding syntax. 
          This binds the native browser tool-tip hover attribute dynamically to the asset's full name, 
          ensuring that if long enterprise corporate text strings overflow or truncate with ellipses inside 
          my layout, a user can still read the full title simply by hovering their mouse pointer over it.
        -->
        <h3 class="stock-card__name" :title="asset.name">
            {{ asset.name }}
        </h3>

        <div class="stock-card__footer">
            <span class="stock-card__cik">{{ asset.cik }}</span>
            <span class="stock-card__action-link">Analyze →</span>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.stock-card {
    background-color: var(--c-bg-surface);
    border: 1px solid var(--c-bg-elevated);
    border-radius: 8px;
    padding: calc(var(--spacing-base) * 2.5);
    cursor: pointer;
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.2s ease,
                box-shadow 0.2s ease;

    &:hover {
        border-color: var(--c-brand-primary);
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.08);
    }

    &:active {
        transform: translateY(0);
    }

    &__header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: calc(var(--spacing-base) * 2);
    }

    &__ticker {
        background-color: rgba(56, 189, 248, 0.1);
        color: var(--c-brand-primary);
        font-weight: 700;
        padding: calc(var(--spacing-base) * 0.4) calc(var(--spacing-base) * 1);
        border-radius: 4px;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    &__id-badge {
        color: var(--c-text-muted);
        font-size: 0.75rem;
    }

    &__name {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--c-text-main);
        margin: 0 0 calc(var(--spacing-base) * 3) 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    &__footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid rgba(148, 163, 184, 0.08);
        padding-top: calc(var(--spacing-base) * 1.5);
    }

    &__cik {
        color: var(--c-text-muted);
        font-family: monospace;
        font-size: 0.8rem;
    }

    &__action-link {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--c-brand-primary);
        opacity: 0.7;
        transition: opacity 0.2s ease;
    }

    &:hover &__action-link {
        opacity: 1;
    }
    
}
</style>