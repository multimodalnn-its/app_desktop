#!/usr/bin/env python3
"""
ITS — Project Manager
Design fedele al Design System ITS (Inter · DM Mono · palette verde #0F6E56)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os, hashlib, sys
from datetime import datetime, date
import uuid

# ─── PERCORSI ────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_FILE   = os.path.join(BASE_DIR, "data", "projects.json")
CONFIG_FILE = os.path.join(BASE_DIR, "data", "config.json")
ASSETS_DIR  = os.path.join(BASE_DIR, "assets")
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ─── DESIGN SYSTEM — DARK THEME ─────────────────────────────
# Colori dark mode (esatti dal DS: @media prefers-color-scheme: dark)
C = {
    "bg":           "#111110",
    "surface":      "#1C1C1A",
    "text":         "#EEEEE8",
    "muted":        "#888882",
    "faint":        "#2A2A28",
    "accent":       "#1D9E75",
    "accent_mid":   "#0F6E56",
    "accent_light": "#083426",
    "danger":       "#E05C5C",
    "danger_bg":    "#2A1010",
    "warn_bg":      "#3A2400",
    "warn_text":    "#EF9F27",
    # tag area dark
    "neuro_bg":  "#0C2A44", "neuro_text":  "#85B7EB",
    "hw_bg":     "#083426", "hw_text":     "#5DCAA5",
    "biz_bg":    "#3A2400", "biz_text":    "#EF9F27",
    "cult_bg":   "#1E1A44", "cult_text":   "#AFA9EC",
}

# Font: Inter per testo, DM Mono per etichette/monospace
F = {
    "hero":   ("Inter", 22, "bold"),
    "h1":     ("Inter", 16, "bold"),
    "h2":     ("Inter", 13, "bold"),
    "body":   ("Inter", 13),
    "small":  ("Inter", 11),
    "micro":  ("Inter", 10),
    "mono":   ("DM Mono", 10),
    "mono_s": ("DM Mono", 9),
}

STATUS_COLORS = {
    "In corso":   (C["hw_bg"],    C["hw_text"]),
    "Da fare":    (C["cult_bg"],  C["cult_text"]),
    "Completato": (C["neuro_bg"], C["neuro_text"]),
    "In pausa":   (C["biz_bg"],   C["biz_text"]),
}

# ─── UTILITÀ ─────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def load_cfg():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}
def save_cfg(d):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(d, f, indent=2)
def load_projects():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []
def save_projects(p):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(p, f, indent=2, ensure_ascii=False)

# ─── COMPONENTI BASE ─────────────────────────────────────────
def sep(parent, pad_y=(8, 8)):
    f = tk.Frame(parent, height=1, bg=C["faint"])
    f.pack(fill="x", pady=pad_y)
    return f

def eyebrow(parent, text, **kw):
    return tk.Label(parent, text=text.upper(),
                    font=F["mono"], fg=C["accent"], bg=kw.pop("bg", C["bg"]),
                    **kw)

def card(parent, **kw):
    """Frame stile card: sfondo bianco, bordo sottile 0.5px, radius simulato."""
    return tk.Frame(parent,
                    bg=C["surface"],
                    highlightbackground=C["faint"],
                    highlightthickness=1,
                    **kw)

class Btn(tk.Button):
    """Pulsante design system: flat, hover, varianti."""
    VARIANTS = {
        "primary": (C["accent"],    "#FFFFFF", C["accent_mid"]),
        "ghost":   (C["bg"],        C["text"],  C["faint"]),
        "outline": (C["surface"],   C["text"],  C["bg"]),
        "danger":  (C["danger_bg"], C["danger"], "#F5C6C6"),
    }
    def __init__(self, parent, text, cmd=None, variant="primary", small=False, **kw):
        bg, fg, hov = self.VARIANTS.get(variant, self.VARIANTS["primary"])
        fnt = F["small"] if small else F["body"]
        px, py = (10, 3) if small else (14, 6)
        super().__init__(parent, text=text, command=cmd,
                         bg=bg, fg=fg, font=fnt,
                         relief="flat", bd=0, cursor="hand2",
                         padx=px, pady=py, **kw)
        self._bg, self._hov = bg, hov
        self.bind("<Enter>", lambda e: self.config(bg=self._hov))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))

class Badge(tk.Label):
    def __init__(self, parent, text, status="Da fare", **kw):
        bg, fg = STATUS_COLORS.get(status, (C["cult_bg"], C["cult_text"]))
        super().__init__(parent, text=text, font=F["mono_s"],
                         bg=bg, fg=fg, padx=8, pady=2, relief="flat", **kw)

# ─── LOGO ────────────────────────────────────────────────────
# ViewBox originale SVG: 595.28 × 841.89 (proporzione A4 verticale ~0.707)
_LOGO_W = 595.28
_LOGO_H = 841.89
_LOGO_RATIO = _LOGO_W / _LOGO_H  # ~0.707

def add_logo(parent, height=80):
    """
    Mostra il logo rispettando le proporzioni originali.
    - Se esiste assets/logo.png: lo usa (thumbnail proporzionale)
    - Altrimenti: ridisegna l'SVG in Canvas con le proporzioni corrette
    height = altezza desiderata in pixel; la larghezza si calcola automaticamente
    """
    width = int(height * _LOGO_RATIO)  # mantieni proporzioni A4
    logo_png = os.path.join(ASSETS_DIR, "logo.png")
    try:
        from PIL import Image, ImageTk
        img = Image.open(logo_png).convert("RGBA")
        # thumbnail proporzionale: non deforma
        img.thumbnail((width * 2, height * 2), Image.LANCZOS)
        # ritaglia al centro se necessario
        img = img.resize((width, height), Image.LANCZOS)
        ph = ImageTk.PhotoImage(img)
        lbl = tk.Label(parent, image=ph, bg=parent.cget("bg"), bd=0)
        lbl.image = ph
        lbl.pack(pady=(20, 8))
        return
    except Exception:
        pass

    # ── Fallback: ridisegno vettoriale dell'SVG originale ──────
    # SVG viewBox: 595.28 × 841.89
    # Scala per adattare all'altezza richiesta
    sx = width  / _LOGO_W
    sy = height / _LOGO_H

    c = tk.Canvas(parent, width=width, height=height,
                  bg=parent.cget("bg"), highlightthickness=0)
    c.pack(pady=(20, 8))

    col = C["accent"]  # colore verde accent (dark mode), visibile su sfondo scuro

    def px(x): return x * sx
    def py(y): return y * sy

    # Rettangolo esterno (cornice)
    c.create_rectangle(px(17.53), py(87.4), px(574.88), py(644.75),
                       outline=col, width=max(1, int(2*sx)))

    # Tetto a V (linea spezzata sinistra-apice-destra)
    roof = [
        px(20.79), py(256.35),
        px(214.7),  py(250.48),
        px(296.21), py(162.51),
        px(377.66), py(250.48),
        px(571.62), py(256.35),
    ]
    c.create_line(*roof, fill=col, width=max(1, int(2*sx)))

    # Seconda fascia orizzontale (balcone)
    c.create_line(px(20.79),  py(407.85), px(214.71), py(407.85),
                  fill=col, width=max(1, int(1.5*sx)))
    c.create_line(px(377.66), py(407.85), px(571.62), py(407.85),
                  fill=col, width=max(1, int(1.5*sx)))
    c.create_line(px(214.71), py(322.75), px(214.71), py(407.85),
                  fill=col, width=max(1, int(1.5*sx)))
    c.create_line(px(377.67), py(322.75), px(377.67), py(407.85),
                  fill=col, width=max(1, int(1.5*sx)))

    # Linee orizzontali basse (fascia finestre)
    c.create_line(px(20.79),  py(566.24), px(214.71), py(566.24),
                  fill=col, width=max(1, int(1.5*sx)))
    c.create_line(px(372.13), py(566.24), px(571.62), py(566.24),
                  fill=col, width=max(1, int(1.5*sx)))
    c.create_line(px(20.79),  py(572.11), px(220.25), py(572.11),
                  fill=col, width=max(1, int(1.5*sx)))
    c.create_line(px(372.13), py(572.11), px(571.62), py(572.11),
                  fill=col, width=max(1, int(1.5*sx)))

    # Arco centrale (porta semicircolare) — approssimato con un arco Canvas
    cx_arc = px(296.21)
    cy_arc = py(566.24)
    r_arc  = px(81.45)
    c.create_arc(cx_arc - r_arc, cy_arc - r_arc,
                 cx_arc + r_arc, cy_arc + r_arc,
                 start=0, extent=180,
                 outline=col, style="arc",
                 width=max(1, int(1.5*sx)))

# ─── SCHERMATA SETUP PASSWORD ────────────────────────────────
class SetupScreen(tk.Frame):
    def __init__(self, parent, on_done):
        super().__init__(parent, bg=C["bg"])
        self.on_done = on_done
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        wrap = tk.Frame(self, bg=C["bg"])
        wrap.place(relx=.5, rely=.5, anchor="center")

        add_logo(wrap)
        tk.Label(wrap, text="ITS — Project Manager", font=F["hero"],
                 bg=C["bg"], fg=C["text"]).pack()
        tk.Label(wrap, text="Prima configurazione: imposta la tua password",
                 font=F["small"], bg=C["bg"], fg=C["muted"]).pack(pady=(4, 20))

        box = card(wrap)
        box.pack(padx=0, fill="x", ipadx=8)

        for lbl, attr, is_first in [
            ("NUOVA PASSWORD",    "e1", True),
            ("CONFERMA PASSWORD", "e2", False),
        ]:
            tk.Label(box, text=lbl, font=F["mono_s"],
                     bg=C["surface"], fg=C["accent"]).pack(anchor="w", padx=20,
                                                           pady=(16 if is_first else 8, 2))
            e = tk.Entry(box, show="●", font=F["body"],
                         bg=C["surface"], fg=C["text"],
                         relief="flat", bd=0, width=30)
            e.pack(fill="x", padx=20, pady=(0, 4), ipady=7)
            setattr(self, attr, e)

        self.e1.pack_configure(pady=(0, 0))
        tk.Frame(box, height=16, bg=C["surface"]).pack()  # bottom padding

        self.e1.bind("<Return>", lambda e: self.e2.focus())
        self.e2.bind("<Return>", lambda e: self._save())

        Btn(wrap, "Imposta password", self._save).pack(pady=16, ipadx=8)
        self.err = tk.Label(wrap, text="", font=F["small"],
                            bg=C["bg"], fg=C["danger"])
        self.err.pack()

    def _save(self):
        p1, p2 = self.e1.get(), self.e2.get()
        if len(p1) < 4:
            self.err.config(text="Minimo 4 caratteri."); return
        if p1 != p2:
            self.err.config(text="Le password non corrispondono."); return
        cfg = load_cfg()
        cfg["password_hash"] = hash_pw(p1)
        save_cfg(cfg)
        self.on_done()

# ─── SCHERMATA LOGIN ─────────────────────────────────────────
class LoginScreen(tk.Frame):
    def __init__(self, parent, on_login):
        super().__init__(parent, bg=C["bg"])
        self.on_login = on_login
        self._tries = 0
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        wrap = tk.Frame(self, bg=C["bg"])
        wrap.place(relx=.5, rely=.5, anchor="center")

        add_logo(wrap)
        tk.Label(wrap, text="ITS — Project Manager", font=F["hero"],
                 bg=C["bg"], fg=C["text"]).pack()
        tk.Label(wrap, text="Accedi per continuare",
                 font=F["small"], bg=C["bg"], fg=C["muted"]).pack(pady=(4, 20))

        box = card(wrap)
        box.pack(fill="x", ipadx=8)
        tk.Label(box, text="PASSWORD", font=F["mono_s"],
                 bg=C["surface"], fg=C["accent"]).pack(anchor="w", padx=20, pady=(16, 2))
        self.pw = tk.Entry(box, show="●", font=F["body"],
                           bg=C["surface"], fg=C["text"],
                           relief="flat", bd=0, width=30)
        self.pw.pack(fill="x", padx=20, pady=(0, 16), ipady=7)
        self.pw.focus()
        self.pw.bind("<Return>", lambda e: self._login())

        Btn(wrap, "Accedi →", self._login).pack(pady=16, ipadx=8)
        self.err = tk.Label(wrap, text="", font=F["small"],
                            bg=C["bg"], fg=C["danger"])
        self.err.pack()

    def _login(self):
        cfg = load_cfg()
        if hash_pw(self.pw.get()) == cfg.get("password_hash", ""):
            self.on_login()
        else:
            self._tries += 1
            self.pw.delete(0, "end")
            self.err.config(text=f"Password errata — tentativo {self._tries}")

# ─── APP PRINCIPALE ───────────────────────────────────────────
class MainApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg"])
        self.pack(fill="both", expand=True)
        self.projects = load_projects()
        self._view = "projects"
        self._filter = "Tutti"
        self._build()

    # ── Layout shell ─────────────────────────────────────────
    def _build(self):
        # ── Sidebar ──────────────────────────────────────────
        self.sb = tk.Frame(self, bg=C["surface"], width=210,
                           highlightbackground=C["faint"], highlightthickness=1)
        self.sb.pack(side="left", fill="y")
        self.sb.pack_propagate(False)

        # Logo + nome
        logo_frm = tk.Frame(self.sb, bg=C["surface"])
        logo_frm.pack(fill="x")
        add_logo(logo_frm, height=50)
        tk.Label(logo_frm, text="ITS", font=("Inter", 12, "bold"),
                 bg=C["surface"], fg=C["text"]).pack()
        tk.Label(logo_frm, text="Project Manager", font=F["mono_s"],
                 bg=C["surface"], fg=C["muted"]).pack(pady=(0, 12))

        sep(self.sb, pad_y=(0, 8))

        # Nav items  (label, view, emoji)
        self._nav_btns = {}
        nav = [
            ("Progetti",    "projects", "📋"),
            ("Nuovo",       "new",      "＋"),
            ("Statistiche", "stats",    "◎"),
        ]
        for label, view, icon in nav:
            b = tk.Button(self.sb,
                          text=f"  {icon}  {label}",
                          font=F["body"],
                          bg=C["surface"], fg=C["muted"],
                          relief="flat", bd=0, anchor="w",
                          padx=16, pady=9, cursor="hand2",
                          command=lambda v=view: self._goto(v))
            b.pack(fill="x")
            b.bind("<Enter>", lambda e, btn=b, v=view: btn.config(
                bg=C["accent_light"],
                fg=C["accent"] if self._view != v else C["accent"]))
            b.bind("<Leave>", lambda e, btn=b, v=view: btn.config(
                bg=C["accent_light"] if self._view == v else C["surface"],
                fg=C["accent"] if self._view == v else C["muted"]))
            self._nav_btns[view] = b

        # Cambio password in fondo
        btm = tk.Frame(self.sb, bg=C["surface"])
        btm.pack(side="bottom", fill="x", pady=12)
        sep(btm, pad_y=(0, 8))
        tk.Button(btm, text="  🔑  Cambia password",
                  font=F["small"], bg=C["surface"], fg=C["muted"],
                  relief="flat", bd=0, anchor="w",
                  padx=16, pady=7, cursor="hand2",
                  command=self._change_pw).pack(fill="x")

        # ── Area contenuto ────────────────────────────────────
        self.content = tk.Frame(self, bg=C["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self._goto("projects")

    def _goto(self, view):
        self._view = view
        for k, b in self._nav_btns.items():
            if k == view:
                b.config(bg=C["accent_light"], fg=C["accent"])
            else:
                b.config(bg=C["surface"], fg=C["muted"])
        for w in self.content.winfo_children():
            w.destroy()
        {"projects": self._page_projects,
         "new":      lambda: self._page_form(None),
         "stats":    self._page_stats}[view]()

    # ── Pagina: lista progetti ────────────────────────────────
    def _page_projects(self):
        self.projects = load_projects()
        root = tk.Frame(self.content, bg=C["bg"])
        root.pack(fill="both", expand=True, padx=28, pady=24)

        # Header
        hdr = tk.Frame(root, bg=C["bg"])
        hdr.pack(fill="x")
        eyebrow(hdr, "Progetti").pack(side="left")
        tk.Label(hdr, text=f"{len(self.projects)} totali",
                 font=F["mono_s"], bg=C["bg"], fg=C["muted"]).pack(side="right", pady=2)
        sep(root, pad_y=(8, 14))

        if not self.projects:
            tk.Label(root, text="Nessun progetto ancora.\nUsa «Nuovo» per iniziare.",
                     font=F["body"], bg=C["bg"], fg=C["muted"],
                     justify="center").pack(expand=True)
            return

        # Filtri tab-style (come il meeting scheduler)
        fil_frm = tk.Frame(root, bg=C["bg"],
                           highlightbackground=C["faint"], highlightthickness=0)
        fil_frm.pack(fill="x", pady=(0, 14))
        stati = ["Tutti", "In corso", "Da fare", "Completato", "In pausa"]
        self._fil_btns = {}
        for s in stati:
            active = self._filter == s
            b = tk.Button(
                fil_frm, text=s,
                font=F["small"],
                bg=C["bg"],
                fg=C["text"] if active else C["muted"],
                relief="flat", bd=0, cursor="hand2",
                padx=10, pady=5,
                command=lambda st=s: self._set_filter(st)
            )
            b.pack(side="left")
            if active:
                # sottolineatura accent
                ind = tk.Frame(fil_frm, height=2,
                               bg=C["accent"], width=b.winfo_reqwidth())
            self._fil_btns[s] = b
        # Separatore sotto i tab
        tk.Frame(fil_frm, height=1, bg=C["faint"]).pack(
            side="bottom", fill="x")

        # Scroll area
        canvas = tk.Canvas(root, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        shown = [p for p in self.projects
                 if self._filter == "Tutti" or p.get("status") == self._filter]
        for p in shown:
            self._project_card(sf, p)

    def _set_filter(self, st):
        self._filter = st
        self._goto("projects")

    def _project_card(self, parent, proj):
        # Outer card
        outer = card(parent)
        outer.pack(fill="x", pady=5, padx=1)

        body = tk.Frame(outer, bg=C["surface"])
        body.pack(fill="x", padx=18, pady=14)

        # Riga 1: titolo + badge status
        row1 = tk.Frame(body, bg=C["surface"])
        row1.pack(fill="x")
        tk.Label(row1, text=proj.get("title", "—"),
                 font=F["h1"], bg=C["surface"], fg=C["text"]).pack(side="left")
        Badge(row1, proj.get("status", "Da fare"),
              status=proj.get("status", "Da fare")).pack(side="right", pady=2)

        # Descrizione
        desc = proj.get("description", "").strip()
        if desc:
            tk.Label(body, text=desc[:110] + ("…" if len(desc) > 110 else ""),
                     font=F["small"], bg=C["surface"], fg=C["muted"],
                     wraplength=480, justify="left").pack(anchor="w", pady=(5, 0))

        # Meta row
        meta = tk.Frame(body, bg=C["surface"])
        meta.pack(fill="x", pady=(10, 0))
        for icon, key in [("📅", "deadline"), ("👤", "client")]:
            val = proj.get(key, "").strip()
            if val:
                tk.Label(meta, text=f"{icon}  {val}",
                         font=F["mono_s"], bg=C["surface"],
                         fg=C["muted"]).pack(side="left", padx=(0, 14))

        # Pulsanti
        btns = tk.Frame(body, bg=C["surface"])
        btns.pack(fill="x", pady=(12, 0))
        Btn(btns, "Modifica", lambda p=proj: self._edit(p),
            variant="outline", small=True).pack(side="left", padx=(0, 6))
        Btn(btns, "Elimina", lambda p=proj: self._delete(p),
            variant="danger", small=True).pack(side="left")

    # ── Pagina: form nuovo / modifica ─────────────────────────
    def _page_form(self, proj):
        editing = proj is not None
        root = tk.Frame(self.content, bg=C["bg"])
        root.pack(fill="both", expand=True, padx=28, pady=24)

        eyebrow(root, "Modifica progetto" if editing else "Nuovo progetto").pack(anchor="w")
        sep(root, pad_y=(8, 18))

        box = card(root)
        box.pack(fill="x")
        inner = tk.Frame(box, bg=C["surface"])
        inner.pack(fill="x", padx=20, pady=18)

        fields = {}

        def row(label, key, default="", options=None, multiline=False):
            tk.Label(inner, text=label, font=F["mono_s"],
                     bg=C["surface"], fg=C["accent"]).pack(anchor="w", pady=(10, 2))
            if options:
                var = tk.StringVar(value=default)
                cb = ttk.Combobox(inner, textvariable=var, values=options,
                                  font=F["body"], state="readonly", width=42)
                cb.pack(fill="x", pady=(0, 2), ipady=4)
                fields[key] = var
            elif multiline:
                t = tk.Text(inner, font=F["body"], bg=C["bg"],
                            fg=C["text"], relief="flat", bd=4,
                            width=44, height=4, wrap="word")
                if default: t.insert("1.0", default)
                t.pack(fill="x", pady=(0, 2))
                fields[key] = t
            else:
                var = tk.StringVar(value=default)
                e = tk.Entry(inner, textvariable=var, font=F["body"],
                             bg=C["bg"], fg=C["text"],
                             relief="flat", bd=4, width=44)
                e.pack(fill="x", pady=(0, 2), ipady=5)
                fields[key] = var

        row("TITOLO PROGETTO",       "title",    proj.get("title","") if proj else "")
        row("CLIENTE / COMMITTENTE", "client",   proj.get("client","") if proj else "")
        row("SCADENZA (YYYY-MM-DD)", "deadline", proj.get("deadline","") if proj else "")
        row("STATO", "status",
            proj.get("status","Da fare") if proj else "Da fare",
            options=["Da fare","In corso","In pausa","Completato"])
        row("NOTE / DESCRIZIONE", "description",
            proj.get("description","") if proj else "", multiline=True)

        sep(root, pad_y=(16, 8))

        btn_row = tk.Frame(root, bg=C["bg"])
        btn_row.pack(fill="x")

        def save():
            title = fields["title"].get().strip()
            if not title:
                messagebox.showwarning("Campo obbligatorio",
                                       "Il titolo è obbligatorio."); return
            desc = fields["description"]
            desc_val = (desc.get("1.0", "end").strip()
                        if isinstance(desc, tk.Text)
                        else desc.get().strip())
            now = datetime.now().strftime("%Y-%m-%d")
            data = {
                "title":       title,
                "client":      fields["client"].get().strip(),
                "deadline":    fields["deadline"].get().strip(),
                "status":      fields["status"].get(),
                "description": desc_val,
                "updated_at":  now,
            }
            if editing:
                proj.update(data)
            else:
                data.update({"id": str(uuid.uuid4()), "created_at": now})
                self.projects.append(data)
            save_projects(self.projects)
            self._goto("projects")

        Btn(btn_row, "💾  Salva", save).pack(side="left", padx=(0, 8))
        Btn(btn_row, "Annulla",
            lambda: self._goto("projects"), variant="ghost").pack(side="left")

    def _edit(self, proj):
        for w in self.content.winfo_children(): w.destroy()
        self._page_form(proj)

    def _delete(self, proj):
        if messagebox.askyesno("Elimina", f"Eliminare «{proj['title']}»?"):
            self.projects = [p for p in self.projects
                             if p.get("id") != proj.get("id")]
            save_projects(self.projects)
            self._goto("projects")

    # ── Pagina: statistiche ───────────────────────────────────
    def _page_stats(self):
        self.projects = load_projects()
        root = tk.Frame(self.content, bg=C["bg"])
        root.pack(fill="both", expand=True, padx=28, pady=24)

        eyebrow(root, "Statistiche").pack(anchor="w")
        sep(root, pad_y=(8, 18))

        totale = len(self.projects)
        cnt = {}
        for p in self.projects:
            s = p.get("status", "Da fare")
            cnt[s] = cnt.get(s, 0) + 1

        # Griglia card statistiche (stile result-row del meeting scheduler)
        grid_frm = tk.Frame(root, bg=C["bg"])
        grid_frm.pack(fill="x")
        stati = ["In corso", "Da fare", "Completato", "In pausa"]
        for i, s in enumerate(stati):
            bg_s, fg_s = STATUS_COLORS.get(s, (C["faint"], C["muted"]))
            c2 = tk.Frame(grid_frm, bg=bg_s,
                          highlightbackground=C["faint"], highlightthickness=1)
            c2.grid(row=0, column=i, padx=5, pady=0, sticky="nsew", ipadx=6)
            tk.Label(c2, text=str(cnt.get(s, 0)),
                     font=("Inter", 26, "bold"),
                     bg=bg_s, fg=fg_s).pack(padx=14, pady=(14, 2))
            tk.Label(c2, text=s, font=F["mono_s"],
                     bg=bg_s, fg=fg_s).pack(padx=14, pady=(0, 14))
            grid_frm.columnconfigure(i, weight=1)

        sep(root, pad_y=(18, 12))

        # Totale
        total_frm = card(root)
        total_frm.pack(fill="x", pady=(0, 18))
        tk.Label(total_frm, text=f"Totale progetti: {totale}",
                 font=F["h1"], bg=C["surface"],
                 fg=C["text"]).pack(padx=18, pady=14, anchor="w")

        # Scadenze imminenti
        oggi = date.today()
        imm = []
        for p in self.projects:
            dl = p.get("deadline", "")
            try:
                diff = (date.fromisoformat(dl) - oggi).days
                if 0 <= diff <= 14: imm.append((diff, p))
            except Exception: pass
        imm.sort(key=lambda x: x[0])

        if imm:
            eyebrow(root, "Scadenze imminenti — 14 giorni",
                    bg=C["bg"]).pack(anchor="w", pady=(0, 8))
            for diff, p in imm:
                row_frm = tk.Frame(root, bg=C["warn_bg"],
                                   highlightbackground=C["faint"],
                                   highlightthickness=1)
                row_frm.pack(fill="x", pady=3)
                tk.Label(row_frm, text=p["title"],
                         font=F["body"], bg=C["warn_bg"],
                         fg=C["text"]).pack(side="left", padx=16, pady=10)
                giorni = "oggi" if diff == 0 else f"tra {diff} g."
                tk.Label(row_frm, text=giorni, font=F["mono_s"],
                         bg=C["warn_bg"],
                         fg=C["warn_text"]).pack(side="right", padx=16)
        elif totale > 0:
            tk.Label(root, text="Nessuna scadenza nei prossimi 14 giorni.",
                     font=F["small"], bg=C["bg"],
                     fg=C["muted"]).pack(anchor="w")

    # ── Cambio password ───────────────────────────────────────
    def _change_pw(self):
        old = simpledialog.askstring("Cambia password",
                                     "Password attuale:", show="*",
                                     parent=self.winfo_toplevel())
        if not old: return
        cfg = load_cfg()
        if hash_pw(old) != cfg.get("password_hash", ""):
            messagebox.showerror("Errore", "Password attuale errata."); return
        n1 = simpledialog.askstring("Cambia password",
                                    "Nuova password (min. 4 caratteri):", show="*",
                                    parent=self.winfo_toplevel())
        if not n1 or len(n1) < 4:
            messagebox.showwarning("Avviso", "Password non valida."); return
        n2 = simpledialog.askstring("Cambia password",
                                    "Conferma:", show="*",
                                    parent=self.winfo_toplevel())
        if n1 != n2:
            messagebox.showerror("Errore", "Le password non coincidono."); return
        cfg["password_hash"] = hash_pw(n1)
        save_cfg(cfg)
        messagebox.showinfo("✓", "Password aggiornata.")

# ─── AVVIO ───────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ITS — Project Manager")
        self.geometry("980x660")
        self.minsize(780, 540)
        self.configure(bg=C["bg"])
        try: self.iconbitmap(os.path.join(ASSETS_DIR, "icon.ico"))
        except: pass
        self._boot()

    def _boot(self):
        for w in self.winfo_children(): w.destroy()
        if not load_cfg().get("password_hash"):
            SetupScreen(self, self._boot)
        else:
            LoginScreen(self, self._main)

    def _main(self):
        for w in self.winfo_children(): w.destroy()
        MainApp(self)

if __name__ == "__main__":
    App().mainloop()
