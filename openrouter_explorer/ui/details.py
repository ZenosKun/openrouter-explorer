"""Fenêtre de détails d'un modèle."""

from __future__ import annotations

import customtkinter as ctk

from ..config import COLORS, FONT
from ..models import Model


class ModelDetailsWindow(ctk.CTkToplevel):
    """Fenêtre modale affichant les informations détaillées d'un modèle."""

    def __init__(self, master, model: Model):
        super().__init__(master)
        self.model = model

        self.title(model.name)
        self.geometry("620x620")
        self.configure(fg_color=COLORS["bg"])
        self.transient(master)
        # grab différé : évite une erreur Windows si la fenêtre n'est pas affichée
        self.after(50, self.grab_set)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_badges()
        self._build_body()
        self._build_close_button()

    def _build_header(self):
        header = ctk.CTkFrame(self, corner_radius=12, fg_color=COLORS["surface"])
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text=self.model.name, anchor="w",
                     font=(FONT, 17, "bold"), text_color=COLORS["text"]
                     ).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 2))
        ctk.CTkLabel(header, text=self.model.id, anchor="w",
                     font=(FONT, 12), text_color=COLORS["text_muted"]
                     ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))

    def _build_badges(self):
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.grid(row=1, column=0, sticky="ew", padx=20, pady=4)

        self._badge(info, "Tools " + ("✓" if self.model.has_tools else "✕"),
                    self.model.has_tools).pack(side="left", padx=(0, 10))
        self._badge(info, "Vision " + ("✓" if self.model.has_vision else "✕"),
                    self.model.has_vision).pack(side="left", padx=(0, 10))

        ctx = self.model.context_length
        ctx_text = f"{ctx:,} tokens" if ctx else "Unknown context"
        ctk.CTkLabel(info, text=ctx_text, font=(FONT, 12),
                     text_color=COLORS["text_muted"]).pack(side="left", padx=8)

    def _badge(self, parent, text, active):
        return ctk.CTkLabel(
            parent, text=text, corner_radius=8, height=30, width=110,
            font=(FONT, 12, "bold"), text_color="white",
            fg_color=COLORS["success"] if active else COLORS["surface_2"],
        )

    def _build_body(self):
        body = ctk.CTkScrollableFrame(self, corner_radius=12,
                                      fg_color=COLORS["surface"], label_text="")
        body.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        body.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(body, text="Description", anchor="w",
                     font=(FONT, 13, "bold"), text_color=COLORS["text"]
                     ).grid(row=0, column=0, sticky="ew", pady=(4, 4))
        ctk.CTkLabel(
            body, text=self.model.description or "No description available.",
            anchor="w", justify="left", wraplength=520,
            font=(FONT, 12), text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, sticky="ew", pady=(0, 12))

        params = self.model.supported_parameters
        ctk.CTkLabel(body, text="Supported Parameters", anchor="w",
                     font=(FONT, 13, "bold"), text_color=COLORS["text"]
                     ).grid(row=2, column=0, sticky="ew", pady=(4, 4))
        ctk.CTkLabel(
            body, text="• " + "\n• ".join(params) if params else "None",
            anchor="w", justify="left", wraplength=520,
            font=(FONT, 12), text_color=COLORS["text_muted"],
        ).grid(row=3, column=0, sticky="ew", pady=(0, 8))

    def _build_close_button(self):
        ctk.CTkButton(
            self, text="Close", width=110, height=38, corner_radius=10,
            font=(FONT, 13, "bold"), fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], command=self.destroy,
        ).grid(row=3, column=0, pady=(6, 18))
