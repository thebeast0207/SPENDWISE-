# 🔧 Spendwise — Implementation Plan & Technical Details

> Technical architecture, code organization, data flow, and implementation details for the Spendwise Finance Tracker.

---

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [Web App Architecture](#2-web-app-architecture)
3. [Desktop App Architecture](#3-desktop-app-architecture)
4. [Data Layer](#4-data-layer)
5. [Design System](#5-design-system)
6. [Page Implementations](#6-page-implementations)
7. [Feature Implementation Log](#7-feature-implementation-log)
8. [Known Issues & Future Work](#8-known-issues--future-work)

---

## 1. Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                     SPENDWISE PROJECT                       │ 
├──────────────────────┬─────────────────────────────────────┤
│     Web App          │          Desktop App                 │
│  (Client-Side SPA)   │       (Python GUI)                   │
├──────────────────────┼─────────────────────────────────────┤
│ expense_tracker.html │ main.py                              │
│ brutalist_home.css   │                                      │
├──────────────────────┼─────────────────────────────────────┤
│ Storage: localStorage│ Storage: CSV + JSON files            │
│ Charts:  Chart.js    │ Charts:  matplotlib + seaborn        │
│ UI:      Vanilla CSS │ UI:      CustomTkinter (dark theme)  │
└──────────────────────┴─────────────────────────────────────┘
```

---

## 2. Web App Architecture

### File Structure
The web app is a **single-page application (SPA)** split across two files:

| File | Size | Purpose |
|---|---|---|
| `expense_tracker.html` | ~140KB | HTML structure + inline `<style>` (design tokens) + `<script>` (all JS logic) |
| `brutalist_home.css` | ~59KB | External CSS for brutalist editorial theme (home, dashboard, transactions, budgets, goals) |

### Page Routing
Pages are toggled via `showPage(id, btn)`:
```javascript
function showPage(id, btn) {
  // 1. Hide all pages, deactivate all nav buttons
  // 2. Show target page, activate button
  // 3. Toggle sidebar visibility (hidden on home)
  // 4. Call page-specific render function
}
```

Page IDs: `home`, `dashboard`, `add`, `transactions`, `budgets`, `goals`, `reports`, `admin`

### JavaScript Modules (within `<script>`)

| Section | Functions | Purpose |
|---|---|---|
| Storage Keys | `getSK()`, `getBK()`, `getGK()`, `getCK()` | Per-user localStorage key generation |
| Persistence | `loadR()`, `saveR()`, `loadB()`, `saveB()`, `loadG()`, `saveG()` | Load/save records, budgets, goals |
| Category Mgmt | `loadCats()`, `saveCats()`, `openCatModal()` | Dynamic category add/remove |
| Auth | `handleAuth()`, `performLogin()`, `handleLogout()` | User registration, login, session management |
| Budget Helpers | `monthSpentByCat()`, `getOverBudget()` | Spending calculations |
| Formatters | `inr()`, `inrS()`, `todayStr()`, `fmtD()` | Currency and date formatting |
| Toast/Modal | `toast()`, `showModal()`, `closeModal()` | UI notifications |
| Init | `init()`, `updateMeta()` | App bootstrap, sidebar stats |
| Dashboard | `renderDash()` | Full dashboard with charts + insights |
| Transactions | `renderTxn()`, `selRow()`, `srt()`, `delSel()` | Table rendering, filtering, sorting |
| Reports | `renderRep()` | Monthly report generation |
| Charts | `drawPie()`, `drawGroupedBar()`, `drawLine()`, `drawBudgetBar()`, `drawBk()` | Chart.js chart rendering |
| Budgets | `buildBformRows()`, `renderBudgets()`, `saveBudgets()`, `renderBstatRows()` | Budget form and status |
| Goals | `addGoal()`, `renderGoals()`, `addFunds()`, `deleteGoal()`, `renderGoalInsights()`, `renderGoalActivity()`, `renderRecommendedGoals()`, `updateWhatIf()` | Full savings goals system |
| Admin | `renderAdmin()`, `promoteAdmin()`, `demoteAdmin()`, `deleteUser()` | User management |
| Export | `exportCSV()`, `exportPNG()` | Data export |
| Animation | Scroll observer, parallax, hero reveal | Editorial animations |

---

## 3. Desktop App Architecture

### Single-File Structure: `main.py` (~68KB, 1548 lines)

| Section | Lines (approx) | Purpose |
|---|---|---|
| Imports & Config | 1–110 | Libraries, color palette, theme config |
| CSV Data Layer | 125–160 | `ensure_csv()`, `load_data()`, `append_expense()` |
| Auth System | 160–250 | Login/signup GUI with hashed passwords |
| Main App Class | 250–1500 | `ExpenseTrackerApp(ctk.CTk)` — full GUI |
| Documentation | 1500–1548 | Feature list and usage notes |

### Class Structure
```python
class ExpenseTrackerApp(ctk.CTk):
    def __init__(self):
        # Window setup, sidebar, page frames
    
    # Navigation
    def show_page(self, page_name)
    
    # Dashboard
    def create_dashboard_page(self)
    def refresh_dashboard(self)
    
    # Add Expense
    def create_add_page(self)
    def add_expense(self)
    
    # Transactions
    def create_transactions_page(self)
    def refresh_transactions(self)
    def delete_selected(self)
    
    # Reports
    def create_reports_page(self)
    def refresh_reports(self)
    
    # Goals
    def create_goals_page(self)
    def refresh_goals(self)
    def add_goal(self)
    def add_funds(self, idx)
    def delete_goal(self, idx)
    
    # Admin
    def create_admin_page(self)
    
    # Export
    def export_csv(self)
    def export_pdf(self)
```

---

## 4. Data Layer

### Web App — localStorage

```javascript
// Storage key pattern: spendwise_<type>_<username>
"spendwise_v5_john"     → JSON array of transaction records
"spendwise_bud_john"    → JSON object { category: amount }
"spendwise_goals_john"  → JSON array of goal objects
"spendwise_cats_john"   → JSON { EXP_CATS: [...], INC_CATS: [...] }
"spendwise_users"       → JSON { username: password }
"spendwise_admins"      → JSON array of sub-admin usernames
"spendwise_active_user" → string (current session)
```

#### Transaction Record Schema
```javascript
{
  type: "Expense" | "Income",
  date: "2026-05-08",        // YYYY-MM-DD
  category: "Food",
  amount: 350.00,
  description: "Lunch at cafe",
  id: 1715152800000          // Date.now() timestamp
}
```

#### Budget Schema
```javascript
{
  "Food": 5000,
  "Transport": 2000,
  "Entertainment": 1500
}
```

#### Goal Schema
```javascript
{
  id: 1715152800000,
  name: "Goa Trip",
  target: 50000,
  saved: 15000,
  activity: [
    { amount: 5000, timestamp: "2026-05-01T10:30:00.000Z" },
    { amount: 10000, timestamp: "2026-05-05T14:15:00.000Z" }
  ],
  createdAt: "2026-04-20T08:00:00.000Z"
}
```

### Desktop App — File System

| File | Format | Content |
|---|---|---|
| `expenses_<user>.csv` | CSV | Date, Category, Amount, Description |
| `goals_<user>.json` | JSON | Array of goal objects |
| `categories_<user>.json` | JSON | Array of category strings |
| `users.json` | JSON | { username: hashed_password } |
| `admins.json` | JSON | Array of sub-admin usernames |

---

## 5. Design System

### CSS Architecture

The styling is split between:
1. **Inline `<style>`** in `expense_tracker.html` — Core design tokens and base styles (~530 lines)
2. **`brutalist_home.css`** — External file with brutalist editorial overrides (~2060 lines)

### Design Tokens (CSS Variables)
```css
:root {
  --bg:     #f8fafc;    /* Page background */
  --bg2:    #ffffff;    /* Card/surface background */
  --bg3:    #f1f5f9;    /* Tertiary background */
  --text:   #0f172a;    /* Primary text */
  --muted:  #475569;    /* Secondary text */
  --cyan:   #0284c7;    /* Primary accent */
  --violet: #7c3aed;    /* Secondary accent */
  --green:  #10b981;    /* Success / Income */
  --amber:  #d97706;    /* Warning */
  --rose:   #e11d48;    /* Danger / Expense */
  --border: rgba(0,0,0,.08);
  --sw:     228px;      /* Sidebar width */
}
```

### Typography System
```
Syne (800)     → Headers, labels, badges, stats (brutalist weight)
Syne (700)     → Sub-headers, button text
DM Sans (400)  → Body text, descriptions, table content
DM Sans (500)  → Emphasized body, input values
Playfair Display → Home page hero accent text
```

### Font Scale
| Element | Size |
|---|---|
| Home hero | 150px |
| Page headers (bd-title) | 72px |
| Dashboard stat values | 40px |
| Section titles | 18-24px |
| Body text | 13-16px |
| Labels/badges | 10-12px |

### Brutalist CSS Classes

| Prefix | Used On | Purpose |
|---|---|---|
| `.abc-*` | Home page | Ashley Brooke Creative Studio editorial layout |
| `.bd-*` | Dashboard, Budgets, Goals | Brutalist dashboard shared components |
| `.brutal-*` | Transactions | Brutalist table and invert animations |
| `.goal-*` | Savings Goals | Goal cards, status, actions |
| `.goals-*` | Savings Goals | Insights, activity, recommendations |
| `.bform-*` | Budgets | Budget form input rows |
| `.bprow-*` | Budgets | Budget progress status rows |

---

## 6. Page Implementations

### Home Page
- **Class**: `.abc-hero`, `.abc-split`, `.abc-marquee`
- **Features**: Parallax floating images, scroll reveal observer, CSS-only marquee
- **Animation**: `mousemove` parallax + IntersectionObserver scroll reveals

### Dashboard
- **Class**: `.brutal-dash`, `.bd-header`, `.bd-stats-grid`
- **Charts**: 4 Chart.js instances (pie, grouped bar, line, horizontal bar)
- **Insights**: Dynamic text generation based on spending patterns

### Transactions
- **Class**: `.brutal-table`, `.brutal-tbl`
- **Features**: Staggered row animation, hover invert, selection highlight
- **Search**: `tokens.every(token => rowStr.includes(token))` — all words must match

### Budgets
- **Class**: `.brutal-dash`, `.bd-budget-left`, `.bd-budget-right`
- **Rendering**: `buildBformRows()` generates input rows, `renderBstatRows()` generates progress bars

### Savings Goals
- **Class**: `.brutal-dash`, `.goals-grid`, `.goals-insights-col`
- **Features**: Smart emoji theming (`GOAL_THEMES` map), activity tracking with timestamps
- **Insights**: Real-time projected completion based on monthly net savings

---

## 7. Feature Implementation Log

### Completed ✅

| # | Feature | Platform | Date | Details |
|---|---|---|---|---|
| 1 | Core expense tracking | Both | Initial | Add/delete transactions, CSV/localStorage persistence |
| 2 | Dashboard with charts | Both | Initial | 4+ chart types, summary cards, recent transactions |
| 3 | Transactions with filters | Both | Initial | Type/month/year/category filters, sorting, search |
| 4 | Budget management | Both | Initial | Set limits, track spending, over-budget alerts |
| 5 | Reports with export | Both | Initial | Monthly reports, CSV export, PNG/PDF chart export |
| 6 | Authentication system | Both | Initial | Login/signup, per-user data isolation |
| 7 | Admin panel | Both | Initial | User management, Head Admin + Sub-Admin roles |
| 8 | Savings goals (basic) | Both | Initial | Create goals, add funds, delete goals |
| 9 | AI NLP search | Both | Phase 2 | Groq API (llama3-8b-8192) for natural language transaction search |
| 10 | Dynamic categories | Both | Phase 2 | Add/remove expense & income categories via UI |
| 11 | Brutalist home page | Web | Phase 3 | Full editorial redesign with Ashley Brooke aesthetic |
| 12 | Brutalist dashboard | Web | Phase 3 | Editorial stat blocks, split layouts, typography overhaul |
| 13 | Brutalist transactions | Web | Phase 3 | Invert-on-hover table, editorial filters, animations |
| 14 | Brutalist budgets page | Web | Phase 3 | "BUD GETS." header, split layout, editorial form rows |
| 15 | Brutalist savings goals | Web | Phase 3 | Summary dashboard, insights panel, what-if calculator, activity feed, recommended goals |

### Phase 3 — Brutalist Editorial Theme Transformation

#### Budget Page Redesign
- Replaced legacy card-based layout with `brutal-dash` class
- Added massive "BUD GETS." header with rose-on-dark typography
- Implemented 3-column stat strip (green/amber/rose)
- Split layout: editorial input rows (left) + live spending status (right)
- Custom CSS in `brutalist_home.css` under `BRUTALIST BUDGET PAGE` section
- Preserved JS function compatibility (IDs unchanged)

#### Savings Goals Page Enhancement
- Replaced basic goal card layout with full brutalist editorial page
- Added 5-column summary dashboard (Total Goals / Target / Saved / On Track / Completed)
- Built brutalist "NEW GOAL" create bar with inline inputs
- Enhanced goal cards with smart emoji/color theming (20+ keyword themes)
- Added 4 new sub-systems:
  - **Savings Insights** — Top contributors ranking, projected completion dates
  - **What-If Calculator** — Interactive monthly savings projections
  - **Activity Feed** — Timestamped contribution history
  - **Recommended Goals** — Smart suggestions with one-click creation
- Added ~470 lines of CSS for goals page styling
- Added ~280 lines of JavaScript for new features

---

## 8. Known Issues & Future Work

### Known Issues
| Issue | Status | Notes |
|---|---|---|
| Goals Add Funds / Delete buttons | Under investigation | onclick handlers present, functions defined — may be a rendering issue |
| Browser file:// protocol | Limitation | Some features may require HTTP server for full functionality |
| Large file size | Acceptable | HTML file is ~140KB due to single-file architecture |

### Potential Future Enhancements
- [ ] Recurring transactions (auto-add monthly bills)
- [ ] Multi-currency support
- [ ] Data sync between web and desktop apps
- [ ] Dark mode toggle for web app
- [ ] Monthly email/notification reports
- [ ] Budget rollover (carry unused budget to next month)
- [ ] Goal milestones and celebration animations
- [ ] Spending heatmap calendar view
- [ ] Import transactions from bank CSV

---

*Last updated: May 2026*
