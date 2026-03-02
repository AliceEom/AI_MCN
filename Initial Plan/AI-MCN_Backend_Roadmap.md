# AI-MCN: Backend Execution Roadmap

## Phase 1: Data Acquisition & Master Processing

### Step 1 & 2: Distributed YouTube Scraping

- **Input:** Raw industry keywords (e.g., "K-beauty", "Indie Games", "Fitness").
- **Task:** Implement `data_collection.py` using the `google-api-python-client`.
- **Logic:**
  - Fetch metadata for 100+ channels per keyword: `channel_id`, `title`, `description`, `subscriber_count`, `view_count`, and `tags`.
  - Store each entry as a JSON object in a master list.
  - Convert the list into a `pandas` DataFrame.

### Step 3: Master Dataset Aggregation

- **Input:** Four separate DataFrames/CSVs (one from each team member).
- **Task:** Execute a merge script in `utils.py`.
- **Logic:**
  - Use `pd.concat` to unify all member datasets.
  - **Deduplication:** Use `drop_duplicates(subset=['channel_id'])` to ensure a clean master list.
  - **SQL Guardrail:** Apply `ON CONFLICT (message_id) DO NOTHING` logic if writing to a database to prevent primary key errors.

---

## Phase 2: Brand Context & Scoring Engine

### Step 4: Brand Context Capture

- **Input:** User data from `app.py` (Category, Audience, Budget, and "Brand Story" text).
- **Task:** Convert Streamlit `st.text_area` input into a structured Markdown "Brand Brief".
- **Logic:** Format raw text into a clean string to be used for NLP vectorization.

### Step 5: Hybrid AI Matching Engine

- **Input:** Master Influencer DataFrame (Step 3) + Brand Brief (Step 4).
- **Task:** Execute `matching_roi.py` to assign a "Confidence Score".
- **Logic:**
  - **Text Analysis (NLP):** Use `scikit-learn` `TfidfVectorizer` to compute cosine similarity between the Brand Brief and influencer tags/titles.
  - **Social Network Analysis (SNA):** Use `NetworkX` to build a graph where edges = shared tags. Compute Betweenness Centrality (to find bridge nodes) and Eigenvector Centrality (to find high-authority nodes).
  - **Composite Brand Score:** Apply weighted logic: `(0.4 * SNA) + (0.3 * Text_Similarity) + (0.3 * Engagement_Ratio)`.

---

## Phase 3: Performance Metrics & Visual Insights

### Step 6: ROI & Content Strategy

- **Input:** Top 5 Matched Influencer Profiles.
- **Task:** Run ROI simulations and generate content via `llm_content.py`.
- **Logic:**
  - **Performance Funnel:** Apply the course framework: `Budget` → `Impressions` → `Clicks` → `Conversions` → `ROA`.
  - **LLM Generation:** Feed influencer profiles to the Claude/OpenAI API to generate 3 sponsorship concepts, ad copy, and posting windows.
  - **Bias Mitigation:** Flag and diversify results to avoid "Popularity Bias" (over-recommending mega-influencers).

### Step 7: Dashboards & Distribution

- **Input:** Final scored dataset and `NetworkX` graph object.
- **Task:** Render the final interface in `app.py`.
- **Logic:**
  - **Interactive SNA Graph:** Use `Pyvis` to visualize the influencer network.
  - **Niche Distribution:** Use `Plotly` to show the spread of influencers across each industry.
  - **Match Scorecard:** Display a bar chart comparing the "Confidence Score" and predicted "ROA" for the Top 5 matches.
