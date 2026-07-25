/**
 * This file, main.ts, serves as the absolute entry point and initialization nexus 
 * for my single-page frontend application. It handles the structural sequence of importing 
 * the Vue core engine, loading my global design tokens, loading the root component, and 
 * anchoring the virtual application layout onto the browser DOM tree.
 */

// Import the factory initialization function directly out of the core Vue reactive engine.
import { createApp } from 'vue'
// Import my master stylesheet layout sheet. By declaring it here at the entry point, 
// Vite processes and compiles my custom variables, resets, responsive grid rules, 
import './styles/main.scss'

// Import the root App component shell which acts as the layout scaffolding for my application.
import App from './App.vue'

/**
 * Application Bootstrapping Sequence:
 * 1. `createApp(App)` instantiates a fresh Vue application instance using the root App component as the base.
 * 2. `.mount('#app')` instructs the Vue engine to search my public index.html file for a raw HTML target node 
 *    bearing the ID selector 'app'. It then takes full control of that container, swapping out flat HTML for 
 *    my fully compiled, dynamic Single Page Application (SPA) DOM tree.
 */
createApp(App).mount('#app')
