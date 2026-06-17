# ================================================================================
#  PERSONAL EXPENSE TRACKER WITH GUI DASHBOARD
#  Author      : College Mini Project
#  Description : A modern dark-themed desktop expense tracker with charts,
#                CSV storage, filtering, and PDF export.
#  File        : main.py  (single-file project)
# ================================================================================

import os
import csv
import json
import hashlib
import datetime

from tkinter import ttk, messagebox
from tkinter.ttk import Treeview

import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import seaborn as sns
import customtkinter as ctk

# ================================================================================
#  GLOBAL CONFIGURATION
# ================================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"
CURRENT_USER = None

def get_csv_file():
    return f"expenses_{CURRENT_USER}.csv" if CURRENT_USER else "expenses.csv"

def get_cat_file():
    return f"categories_{CURRENT_USER}.json" if CURRENT_USER else "categories.json"

def get_goals_file():
    return f"goals_{CURRENT_USER}.json" if CURRENT_USER else "goals.json"

def load_sub_admins():
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return []

def save_sub_admins(admins):
    try:
        with open(ADMINS_FILE, "w", encoding="utf-8") as f: json.dump(admins, f)
    except Exception: pass

DEFAULT_CATEGORIES = ["Food", "Transport", "Rent", "Entertainment",
                      "Bills", "Shopping", "Healthcare", "Others"]

def load_categories():
    cat_file = get_cat_file()
    if os.path.exists(cat_file):
        try:
            with open(cat_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
    return DEFAULT_CATEGORIES.copy()

def save_categories(cats):
    try:
        with open(get_cat_file(), "w", encoding="utf-8") as f:
            json.dump(cats, f)
    except Exception:
        pass

CATEGORIES = load_categories()

def load_goals():
    g_file = get_goals_file()
    if os.path.exists(g_file):
        try:
            with open(g_file, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return []

def save_goals(goals):
    try:
        with open(get_goals_file(), "w", encoding="utf-8") as f: json.dump(goals, f)
    except Exception: pass

# Color Palette (dark theme)
BG_DARK    = "#0f1117"
BG_CARD    = "#1a1d27"
BG_SIDEBAR = "#12151f"
ACCENT     = "#4f8ef7"
ACCENT2    = "#7c5cbf"
TEXT_MAIN  = "#e8eaf0"
TEXT_DIM   = "#6b7280"
SUCCESS    = "#22c55e"
DANGER     = "#ef4444"
WARNING    = "#f59e0b"

CATEGORY_COLORS = [
    "#4f8ef7", "#7c5cbf", "#22c55e", "#f59e0b",
    "#ef4444", "#06b6d4", "#ec4899", "#a78bfa"
]

sns.set_theme(style="darkgrid", rc={
    "axes.facecolor":   "#1a1d27",
    "figure.facecolor": "#12151f",
    "axes.edgecolor":   "#2d3148",
    "axes.labelcolor":  "#e8eaf0",
    "xtick.color":      "#9ca3af",
    "ytick.color":      "#9ca3af",
    "grid.color":       "#2d3148",
    "text.color":       "#e8eaf0",
})


# ================================================================================
#  CSV DATA LAYER
# ================================================================================

def ensure_csv():
    """Create expenses.csv with headers if it does not exist."""
    c_file = get_csv_file()
    if not os.path.exists(c_file):
        with open(c_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Description"])


def load_data() -> pd.DataFrame:
    """Load the CSV into a DataFrame; return empty DF on error."""
    if not CURRENT_USER:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
    ensure_csv()
    try:
        df = pd.read_csv(get_csv_file(), parse_dates=["Date"])
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        df.dropna(subset=["Date"], inplace=True)
        df.sort_values("Date", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])


def append_expense(date_str: str, category: str, amount: float, description: str):
    """Append a single expense row to the CSV."""
    with open(get_csv_file(), "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date_str, category, f"{amount:.2f}", description])


def save_full_df(df: pd.DataFrame):
    """Overwrite CSV with an updated DataFrame (used after deletion)."""
    df_to_save = df.copy()
    df_to_save["Date"] = df_to_save["Date"].dt.strftime("%Y-%m-%d")
    df_to_save.to_csv(get_csv_file(), index=False)


# ================================================================================
#  UTILITY HELPERS
# ================================================================================

def fmt_inr(value: float) -> str:
    """Format a number as ₹ Indian currency with commas."""
    try:
        return "₹{:,.2f}".format(value)
    except Exception:
        return "₹0.00"


def current_month_data(df: pd.DataFrame) -> pd.DataFrame:
    now = datetime.date.today()
    return df[(df["Date"].dt.month == now.month) & (df["Date"].dt.year == now.year)]


def embed_chart(fig, parent_frame, toolbar: bool = False):
    """
    Embed a matplotlib figure into a CTkFrame/tk parent widget.
    Returns (canvas, optional toolbar widget).
    """
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
    if toolbar:
        tb = NavigationToolbar2Tk(canvas, parent_frame)
        tb.update()
    return canvas


# ================================================================================
#  CHART BUILDERS  (return matplotlib Figure objects)
# ================================================================================

def build_pie_chart(df: pd.DataFrame, title: str = "Spending by Category") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(4.8, 3.6), facecolor="#12151f")
    if df.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                color=TEXT_DIM, fontsize=12)
        ax.axis("off")
        fig.tight_layout()
        return fig

    group = df.groupby("Category")["Amount"].sum().reset_index()
    group.sort_values("Amount", ascending=False, inplace=True)

    _wedges, texts, autotexts = ax.pie(
        group["Amount"],
        labels=group["Category"],
        autopct="%1.1f%%",
        colors=CATEGORY_COLORS[:len(group)],
        startangle=140,
        wedgeprops=dict(width=0.6, edgecolor="#12151f", linewidth=2),
        pctdistance=0.75,
    )
    for t in texts:
        t.set_color(TEXT_MAIN)
        t.set_fontsize(8)
    for at in autotexts:
        at.set_color(TEXT_MAIN)
        at.set_fontsize(7)

    ax.set_title(title, color=TEXT_MAIN, fontsize=11, pad=10, fontweight="bold")
    fig.tight_layout()
    return fig


def build_bar_chart(df: pd.DataFrame, title: str = "Monthly Expenses (Last 12 Months)") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6.4, 3.6), facecolor="#12151f")
    if df.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                color=TEXT_DIM, fontsize=12)
        ax.axis("off")
        fig.tight_layout()
        return fig

    df2 = df.copy()
    df2["YearMonth"] = df2["Date"].dt.to_period("M")
    monthly = df2.groupby("YearMonth")["Amount"].sum().reset_index()
    monthly["YearMonth"] = monthly["YearMonth"].astype(str)

    # Keep last 12 months
    monthly = monthly.tail(12)

    bars = ax.bar(monthly["YearMonth"], monthly["Amount"],
                  color=ACCENT, edgecolor="#0f1117", linewidth=0.8, width=0.6)

    # Gradient-like effect: darken leftmost bars
    for i, bar in enumerate(bars):
        alpha = 0.5 + 0.5 * (i / max(len(bars) - 1, 1))
        bar.set_alpha(alpha)

    ax.set_xlabel("Month", color=TEXT_DIM, fontsize=8)
    ax.set_ylabel("Amount (₹)", color=TEXT_DIM, fontsize=8)
    ax.set_title(title, color=TEXT_MAIN, fontsize=11, pad=10, fontweight="bold")
    ax.tick_params(axis="x", rotation=45, labelsize=7, colors=TEXT_DIM)
    ax.tick_params(axis="y", labelsize=7, colors=TEXT_DIM)
    ax.spines[:].set_visible(False)
    fig.tight_layout()
    return fig


# ================================================================================
#  MAIN APPLICATION CLASS
# ================================================================================

class ExpenseTrackerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ---------- Window setup ----------
        self.title("Expense Tracker — Dashboard")
        self.geometry("1200x800")
        self.minsize(1000, 680)
        self.configure(fg_color=BG_DARK)

        # Refs to embedded chart canvases (for destruction on refresh)
        self._dash_pie_canvas   = None
        self._dash_bar_canvas   = None
        self._rep_pie_canvas    = None
        self._rep_bar_canvas    = None
        
        self.df = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

        # ---------- Pre-declare all widget attributes ----------
        # Login screen
        self.login_sub = None
        self.user_entry = None
        self.pass_entry = None
        self.auth_msg = None
        self.auth_btn = None
        self.auth_mode = "login"
        self.switch_btn = None
        self.user_count_lbl = None
        # Sidebar
        self.nav_buttons = {}
        self.admin_btn = None
        # Goals page
        self.goal_name_var = None
        self.goal_target_var = None
        self.goals_container = None
        # Admin page
        self.admin_tree = None
        self.admin_btn_frame = None
        self.btn_promote = None
        self.btn_demote = None
        self.btn_del = None
        # Dashboard page
        self.dash_date_label = None
        self.cards_frame = None
        self.card_labels = {}
        self.insights_frame = None
        self.insights_list_container = None
        self.dash_pie_frame = None
        self.dash_bar_frame = None
        # Add Expense page
        self.entry_date = None
        self.opt_category = None
        self.entry_amount = None
        self.entry_desc = None
        self.add_status = None
        # Transactions page
        self.search_entry = None
        self.txn_month_var = None
        self.txn_year_var = None
        self.tree = None
        self.txn_summary = None
        # Reports page
        self.rep_month_var = None
        self.rep_year_var = None
        self.rep_summary_label = None
        self.rep_pie_frame = None
        self.rep_bar_frame = None

        self._build_ui()

    # ============================================================
    #  UI SKELETON
    # ============================================================

    def _build_login_screen(self):
        frame = ctk.CTkFrame(self, fg_color=BG_DARK)
        card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=14, width=400, height=450)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Welcome Back", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_MAIN).pack(pady=(40, 5))
        self.login_sub = ctk.CTkLabel(card, text="Log in to your account", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.login_sub.pack(pady=(0, 20))

        self.user_entry = ctk.CTkEntry(card, placeholder_text="Username", font=ctk.CTkFont(size=13), height=42, fg_color="#1e2235", border_color="#2d3148")
        self.user_entry.pack(fill="x", padx=30, pady=10)
        self.user_entry.bind("<Return>", lambda e: self._handle_auth())
        
        self.pass_entry = ctk.CTkEntry(card, placeholder_text="Password", show="*", font=ctk.CTkFont(size=13), height=42, fg_color="#1e2235", border_color="#2d3148")
        self.pass_entry.pack(fill="x", padx=30, pady=10)
        self.pass_entry.bind("<Return>", lambda e: self._handle_auth())

        self.auth_msg = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12))
        self.auth_msg.pack(pady=5)

        self.auth_btn = ctk.CTkButton(card, text="Login", font=ctk.CTkFont(size=14, weight="bold"), height=44, fg_color=ACCENT, command=self._handle_auth)
        self.auth_btn.pack(fill="x", padx=30, pady=10)

        self.auth_mode = "login"
        self.switch_btn = ctk.CTkButton(card, text="Don't have an account? Sign up", font=ctk.CTkFont(size=12), fg_color="transparent", text_color=ACCENT, hover_color=BG_CARD, command=self._switch_auth_mode)
        self.switch_btn.pack(pady=10)
        
        self.user_count_lbl = ctk.CTkLabel(card, text="Registered Users: 0", font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.user_count_lbl.pack(side="bottom", pady=20)
        self._update_user_count()
        
        return frame
        
    def _update_user_count(self):
        count = 0
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    count = len(json.load(f))
            except Exception:
                pass
        if hasattr(self, 'user_count_lbl'):
            self.user_count_lbl.configure(text=f"Registered Users: {count}")

    def _switch_auth_mode(self):
        self.auth_mode = "signup" if self.auth_mode == "login" else "login"
        if self.auth_mode == "login":
            self.auth_btn.configure(text="Login")
            self.switch_btn.configure(text="Don't have an account? Sign up")
            self.login_sub.configure(text="Log in to your account")
        else:
            self.auth_btn.configure(text="Sign Up")
            self.switch_btn.configure(text="Already have an account? Log in")
            self.login_sub.configure(text="Create a new account")
        self.auth_msg.configure(text="")

    def _handle_auth(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get()
        if not u or not p:
            self.auth_msg.configure(text="Please fill all fields", text_color=DANGER)
            return

        users = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        
        hashed_p = hashlib.sha256(p.encode()).hexdigest()
        if self.auth_mode == "signup":
            if u in users:
                self.auth_msg.configure(text="Username already exists", text_color=DANGER)
                return
            users[u] = hashed_p
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f)
            self._update_user_count()
            self.auth_msg.configure(text="Account created! Logging in...", text_color=SUCCESS)
            self.after(1000, lambda: self._perform_login(u))
        else:
            if u not in users or users[u] != hashed_p:
                self.auth_msg.configure(text="Invalid credentials", text_color=DANGER)
                return
            self._perform_login(u)

    def _perform_login(self, username):
        global CURRENT_USER
        CURRENT_USER = username
        CATEGORIES.clear()
        CATEGORIES.extend(load_categories())
        self.df = load_data()
        self._refresh_categories()
        
        subs = load_sub_admins()
        self.admin_btn.pack_forget()
        if CURRENT_USER.lower() == "admin" or CURRENT_USER in subs:
            self.admin_btn.pack(side="bottom", fill="x", padx=12, pady=(0, 20))
        
        self.login_frame.pack_forget()
        self.main_container.pack(fill="both", expand=True)
        self.clear_data_btn.place(relx=1.0, rely=1.0, x=-24, y=-24, anchor="se")
        self.show_page("dashboard")

    def _build_ui(self):
        self.login_frame = self._build_login_screen()
        self.login_frame.pack(fill="both", expand=True)

        self.main_container = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        
        # ---- Sidebar ----
        self.sidebar = ctk.CTkFrame(self.main_container, width=210, corner_radius=0,
                                    fg_color=BG_SIDEBAR)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # ---- Main content area ----
        self.content = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

        # 🔥 Top Right Profile Bar
        self.top_bar = ctk.CTkFrame(self.content, fg_color="transparent", height=50)
        self.top_bar.pack(fill="x", padx=24, pady=(15, 0))
        
        self.profile_btn = ctk.CTkButton(
            self.top_bar, text="👤",
            font=ctk.CTkFont(size=18),
            fg_color=ACCENT2, hover_color="#6d48b0",
            width=40, height=40, corner_radius=20,
            command=self._show_account_details
        )
        self.profile_btn.pack(side="right")

        # Build all pages (hidden initially)
        self.page_dashboard    = self._build_dashboard_page()
        self.page_add          = self._build_add_page()
        self.page_transactions = self._build_transactions_page()
        self.page_reports      = self._build_reports_page()
        self.page_goals        = self._build_goals_page()
        self.page_admin        = self._build_admin_page()

        self.pages = {
            "dashboard":    self.page_dashboard,
            "add":          self.page_add,
            "transactions": self.page_transactions,
            "goals":        self.page_goals,
            "reports":      self.page_reports,
            "admin":        self.page_admin,
        }
        
        # 🔥 Floating Clear Data Button (Bottom Right)
        self.clear_data_btn = ctk.CTkButton(
            self, text="🗑 Clear All Data",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=DANGER, hover_color="#b91c1c",
            text_color="#ffffff", corner_radius=18,
            width=130, height=36,
            command=self._clear_all_data
        )

    # ============================================================
    #  SIDEBAR
    # ============================================================

    def _build_sidebar(self):
        # Logo / title
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", cursor="hand2")
        logo_frame.pack(pady=(28, 8), padx=16, fill="x")

        lbl_icon = ctk.CTkLabel(logo_frame, text="💰", font=ctk.CTkFont(size=28), cursor="hand2")
        lbl_icon.pack()
        lbl_title = ctk.CTkLabel(logo_frame, text="Spendwise",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_MAIN, cursor="hand2")
        lbl_title.pack()
        lbl_sub = ctk.CTkLabel(logo_frame, text="Personal Finance Dashboard",
                     font=ctk.CTkFont(size=9), text_color=TEXT_DIM, cursor="hand2")
        lbl_sub.pack()
        
        for widget in [logo_frame, lbl_icon, lbl_title, lbl_sub]:
            widget.bind("<Button-1>", lambda e: self.show_page("dashboard"))

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2d3148").pack(
            fill="x", padx=16, pady=16)

        # Nav buttons
        nav_items = [
            ("🏠  Dashboard",     "dashboard"),
            ("➕  Add Expense",   "add"),
            ("📋  Transactions",  "transactions"),
            ("🏆  Savings Goals", "goals"),
            ("📊  Reports",       "reports"),
        ]
        self.nav_buttons = {}
        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                font=ctk.CTkFont(size=13),
                fg_color="transparent", hover_color="#1e2235",
                text_color=TEXT_DIM, corner_radius=8, height=42,
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[key] = btn
            
        self.admin_btn = ctk.CTkButton(
            self.sidebar, text="👑  Admin Panel", anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent", hover_color="#3f1d24",
            text_color=WARNING, corner_radius=8, height=42,
            command=lambda: self.show_page("admin")
        )
        # Don't pack it yet (handled in _perform_login)

        # Bottom info
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2d3148").pack(
            fill="x", padx=16, pady=(10, 16), side="bottom")
        ctk.CTkLabel(self.sidebar, text="v1.0  |  CSV Storage",
                     font=ctk.CTkFont(size=9), text_color=TEXT_DIM).pack(
            side="bottom", pady=(0, 10))

    def _handle_logout(self):
        global CURRENT_USER
        CURRENT_USER = None
        self.user_entry.delete(0, "end")
        self.pass_entry.delete(0, "end")
        self.admin_btn.pack_forget()
        self.main_container.pack_forget()
        self.clear_data_btn.place_forget()
        self._update_user_count()
        self.login_frame.pack(fill="both", expand=True)

    def _show_account_details(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Account Details")
        popup.geometry("320x250")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=BG_DARK)
        
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 160
        y = self.winfo_y() + (self.winfo_height() // 2) - 125
        popup.geometry(f"+{x}+{y}")
        
        card = ctk.CTkFrame(popup, fg_color=BG_CARD, corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(card, text="👤", font=ctk.CTkFont(size=40, family="Segoe UI Emoji")).pack(pady=(15, 5))
        ctk.CTkLabel(card, text=CURRENT_USER, font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_MAIN).pack()
        
        ctk.CTkLabel(card, text=f"Total Records: {len(self.df)}", font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(pady=(0, 15))
        
        ctk.CTkButton(card, text="🚪 Logout", fg_color="transparent", border_width=1, border_color=DANGER, text_color=DANGER, hover_color="#3f1d24", font=ctk.CTkFont(weight="bold"), command=lambda: [popup.destroy(), self._handle_logout()]).pack(pady=5)
        ctk.CTkButton(card, text="Close", fg_color="#2d3148", hover_color="#3f4563", text_color=TEXT_MAIN, command=popup.destroy).pack(pady=5)
        
    def show_page(self, key: str):
        """Hide all pages, show the requested one, highlight nav button."""
        for k, frame in self.pages.items():
            frame.pack_forget()
        for k, btn in self.nav_buttons.items():
            btn.configure(
                fg_color=ACCENT if k == key else "transparent",
                text_color=TEXT_MAIN if k == key else TEXT_DIM,
            )
        self.pages[key].pack(fill="both", expand=True)

        # Refresh data-dependent pages
        self.df = load_data()
        if key == "dashboard":
            self._refresh_dashboard()
        elif key == "transactions":
            self._refresh_treeview()
        elif key == "reports":
            self._refresh_reports()
        elif key == "goals":
            self._refresh_goals_page()
        elif key == "admin":
            self._refresh_admin_page()

    # ============================================================
    #  GOALS PAGE
    # ============================================================
    def _build_goals_page(self) -> ctk.CTkScrollableFrame:
        frame = ctk.CTkScrollableFrame(self.content, fg_color=BG_DARK, scrollbar_button_color="#2d3148")

        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(hdr, text="Savings Goals", font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT_MAIN).pack(side="left")

        add_frame = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10)
        add_frame.pack(fill="x", padx=24, pady=10)
        self.goal_name_var = ctk.StringVar()
        self.goal_target_var = ctk.StringVar()
        
        ctk.CTkEntry(add_frame, textvariable=self.goal_name_var, placeholder_text="Goal Name (e.g. Vacation)", width=200, fg_color="#1e2235", border_color="#2d3148").pack(side="left", padx=10, pady=15)
        ctk.CTkEntry(add_frame, textvariable=self.goal_target_var, placeholder_text="Target Amount (₹)", width=150, fg_color="#1e2235", border_color="#2d3148").pack(side="left", padx=10, pady=15)
        ctk.CTkButton(add_frame, text="➕ Create Goal", fg_color=SUCCESS, hover_color="#16a34a", command=self._create_goal).pack(side="left", padx=10, pady=15)

        self.goals_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.goals_container.pack(fill="both", expand=True, padx=24, pady=10)

        return frame

    def _refresh_goals_page(self):
        for w in self.goals_container.winfo_children(): w.destroy()
        goals = load_goals()
        if not goals:
            ctk.CTkLabel(self.goals_container, text="No savings goals yet. Create one above!", text_color=TEXT_DIM).pack(pady=40)
            return
            
        for i, g in enumerate(goals):
            card = ctk.CTkFrame(self.goals_container, fg_color=BG_CARD, corner_radius=10)
            card.pack(fill="x", pady=8)
            
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(15, 5))
            ctk.CTkLabel(top_row, text=f"🏆 {g['name']}", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_MAIN).pack(side="left")
            
            pct = min(100, int((g['saved'] / g['target']) * 100)) if g['target'] > 0 else 0
            ctk.CTkLabel(top_row, text=f"{fmt_inr(g['saved'])} / {fmt_inr(g['target'])}  ({pct}%)", font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(side="right")
            
            bar = ctk.CTkProgressBar(card, height=12, fg_color="#1e2235", progress_color=SUCCESS if pct >= 100 else ACCENT)
            bar.set(pct / 100.0)
            bar.pack(fill="x", padx=15, pady=8)
            
            bot_row = ctk.CTkFrame(card, fg_color="transparent")
            bot_row.pack(fill="x", padx=15, pady=(5, 15))
            ctk.CTkButton(bot_row, text="➕ Add Funds", width=110, height=28, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#1e2235", hover_color="#2d3148", command=lambda idx=i: self._add_goal_funds(idx)).pack(side="left")
            ctk.CTkButton(bot_row, text="🗑 Delete", width=60, height=28, font=ctk.CTkFont(size=11), fg_color="transparent", text_color=DANGER, hover_color="#3f1d24", command=lambda idx=i: self._delete_goal(idx)).pack(side="right")

    def _create_goal(self):
        n, t = self.goal_name_var.get().strip(), self.goal_target_var.get().strip()
        if not n or not t: return messagebox.showerror("Error", "Please fill both fields.", parent=self)
        try: t_amt = float(t)
        except ValueError: return messagebox.showerror("Error", "Target must be a number.", parent=self)
        if t_amt <= 0: return messagebox.showerror("Error", "Target must be > 0.", parent=self)
        goals = load_goals()
        goals.append({"name": n, "target": t_amt, "saved": 0})
        save_goals(goals)
        self.goal_name_var.set(""); self.goal_target_var.set(""); self._refresh_goals_page()

    def _add_goal_funds(self, idx):
        goals = load_goals()
        val = ctk.CTkInputDialog(text=f"Add funds to '{goals[idx]['name']}':\n(Enter amount in ₹)", title="Add Funds").get_input()
        if val:
            try: goals[idx]['saved'] += float(val); save_goals(goals); self._refresh_goals_page()
            except ValueError: messagebox.showerror("Error", "Invalid amount.", parent=self)

    def _delete_goal(self, idx):
        goals = load_goals()
        if messagebox.askyesno("Delete", f"Delete goal '{goals[idx]['name']}'?", parent=self):
            goals.pop(idx); save_goals(goals); self._refresh_goals_page()

    # ============================================================
    #  ADMIN PAGE
    # ============================================================
    def _build_admin_page(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color=BG_DARK)

        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(hdr, text="Admin Control Panel", font=ctk.CTkFont(size=22, weight="bold"), text_color=WARNING).pack(side="left")
        
        # Table
        tree_container = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10)
        tree_container.pack(fill="both", expand=True, padx=24, pady=(20, 16))

        cols = ("Username", "Role", "Password Hash")
        self.admin_tree = Treeview(tree_container, columns=cols, show="headings", style="Custom.Treeview", selectmode="browse")
        self.admin_tree.heading("Username", text="Username")
        self.admin_tree.heading("Role", text="Role")
        self.admin_tree.heading("Password Hash", text="Password Hash (SHA-256)")
        self.admin_tree.column("Username", width=200, anchor="w")
        self.admin_tree.column("Role", width=120, anchor="w")
        self.admin_tree.column("Password Hash", width=480, anchor="w")

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.admin_tree.yview)
        self.admin_tree.configure(yscrollcommand=vsb.set)
        self.admin_tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        vsb.pack(side="right", fill="y", pady=4)
        
        self.admin_btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.admin_btn_frame.pack(fill="x", padx=24, pady=10)
        
        self.btn_promote = ctk.CTkButton(self.admin_btn_frame, text="⬆ Promote to Sub-Admin", fg_color=ACCENT, hover_color="#3a6fd8", font=ctk.CTkFont(weight="bold"), command=self._promote_user)
        self.btn_demote = ctk.CTkButton(self.admin_btn_frame, text="⬇ Demote", fg_color="transparent", border_width=1, border_color=ACCENT2, text_color=ACCENT2, font=ctk.CTkFont(weight="bold"), command=self._demote_user)
        self.btn_del = ctk.CTkButton(self.admin_btn_frame, text="🗑 Delete Selected User", fg_color=DANGER, hover_color="#b91c1c", font=ctk.CTkFont(weight="bold"), command=self._delete_user)
        
        self.btn_del.pack(side="right")

        return frame
        
    def _refresh_admin_page(self):
        for row in self.admin_tree.get_children():
            self.admin_tree.delete(row)
            
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    users = json.load(f)
                subs = load_sub_admins()
                for u, p in users.items():
                    if u.lower() == "admin":
                        role = "👑 Head Admin"
                    elif u in subs:
                        role = "🛡️ Sub-Admin"
                    else:
                        role = "👤 User"
                    self.admin_tree.insert("", "end", values=(u, role, p))
            except Exception:
                pass
                
        if CURRENT_USER.lower() == "admin":
            self.btn_promote.pack(side="left", padx=(0, 10))
            self.btn_demote.pack(side="left")
        else:
            self.btn_promote.pack_forget()
            self.btn_demote.pack_forget()
            
    def _promote_user(self):
        selected = self.admin_tree.selection()
        if not selected: return messagebox.showwarning("Error", "Select a user to promote.", parent=self)
        user = self.admin_tree.item(selected[0])["values"][0]
        if user.lower() == "admin": return messagebox.showerror("Error", "Already the Head Admin.", parent=self)
        
        subs = load_sub_admins()
        if user in subs: return messagebox.showinfo("Info", "User is already a Sub-Admin.", parent=self)
        if len(subs) >= 2: return messagebox.showerror("Limit Reached", "Maximum of 2 Sub-Admins allowed. Demote one first.", parent=self)
        
        subs.append(user)
        save_sub_admins(subs)
        self._refresh_admin_page()
        messagebox.showinfo("Success", f"👑 {user} promoted to Sub-Admin!", parent=self)
        
    def _demote_user(self):
        selected = self.admin_tree.selection()
        if not selected: return messagebox.showwarning("Error", "Select a user to demote.", parent=self)
        user = self.admin_tree.item(selected[0])["values"][0]
        
        subs = load_sub_admins()
        if user in subs:
            if messagebox.askyesno("Confirm", f"Demote {user} to a regular user?", parent=self):
                subs.remove(user)
                save_sub_admins(subs)
                self._refresh_admin_page()
                messagebox.showinfo("Success", f"👤 {user} demoted to regular user.", parent=self)
                
    def _delete_user(self):
        selected = self.admin_tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a user to delete.", parent=self)
            return
            
        item = self.admin_tree.item(selected[0])
        user_to_delete = item["values"][0]
        role = item["values"][1]
        
        if user_to_delete.lower() == "admin":
            messagebox.showerror("Error", "Cannot delete the master admin account.", parent=self)
            return
            
        if CURRENT_USER.lower() != "admin" and "Sub-Admin" in role:
            messagebox.showerror("Error", "Only the Head Admin can delete Sub-Admins.", parent=self)
            return
            
        if messagebox.askyesno("Confirm", f"Delete user '{user_to_delete}' and ALL their data?", parent=self):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    users = json.load(f)
                if user_to_delete in users:
                    del users[user_to_delete]
                    with open(USERS_FILE, "w", encoding="utf-8") as f:
                        json.dump(users, f)
                
                # Delete their data files
                if os.path.exists(f"expenses_{user_to_delete}.csv"): os.remove(f"expenses_{user_to_delete}.csv")
                if os.path.exists(f"categories_{user_to_delete}.json"): os.remove(f"categories_{user_to_delete}.json")
                
                self._refresh_admin_page()
                self._update_user_count()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)
    # ============================================================
    #  DASHBOARD PAGE
    # ============================================================

    def _build_dashboard_page(self) -> ctk.CTkScrollableFrame:
        frame = ctk.CTkScrollableFrame(self.content, fg_color=BG_DARK,
                                       scrollbar_button_color="#2d3148")

        # Header
        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(hdr, text="Dashboard",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT_MAIN).pack(side="left")
        self.dash_date_label = ctk.CTkLabel(
            hdr, text=datetime.date.today().strftime("%B %d, %Y"),
            font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.dash_date_label.pack(side="right", padx=4)

        # ---- Summary Cards Row ----
        self.cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=20, pady=12)
        self.card_labels = {}
        card_defs = [
            ("total",     "💳 Total Expenses",   ACCENT),
            ("month",     "📅 This Month",        SUCCESS),
            ("avg_daily", "📈 Avg Daily",         WARNING),
            ("top_cat",   "🏆 Top Category",      ACCENT2),
        ]
        for col, (key, title, color) in enumerate(card_defs):
            c = ctk.CTkFrame(self.cards_frame, fg_color=BG_CARD,
                             corner_radius=12)
            c.grid(row=0, column=col, padx=8, pady=4, sticky="nsew")
            self.cards_frame.grid_columnconfigure(col, weight=1)

            ctk.CTkLabel(c, text=title, font=ctk.CTkFont(size=10),
                         text_color=TEXT_DIM).pack(anchor="w", padx=14, pady=(14, 2))

            val_lbl = ctk.CTkLabel(c, text="—",
                                   font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color=color)
            val_lbl.pack(anchor="w", padx=14, pady=(0, 14))
            self.card_labels[key] = val_lbl

        # ---- Insights Row ----
        self.insights_frame = ctk.CTkFrame(frame, fg_color="#12151f", corner_radius=12, border_width=1, border_color=ACCENT)
        self.insights_frame.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(self.insights_frame, text="🤖 Smart Insights", font=ctk.CTkFont(size=14, weight="bold"), text_color=ACCENT).pack(anchor="w", padx=16, pady=(12, 4))
        self.insights_list_container = ctk.CTkFrame(self.insights_frame, fg_color="transparent")
        self.insights_list_container.pack(fill="x", padx=16, pady=(0, 12))

        # ---- Charts Row ----
        charts_row = ctk.CTkFrame(frame, fg_color="transparent")
        charts_row.pack(fill="both", expand=True, padx=20, pady=4)
        charts_row.grid_columnconfigure(0, weight=2)
        charts_row.grid_columnconfigure(1, weight=3)

        # Pie chart container
        self.dash_pie_frame = ctk.CTkFrame(charts_row, fg_color=BG_CARD,
                                           corner_radius=12)
        self.dash_pie_frame.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="nsew")
        ctk.CTkLabel(self.dash_pie_frame, text="Category Breakdown (This Month)",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w", padx=12, pady=(10, 0))

        # Bar chart container
        self.dash_bar_frame = ctk.CTkFrame(charts_row, fg_color=BG_CARD,
                                           corner_radius=12)
        self.dash_bar_frame.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="nsew")
        ctk.CTkLabel(self.dash_bar_frame, text="Monthly Trend (Last 12 Months)",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w", padx=12, pady=(10, 0))

        return frame

    def _refresh_dashboard(self):
        """Recalculate summary cards and re-embed charts."""
        df = self.df
        month_df = current_month_data(df)

        # --- Cards ---
        total = df["Amount"].sum() if not df.empty else 0
        month_total = month_df["Amount"].sum() if not month_df.empty else 0

        # Average daily over days with at least one expense
        if not df.empty:
            unique_days = df["Date"].dt.date.nunique()
            avg_daily = df["Amount"].sum() / unique_days if unique_days else 0
        else:
            avg_daily = 0

        if not df.empty:
            top_cat = df.groupby("Category")["Amount"].sum().idxmax()
        else:
            top_cat = "—"

        self.card_labels["total"].configure(text=fmt_inr(total))
        self.card_labels["month"].configure(text=fmt_inr(month_total))
        self.card_labels["avg_daily"].configure(text=fmt_inr(avg_daily))
        self.card_labels["top_cat"].configure(text=top_cat)
        
        # --- Smart Insights ---
        for widget in self.insights_list_container.winfo_children(): widget.destroy()
        insights = []
        now = datetime.date.today()
        pm = now.month - 1 if now.month > 1 else 12
        py = now.year if now.month > 1 else now.year - 1
        pm_df = df[(df["Date"].dt.month == pm) & (df["Date"].dt.year == py)]
        
        cm_cat = month_df.groupby("Category")["Amount"].sum()
        pm_cat = pm_df.groupby("Category")["Amount"].sum()
        
        max_spike, spike_cat = 0, None
        for cat, amt in cm_cat.items():
            if cat in pm_cat and pm_cat[cat] > 0:
                pct = ((amt - pm_cat[cat]) / pm_cat[cat]) * 100
                if pct > 20 and pct > max_spike:
                    max_spike, spike_cat = pct, cat
                    
        if spike_cat: insights.append(f"📈 Spending Spike: You've spent {int(max_spike)}% more on {spike_cat} this month compared to last month.")
            
        goals = load_goals()
        active_goals = [g for g in goals if g["saved"] < g["target"]]
        if active_goals:
            tg = active_goals[0]
            pct = int((tg["saved"] / tg["target"]) * 100) if tg["target"] > 0 else 0
            if pct > 0: insights.append(f"🎉 Great job! You are {pct}% of the way to your '{tg['name']}' goal.")
        
        if len(insights) == 0 and avg_daily > 0: insights.append(f"💡 You are spending an average of {fmt_inr(avg_daily)} per day this month.")
        if not insights: insights.append("🌱 Log more transactions to unlock personalized insights!")
            
        for ins in insights:
            row = ctk.CTkFrame(self.insights_list_container, fg_color="#1a1d27", corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkFrame(row, width=3, fg_color=ACCENT).pack(side="left", fill="y", pady=6, padx=(6,0))
            ctk.CTkLabel(row, text=ins, font=ctk.CTkFont(size=12), text_color=TEXT_MAIN).pack(side="left", padx=10, pady=8)

        # --- Pie Chart ---
        if self._dash_pie_canvas:
            self._dash_pie_canvas.get_tk_widget().destroy()
            plt.close("all")
        pie_fig = build_pie_chart(month_df)
        self._dash_pie_canvas = embed_chart(pie_fig, self.dash_pie_frame)

        # --- Bar Chart ---
        if self._dash_bar_canvas:
            self._dash_bar_canvas.get_tk_widget().destroy()
        bar_fig = build_bar_chart(df)
        self._dash_bar_canvas = embed_chart(bar_fig, self.dash_bar_frame)

    # ============================================================
    #  ADD EXPENSE PAGE
    # ============================================================

    def _build_add_page(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color=BG_DARK)

        # Header
        ctk.CTkLabel(frame, text="Add New Expense",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT_MAIN).pack(anchor="w", padx=28, pady=(24, 4))
        ctk.CTkLabel(frame, text="Fill in the details below to record an expense.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(
            anchor="w", padx=28)

        # Card form
        card = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=14)
        card.pack(padx=28, pady=20, fill="x")

        # --- Field: Date ---
        self._add_field_label(card, "📅  Date (YYYY-MM-DD)")
        self.entry_date = ctk.CTkEntry(
            card, placeholder_text=str(datetime.date.today()),
            font=ctk.CTkFont(size=13), height=42, corner_radius=8,
            fg_color="#1e2235", border_color="#2d3148", text_color=TEXT_MAIN)
        self.entry_date.pack(fill="x", padx=20, pady=(0, 14))

        # --- Field: Category ---
        cat_lbl_frame = ctk.CTkFrame(card, fg_color="transparent")
        cat_lbl_frame.pack(fill="x", padx=20, pady=(16, 4))
        ctk.CTkLabel(cat_lbl_frame, text="🏷️  Category", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DIM).pack(side="left")
        ctk.CTkButton(cat_lbl_frame, text="⚙ Manage", width=60, height=20, font=ctk.CTkFont(size=11),
                      fg_color="transparent", text_color=ACCENT, hover_color="#1e2235",
                      command=self._open_manage_categories).pack(side="right")

        self.opt_category = ctk.CTkOptionMenu(
            card, values=CATEGORIES, font=ctk.CTkFont(size=13),
            height=42, corner_radius=8,
            fg_color="#1e2235", button_color=ACCENT,
            dropdown_fg_color="#1a1d27", text_color=TEXT_MAIN)
        self.opt_category.set(CATEGORIES[0] if CATEGORIES else "")
        self.opt_category.pack(fill="x", padx=20, pady=(0, 14))

        # --- Field: Amount ---
        self._add_field_label(card, "💵  Amount (₹)")
        self.entry_amount = ctk.CTkEntry(
            card, placeholder_text="0.00",
            font=ctk.CTkFont(size=13), height=42, corner_radius=8,
            fg_color="#1e2235", border_color="#2d3148", text_color=TEXT_MAIN)
        self.entry_amount.pack(fill="x", padx=20, pady=(0, 14))

        # --- Field: Description ---
        self._add_field_label(card, "📝  Description")
        self.entry_desc = ctk.CTkEntry(
            card, placeholder_text="e.g. Lunch at canteen",
            font=ctk.CTkFont(size=13), height=42, corner_radius=8,
            fg_color="#1e2235", border_color="#2d3148", text_color=TEXT_MAIN)
        self.entry_desc.pack(fill="x", padx=20, pady=(0, 20))

        # --- Submit button ---
        ctk.CTkButton(
            card, text="➕  Add Expense",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=48, corner_radius=10,
            fg_color=ACCENT, hover_color="#3a6fd8",
            command=self._submit_expense
        ).pack(padx=20, pady=(0, 20), fill="x")

        # Status label
        self.add_status = ctk.CTkLabel(
            card, text="", font=ctk.CTkFont(size=12),
            text_color=SUCCESS)
        self.add_status.pack(pady=(0, 12))

        return frame

    def _add_field_label(self, parent, text: str):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w", padx=20, pady=(16, 4))

    def _submit_expense(self):
        """Validate form and save to CSV."""
        date_str  = self.entry_date.get().strip() or str(datetime.date.today())
        category  = self.opt_category.get()
        amt_str   = self.entry_amount.get().strip()
        desc      = self.entry_desc.get().strip()

        # Validate date
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.add_status.configure(
                text="⚠  Invalid date format. Use YYYY-MM-DD.", text_color=DANGER)
            return

        # Validate amount
        try:
            amount = float(amt_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.add_status.configure(
                text="⚠  Amount must be a positive number.", text_color=DANGER)
            return

        if not desc:
            desc = "—"

        append_expense(date_str, category, amount, desc)
        self.df = load_data()

        # Clear fields
        self.entry_date.delete(0, "end")
        self.entry_amount.delete(0, "end")
        self.entry_desc.delete(0, "end")
        self.opt_category.set(CATEGORIES[0])

        self.add_status.configure(
            text=f"✅  Expense of {fmt_inr(amount)} added successfully!", text_color=SUCCESS)
        self.after(3000, lambda: self.add_status.configure(text=""))

    def _open_manage_categories(self):
        manage_win = ctk.CTkToplevel(self)
        manage_win.title("Manage Categories")
        manage_win.geometry("300x400")
        manage_win.attributes("-topmost", True)
        
        ctk.CTkLabel(manage_win, text="Manage Categories", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_MAIN).pack(pady=(15, 10))
        
        list_frame = ctk.CTkScrollableFrame(manage_win, fg_color=BG_CARD)
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        def refresh_list():
            for widget in list_frame.winfo_children():
                widget.destroy()
            for cat in CATEGORIES:
                row = ctk.CTkFrame(list_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=cat, text_color=TEXT_MAIN).pack(side="left", padx=5)
                ctk.CTkButton(row, text="🗑", width=30, fg_color=DANGER, hover_color="#b91c1c",
                              command=lambda c=cat: remove_cat(c)).pack(side="right", padx=5)

        def add_cat():
            new_cat = entry.get().strip()
            if new_cat and new_cat not in CATEGORIES:
                CATEGORIES.append(new_cat)
                save_categories(CATEGORIES)
                refresh_list()
                self._refresh_categories()
            entry.delete(0, "end")

        def remove_cat(c):
            if c in CATEGORIES:
                CATEGORIES.remove(c)
                if not CATEGORIES:
                    CATEGORIES.append("Others")
                save_categories(CATEGORIES)
                refresh_list()
                self._refresh_categories()

        refresh_list()
        
        add_frame = ctk.CTkFrame(manage_win, fg_color="transparent")
        add_frame.pack(fill="x", padx=15, pady=15)
        
        entry = ctk.CTkEntry(add_frame, placeholder_text="New Category", text_color=TEXT_MAIN, fg_color="#1e2235", border_color="#2d3148")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(add_frame, text="Add", width=50, fg_color=SUCCESS, hover_color="#16a34a", command=add_cat).pack(side="right")

    def _refresh_categories(self):
        self.opt_category.configure(values=CATEGORIES)
        if self.opt_category.get() not in CATEGORIES:
            self.opt_category.set(CATEGORIES[0] if CATEGORIES else "")

    # ============================================================
    #  TRANSACTIONS PAGE
    # ============================================================

    def _build_transactions_page(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color=BG_DARK)

        # Header
        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(hdr, text="Transactions",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT_MAIN).pack(side="left")

# 🔥 ADVANCED DYNAMIC SEARCH BAR (Desktop)
        search_frame = ctk.CTkFrame(frame, fg_color="#1a1d27", corner_radius=12, border_width=1, border_color=ACCENT)
        search_frame.pack(fill="x", padx=24, pady=8)
        
        ctk.CTkLabel(search_frame, text="🔍 Live Search:", font=ctk.CTkFont(size=13, weight="bold"), 
                     text_color=ACCENT).pack(side="left", padx=(16, 8), pady=12)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Type multiple words to filter anywhere (e.g. 'food 500')...",
                                     font=ctk.CTkFont(size=13), height=40, fg_color="#12151f", border_width=0)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=8)
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_treeview())
        
        clear_btn = ctk.CTkButton(search_frame, text="✖ Clear", font=ctk.CTkFont(size=12, weight="bold"),
                                   height=32, width=60, fg_color="#2d3148", text_color=TEXT_MAIN, 
                                   hover_color="#3f4563",
                                   command=self._clear_search)
        clear_btn.pack(side="right", padx=12, pady=8)

        # ---- Filter Bar ----
        filter_frame = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10)
        filter_frame.pack(fill="x", padx=24, pady=8)

        months = ["All"] + [str(m) for m in range(1, 13)]
        self.txn_month_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(filter_frame, values=months, variable=self.txn_month_var,
                          width=90, height=34, fg_color="#1e2235",
                          button_color=ACCENT, dropdown_fg_color="#1a1d27",
                          font=ctk.CTkFont(size=12),
                          command=lambda _: self._refresh_treeview()
                          ).pack(side="left", padx=4, pady=6)

        current_yr = datetime.date.today().year
        years = ["All"] + [str(y) for y in range(current_yr - 5, current_yr + 1)]
        self.txn_year_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(filter_frame, values=years, variable=self.txn_year_var,
                          width=100, height=34, fg_color="#1e2235",
                          button_color=ACCENT, dropdown_fg_color="#1a1d27",
                          font=ctk.CTkFont(size=12),
                          command=lambda _: self._refresh_treeview()
                          ).pack(side="left", padx=4, pady=6)

        ctk.CTkButton(filter_frame, text="🗑  Delete Selected",
                      font=ctk.CTkFont(size=12), height=34,
                      fg_color=DANGER, hover_color="#b91c1c", width=160,
                      command=self._delete_selected).pack(side="right", padx=16, pady=6)

        # ---- Treeview Table ----
        tree_container = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10)
        tree_container.pack(fill="both", expand=True, padx=24, pady=(4, 16))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background="#1a1d27",
                        foreground=TEXT_MAIN,
                        fieldbackground="#1a1d27",
                        rowheight=32,
                        font=("Segoe UI", 11),
                        borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                        background="#12151f",
                        foreground=TEXT_DIM,
                        font=("Segoe UI", 11, "bold"),
                        relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#ffffff")])

        cols = ("Date", "Category", "Amount", "Description")
        self.tree = Treeview(tree_container, columns=cols, show="headings",
                             style="Custom.Treeview", selectmode="browse")

        col_widths = {"Date": 120, "Category": 130, "Amount": 110, "Description": 400}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths[col], anchor="w")

        vsb = ttk.Scrollbar(tree_container, orient="vertical",
                             command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        vsb.pack(side="right", fill="y", pady=4)

        # Summary bar
        self.txn_summary = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.txn_summary.pack(anchor="w", padx=28, pady=(0, 8))

        return frame

    def _clear_search(self):
        """Clear the dynamic search bar."""
        self.search_entry.delete(0, "end")
        self._refresh_treeview()

    def _refresh_treeview(self):
        """Reload the treeview with live search + optional month/year filter."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        df = self.df.copy()
        m = self.txn_month_var.get()
        y = self.txn_year_var.get()

        if m != "All":
            df = df[df["Date"].dt.month == int(m)]
        if y != "All":
            df = df[df["Date"].dt.year == int(y)]
            
        # 🔥 Apply Dynamic Real-Time Keyword Search
        query_input = getattr(self, "search_entry", None)
        if query_input and query_input.get().strip():
            tokens = query_input.get().strip().lower().split()
            for token in tokens:
                # Check if token exists in ANY column (Date, Category, Amount, or Description)
                mask = df.astype(str).apply(lambda col, t=token: col.str.lower().str.contains(t)).any(axis=1)
                df = df[mask]

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(
                row["Date"].strftime("%Y-%m-%d"),
                row["Category"],
                fmt_inr(row["Amount"]),
                row["Description"],
            ))

        total = df["Amount"].sum()
        self.txn_summary.configure(
            text=f"Showing {len(df)} record(s)  |  Total: {fmt_inr(total)}")

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection",
                                   "Please select a row to delete.", parent=self)
            return

        item = self.tree.item(selected[0])
        vals = item["values"]   # (Date, Category, Amount, Description)
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete expense:\n  Date: {vals[0]}\n  Category: {vals[1]}\n  Amount: {vals[2]}\n\nThis cannot be undone.",
            parent=self
        )
        if not confirm:
            return

        df = self.df.copy()
        # Match on date + category + amount (first match)
        amount_float = float(str(vals[2]).replace("₹", "").replace(",", ""))
        mask = (
            (df["Date"].dt.strftime("%Y-%m-%d") == str(vals[0])) &
            (df["Category"] == str(vals[1])) &
            (df["Amount"].round(2) == round(amount_float, 2)) &
            (df["Description"] == str(vals[3]))
        )
        idx = df[mask].index
        if len(idx) > 0:
            df.drop(idx[0], inplace=True)
            df.reset_index(drop=True, inplace=True)
            save_full_df(df)
            self.df = load_data()
            self._refresh_treeview()
            messagebox.showinfo("Deleted", "Expense record deleted.", parent=self)
        else:
            messagebox.showerror("Error", "Could not find the record to delete.",
                                 parent=self)

    # ============================================================
    #  REPORTS PAGE
    # ============================================================

    def _build_reports_page(self) -> ctk.CTkScrollableFrame:
        frame = ctk.CTkScrollableFrame(self.content, fg_color=BG_DARK,
                                       scrollbar_button_color="#2d3148")

        # Header
        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(hdr, text="Reports",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT_MAIN).pack(side="left")

        # ---- Month Selector ----
        sel_frame = ctk.CTkFrame(frame, fg_color=BG_CARD, corner_radius=10)
        sel_frame.pack(fill="x", padx=24, pady=8)

        ctk.CTkLabel(sel_frame, text="Select Month:",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(
            side="left", padx=16, pady=10)

        months = [str(m) for m in range(1, 13)]
        self.rep_month_var = ctk.StringVar(value=str(datetime.date.today().month))
        ctk.CTkOptionMenu(sel_frame, values=months, variable=self.rep_month_var,
                          width=90, height=34, fg_color="#1e2235",
                          button_color=ACCENT, dropdown_fg_color="#1a1d27",
                          font=ctk.CTkFont(size=12),
                          command=lambda _: self._refresh_reports()
                          ).pack(side="left", padx=4, pady=6)

        current_yr = datetime.date.today().year
        years = [str(y) for y in range(current_yr - 5, current_yr + 1)]
        self.rep_year_var = ctk.StringVar(value=str(current_yr))
        ctk.CTkOptionMenu(sel_frame, values=years, variable=self.rep_year_var,
                          width=100, height=34, fg_color="#1e2235",
                          button_color=ACCENT, dropdown_fg_color="#1a1d27",
                          font=ctk.CTkFont(size=12),
                          command=lambda _: self._refresh_reports()
                          ).pack(side="left", padx=4, pady=6)

        # ---- Export Buttons ----
        ctk.CTkButton(sel_frame, text="📥 Export to CSV",
                      font=ctk.CTkFont(size=12), height=34, width=160,
                      fg_color=SUCCESS, hover_color="#16a34a",
                      command=self._export_csv).pack(side="right", padx=4, pady=6)
        ctk.CTkButton(sel_frame, text="📄 Export Charts to PDF",
                      font=ctk.CTkFont(size=12), height=34, width=190,
                      fg_color=ACCENT2, hover_color="#6d48b0",
                      command=self._export_pdf).pack(side="right", padx=4, pady=6)

        # ---- Summary Card ----
        self.rep_summary_label = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.rep_summary_label.pack(anchor="w", padx=28, pady=(4, 0))

        # ---- Charts ----
        charts_row = ctk.CTkFrame(frame, fg_color="transparent")
        charts_row.pack(fill="both", expand=True, padx=20, pady=8)
        charts_row.grid_columnconfigure(0, weight=2)
        charts_row.grid_columnconfigure(1, weight=3)

        self.rep_pie_frame = ctk.CTkFrame(charts_row, fg_color=BG_CARD,
                                          corner_radius=12)
        self.rep_pie_frame.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="nsew")

        self.rep_bar_frame = ctk.CTkFrame(charts_row, fg_color=BG_CARD,
                                          corner_radius=12)
        self.rep_bar_frame.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="nsew")

        return frame

    def _refresh_reports(self):
        """Redraw report charts based on selected month/year."""
        df = self.df
        try:
            m = int(self.rep_month_var.get())
            y = int(self.rep_year_var.get())
        except ValueError:
            return

        month_df = df[(df["Date"].dt.month == m) & (df["Date"].dt.year == y)]
        month_name = datetime.date(y, m, 1).strftime("%B %Y")

        total = month_df["Amount"].sum()
        self.rep_summary_label.configure(
            text=f"📊  {month_name}  —  Total: {fmt_inr(total)}  |  "
                 f"Transactions: {len(month_df)}")

        # Pie
        if self._rep_pie_canvas:
            self._rep_pie_canvas.get_tk_widget().destroy()
            plt.close("all")
        pie_fig = build_pie_chart(month_df, title=f"Categories — {month_name}")
        self._rep_pie_canvas = embed_chart(pie_fig, self.rep_pie_frame)

        # Bar
        if self._rep_bar_canvas:
            self._rep_bar_canvas.get_tk_widget().destroy()
        bar_fig = build_bar_chart(df, title="Monthly Trend (Last 12 Months)")
        self._rep_bar_canvas = embed_chart(bar_fig, self.rep_bar_frame)

    # ============================================================
    #  EXPORT FUNCTIONS
    # ============================================================

    def _export_csv(self):
        """Copy the full expenses.csv to an export file with timestamp."""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expenses_export_{ts}.csv"
        self.df.copy().assign(
            Date=lambda d: d["Date"].dt.strftime("%Y-%m-%d")
        ).to_csv(filename, index=False)
        messagebox.showinfo("Export Successful",
                            f"CSV exported as:\n{filename}", parent=self)

    def _export_pdf(self):
        """Save pie chart + bar chart + text summary to a single PDF."""
        try:
            m = int(self.rep_month_var.get())
            y = int(self.rep_year_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid month/year selection.", parent=self)
            return

        df = self.df
        month_df = df[(df["Date"].dt.month == m) & (df["Date"].dt.year == y)]
        month_name = datetime.date(y, m, 1).strftime("%B %Y")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expense_report_{month_name.replace(' ', '_')}_{ts}.pdf"

        pie_fig = build_pie_chart(month_df, title=f"Category Breakdown — {month_name}")
        bar_fig = build_bar_chart(df, title="Monthly Trend (Last 12 Months)")

        # Text summary figure
        txt_fig, ax = plt.subplots(figsize=(8, 4), facecolor="#12151f")
        ax.axis("off")
        summary_lines = [
            f"EXPENSE REPORT — {month_name}",
            "",
            f"Total Spending   : {fmt_inr(month_df['Amount'].sum())}",
            f"No. of Records   : {len(month_df)}",
        ]
        if not month_df.empty:
            grp = month_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            summary_lines.append("")
            summary_lines.append("Category Breakdown:")
            for cat, amt in grp.items():
                pct = amt / month_df["Amount"].sum() * 100
                summary_lines.append(f"  {cat:<16} {fmt_inr(amt)}   ({pct:.1f}%)")

        summary_lines += [
            "",
            f"Generated on : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Expense Tracker — Personal Finance Dashboard",
        ]
        ax.text(0.05, 0.95, "\n".join(summary_lines),
                transform=ax.transAxes,
                verticalalignment="top", horizontalalignment="left",
                color=TEXT_MAIN, fontsize=11,
                fontfamily="monospace")

        with pdf_backend.PdfPages(filename) as pp:
            pp.savefig(txt_fig, bbox_inches="tight")
            pp.savefig(pie_fig, bbox_inches="tight")
            pp.savefig(bar_fig, bbox_inches="tight")

        plt.close(txt_fig)
        plt.close(pie_fig)
        plt.close(bar_fig)
        messagebox.showinfo("PDF Exported",
                            f"Report saved as:\n{filename}", parent=self)
                            
    def _clear_all_data(self):
        """Wipes all CSV data completely."""
        confirm1 = messagebox.askyesno("Clear All Data", 
                                       "⚠️ WARNING: This will permanently delete ALL your transactions.\n\nAre you sure you want to proceed?", 
                                       parent=self)
        if not confirm1:
            return
            
        confirm2 = messagebox.askyesno("Final Confirmation", 
                                       "This cannot be undone. Wipe all data?", 
                                       parent=self)
        if not confirm2:
            return

        # Wipe CSV safely
        with open(get_csv_file(), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Description"])
            
        if os.path.exists(get_goals_file()): os.remove(get_goals_file())
            
        self.df = load_data()
        
        # Reload active page
        for key, frame in self.pages.items():
            if frame.winfo_ismapped():
                self.show_page(key)
                break
                
        messagebox.showinfo("Success", "All data has been cleared.", parent=self)


# ================================================================================
#  ENTRY POINT
# ================================================================================

if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()


# ================================================================================
#  PROJECT INFORMATION
# ================================================================================
#
#  INSTALLATION COMMAND:
#      pip install customtkinter pandas matplotlib seaborn
#
#  HOW TO RUN:
#      python main.py
#      (Make sure you are in the same directory as main.py)
#      A file "expenses.csv" will be auto-created on first run.
#
#  FEATURES:
#    ✅  Modern dark-themed GUI using CustomTkinter
#    ✅  Dashboard with 4 summary cards (Total, Month, Avg Daily, Top Category)
#    ✅  Interactive Pie Chart — category-wise breakdown for selected month
#    ✅  Bar Chart — monthly spending trend for last 12 months
#    ✅  Add Expense form with validation (date format + positive amount)
#    ✅  Transactions page with Treeview table + month/year filter
#    ✅  Delete selected expense (updates CSV immediately)
#    ✅  Reports page with month selector and refreshable charts
#    ✅  Export full data to CSV with timestamp
#    ✅  Export Pie + Bar charts + text summary to PDF (matplotlib PdfPages)
#    ✅  Data persisted in expenses.csv (auto-created if missing)
#    ✅  Real-time chart refresh after every add/delete
#    ✅  Clean, well-commented single-file code
#
#  LIBRARIES USED:
#    • customtkinter  — modern dark-themed widgets
#    • pandas         — CSV data management and filtering
#    • matplotlib     — chart rendering and PDF export
#    • seaborn        — chart styling
#    • tkinter.ttk    — Treeview table widget
#
#  PREDEFINED CATEGORIES:
#    Food, Transport, Rent, Entertainment, Bills,
#    Shopping, Healthcare, Others
#
#  CSV FORMAT  (expenses.csv):
#    Date (YYYY-MM-DD), Category, Amount, Description
#
# ================================================================================
