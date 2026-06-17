# SPENDWISE-
Spendwise is a secure, local-first personal finance ecosystem combining a vanilla JavaScript web SPA and a Pandas-driven Python desktop GUI to deliver real-time asset tracking, multi-token ledger search, and rule-based spending insights with zero cloud dependency.


# 💸 Spendwise — AI-Powered Personal Finance & Budget Tracker

> A modern, local-first personal finance ecosystem available as both a **Web Application (SPA)** and a **Python Desktop GUI**. Track expenses, manage budgets, calculate savings goals, and generate automated financial audits—all wrapped in a striking **Brutalist Editorial** design language.


## 📸 Overview

Spendwise was developed to bridge the gap between tedious manual spreadsheets and overly complex, cloud-dependent banking apps. By utilizing a **Local-First Architecture**, all financial data is processed directly on the user's machine, ensuring zero latency and absolute data privacy.

The project is dual-platform:
- **Web App:** A zero-build Single-Page Application (SPA) powered by vanilla JavaScript and Chart.js.
- **Desktop App:** A robust Python GUI application utilizing CustomTkinter, Pandas, and Matplotlib.

---

## ✨ Key Features

### 🎨 Brutalist Editorial UI
Rejects standard "soft" UI trends in favor of massive typography (Syne font), bold geometric borders, high-contrast inversions, and kinetic scroll animations.

### 🧠 Smart Algorithmic Insights
The backend uses a deterministic, rule-based engine to analyze spending patterns. It automatically detects month-over-month spending spikes (>20% delta) and projects savings goal completion dates.

### 🔍 Multi-Token NLP Search
The transaction ledger features a dynamic live search. Users can type fragmented, conversational queries (e.g., `"food 500"`), and the engine will instantly cross-reference all tokens against every column simultaneously.

### 🎯 Split-Screen Budget Controls
Set absolute limits per category and track health via a real-time, 3-color status strip:
* **Green:** Under Budget
* **Amber:** Nearing Limit (>80%)
* **Rose:** Over Budget (triggers automated modal alerts)

### 🏆 Gamified Savings Goals
Create visually engaging, emoji-themed savings goals. Includes an interactive **"What-If" Calculator** to project how extra monthly contributions accelerate your wealth-building timeline.

### 🔐 Hierarchical Security & Data Isolation
Features a localized authentication system with SHA-256 cryptographic password hashing. Includes a dedicated **Admin Panel** supporting Head Admin and Sub-Admin role assignments.

---

## 🛠 Technology Stack

### Web Application (Client-Side SPA)
* **Core:** HTML5, CSS3 (Vanilla), ES6+ JavaScript
* **Database:** Browser `localStorage` (NoSQL Document Store)
* **Data Visualization:** Chart.js 4.4
* **Typography:** Google Fonts (Syne, DM Sans, Playfair Display)

### Desktop Application (Python GUI)
* **Core:** Python 3
* **GUI Framework:** CustomTkinter (Modern Dark Theme)
* **Data Engine:** Pandas (Dataframe Vectorization & Filtering)
* **Visualization:** Matplotlib, Seaborn
* **Database:** Local File System (CSV for ledgers, JSON for configs/auth)

---

## 🚀 Getting Started

### Running the Web App
The web application is completely serverless. 
1. Clone the repository.
2. Open `expense_tracker.html` in any modern web browser.
3. Start tracking!

### Running the Desktop App
1. Clone the repository.
2. Ensure you have Python 3 installed.
3. Install the required dependencies:
   ```bash
   pip install customtkinter pandas matplotlib seaborn


### Running the application

1. In bash use
     python main.py

2. For VS CODE users
    Firstly install live server extention and then run with live server


### Project Architecture 

spendwise/
├── expense_tracker.html    # Web app — single-file SPA (HTML + CSS + JS)

├── brutalist_home.css      # External CSS — brutalist editorial design tokens

├── main.py                 # Desktop app — Python GUI & Pandas backend

├── README.md               # Project documentation

├── IMPLEMENTATION.md       # Technical architecture & schema docs

└── assets/                 # Folder for README screenshots


### 👨‍💻 Authors & Credits

Developed as a College Mini Project by:

1.Aniket Singh - Machine Learning Engineer

2.Yash Jangid - Lead Statistician
