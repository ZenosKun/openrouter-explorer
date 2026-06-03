"""Fenêtre principale de l'application."""

from __future__ import annotations

import json
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from typing import List

import customtkinter as ctk

from ..api import fetch_free_models, OpenRouterError
from ..config import (COLORS, FONT, FILTER_ALL, FILTER_OPTIONS,
                      WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_SIZE)
from ..models import Model, filter_models, sort_models
from .details import ModelDetailsWindow

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class OpenRouterModelsGUI(ctk.CTk):
    """Fenêtre principale : recherche, filtres, statistiques et tableau."""

    def __init__(self):
        super().__init__()

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)
        self.configure(fg_color=COLORS["bg"])

        self.models: List[Model] = []
        self.filtered: List[Model] = []
        self.sort_column = "name"
        self.sort_reverse = False
        self.loading = False
        self._loading_dots = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_toolbar()
        self._build_stats()
        self._build_table()
        self._build_statusbar()

        self.bind("<F5>", lambda e: self.refresh_models())
        self.after(300, self.refresh_models)

    # ------------------------------------------------------------------ UI
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 6))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="O", width=48, height=48, corner_radius=12,
            fg_color=COLORS["accent"], text_color="white", font=(FONT, 18, "bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(0, 16))

        ctk.CTkLabel(header, text="OpenRouter", anchor="w",
                     font=(FONT, 22, "bold"), text_color=COLORS["text"]
                     ).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(header, text="Free Models Explorer", anchor="w",
                     font=(FONT, 13), text_color=COLORS["text_muted"]
                     ).grid(row=1, column=1, sticky="nw")

        self.refresh_btn = ctk.CTkButton(
            header, text="Refresh", width=110, height=38, corner_radius=10,
            font=(FONT, 13, "bold"), fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], command=self.refresh_models,
        )
        self.refresh_btn.grid(row=0, column=2, rowspan=2, padx=(8, 0))

        ctk.CTkButton(
            header, text="Export", width=110, height=38, corner_radius=10,
            font=(FONT, 13, "bold"), fg_color=COLORS["surface_2"],
            hover_color=COLORS["border"], command=self.save_to_json,
        ).grid(row=0, column=3, rowspan=2, padx=(10, 0))

    def _build_toolbar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, sticky="ew", padx=24, pady=(10, 6))
        bar.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            bar, textvariable=self.search_var, height=42, corner_radius=10,
            border_width=1, border_color=COLORS["border"], fg_color=COLORS["surface"],
            font=(FONT, 13), placeholder_text="Search by name or ID...",
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")

        self.filter_var = ctk.StringVar(value=FILTER_ALL)
        ctk.CTkOptionMenu(
            bar, variable=self.filter_var, width=170, height=42, corner_radius=10,
            font=(FONT, 13), fg_color=COLORS["surface"],
            button_color=COLORS["surface_2"], button_hover_color=COLORS["border"],
            values=FILTER_OPTIONS, command=lambda _: self._apply_and_render(),
        ).grid(row=0, column=1, padx=(12, 0))

        self.search_var.trace_add("write", lambda *_: self._apply_and_render())

    def _build_stats(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=2, column=0, sticky="ew", padx=24, pady=(6, 4))
        for i in range(4):
            wrap.grid_columnconfigure(i, weight=1, uniform="stat")

        self.stat_labels = {}
        cards = [
            ("total",  "Total Models",   COLORS["accent"]),
            ("tools",  "With Tools",     COLORS["cyan"]),
            ("vision", "With Vision",    COLORS["violet"]),
            ("both",   "Tools + Vision", COLORS["success"]),
        ]
        for i, (key, label, color) in enumerate(cards):
            card = ctk.CTkFrame(wrap, corner_radius=10, fg_color=COLORS["surface"])
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 10, 0))
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkFrame(card, width=3, height=38, corner_radius=3, fg_color=color
                         ).grid(row=0, column=0, rowspan=2, sticky="ns", padx=(10, 0), pady=10)

            value = ctk.CTkLabel(card, text="0", anchor="w",
                                 font=(FONT, 22, "bold"), text_color=color)
            value.grid(row=0, column=1, sticky="w", padx=12, pady=(10, 0))

            ctk.CTkLabel(card, text=label, anchor="w", font=(FONT, 11),
                         text_color=COLORS["text_muted"]
                         ).grid(row=1, column=1, sticky="w", padx=12, pady=(0, 10))

            self.stat_labels[key] = value

    def _build_table(self):
        container = ctk.CTkFrame(self, corner_radius=12, fg_color=COLORS["surface"])
        container.grid(row=3, column=0, sticky="nsew", padx=24, pady=(8, 6))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Modern.Treeview", background=COLORS["surface"],
                        fieldbackground=COLORS["surface"], foreground=COLORS["text"],
                        borderwidth=0, rowheight=40, font=(FONT, 11))
        style.configure("Modern.Treeview.Heading", background=COLORS["surface_2"],
                        foreground=COLORS["text_muted"], relief="flat", borderwidth=0,
                        font=(FONT, 11, "bold"), padding=(12, 12))
        style.map("Modern.Treeview.Heading", background=[("active", COLORS["border"])])
        style.map("Modern.Treeview", background=[("selected", COLORS["accent"])],
                  foreground=[("selected", "white")])

        columns = ("tools", "vision", "name", "context", "id")
        self.tree = ttk.Treeview(container, columns=columns, show="headings",
                                 style="Modern.Treeview", selectmode="extended")
        headings = {
            "tools": ("Tools", 90, "center"),
            "vision": ("Vision", 90, "center"),
            "name": ("Model Name", 380, "w"),
            "context": ("Context", 120, "center"),
            "id": ("OpenRouter ID", 360, "w"),
        }
        for col, (text, width, anchor) in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=width, anchor=anchor, minwidth=70)

        self.tree.tag_configure("odd", background=COLORS["surface"])
        self.tree.tag_configure("even", background=COLORS["row_alt"])

        scrollbar = ctk.CTkScrollbar(container, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(4, 10), pady=10)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self._build_context_menu()

    def _build_context_menu(self):
        self.context_menu = tk.Menu(
            self, tearoff=0, bg=COLORS["surface_2"], fg=COLORS["text"],
            activebackground=COLORS["accent"], activeforeground="white",
            font=(FONT, 10), borderwidth=0, relief="flat",
        )
        self.context_menu.add_command(label="Copy ID", command=self.copy_model_id)
        self.context_menu.add_command(label="View Details",
                                      command=self.show_selected_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export Selected",
                                      command=self.export_selected)

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, corner_radius=10, fg_color=COLORS["surface"], height=40)
        bar.grid(row=4, column=0, sticky="ew", padx=24, pady=(6, 18))
        bar.grid_columnconfigure(1, weight=1)

        self.status_dot = ctk.CTkLabel(bar, text="●", font=(FONT, 14),
                                       text_color=COLORS["success"], width=20)
        self.status_dot.grid(row=0, column=0, padx=(14, 4), pady=8)

        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(bar, textvariable=self.status_var, anchor="w", font=(FONT, 12),
                     text_color=COLORS["text_muted"]
                     ).grid(row=0, column=1, sticky="w", pady=8)

        self.timestamp_var = ctk.StringVar(value="")
        ctk.CTkLabel(bar, textvariable=self.timestamp_var, anchor="e", font=(FONT, 11),
                     text_color=COLORS["text_muted"]
                     ).grid(row=0, column=2, sticky="e", padx=14, pady=8)

    # --------------------------------------------------------------- data
    def refresh_models(self):
        if self.loading:
            return
        self.loading = True
        self._loading_dots = 0
        self.status_dot.configure(text_color=COLORS["warning"])
        self.refresh_btn.configure(state="disabled")
        self._animate_loading()
        threading.Thread(target=self._load_thread, daemon=True).start()

    def _animate_loading(self):
        if self.loading:
            self.status_var.set("Loading models" + "." * (self._loading_dots % 4))
            self._loading_dots += 1
            self.after(300, self._animate_loading)

    def _load_thread(self):
        try:
            models = fetch_free_models()
            self.after(0, lambda: self._on_loaded(models))
        except OpenRouterError as exc:
            self.after(0, lambda: self.show_error(str(exc)))
        except Exception as exc:  # filet de sécurité
            self.after(0, lambda: self.show_error(f"Unexpected error: {exc}"))

    def _on_loaded(self, models: List[Model]):
        self.loading = False
        self.models = models
        self.refresh_btn.configure(state="normal")
        self.status_dot.configure(text_color=COLORS["success"])
        self.status_var.set(f"Loaded {len(models)} free models")
        self.timestamp_var.set(f"Updated {datetime.now().strftime('%H:%M:%S')}")
        self._update_stats()
        self._apply_and_render()

    def _update_stats(self):
        tools = sum(1 for m in self.models if m.has_tools)
        vision = sum(1 for m in self.models if m.has_vision)
        both = sum(1 for m in self.models if m.has_tools and m.has_vision)
        self.stat_labels["total"].configure(text=str(len(self.models)))
        self.stat_labels["tools"].configure(text=str(tools))
        self.stat_labels["vision"].configure(text=str(vision))
        self.stat_labels["both"].configure(text=str(both))

    # --------------------------------------------- filter / sort / render
    def _apply_and_render(self):
        if not hasattr(self, "filter_var"):
            return
        models = filter_models(self.models, self.search_var.get(), self.filter_var.get())
        self.filtered = sort_models(models, self.sort_column, self.sort_reverse)
        self._render_rows()

    def _render_rows(self):
        self.tree.delete(*self.tree.get_children())
        for i, m in enumerate(self.filtered):
            self.tree.insert(
                "", "end",
                values=("✓" if m.has_tools else "—",
                        "✓" if m.has_vision else "—",
                        m.name, m.context_label, m.id),
                tags=("even" if i % 2 == 0 else "odd",),
            )

    def sort_by(self, column: str):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self._apply_and_render()

    # ------------------------------------------------------------ actions
    def _selected_models(self) -> List[Model]:
        result = []
        for item_id in self.tree.selection():
            values = self.tree.item(item_id)["values"]
            name, mid = values[2], values[4]
            for m in self.models:
                if m.name == name and m.id == mid:
                    result.append(m)
                    break
        return result

    def copy_model_id(self):
        models = self._selected_models()
        if models:
            self.clipboard_clear()
            self.clipboard_append(models[0].id)
            self.status_var.set(f"Copied: {models[0].id}")

    def show_selected_details(self):
        models = self._selected_models()
        if models:
            ModelDetailsWindow(self, models[0])

    def _show_context_menu(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            if row not in self.tree.selection():
                self.tree.selection_set(row)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def _on_double_click(self, _event):
        models = self._selected_models()
        if models:
            ModelDetailsWindow(self, models[0])

    def export_selected(self):
        models = self._selected_models()
        if models:
            self._write_json(models, f"Exported {len(models)} selected models")

    def save_to_json(self):
        if not self.filtered:
            messagebox.showwarning("Warning", "No models to save")
            return
        self._write_json(self.filtered, f"Saved {len(self.filtered)} models")

    def _write_json(self, models: List[Model], success_msg: str):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Save models",
        )
        if not filename:
            return
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump([m.to_dict() for m in models], f,
                          indent=2, ensure_ascii=False)
            self.status_var.set(success_msg)
        except OSError as exc:
            self.show_error(f"Save error: {exc}")

    def show_error(self, message: str):
        self.loading = False
        self.refresh_btn.configure(state="normal")
        self.status_dot.configure(text_color=COLORS["danger"])
        self.status_var.set("Error")
        messagebox.showerror("Error", message)
