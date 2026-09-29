import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import math
import time

BG          = "#F0EFED"       
PANEL       = "#E8E6E3"       
SIDEBAR     = "#DDDBD7"       
BORDER      = "#C8C5C0"       
TEXT_DARK   = "#2B2926"       
TEXT_MID    = "#6B6762"       
TEXT_LIGHT  = "#9A9691"       

ACC_DARK    = "#3D3530"       
ACC_MED     = "#6E5F54"       
ACC_LIGHT   = "#A8957F"       
OBST_NODE   = "#4A3F35"       
OBST_TEXT   = "#F5F0EB"       

BST_NODE    = "#8B7355"
BST_TEXT    = "#F5F0EB"

HEAT = ["#EAE8E5","#D5D0C9","#BAB3A8","#9D9487","#7F7468","#645A4D","#4A3F35","#2E2520"]

TRACE_BG    = "#E2DED9"
TRACE_HL    = "#6E5F54"



def obst_dp(keys, freq):
    
    n = len(keys)
    e = [[0.0]*(n+2) for _ in range(n+2)]
    w = [[0.0]*(n+2) for _ in range(n+2)]
    root = [[0]*(n+1) for _ in range(n+1)]

    for i in range(1, n+2):
        e[i][i-1] = 0.0
        w[i][i-1] = 0.0

    for length in range(1, n+1):          
        for i in range(1, n-length+2):    
            j = i + length - 1            
            e[i][j] = float('inf')
            w[i][j] = w[i][j-1] + freq[j-1]
            for r in range(i, j+1):
                t = e[i][r-1] + e[r+1][j] + w[i][j]
                if t < e[i][j]:
                    e[i][j] = t
                    root[i][j] = r
    return e, w, root


def build_tree(root_table, i, j, keys):
    """Recursively build tree as nested dict."""
    if i > j:
        return None
    r = root_table[i][j]
    return {
        "key": keys[r-1],
        "r_idx": r,
        "left":  build_tree(root_table, i,   r-1, keys),
        "right": build_tree(root_table, r+1, j,   keys),
    }


def build_balanced_bst(keys):
    """Build a balanced BST from sorted keys."""
    def helper(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return {
            "key":   keys[mid],
            "r_idx": mid+1,
            "left":  helper(lo, mid-1),
            "right": helper(mid+1, hi),
        }
    return helper(0, len(keys)-1)


def tree_height(node):
    if node is None:
        return 0
    return 1 + max(tree_height(node["left"]), tree_height(node["right"]))


def assign_positions(node, depth=0, counter=[0]):
    """Assign (x_order, depth) to each node via in-order traversal."""
    if node is None:
        return
    assign_positions(node["left"], depth+1, counter)
    node["x_order"] = counter[0]
    node["depth"]   = depth
    counter[0] += 1
    assign_positions(node["right"], depth+1, counter)


def avg_search_cost(node, keys, freq, depth=1):
    """Compute weighted path length (average search cost)."""
    if node is None:
        return 0.0
    total_freq = sum(freq)
    p = freq[node["r_idx"]-1] / total_freq if total_freq else 0
    return p * depth + avg_search_cost(node["left"],  keys, freq, depth+1) \
                     + avg_search_cost(node["right"], keys, freq, depth+1)

class OBSTApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OBST — Optimal Binary Search Tree · Dynamic Programming")
        self.configure(bg=BG)
        self.geometry("1400x860")
        self.minsize(1100, 720)

        self._keys_entries  = []
        self._freq_entries  = []
        self._row_frames    = []
        self._dp_cells      = {}          
        self._trace_steps   = []
        self._trace_idx     = 0
        self._trace_running = False
        self._last_keys     = []
        self._last_freq     = []
        self._last_root     = None

        self._build_ui()
        self._add_row()
        self._add_row()
        self._add_row()


    def _build_ui(self):
        bar = tk.Frame(self, bg=ACC_DARK, height=46)
        bar.pack(fill="x", side="top")
        tk.Label(bar, text="OBST", bg=ACC_DARK, fg="#F5F0EB",
                 font=("Courier", 18, "bold")).pack(side="left", padx=16, pady=8)
        tk.Label(bar, text="Optimal Binary Search Tree  ·  Dynamic Programming",
                 bg=ACC_DARK, fg=ACC_LIGHT,
                 font=("Courier", 11)).pack(side="left", pady=8)

        paned = tk.PanedWindow(self, orient="horizontal",
                               bg=BG, sashwidth=4, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=0, pady=0)

        self._left = tk.Frame(paned, bg=SIDEBAR, width=260)
        paned.add(self._left, minsize=230)

        self._center = tk.Frame(paned, bg=BG)
        paned.add(self._center, minsize=500)

        self._build_left_panel()
        self._build_center_notebook()


    def _build_left_panel(self):
        p = self._left
        tk.Label(p, text="DATA INPUT", bg=SIDEBAR, fg=TEXT_MID,
                 font=("Courier", 9, "bold")).pack(anchor="w", padx=12, pady=(12,4))

        mf = tk.Frame(p, bg=SIDEBAR)
        mf.pack(fill="x", padx=12, pady=4)
        tk.Label(mf, text="Mode:", bg=SIDEBAR, fg=TEXT_DARK,
                 font=("Courier", 9)).pack(side="left")
        self._mode = tk.StringVar(value="freq")
        ttk.Radiobutton(mf, text="Frequency", variable=self._mode,
                        value="freq").pack(side="left", padx=4)
        ttk.Radiobutton(mf, text="Probability", variable=self._mode,
                        value="prob").pack(side="left")

        hf = tk.Frame(p, bg=SIDEBAR)
        hf.pack(fill="x", padx=12, pady=(6,2))
        tk.Label(hf, text="Key", bg=SIDEBAR, fg=TEXT_MID,
                 font=("Courier", 8, "bold"), width=8).pack(side="left")
        tk.Label(hf, text="Freq / Prob", bg=SIDEBAR, fg=TEXT_MID,
                 font=("Courier", 8, "bold")).pack(side="left", padx=8)

        outer = tk.Frame(p, bg=SIDEBAR)
        outer.pack(fill="both", expand=True, padx=6, pady=2)
        canvas = tk.Canvas(outer, bg=SIDEBAR, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self._rows_frame = tk.Frame(canvas, bg=SIDEBAR)
        self._rows_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self._rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        bf = tk.Frame(p, bg=SIDEBAR)
        bf.pack(fill="x", padx=10, pady=6)
        self._btn(bf, "+ Add Row",    self._add_row,      ACC_MED,   "#F5F0EB").pack(fill="x", pady=2)
        self._btn(bf, "✓ Sanitize",   self._sanitize,     BORDER,    TEXT_DARK).pack(fill="x", pady=2)
        sep = tk.Frame(p, bg=BORDER, height=1)
        sep.pack(fill="x", padx=10, pady=4)
        self._btn(bf, "▶  Run OBST",  self._run_obst,     ACC_DARK,  "#F5F0EB").pack(fill="x", pady=2)
        self._btn(bf, "↺  Reset",     self._reset_all,    PANEL,     TEXT_DARK).pack(fill="x", pady=2)

        self._status = tk.Label(p, text="", bg=SIDEBAR, fg=TEXT_MID,
                                font=("Courier", 8), wraplength=220, justify="left")
        self._status.pack(fill="x", padx=12, pady=4)

    def _btn(self, parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg, relief="flat",
                         font=("Courier", 9, "bold"),
                         cursor="hand2", padx=6, pady=5,
                         activebackground=ACC_LIGHT, activeforeground=TEXT_DARK,
                         bd=0)

    def _add_row(self, key_val="", freq_val=""):
        row = len(self._keys_entries) + 1
        f = tk.Frame(self._rows_frame, bg=SIDEBAR)
        f.pack(fill="x", pady=2, padx=4)

        ke = tk.Entry(f, width=7, bg=PANEL, fg=TEXT_DARK, relief="flat",
                      font=("Courier", 10), insertbackground=TEXT_DARK)
        ke.pack(side="left", padx=(0,4), ipady=3)
        ke.insert(0, key_val)

        fe = tk.Entry(f, width=9, bg=PANEL, fg=TEXT_DARK, relief="flat",
                      font=("Courier", 10), insertbackground=TEXT_DARK)
        fe.pack(side="left", padx=(0,4), ipady=3)
        fe.insert(0, freq_val)

        del_btn = tk.Button(f, text="✕", bg=SIDEBAR, fg=TEXT_MID,
                            relief="flat", font=("Courier", 8), cursor="hand2",
                            command=lambda ff=f, ke=ke, fe=fe: self._del_row(ff, ke, fe),
                            bd=0, padx=2)
        del_btn.pack(side="left")

        self._keys_entries.append(ke)
        self._freq_entries.append(fe)
        self._row_frames.append(f)

    def _del_row(self, frame, ke, fe):
        idx = self._keys_entries.index(ke)
        self._keys_entries.pop(idx)
        self._freq_entries.pop(idx)
        self._row_frames.pop(idx)
        frame.destroy()

    def _sanitize(self):
        raw = []
        for ke, fe in zip(self._keys_entries, self._freq_entries):
            k = ke.get().strip()
            f = fe.get().strip()
            if k and f:
                try:
                    raw.append((float(k), float(f)))
                except ValueError:
                    messagebox.showerror("Validation Error",
                                         f"Non-numeric value: key='{k}' freq='{f}'")
                    return
        if not raw:
            messagebox.showwarning("Empty", "Add at least one key/frequency pair.")
            return
        seen = set()
        unique = []
        for k, f in sorted(raw, key=lambda x: x[0]):
            if k not in seen:
                seen.add(k)
                unique.append((k, f))
        for i, frame in enumerate(self._row_frames):
            frame.destroy()
        self._keys_entries.clear()
        self._freq_entries.clear()
        self._row_frames.clear()
        for k, f in unique:
            kstr = str(int(k)) if k == int(k) else str(k)
            fstr = str(int(f)) if f == int(f) else str(round(f, 4))
            self._add_row(kstr, fstr)
        self._status.config(text=f"Sanitized: {len(unique)} unique sorted keys.")


    def _build_center_notebook(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",          background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",      background=PANEL, foreground=TEXT_MID,
                        font=("Courier", 9, "bold"), padding=[12, 5])
        style.map("TNotebook.Tab",
                  background=[("selected", ACC_DARK)],
                  foreground=[("selected", "#F5F0EB")])

        self._nb = ttk.Notebook(self._center)
        self._nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._tab_tree  = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_tree, text=" ⌥ Tree Comparison ")

        self._tab_dp    = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_dp,   text=" ▦ DP Matrix ")

        self._tab_trace = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_trace, text=" ▷ Algorithm Trace ")

        self._build_tree_tab()
        self._build_dp_tab()
        self._build_trace_tab()


    def _build_tree_tab(self):
        t = self._tab_tree
        cf = tk.Frame(t, bg=BG)
        cf.pack(fill="both", expand=True)

        lf = tk.Frame(cf, bg=BG)
        lf.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tk.Label(lf, text="OPTIMAL BST  (DP)", bg=BG, fg=ACC_DARK,
                 font=("Courier", 11, "bold")).pack(anchor="w", pady=(4,2))
        self._obst_cost_lbl = tk.Label(lf, text="Avg Search Cost: —",
                                       bg=BG, fg=TEXT_MID, font=("Courier", 9))
        self._obst_cost_lbl.pack(anchor="w")
        self._canvas_obst = tk.Canvas(lf, bg=PANEL, highlightthickness=1,
                                      highlightbackground=BORDER)
        self._canvas_obst.pack(fill="both", expand=True)

        sep = tk.Frame(cf, bg=BORDER, width=1)
        sep.pack(side="left", fill="y", pady=12)

        rf = tk.Frame(cf, bg=BG)
        rf.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tk.Label(rf, text="STANDARD BALANCED BST", bg=BG, fg=BST_NODE,
                 font=("Courier", 11, "bold")).pack(anchor="w", pady=(4,2))
        self._bst_cost_lbl = tk.Label(rf, text="Avg Search Cost: —",
                                      bg=BG, fg=TEXT_MID, font=("Courier", 9))
        self._bst_cost_lbl.pack(anchor="w")
        self._canvas_bst = tk.Canvas(rf, bg=PANEL, highlightthickness=1,
                                     highlightbackground=BORDER)
        self._canvas_bst.pack(fill="both", expand=True)


    def _build_dp_tab(self):
        t = self._tab_dp
        info = tk.Frame(t, bg=BG)
        info.pack(fill="x", padx=10, pady=6)
        tk.Label(info, text="Click any cell to highlight its subtree on the OBST canvas.",
                 bg=BG, fg=TEXT_MID, font=("Courier", 9)).pack(side="left")

        lg = tk.Frame(info, bg=BG)
        lg.pack(side="right")
        tk.Label(lg, text="Cost:", bg=BG, fg=TEXT_MID, font=("Courier", 8)).pack(side="left")
        for i, h in enumerate(HEAT):
            tk.Label(lg, bg=h, width=2, relief="flat").pack(side="left", padx=1)
        tk.Label(lg, text="Low → High", bg=BG, fg=TEXT_MID, font=("Courier", 8)).pack(side="left", padx=4)

        outer = tk.Frame(t, bg=BG)
        outer.pack(fill="both", expand=True, padx=10, pady=4)
        self._dp_canvas  = tk.Canvas(outer, bg=BG, highlightthickness=0)
        hscroll = ttk.Scrollbar(outer, orient="horizontal",
                                command=self._dp_canvas.xview)
        vscroll = ttk.Scrollbar(outer, orient="vertical",
                                command=self._dp_canvas.yview)
        self._dp_inner = tk.Frame(self._dp_canvas, bg=BG)
        self._dp_inner.bind("<Configure>",
            lambda e: self._dp_canvas.configure(
                scrollregion=self._dp_canvas.bbox("all")))
        self._dp_canvas.create_window((0,0), window=self._dp_inner, anchor="nw")
        self._dp_canvas.configure(xscrollcommand=hscroll.set,
                                  yscrollcommand=vscroll.set)
        self._dp_canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")

        self._dp_detail = tk.Label(t, text="", bg=TRACE_BG, fg=TEXT_DARK,
                                   font=("Courier", 9), anchor="w", padx=8, pady=4)
        self._dp_detail.pack(fill="x", padx=10, pady=(0,6))


    def _build_trace_tab(self):
        t = self._tab_trace
        ctrl = tk.Frame(t, bg=BG)
        ctrl.pack(fill="x", padx=10, pady=8)
        self._btn(ctrl, "◀ Prev", self._trace_prev, PANEL, TEXT_DARK).pack(side="left", padx=4)
        self._btn(ctrl, "▶ Next", self._trace_next, ACC_MED, "#F5F0EB").pack(side="left", padx=4)
        self._btn(ctrl, "⏵ Auto Play", self._trace_auto, ACC_DARK, "#F5F0EB").pack(side="left", padx=4)
        self._btn(ctrl, "⏹ Stop", self._trace_stop, PANEL, TEXT_DARK).pack(side="left", padx=4)

        self._trace_progress = tk.Label(ctrl, text="Step 0 / 0", bg=BG, fg=TEXT_MID,
                                        font=("Courier", 9))
        self._trace_progress.pack(side="right", padx=10)

        tf = tk.Frame(t, bg=BG)
        tf.pack(fill="both", expand=True, padx=10, pady=4)
        self._trace_text = tk.Text(tf, bg=TRACE_BG, fg=TEXT_DARK,
                                   font=("Courier", 10), relief="flat",
                                   state="disabled", wrap="word",
                                   padx=10, pady=8)
        ts = ttk.Scrollbar(tf, orient="vertical", command=self._trace_text.yview)
        self._trace_text.configure(yscrollcommand=ts.set)
        self._trace_text.pack(side="left", fill="both", expand=True)
        ts.pack(side="right", fill="y")

        self._trace_text.tag_configure("header", font=("Courier", 11, "bold"),
                                       foreground=ACC_DARK)
        self._trace_text.tag_configure("highlight", background=ACC_MED,
                                       foreground="#F5F0EB")
        self._trace_text.tag_configure("best", foreground=OBST_NODE,
                                       font=("Courier", 10, "bold"))
        self._trace_text.tag_configure("normal", foreground=TEXT_DARK)
        self._trace_text.tag_configure("dim", foreground=TEXT_LIGHT)

    def _get_data(self):
        keys, freqs = [], []
        for ke, fe in zip(self._keys_entries, self._freq_entries):
            k = ke.get().strip()
            f = fe.get().strip()
            if k and f:
                try:
                    keys.append(float(k))
                    freqs.append(float(f))
                except ValueError:
                    return None, None
        return keys, freqs

    def _run_obst(self):
        keys, freqs = self._get_data()
        if not keys:
            messagebox.showwarning("No Data", "Please enter keys and frequencies.")
            return
        if len(keys) < 2:
            messagebox.showwarning("Too Few", "Enter at least 2 keys.")
            return

        n = len(keys)
        e, w, root_table = obst_dp(keys, freqs)
        obst_tree = build_tree(root_table, 1, n, keys)
        bst_tree  = build_balanced_bst(keys)

        self._last_keys  = keys
        self._last_freq  = freqs
        self._last_root  = root_table

        total_f = sum(freqs)
        norm_freq = [f/total_f for f in freqs]
        obst_cost = e[1][n] / total_f
        bst_cost  = avg_search_cost(bst_tree, keys, freqs)

        self._obst_cost_lbl.config(
            text=f"Avg Search Cost: {obst_cost:.4f}  {'★ Better' if obst_cost<=bst_cost else ''}")
        self._bst_cost_lbl.config(
            text=f"Avg Search Cost: {bst_cost:.4f}  {'★ Better' if bst_cost<obst_cost else ''}")

        self._draw_tree(obst_tree, self._canvas_obst, OBST_NODE, OBST_TEXT, ACC_DARK)
        self._draw_tree(bst_tree,  self._canvas_bst,  BST_NODE,  BST_TEXT,  ACC_MED)
        self._build_dp_grid(e, w, root_table, n, keys)
        self._build_trace(e, w, root_table, n, keys)
        self._status.config(text=f"Done. n={n} keys. OBST cost={obst_cost:.4f}")
        self._nb.select(self._tab_tree)


    def _draw_tree(self, tree, canvas, node_color, text_color, edge_color):
        canvas.delete("all")
        if tree is None:
            return
        counter = [0]
        assign_positions(tree, 0, counter)
        n_nodes = counter[0]
        h = tree_height(tree)

        canvas.update_idletasks()
        W = canvas.winfo_width()  or 600
        H = canvas.winfo_height() or 400
        pad_x = max(30, W // (n_nodes + 1))
        pad_y = max(40, (H - 30) // (h + 1))
        r = min(22, pad_x // 2 - 2, pad_y // 2 - 4)

        def pos(node):
            x = (node["x_order"] + 1) * (W / (n_nodes + 1))
            y = (node["depth"] + 1) * pad_y
            return x, y

        def draw_node(node):
            if node is None:
                return
            x, y = pos(node)
            if node["left"]:
                cx, cy = pos(node["left"])
                canvas.create_line(x, y, cx, cy, fill=edge_color, width=2)
                draw_node(node["left"])
            if node["right"]:
                cx, cy = pos(node["right"])
                canvas.create_line(x, y, cx, cy, fill=edge_color, width=2)
                draw_node(node["right"])
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=node_color,
                               outline=edge_color, width=2)
            k = node["key"]
            label = str(int(k)) if k == int(k) else str(round(k, 2))
            canvas.create_text(x, y, text=label, fill=text_color,
                               font=("Courier", 9, "bold"))

        draw_node(tree)

    def _highlight_subtree(self, canvas, tree, i, j, keys, node_color, edge_color):
        """Re-draw with highlighted subtree [i,j] (1-indexed)."""
        self._draw_tree(tree, canvas, node_color, OBST_TEXT, edge_color)
        if tree is None:
            return
        n_nodes = sum(1 for _ in self._iter_nodes(tree))
        h = tree_height(tree)
        canvas.update_idletasks()
        W = canvas.winfo_width() or 600
        H = canvas.winfo_height() or 400
        pad_y = max(40, (H - 30) // (h + 1))
        r = min(22, 28)

        target_keys = set(keys[k-1] for k in range(i, j+1))

        def recolor(node):
            if node is None:
                return
            recolor(node["left"])
            recolor(node["right"])
            if node["key"] in target_keys:
                x = (node["x_order"] + 1) * (W / (n_nodes + 1))
                y = (node["depth"] + 1) * pad_y
                canvas.create_oval(x-r, y-r, x+r, y+r,
                                   fill=ACC_LIGHT, outline=ACC_DARK, width=3)
                k = node["key"]
                label = str(int(k)) if k == int(k) else str(round(k, 2))
                canvas.create_text(x, y, text=label, fill=TEXT_DARK,
                                   font=("Courier", 10, "bold"))
        recolor(tree)

    def _iter_nodes(self, node):
        if node is None:
            return
        yield node
        yield from self._iter_nodes(node["left"])
        yield from self._iter_nodes(node["right"])


    def _build_dp_grid(self, e, w, root_table, n, keys):
        for widget in self._dp_inner.winfo_children():
            widget.destroy()
        self._dp_cells.clear()

        CELL_W = 72
        CELL_H = 38

        max_e = max(e[i][j] for i in range(1, n+1) for j in range(i, n+1))
        min_e = min(e[i][j] for i in range(1, n+1) for j in range(i, n+1))

        def heat_color(val):
            if max_e == min_e:
                return HEAT[0]
            idx = int((val - min_e) / (max_e - min_e) * (len(HEAT)-1))
            return HEAT[max(0, min(idx, len(HEAT)-1))]

        tk.Label(self._dp_inner, text="i \\ j", bg=BG, fg=TEXT_MID,
                 font=("Courier", 8, "bold"),
                 width=6, height=2, relief="flat").grid(row=0, column=0, padx=1, pady=1)
        for j in range(1, n+1):
            kj = keys[j-1]
            kstr = str(int(kj)) if kj == int(kj) else str(round(kj,2))
            tk.Label(self._dp_inner, text=f"j={j}\n({kstr})", bg=PANEL, fg=TEXT_MID,
                     font=("Courier", 7), width=9, height=2,
                     relief="flat").grid(row=0, column=j, padx=1, pady=1)

        for i in range(1, n+1):
            ki = keys[i-1]
            kstr = str(int(ki)) if ki == int(ki) else str(round(ki,2))
            tk.Label(self._dp_inner, text=f"i={i}\n({kstr})", bg=PANEL, fg=TEXT_MID,
                     font=("Courier", 7), width=6, height=2,
                     relief="flat").grid(row=i, column=0, padx=1, pady=1)
            for j in range(1, n+1):
                if j < i:
                    lbl = tk.Label(self._dp_inner, text="", bg=BG,
                                   width=9, height=2, relief="flat")
                    lbl.grid(row=i, column=j, padx=1, pady=1)
                else:
                    cost = e[i][j]
                    root_k = root_table[i][j]
                    rk = keys[root_k-1]
                    rkstr = str(int(rk)) if rk == int(rk) else str(round(rk,2))
                    bg = heat_color(cost)
                    fg = "#F5F0EB" if HEAT.index(bg) > 3 else TEXT_DARK
                    text = f"{cost:.2f}\nr={rkstr}"
                    lbl = tk.Label(self._dp_inner, text=text,
                                   bg=bg, fg=fg,
                                   font=("Courier", 7), width=9, height=2,
                                   relief="flat", cursor="hand2")
                    lbl.grid(row=i, column=j, padx=1, pady=1)
                    self._dp_cells[(i, j)] = lbl
                    lbl.bind("<Button-1>",
                             lambda e, ii=i, jj=j: self._dp_cell_click(ii, jj))
                    lbl.bind("<Enter>",
                             lambda e, lbl=lbl, bg=bg: lbl.config(
                                 relief="sunken", bd=1))
                    lbl.bind("<Leave>",
                             lambda e, lbl=lbl: lbl.config(relief="flat", bd=0))

    def _dp_cell_click(self, i, j):
        if not self._last_keys:
            return
        keys = self._last_keys
        root_table = self._last_root
        e, w, _ = obst_dp(keys, self._last_freq)
        root_k = root_table[i][j]
        rk = keys[root_k-1]
        rkstr = str(int(rk)) if rk == int(rk) else str(round(rk, 2))
        ki_str = str(int(keys[i-1])) if keys[i-1]==int(keys[i-1]) else str(round(keys[i-1],2))
        kj_str = str(int(keys[j-1])) if keys[j-1]==int(keys[j-1]) else str(round(keys[j-1],2))
        self._dp_detail.config(
            text=f"  Range [{i},{j}]  keys {ki_str}..{kj_str}  |  "
                 f"Optimal Root: {rkstr}  |  Cost e[{i}][{j}] = {e[i][j]:.4f}  |  "
                 f"Weight w = {w[i][j]:.4f}")
        obst_tree = build_tree(root_table, 1, len(keys), keys)
        counter = [0]
        assign_positions(obst_tree, 0, counter)
        self._highlight_subtree(self._canvas_obst, obst_tree, i, j,
                                keys, OBST_NODE, ACC_DARK)
        self._nb.select(self._tab_tree)


    def _build_trace(self, e, w, root_table, n, keys):
        self._trace_steps = []

        def ks(idx):
            k = keys[idx-1]
            return str(int(k)) if k == int(k) else str(round(k, 2))

        self._trace_steps.append({
            "header": "OBST — Algorithm Overview",
            "body": (
                f"We have n={n} keys: {', '.join(ks(i+1) for i in range(n))}\n\n"
                "The standard O(n³) dynamic programming algorithm fills a table\n"
                "e[i][j] = minimum expected search cost for keys i..j.\n\n"
                "We iterate over chain lengths L = 1, 2, ..., n.\n"
                "For each range [i, j], we try every possible root r in [i,j]\n"
                "and pick the one with minimum cost."
            ),
            "highlight": []
        })

        for length in range(1, n+1):
            self._trace_steps.append({
                "header": f"Chain Length L = {length}",
                "body": (
                    f"Solving all sub-problems of length {length}.\n"
                    f"There are {n-length+1} sub-problem(s) of this length.\n"
                    f"Each sub-problem tests up to {length} root candidate(s)."
                ),
                "highlight": []
            })
            for i in range(1, n-length+2):
                j = i + length - 1
                best_r = root_table[i][j]
                lines = [f"Sub-problem  [{i}, {j}]  keys {ks(i)}..{ks(j)}\n",
                         f"Weight  w[{i}][{j}] = {w[i][j]:.4f}\n\n",
                         "Testing each root r:\n"]
                candidates = []
                for r in range(i, j+1):
                    cost_r = e[i][r-1] + e[r+1][j] + w[i][j]
                    marker = " ◀ BEST" if r == best_r else ""
                    candidates.append((r, cost_r, marker))
                    lines.append(f"  r = {ks(r)} : e[{i}][{r-1}] + e[{r+1}][{j}] + {w[i][j]:.4f}"
                                 f" = {cost_r:.4f}{marker}\n")
                lines.append(f"\n→ Optimal root for [{i},{j}] = {ks(best_r)}")
                lines.append(f"\n→ e[{i}][{j}] = {e[i][j]:.4f}")
                self._trace_steps.append({
                    "header": f"L={length}  ·  Range [{i}, {j}]",
                    "body": "".join(lines),
                    "highlight": [(i, j)],
                    "best_r": best_r,
                    "candidates": candidates
                })

        self._trace_steps.append({
            "header": "Result",
            "body": (
                f"Final answer: e[1][{n}] = {e[1][n]:.4f}\n\n"
                f"Total sum of frequencies = {sum(self._last_freq):.4f}\n"
                f"Average search cost = {e[1][n]/sum(self._last_freq):.4f}\n\n"
                "The OBST is stored in root[i][j] table.\n"
                "Navigate to the 'Tree Comparison' tab to see both trees."
            ),
            "highlight": []
        })

        self._trace_idx = 0
        self._render_trace_step()

    def _render_trace_step(self):
        if not self._trace_steps:
            return
        step = self._trace_steps[self._trace_idx]
        total = len(self._trace_steps)
        self._trace_progress.config(
            text=f"Step {self._trace_idx+1} / {total}")

        t = self._trace_text
        t.configure(state="normal")
        t.delete("1.0", "end")
        t.insert("end", step["header"] + "\n", "header")
        t.insert("end", "─" * 60 + "\n\n", "dim")
        body = step.get("body", "")
        for line in body.splitlines(keepends=True):
            if "◀ BEST" in line:
                t.insert("end", line, "best")
            else:
                t.insert("end", line, "normal")
        t.configure(state="disabled")

        for cell_lbl in self._dp_cells.values():
            bg = cell_lbl.cget("bg")
            cell_lbl.config(relief="flat", bd=0)
        for (ci, cj) in step.get("highlight", []):
            if (ci, cj) in self._dp_cells:
                self._dp_cells[(ci, cj)].config(relief="ridge", bd=3)

    def _trace_prev(self):
        if self._trace_idx > 0:
            self._trace_idx -= 1
            self._render_trace_step()

    def _trace_next(self):
        if self._trace_idx < len(self._trace_steps) - 1:
            self._trace_idx += 1
            self._render_trace_step()

    def _trace_auto(self):
        self._trace_running = True
        self._auto_step()

    def _auto_step(self):
        if not self._trace_running:
            return
        if self._trace_idx < len(self._trace_steps) - 1:
            self._trace_idx += 1
            self._render_trace_step()
            self.after(900, self._auto_step)
        else:
            self._trace_running = False

    def _trace_stop(self):
        self._trace_running = False

    def _reset_all(self):
        for frame in self._row_frames:
            frame.destroy()
        self._keys_entries.clear()
        self._freq_entries.clear()
        self._row_frames.clear()
        self._canvas_obst.delete("all")
        self._canvas_bst.delete("all")
        for w in self._dp_inner.winfo_children():
            w.destroy()
        self._dp_cells.clear()
        self._trace_steps.clear()
        self._trace_idx = 0
        self._last_keys.clear()
        self._last_freq.clear()
        self._last_root = None
        t = self._trace_text
        t.configure(state="normal")
        t.delete("1.0", "end")
        t.configure(state="disabled")
        self._status.config(text="Reset.")
        self._obst_cost_lbl.config(text="Avg Search Cost: —")
        self._bst_cost_lbl.config(text="Avg Search Cost: —")
        self._dp_detail.config(text="")
        self._add_row()
        self._add_row()
        self._add_row()

if __name__ == "__main__":
    app = OBSTApp()
    example = [("10","3"),("20","3"),("30","1"),("40","1")]
    for frame in list(app._row_frames):
        frame.destroy()
    app._keys_entries.clear()
    app._freq_entries.clear()
    app._row_frames.clear()
    for k, f in example:
        app._add_row(k, f)
    app.mainloop()
