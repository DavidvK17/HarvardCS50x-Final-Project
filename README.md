# Business Analytics: A Full-Stack SEC-Driven Corporate Fundamentals Dashboard
#### Video Demo:  https://www.youtube.com/watch?v=hjWxJ1yFjts
#### Description:

## Project Motivation & Core Concept
Business Analytics is a full-stack financial analytics web application designed to automate the highly tedious process of tracking, calculating, and visualizing corporate financial fundamentals. For several years, I have manually maintained an expanding Google Workspace spreadsheet to log key annual financial metrics—specifically revenue, operating income, operating margins, and year-over-year (YoY) revenue growth rates—for the equities within my personal investment portfolio and watchlist. Scouring through complex SEC annual reports (Form 10-K filings) and manually porting these figures into custom charts became a massive operational bottleneck. I even resorted to paying out-of-pocket for commercial data visualization platforms just to view clean multi-year historical trajectories.

Thanks to the foundational software engineering, database design, and web architecture skills I acquired throughout my journey in Harvard's CS50x, I realized I possessed the tools to build a custom, automated alternative. I designed this application to aggregate public market index listings from scratch, cross-reference them with federal identifiers, pull their complete financial histories directly from the U.S. Securities and Exchange Commission (SEC) EDGAR API, calculate growth vectors, and visualize the findings on an analytical frontend interface. Building Business Analytics allowed me to deeply practice full-stack integration, master relational junction tables in SQL, write highly structured type-safe frontend code, and deploy automated backend pipelines that respect federal scraping boundaries.

---

## Getting Started & Execution

### Server
Inside the `backend` directory, run: uvicorn main:app --host 0.0.0.0 --port 5000 --reload, make sure to change port 5000 visibility to public thereafter
Inside the `frontend` directory, run: npm run dev

---

## High-Level System Architecture
The software is split into a decoupled three-tier system, ensuring a clean separation of concerns:
*   **Database & Ingestion Layer (Python, Pandas, SQLite):** I utilized `pandas` to scrape live index constituent tables from Wikipedia, and used native `requests` to seed a localized SQLite database (`portfolio.db`).
*   **SEC Extraction Pipeline (Python, SEC EDGAR API):** A heavy-duty data pipeline (`fetch_sec.py`) pulls down raw XBRL JSON payloads directly from the federal SEC database using standard HTTP protocols, strips out reporting anomalies, handles restated filings, and calculates core metrics.
*   **Backend REST API (Python, FastAPI, Uvicorn):** I implemented an asynchronous server using the FastAPI framework to handle incoming frontend queries, execute optimized SQL lookups, and dispatch clean JSON payloads downstream.
*   **Analytical UI Canvas (Vue 3, TypeScript, SCSS, Chart.js):** I constructed a highly responsive Single Page Application (SPA) leveraging the Vue 3 Composition API combined with TypeScript to guarantee static type safety. The interface handles state propagation, dynamic client-side filtering, and mounts dynamic Chart.js configurations to visually map financial trends.

---

## Detailed Directory and File Breakdown

### The Data & Backend Layer
*   **`backend/init_db.py`**
    This script initializes my localized relational database structure and provides the baseline asset seeding pipeline. It opens a transaction handle to `portfolio.db` and establishes the schemas for three tables: `assets`, `fundamentals`, and `asset_index_mapping` (a junction table designed to resolve the many-to-many relationship where a single stock like Apple exists in both the S&P 500 and Nasdaq-100 simultaneously). I leveraged the `pandas` library (`pd.read_html`) in this file to scrape live index component tables from Wikipedia. The script sanitizes formatting anomalies (like share-class dot notations), resolves composite descriptions via string splits, harvests the official master ticker-to-CIK directory from the SEC server via `requests`, and maps the components cleanly to disk using optimized batch SQL `executemany` statements.
*   **`backend/fetch_sec.py`**
    The heavy-duty financial data extraction engine of my application. This script systematically loops through every asset stored in my database, pads their unique Central Index Keys (CIKs) out to the strict SEC-mandated 10-digit format, and queries the live SEC EDGAR API company facts repository. It relies on deep native JSON dictionary traversal to navigate the dense, multi-tiered US-GAAP taxonomy tree. It iterates through an array of alternative filing tags to capture revenue and operating income, utilizes a datetime duration filter to isolate full-year 10-K filings from intermediate quarterly 10-Q noise, isolates data revisions by checking filing dates, computes operating margins and year-over-year revenue growth rates, and saves the final normalized arrays back to the SQL `fundamentals` table.
*   **`backend/main.py`**
    The central routing controller for my backend API. It initializes the FastAPI application instance, configures the cross-origin resource sharing (CORS) middleware headers to authorize secure browser communication from my frontend dev environment, and exposes two vital asynchronous endpoints: `/api/assets` (to serve component arrays matching a selected index) and `/api/fundamentals/{asset_id}` (to serve complete analytics series to my visualization layout).

### The UI & Component Layer
*   **`frontend/src/main.ts`**
    The central bootstrapper and script entry point for the frontend ecosystem. It handles importing the core application factory from Vue, registers my global master stylesheet layout (`main.scss`), compiles the base layout wrapper template (`App.vue`), and anchors the virtual application tree onto the native browser DOM index container `#app`.
*   **`frontend/src/App.vue`**
    The master root component shell of the user interface. It establishes the global structural layout frame and acts as the central state synchronization hub for the client application. It manages reactive properties tracking both the currently selected market index (S&P 500, Nasdaq-100, Dow 30) and the specific target asset ID selected for analytical evaluation. It coordinates dashboard behavior by feeding these reactive values down as state bindings to child layouts (`StockGrid.vue` and `ChartView.vue`).
*   **`frontend/src/types/index.ts`**
    My dedicated data modeling layer. It explicitly models the shape of data flowing over the network by exporting two key interfaces: `Asset` and `AssetFundamentals`. By defining highly volatile corporate data points (like `revenue` and `revenue_growth`) as `number | null` structures, it forces all components to explicitly handle empty or missing records, protecting the application from runtime browser crashes.
*   **`frontend/src/styles/main.scss`**
    The centralized layout system written in Sass (SCSS). Following structural software engineering best practices, I refactored repetitive style declarations out of local components and into this master manifest. It houses my application design tokens (slate color grids, font hierarchies) and standardizes global visual assets.
*   **`frontend/src/components/StockGrid.vue`**
    The primary control panel template for my dashboard. It watches for active index selection updates passed down from the parent shell, triggers non-blocking async network operations to update lists, handles visual states for loading flags or connection drops, and computes highly optimized local string search queries against tickers and names to filter the UI locally without re-hitting the server.
*   **`frontend/src/components/StockCard.vue`**
    A presentation-focused visual widget ("dumb component") designed to map clean property payloads into user-facing layout nodes. It renders individual asset tickers, prints full corporate designations equipped with protective HTML hover title indicators to handle long text truncations, and registers pointer click-event emitters to notify the master grid exactly which equity is chosen for analysis.
*   **`frontend/src/components/ChartView.vue`**
    The analytical focal point of Business Analytics. It imports vital tracking scales, tooltips, and line nodes from the core Chart.js engine and registers their capabilities using `vue-chartjs` module wrappers. Upon catching an updated `assetId` from the parent view, it pulls the historical database metrics, processes large absolute currencies down into readable "Billions ($B)" fractions to optimize axis spacing, and updates four unique dynamic visual datasets tracking volumes, margins, and financial trajectories.

---

## Design Choices & Engineering Challenges

### 1. The Wikipedia Web Ingestion Challenge vs. The Pandas Breakthrough
My first major engineering hurdle involved harvesting the initial component lists for the major market indices within `init_db.py`. Initially, I attempted to build a custom scraper using raw string filtering and regular expressions (Regex) to slice the underlying HTML markup. While this strategy worked on highly uniform code layouts, it failed completely when introduced to the Nasdaq-100 index page, which featured irregular column nesting, erratic row spans, and custom inline style overrides. My parser broke repeatedly, leading to corrupted data payloads.

This obstacle led to an eye-opening architectural breakthrough: instead of trying to patch an unmaintainable regex routine, I integrated the `pandas` library. Passing web URLs directly into `pd.read_html()` allowed me to instantly isolate and extract clean, structured dataframes from the underlying HTML tables. By deploying `pandas` utility methods, I easily sanitized column metrics, filtered missing rows, and resolved composite descriptions uniformly, drastically reducing codebase complexity and building a highly robust database seeding engine.

### 2. Navigating the Multi-Tiered SEC XBRL JSON Tree & GAAP Taxonomy
When writing the parsing engine inside `fetch_sec.py`, I discovered that public corporations disclose their financial facts under radically varying accounting taxonomies depending on their industry sector. For instance, a technology firm might report its top-line earnings under the tag `Revenues`, whereas an online retail platform might call it `SalesRevenueNet`, and a financial group might list it under `RevenuesNetOfInterestExpense`.

To solve this inconsistency without crashing my network loops, I implemented a prioritized fallback array of alternative U.S. GAAP taxonomy strings for both revenue and operating income, looping through them sequentially until a valid dataset was successfully matched.

Additionally, corporations frequently amend past filings years after submission. To prevent older data points from colliding with or corrupting newer restatements, I designed an override system that checks the raw SEC timestamp (`filed_date`) for each entry, ensuring that updated or restated financial records cleanly overwrite legacy rows in my database.

### 3. Proactively Mitigating Strict Federal API Rate Limits
When designing the data extraction engine inside `fetch_sec.py`, a primary architectural consideration was ensuring strict compliance with federal infrastructure access boundaries. A thorough review of the official SEC EDGAR API developer documentation revealed a stringent network security policy: automated scripts are strictly capped at a maximum velocity of 10 requests per second, and anonymous, improperly declared, or high-velocity IP addresses face immediate automated firewall bans (`HTTP 403 Forbidden`).

To ensure the application operated safely within these compliance guidelines from day one, I engineered defensive rate-limiting directly into the pipeline's execution block. Along with structuring a custom, compliant User-Agent header, I embedded an explicit `time.sleep(0.15)` delay at the conclusion of every individual company processing loop. This intentionally throttled the extraction engine down to a highly stable rate of roughly 6.6 requests per second, ensuring uninterrupted, safe data ingestion without risking server-side blacklisting or infrastructure strain.

### 4. Defining the Scope of the Minimum Viable Product (MVP)
A major design challenge was fighting feature creep. As an active investor, I wanted to instantly implement advanced features, such as multi-asset comparison lines, automatic portfolio trackers, authentication guard lines, international indices, and live cloud deployment setups on platforms like AWS, GCP, or Azure.

However, drawing on software architecture principles, I chose to ruthlessly prioritize the absolute core features needed for a stable Minimum Viable Product. I deliberately deferred secondary features to subsequent iteration phases, allowing me to focus entirely on building a highly reliable data pipeline, writing clean TypeScript definitions, and maintaining structural state management across the full stack.

---

## Future Roadmap Evolution
Business Analytics is engineered to grow far beyond this academic submission. My immediate next step is to introduce a secure user authentication layer using JSON Web Tokens (JWT) to support personalized watchlists and user portfolio tracking. I also plan to implement a multi-asset comparison view so users can overlay the performance lines of competing companies on a single chart canvas. Finally, I intend to containerize the entire multi-tier system using Docker to make it ready for production deployment on cloud infrastructure.
