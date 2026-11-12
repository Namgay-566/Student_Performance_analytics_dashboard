import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------- DATA LAYER ----------------------------
class DataManager:
    @staticmethod
    def generate_sample_data(n=50, save_path="students.csv"):
        np.random.seed(42)
        subjects = ["Math", "Science", "English", "History", "Computer"]
        data = {
            "Student_ID": [f"S{str(i).zfill(3)}" for i in range(1, n + 1)],
            "Name": [f"Student_{i}" for i in range(1, n + 1)],
            "Gender": np.random.choice(["Male", "Female"], n),
            "Age": np.random.randint(16, 21, n),
        }
        for sub in subjects:
            data[sub] = np.random.randint(40, 100, n)
        df = pd.DataFrame(data)
        df["Total"] = df[subjects].sum(axis=1)
        df["Average"] = df[subjects].mean(axis=1).round(2)
        df["Grade"] = df["Average"].apply(DataManager._assign_grade)
        df.to_csv(save_path, index=False)
        return df

    @staticmethod
    def _assign_grade(avg):
        if avg >= 90: return "A+"
        elif avg >= 80: return "A"
        elif avg >= 70: return "B"
        elif avg >= 60: return "C"
        elif avg >= 50: return "D"
        return "F"

    @staticmethod
    def load_csv(path):
        df = pd.read_csv(path)
        subjects = ["Math", "Science", "English", "History", "Computer"]
        if "Average" not in df.columns:
            df["Average"] = df[subjects].mean(axis=1).round(2)
        if "Grade" not in df.columns:
            df["Grade"] = df["Average"].apply(DataManager._assign_grade)
        return df

# ---------------------------- ANALYTICS LAYER ----------------------------
class Analyzer:
    SUBJECTS = ["Math", "Science", "English", "History", "Computer"]

    def __init__(self, df):
        self.df = df

    def subject_stats(self):
        return self.df[self.SUBJECTS].agg(["mean", "median", "std", "min", "max"]).round(2)

    def top_students(self, n=5):
        return self.df.nlargest(n, "Average")[["Name", "Average", "Grade"]]

    def grade_distribution(self):
        return self.df["Grade"].value_counts().sort_index()

    def gender_performance(self):
        return self.df.groupby("Gender")[self.SUBJECTS].mean().round(2)

    def pass_fail(self):
        passed = (self.df["Average"] >= 50).sum()
        failed = len(self.df) - passed
        return pd.Series({"Passed": passed, "Failed": failed})

# ---------------------------- GUI LAYER ----------------------------
class DashboardApp:
    # ---- Theme colors ----
    BG        = "#f4f6f9"      # Light gray background
    CARD_BG   = "#ffffff"      # White card background
    PRIMARY   = "#2c3e50"      # Dark blue-slate (toolbar)
    ACCENT    = "#3498db"      # Blue (buttons)
    SUCCESS   = "#27ae60"      # Green
    WARN      = "#e67e22"      # Orange
    DANGER    = "#e74c3c"      # Red
    TEXT      = "#2c3e50"      # Main text color
    MUTED     = "#7f8c8d"      # Muted text

    # Grade → row color mapping
    GRADE_COLORS = {
        "A+": "#d5f5e3", "A": "#d5f5e3",
        "B":  "#d6eaf8", "C": "#fef9e7",
        "D":  "#fdebd0", "F": "#fadbd8",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("📊 Student Performance Analytics Dashboard")
        self.root.geometry("1200x780")
        self.root.configure(bg=self.BG)

        self.df = None
        self.analyzer = None

        self._setup_style()
        self._build_toolbar()
        self._build_tabs()

    # ---------- ttk styling ----------
    def _setup_style(self):
        style = ttk.Style()
        # Use a clean theme
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Notebook tabs
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#dfe6e9",
                        foreground=self.TEXT,
                        padding=(20, 10),
                        font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", self.CARD_BG)],
                  foreground=[("selected", self.ACCENT)])

        # Treeview
        style.configure("Treeview",
                        background=self.CARD_BG,
                        foreground=self.TEXT,
                        fieldbackground=self.CARD_BG,
                        rowheight=28,                    # ← fixes cut-off text
                        font=("Segoe UI", 10),
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=self.PRIMARY,
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        padding=(8, 8),
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[("active", "#34495e")])
        style.map("Treeview",
                  background=[("selected", self.ACCENT)],
                  foreground=[("selected", "white")])

        # Combobox
        style.configure("TCombobox",
                        padding=6,
                        font=("Segoe UI", 10))

    # ---------- Toolbar ----------
    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=self.PRIMARY, height=64)
        bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(bar, text="🎓  Student Analytics",
                 fg="white", bg=self.PRIMARY,
                 font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=20, pady=12)

        # Buttons (right side, in order)
        self._mk_btn(bar, "📂  Load CSV",       self.load_csv,      self.ACCENT)
        self._mk_btn(bar, "🎲  Generate Sample", self.generate_data, self.SUCCESS)
        self._mk_btn(bar, "💾  Export",         self.export_data,   self.WARN)

    def _mk_btn(self, parent, text, cmd, color):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color, fg="white",
                      activebackground=color, activeforeground="white",
                      relief=tk.FLAT, borderwidth=0,
                      padx=16, pady=8,
                      font=("Segoe UI", 10, "bold"),
                      cursor="hand2")
        b.pack(side=tk.RIGHT, padx=6, pady=14)
        # hover effect
        b.bind("<Enter>", lambda e: b.configure(bg=self._lighten(color)))
        b.bind("<Leave>", lambda e: b.configure(bg=color))
        return b

    @staticmethod
    def _lighten(hex_color, amount=0.15):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, int(r + 255 * amount))
        g = min(255, int(g + 255 * amount))
        b = min(255, int(b + 255 * amount))
        return f"#{r:02x}{g:02x}{b:02x}"

    # ---------- Tabs ----------
    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        self.tab_data     = ttk.Frame(self.notebook)
        self.tab_analysis = ttk.Frame(self.notebook)
        self.tab_charts   = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_data,     text="📋  Data")
        self.notebook.add(self.tab_analysis, text="🔍  Analysis")
        self.notebook.add(self.tab_charts,   text="📈  Charts")

        self._build_data_tab()
        self._build_analysis_tab()
        self._build_charts_tab()

    # ---------- Data tab ----------
    def _build_data_tab(self):
        # Status card
        top = tk.Frame(self.tab_data, bg=self.CARD_BG, height=48)
        top.pack(fill=tk.X, padx=8, pady=(8, 0))
        top.pack_propagate(False)

        self.info_label = tk.Label(
            top,
            text="No data loaded. Click 'Generate Sample' or 'Load CSV'.",
            font=("Segoe UI", 11), fg=self.MUTED, bg=self.CARD_BG, anchor="w")
        self.info_label.pack(fill=tk.X, padx=14, pady=12)

        # Table
        table_frame = tk.Frame(self.tab_data, bg=self.CARD_BG)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        columns = ("ID", "Name", "Gender", "Age",
                   "Math", "Science", "English", "History", "Computer",
                   "Average", "Grade")
        self.tree = ttk.Treeview(table_frame, columns=columns,
                                 show="headings", style="Treeview")

        widths = {"ID": 70, "Name": 130, "Gender": 90, "Age": 60,
                  "Math": 80, "Science": 80, "English": 80,
                  "History": 80, "Computer": 90,
                  "Average": 90, "Grade": 70}

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=widths.get(col, 85),
                             anchor="center", stretch=True)

        # Zebra striping tags
        self.tree.tag_configure("odd",  background="#ffffff")
        self.tree.tag_configure("even", background="#f8f9fa")
        for grade, color in self.GRADE_COLORS.items():
            self.tree.tag_configure(f"grade_{grade}", background=color)

        vsb = ttk.Scrollbar(table_frame, orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    # ---------- Analysis tab ----------
    def _build_analysis_tab(self):
        card = tk.Frame(self.tab_analysis, bg=self.CARD_BG)
        card.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.analysis_text = tk.Text(
            card, font=("Consolas", 10),
            wrap=tk.WORD, bg=self.CARD_BG, fg=self.TEXT,
            relief=tk.FLAT, padx=24, pady=20,
            spacing1=2, spacing3=2)
        self.analysis_text.pack(fill=tk.BOTH, expand=True)

        # Nicer output: tag styles for headers
        self.analysis_text.tag_configure(
            "h1", font=("Consolas", 12, "bold"), foreground=self.PRIMARY,
            spacing1=8, spacing3=8)
        self.analysis_text.tag_configure(
            "h2", font=("Consolas", 10, "bold"), foreground=self.ACCENT,
            spacing1=6, spacing3=6)

    # ---------- Charts tab ----------
    def _build_charts_tab(self):
        top = tk.Frame(self.tab_charts, bg=self.BG)
        top.pack(fill=tk.X, padx=8, pady=10)

        tk.Label(top, text="Chart Type:",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.BG, fg=self.TEXT).pack(side=tk.LEFT, padx=(6, 8))

        self.chart_var = tk.StringVar(value="Subject Averages")
        options = ["Subject Averages", "Grade Distribution", "Top 10 Students",
                   "Math vs Science Scatter", "Gender Comparison", "Pass vs Fail"]
        dropdown = ttk.Combobox(top, textvariable=self.chart_var,
                                values=options, state="readonly", width=26)
        dropdown.pack(side=tk.LEFT)
        dropdown.bind("<<ComboboxSelected>>", lambda e: self.render_chart())

        self._mk_btn(top, "🔄  Refresh", self.render_chart, self.SUCCESS)

        self.chart_frame = tk.Frame(self.tab_charts, bg=self.CARD_BG,
                                    highlightbackground="#dcdde1",
                                    highlightthickness=1)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    # ---------- Actions ----------
    def generate_data(self):
        self.df = DataManager.generate_sample_data(50, "students.csv")
        self.analyzer = Analyzer(self.df)
        self._refresh_all()
        messagebox.showinfo("Success", "Generated 50 sample students and saved to students.csv")

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            self.df = DataManager.load_csv(path)
            self.analyzer = Analyzer(self.df)
            self._refresh_all()
            messagebox.showinfo("Success", f"Loaded {len(self.df)} records.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load:\n{e}")

    def export_data(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load data first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="report.csv")
        if path:
            self.df.to_csv(path, index=False)
            messagebox.showinfo("Exported", f"Saved to {path}")

    def _refresh_all(self):
        self._refresh_table()
        self._refresh_analysis()
        self.render_chart()

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, (_, r) in enumerate(self.df.iterrows()):
            grade = str(r["Grade"])
            tag = f"grade_{grade}" if grade in self.GRADE_COLORS else ("even" if i % 2 else "odd")
            self.tree.insert("", tk.END, values=(
                r["Student_ID"], r["Name"], r["Gender"], r["Age"],
                r["Math"], r["Science"], r["English"], r["History"],
                r["Computer"], f"{r['Average']:.2f}", grade
            ), tags=(tag,))

        self.info_label.config(
            text=(f"✅  {len(self.df)} students loaded   |   "
                  f"Class Average: {self.df['Average'].mean():.2f}   |   "
                  f"Top Score: {self.df['Average'].max():.2f}"),
            fg=self.SUCCESS)

    def _refresh_analysis(self):
        a = self.analyzer
        stats = a.subject_stats()
        top = a.top_students(5)
        grades = a.grade_distribution()
        gender = a.gender_performance()

        t = self.analysis_text
        t.delete("1.0", tk.END)

        t.insert(tk.END, "=" * 66 + "\n", "h1")
        t.insert(tk.END, "            📊  CLASS PERFORMANCE REPORT\n", "h1")
        t.insert(tk.END, "=" * 66 + "\n\n", "h1")

        t.insert(tk.END, f"Total Students : {len(self.df)}\n")
        t.insert(tk.END, f"Overall Average: {self.df['Average'].mean():.2f}\n")
        t.insert(tk.END, f"Highest Average: {self.df['Average'].max():.2f}\n")
        t.insert(tk.END, f"Lowest Average : {self.df['Average'].min():.2f}\n")
        t.insert(tk.END, f"Std Deviation  : {self.df['Average'].std():.2f}\n\n")

        t.insert(tk.END, "─" * 66 + "\n", "h2")
        t.insert(tk.END, "📚  SUBJECT-WISE STATISTICS\n", "h2")
        t.insert(tk.END, "─" * 66 + "\n", "h2")
        t.insert(tk.END, f"{'Subject':<12}{'Mean':>8}{'Median':>9}{'Std':>8}{'Min':>7}{'Max':>7}\n")
        for sub in Analyzer.SUBJECTS:
            s = stats[sub]
            t.insert(tk.END,
                     f"{sub:<12}{s['mean']:>8.2f}{s['median']:>9.2f}"
                     f"{s['std']:>8.2f}{s['min']:>7.0f}{s['max']:>7.0f}\n")

        t.insert(tk.END, "\n" + "─" * 66 + "\n", "h2")
        t.insert(tk.END, "🏆  TOP 5 STUDENTS\n", "h2")
        t.insert(tk.END, "─" * 66 + "\n", "h2")
        for i, (_, row) in enumerate(top.iterrows(), 1):
            t.insert(tk.END,
                     f"{i}. {row['Name']:<15}  Average: {row['Average']:>6.2f}   Grade: {row['Grade']}\n")

        t.insert(tk.END, "\n" + "─" * 66 + "\n", "h2")
        t.insert(tk.END, "🎯  GRADE DISTRIBUTION\n", "h2")
        t.insert(tk.END, "─" * 66 + "\n", "h2")
        for grade, count in grades.items():
            bar = "█" * count
            t.insert(tk.END, f"{grade:<4} {count:>3}  {bar}\n")

        t.insert(tk.END, "\n" + "─" * 66 + "\n", "h2")
        t.insert(tk.END, "👥  GENDER-WISE AVERAGE\n", "h2")
        t.insert(tk.END, "─" * 66 + "\n", "h2")
        for g, row in gender.iterrows():
            t.insert(tk.END, f"{g:<8}  Avg: {row.mean():.2f}\n")

    # ---------- Charts ----------
    def render_chart(self):
        if self.df is None:
            return

        for w in self.chart_frame.winfo_children():
            w.destroy()

        chart = self.chart_var.get()
        fig, ax = plt.subplots(figsize=(9, 5), dpi=90)
        fig.patch.set_facecolor(self.CARD_BG)

        palette = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12",
                   "#9b59b6", "#1abc9c", "#e67e22"]

        if chart == "Subject Averages":
            means = self.df[Analyzer.SUBJECTS].mean()
            bars = ax.bar(means.index, means.values,
                          color=palette[:len(means)], edgecolor="white", linewidth=1.5)
            for bar, val in zip(bars, means.values):
                ax.text(bar.get_x() + bar.get_width() / 2, val + 1,
                        f"{val:.1f}", ha="center", fontsize=10, fontweight="bold")
            ax.set_title("Average Marks per Subject", fontweight="bold", fontsize=13)
            ax.set_ylabel("Average Marks")
            ax.set_ylim(0, 105)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="y", alpha=0.3, linestyle="--")

        elif chart == "Grade Distribution":
            grades = self.analyzer.grade_distribution()
            colors = ["#2ecc71", "#27ae60", "#f1c40f", "#e67e22", "#e74c3c", "#c0392b"]
            ax.pie(grades.values, labels=grades.index, autopct="%1.1f%%",
                   colors=colors[:len(grades)], startangle=90,
                   wedgeprops={"edgecolor": "white", "linewidth": 2})
            ax.set_title("Grade Distribution", fontweight="bold", fontsize=13)

        elif chart == "Top 10 Students":
            top10 = self.df.nlargest(10, "Average")
            ax.barh(top10["Name"], top10["Average"],
                    color=plt.cm.viridis(np.linspace(0.2, 0.9, 10)))
            ax.invert_yaxis()
            ax.set_title("Top 10 Students by Average", fontweight="bold", fontsize=13)
            ax.set_xlabel("Average Marks")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="x", alpha=0.3, linestyle="--")

        elif chart == "Math vs Science Scatter":
            colors_map = {"Male": "#3498db", "Female": "#e91e63"}
            for gender, grp in self.df.groupby("Gender"):
                ax.scatter(grp["Math"], grp["Science"], label=gender,
                           alpha=0.75, s=70, c=colors_map.get(gender, "gray"),
                           edgecolors="white", linewidths=1)
            ax.set_xlabel("Math Marks")
            ax.set_ylabel("Science Marks")
            ax.set_title("Math vs Science Performance", fontweight="bold", fontsize=13)
            ax.legend(frameon=True)
            ax.grid(alpha=0.3, linestyle="--")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        elif chart == "Gender Comparison":
            gender = self.analyzer.gender_performance()
            x = np.arange(len(Analyzer.SUBJECTS))
            width = 0.35
            for i, (g, row) in enumerate(gender.iterrows()):
                ax.bar(x + i * width, row.values, width,
                       label=g, color=palette[i], edgecolor="white")
            ax.set_xticks(x + width / 2)
            ax.set_xticklabels(Analyzer.SUBJECTS)
            ax.set_ylabel("Average Marks")
            ax.set_title("Gender-wise Subject Comparison", fontweight="bold", fontsize=13)
            ax.legend(frameon=True)
            ax.grid(axis="y", alpha=0.3, linestyle="--")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        elif chart == "Pass vs Fail":
            pf = self.analyzer.pass_fail()
            bars = ax.bar(pf.index, pf.values,
                          color=[self.SUCCESS, self.DANGER],
                          width=0.5, edgecolor="white", linewidth=2)
            for bar, val in zip(bars, pf.values):
                ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5,
                        str(val), ha="center", fontweight="bold", fontsize=13)
            ax.set_title("Pass vs Fail (Average ≥ 50)", fontweight="bold", fontsize=13)
            ax.set_ylabel("Number of Students")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="y", alpha=0.3, linestyle="--")

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ---------------------------- ENTRY POINT ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()