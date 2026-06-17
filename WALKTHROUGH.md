# 📖 Spendwise — Feature Walkthrough

> Step-by-step guide through every feature of the Spendwise Finance Tracker (Web Application).

---

## Table of Contents
1. [Authentication](#1-authentication)
2. [Home Page](#2-home-page)
3. [Dashboard](#3-dashboard)
4. [Add Transaction](#4-add-transaction)
5. [Transactions Ledger](#5-transactions-ledger)
6. [Budgets](#6-budgets)
7. [Savings Goals](#7-savings-goals)
8. [Reports](#8-reports)
9. [Admin Panel](#9-admin-panel)
10. [Category Management](#10-category-management)
11. [Desktop App (main.py)](#11-desktop-app)

---

## 1. Authentication

### First Time — Sign Up
1. Open `expense_tracker.html` in your browser
2. You'll see the login screen. Click **"Don't have an account? Sign up"**
3. Enter a **username** and **password**, then click **Sign Up**
4. You're automatically logged in after registration

### Returning User — Log In
1. Enter your existing credentials and click **Login**
2. Your data (transactions, budgets, goals) is loaded from localStorage

### Admin Access
- Log in with username **`admin`** to access the Admin Panel
- The admin password is set during the first signup as "admin"
- Admin can promote up to 2 **Sub-Admins**, delete users, and view all accounts

---

## 2. Home Page

The first thing you see after login is the **Brutalist Editorial Home Page**:

### What You'll See
- **Giant "MASTER YOUR MONEY" hero text** with floating editorial images
- **"Your finances, your rules."** tagline with animated underline
- **Service cards** showcasing app features (Track, Budget, Save, Report)
- Each card has a hover effect — shifts up with a shadow offset

### Navigation
- The **sidebar** appears on the left when you navigate to any page other than Home
- Home hides the sidebar for a full-bleed experience
- Use the sidebar buttons to navigate between pages

---

## 3. Dashboard

Navigate: **Sidebar → 📊 Dashboard**

### Summary Cards (Top Row)
Five brutalist stat blocks with editorial typography:
1. **Total Expenses** — Current month (rose colored)
2. **Total Income** — Current month (green colored)
3. **Net Yield** — Income minus expenses
4. **Velocity** — Average daily spend rate
5. **Budget State** — Number of categories within budget

### Charts
- **Monthly Comparison** — Grouped bar chart showing income vs expenses for last 12 months
- **Category Split** — Donut chart breaking down expenses by category
- **Balance Trajectory** — Line chart showing cumulative balance over time
- **Budget Controls** — Horizontal bar chart comparing spending vs budget limits

### Smart Insights
- AI-generated tips based on your spending patterns:
  - Top spending category identification
  - Spending spike detection (vs previous month)
  - Savings goal progress projection

### Mini Budget Bars
- Quick visual of each budget category's consumption rate
- Color-coded: green (safe), amber (≥80%), red (over)

### Recent Transactions
- Last 7 transactions with emoji icons, category, date, and amount

---

## 4. Add Transaction

Navigate: **Sidebar → ➕ Add Transaction**

### How to Add an Expense
1. **Select Type** — Toggle between Expense (red) and Income (green) using the buttons
2. **Pick Date** — Defaults to today
3. **Choose Category** — Dropdown updates based on type (8 expense categories, 5 income categories)
4. **Enter Amount** — Use the giant number input or click quick-add chips:
   - ₹100, ₹500, ₹1K, ₹5K, ₹10K
5. **Add Description** — Optional note
6. **Click Submit** — "➕ Add Expense" or "➕ Add Income"

### After Submitting
- A toast notification confirms the entry
- Quick Stats update in real-time (Today, This Week, This Month totals)
- If you exceed a budget limit, you'll see:
  - An inline budget alert banner
  - A modal popup listing all over-budget categories

---

## 5. Transactions Ledger

Navigate: **Sidebar → 🧾 Transactions**

### Viewing Transactions
- All transactions appear in a brutalist-styled table
- Columns: Type, Date, Category, Amount, Description
- Rows animate in with a staggered delay

### Filtering
- **Type**: All / Expense / Income
- **Month**: January–December / All
- **Year**: Last 6 years / All
- **Category**: All categories available
- **Search bar**: Multi-token text search (matches across all fields simultaneously)

### Actions
- **Click a row** to select it (highlighted with a border)
- **Delete Selected** — Removes the selected transaction after confirmation
- **Reset Filters** — Clears all filters
- **🧪 Load Test Data** — Generates sample data for testing
- **📥 Export CSV** — Downloads all transactions as CSV

### Footer Stats
- Shows: Record count, Total Expenses, Total Income, Net balance

---

## 6. Budgets

Navigate: **Sidebar → 🎯 Budgets**

### Setting Budgets (Left Panel)
1. Each expense category appears as an editorial row with an input field
2. Enter a monthly ₹ limit for any category (e.g., Food: ₹5000)
3. Click the **"SAVE BUDGETS"** button at the bottom
4. Success/failure status appears inline

### Monitoring Spending (Right Panel)
- Each category with a budget shows:
  - Current spending vs budget limit
  - A progress bar (green → amber → red as you approach the limit)
  - Status badge: ✓ UNDER / ⚡ NEAR / ✗ OVER
- The top of the panel shows three summary stats:
  - 🟢 Under Budget count
  - 🟡 Near Limit count (≥80%)
  - 🔴 Over Budget count

---

## 7. Savings Goals

Navigate: **Sidebar → 🏆 Savings Goals**

### A. Summary Dashboard (Top)
Five stat blocks showing:
1. **Total Goals** — How many goals you've created
2. **Total Target** — Combined target amount across all goals
3. **Total Saved** — How much you've saved so far
4. **On Track** — Goals that have some progress but aren't complete
5. **Completed** — Goals where saved ≥ target

### B. Creating a Goal
1. Use the **"+ NEW GOAL"** bar at the top
2. Enter a goal name (e.g., "Goa Trip")
3. Enter the target amount (e.g., ₹50,000)
4. Click **CREATE**
5. The goal card appears immediately with an auto-assigned emoji and color theme

### C. Goal Cards
Each goal shows:
- **Themed emoji icon** — auto-detected from the name (e.g., "vacation" → ✈️, "car" → 🚗)
- **Progress bar** — visual fill with the goal's theme color
- **Status label** — NOT STARTED / IN PROGRESS / ALMOST THERE / COMPLETED
- **Percentage** — big bold number showing progress
- **Saved / Remaining amounts**
- **+ ADD FUNDS** — click to contribute money to this goal
- **🗑 Delete** — remove the goal

### D. Savings Insights (Right Panel)

#### 🚀 Top Contributors
- Ranks your goals by completion percentage
- Shows 🥇🥈🥉 medals for top 3

#### 📅 Projected Completion
- Calculates estimated completion date based on your current monthly savings rate (income - expenses)
- Shows "Needs income data" if no income recorded this month

#### 💡 What-If Calculator
- Enter a hypothetical monthly savings amount
- Instantly see how many months each goal would take to complete
- Example: "If you save ₹5,000/month → Goa Trip: 8 months → Aug 2026"

### E. Recent Activity Feed
- Shows the last 5 fund contributions
- Each entry shows: amount, goal name, and time ago
- Example: "₹5,000 added to Goa Trip – 2 hours ago"

### F. Recommended Goals
- When you have fewer than 5 goals, smart suggestions appear:
  - 🛡️ Emergency Fund (₹1,00,000)
  - ✈️ Vacation Trip (₹50,000)
  - 📱 New Gadget (₹30,000)
  - 📈 Investment Fund (₹2,00,000)
  - etc.
- Click any suggestion to create it instantly with one click

---

## 8. Reports

Navigate: **Sidebar → 📈 Reports**

### Generating a Report
1. Select **Month** and **Year** using the dropdowns
2. The report auto-generates with:
   - **Summary stats**: Expenses, Income, Net Savings, Savings Rate %
   - **Category Pie Chart** — Donut chart of expense breakdown
   - **Category Bars** — Percentage bars for each category
   - **Income vs Expenses** — Grouped bar chart (12 months)
   - **Cumulative Balance** — Line chart (all-time trajectory)

### Exporting
- **📥 Export CSV** — Downloads all transactions as a CSV file
- **🖼 Save Charts** — Saves pie, bar, and line charts as PNG images

---

## 9. Admin Panel

Navigate: **Sidebar → 👑 Admin Panel** (only visible to admins)

### Head Admin (username: "admin")
- View all registered users with their passwords
- **⬆ Promote** any user to Sub-Admin (max 2 slots)
- **⬇ Demote** Sub-Admins back to regular users
- **🗑 Delete** any non-admin user (permanently wipes their data)

### Sub-Admins
- Can view users and delete regular users
- Cannot promote/demote other admins
- Cannot delete other Sub-Admins

---

## 10. Category Management

Available from: **Category modal** (accessible from the Dashboard or Add Transaction pages)

### Adding a Category
1. Open the category management modal
2. Select whether it's an **Expense** or **Income** category
3. Type the new category name
4. Click **Add**

### Removing a Category
- Each custom category has a **🗑** delete button
- Default categories cannot be removed
- Changes persist across sessions

---

## 11. Desktop App

### Running
```bash
python main.py
```

### Pages
The desktop app mirrors the web app with these pages:
- **Dashboard** — Summary cards + pie/bar charts
- **Add Expense** — Form with date, category, amount, description
- **Transactions** — Treeview table with filters
- **Reports** — Monthly charts with PDF export capability
- **Savings Goals** — Goal cards with progress tracking
- **Admin Panel** — User management (for admin users)

### Key Differences from Web App
| Feature | Web App | Desktop App |
|---|---|---|
| Data Storage | localStorage | CSV + JSON files |
| Charts | Chart.js (interactive) | matplotlib (static, PDF export) |
| Theme | Brutalist Editorial (light bg) | Dark theme (CustomTkinter) |
| Search | Multi-token text search | AI-powered NLP search (Groq API) |
| Export | CSV + PNG | CSV + PDF (with charts) |

---

## 🔧 Troubleshooting

| Issue | Solution |
|---|---|
| Login screen won't load | Clear browser cache and reload |
| Charts not showing | Ensure Chart.js CDN is accessible (needs internet) |
| Budgets not saving | Check that categories haven't been deleted |
| Goals buttons not working | Refresh the page — JS may need reinitialization |
| Desktop app won't start | Install all dependencies: `pip install customtkinter pandas matplotlib seaborn` |

---

*Last updated: May 2026*
