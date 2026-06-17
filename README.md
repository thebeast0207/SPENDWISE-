# 💸 Spendwise — Personal Finance & Budget Tracker

> A modern, feature-rich personal finance tracker available as both a **web application** and a **desktop GUI application**. Track expenses, manage budgets, set savings goals, and generate financial reports — all with a stunning brutalist editorial design.

--- TO ACTUALLY ACCESS THE WEBSITE USE API Key from anywhere you like 


## 📸 Overview

Spendwise is a dual-platform expense tracking system built as a college mini project. It provides:

- **Web App** (`expense_tracker.html`) — A single-page application with a brutalist editorial design, powered by vanilla JavaScript and Chart.js
- **Desktop App** (`main.py`) — A Python GUI application using CustomTkinter with dark theme, pandas data management, and matplotlib charts

Both apps share the same core features but are independently functional with their own data storage.

---

## ✨ Features

### 🏠 Home Page
- Brutalist editorial design inspired by Ashley Brooke / ABCS aesthetic
- Massive typography hero section with floating images
- Animated scroll reveals and parallax effects
- Interactive services showcase with hover animations
- Marquee footer with continuous animation

### 📊 Dashboard
- Real-time financial overview with 5 key metrics (Expenses, Income, Net Yield, Velocity, Budget State)
- Monthly bar chart (last 12 months — income vs expenses)
- Category split donut chart
- Cumulative balance trajectory line chart
- Budget controls bar chart
- Smart insights panel with AI-generated financial tips
- Recent transactions ledger

### ➕ Add Transaction
- Split editorial layout (hero image left, form right)
- Giant animated amount input with quick-add chips (₹100, ₹500, ₹1K, ₹5K, ₹10K)
- Expense/Income toggle with dynamic category switching
- Real-time quick stats (today, weekly, monthly)
- Automatic budget alert detection and modal popup

### 🧾 Transactions Ledger
- Brutalist table with hover-invert animations
- Multi-token search across all fields
- Filters: type, month, year, category
- Sortable by date and amount
- Row selection with delete capability
- CSV export
- Test data generator

### 🎯 Budgets Page
- Brutalist editorial theme with massive "BUD GETS." header
- 3-column colored stat strip (Under Budget / Near Limit / Over Budget)
- Split layout: left panel for setting ₹ limits per category, right panel for live spending status
- Per-category progress bars with color-coded badges (green/amber/red)
- Auto-alerts when overspending

### 🏆 Savings Goals Page
- **Summary Dashboard** — Total Goals, Total Target, Total Saved (with % overall), On Track count, Completed count
- **Create Goal Bar** — Brutalist inline form to create goals instantly
- **Active Goals Grid** — Rich goal cards with emoji themes, progress bars, status labels, and action buttons
- **Savings Insights Panel**:
  - 🚀 Top Contributors — ranked by progress percentage
  - 📅 Projected Completion — estimated dates based on monthly savings rate
  - 💡 What-If Calculator — "If you save ₹X more/month..." interactive projections
- **Recent Activity Feed** — Last 5 contributions with timestamps ("₹5,000 added to Goa Trip – 2 hours ago")
- **Recommended Goals** — Smart suggestions (Emergency Fund, Vacation, Gadget, etc.) with one-click creation

### 📈 Reports
- Monthly period selector
- Expense category breakdown (pie chart + legend bars)
- Income vs Expenses comparison (grouped bar chart)
- Cumulative balance (line chart)
- CSV and PNG chart exports

### 🔐 Authentication
- User registration and login
- Per-user data isolation (transactions, budgets, goals, categories)
- Admin panel with user management
- Head Admin + Sub-Admin role hierarchy (max 2 sub-admins)
- Profile icon with account details modal

### ⚙️ Additional Features
- Dynamic category management (add/remove expense & income categories)
- Toast notifications for all actions
- Budget alert modal popups
- "Clear All Data" danger button with double confirmation
- Savings rate progress bar in sidebar
- Over-budget badge indicator
- Responsive design for smaller screens

---

## 🛠 Technology Stack

### Web App
| Technology | Purpose |
|---|---|
| HTML5 | Page structure and semantic elements |
| CSS3 (Vanilla) | Brutalist editorial design system |
| JavaScript (ES6+) | Application logic, DOM manipulation, routing |
| Chart.js 4.4 | Interactive charts (bar, pie, line, doughnut) |
| Google Fonts | Typography (Syne, DM Sans, Playfair Display) |
| localStorage | Data persistence (transactions, budgets, goals) |

### Desktop App
| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| CustomTkinter | Modern dark-themed GUI widgets |
| pandas | CSV data management and filtering |
| matplotlib | Chart rendering and PDF export |
| seaborn | Chart styling |
| tkinter.ttk | Treeview table widget |

---

## 🚀 Getting Started

### Web App
Simply open the HTML file in any modern browser:
```
expense_tracker.html
```
No server or build step required — it's a fully self-contained single-page app.

### Desktop App
1. Install dependencies:
```bash
pip install customtkinter pandas matplotlib seaborn
```
2. Run:
```bash
python main.py
```

---

## 📁 Project Structure

```
speedwise-main/
├── expense_tracker.html    # Web app — single-file SPA (HTML + CSS + JS)
├── brutalist_home.css      # External CSS — brutalist editorial theme
├── main.py                 # Desktop app — Python GUI (single-file)
├── README.md               # This file
├── WALKTHROUGH.md          # Detailed feature walkthrough
├── IMPLEMENTATION.md       # Technical implementation details
├── TODO.md                 # Development progress tracker
└── LICENSE                 # GNU GPL v3
```

### Data Files (auto-generated at runtime)
- `expenses_<user>.csv` — Desktop app transaction data
- `categories_<user>.json` — Desktop app custom categories
- `goals_<user>.json` — Desktop app savings goals
- `users.json` — Desktop app user credentials
- `admins.json` — Desktop app admin list

---

## 🎨 Design Philosophy

The web app uses a **Brutalist Editorial** design language:
- **Massive typography** — Syne font at enormous sizes (up to 150px) for headers
- **Bold borders** — 2-4px solid borders instead of rounded cards
- **Zero border-radius** — Square corners everywhere for a raw, editorial feel
- **High contrast** — Dark/light inversions, vibrant accent colors
- **Kinetic interactions** — Hover shifts, box-shadow offsets, color inversions
- **Full-bleed layouts** — Edge-to-edge sections with no padding containers

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

College Mini Project — Personal Expense Tracker with GUI Dashboard

Developed as a College Mini Project by:

Aniket Singh - Machine Learning Engineer

Yash Jangid - Lead Statistician
