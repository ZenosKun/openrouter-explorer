"""Modèle de données et logique de filtrage/tri, sans dépendance à l'UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .config import FILTER_TOOLS, FILTER_VISION, FILTER_BOTH


@dataclass
class Model:
    """Représente un modèle OpenRouter gratuit."""

    id: str
    name: str
    context_length: int | None = None
    description: str = ""
    supported_parameters: List[str] = field(default_factory=list)
    architecture: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_tools(self) -> bool:
        return "tools" in self.supported_parameters

    @property
    def has_vision(self) -> bool:
        return "image" in self.architecture.get("input_modalities", [])

    @property
    def context_label(self) -> str:
        if not self.context_length:
            return "—"
        return f"{self.context_length // 1000}K"

    @classmethod
    def from_api(cls, raw: Dict[str, Any]) -> "Model":
        """Construit un Model à partir d'une entrée brute de l'API."""
        model_id = raw["id"].replace("\n", "").replace("\r", "").strip()
        return cls(
            id=model_id,
            name=raw["name"].strip() if raw.get("name") else "Unknown",
            context_length=raw.get("context_length"),
            description=(raw.get("description", "") or "")[:400].strip(),
            supported_parameters=raw.get("supported_parameters", []),
            architecture=raw.get("architecture", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "context_length": self.context_length,
            "description": self.description,
            "supported_parameters": self.supported_parameters,
            "architecture": self.architecture,
        }


def filter_models(models: List[Model], search: str = "",
                   capability: str | None = None) -> List[Model]:
    """Filtre une liste de modèles par texte de recherche et capacité."""
    result = models
    term = search.strip().lower()
    if term:
        result = [m for m in result if term in m.name.lower() or term in m.id.lower()]

    if capability == FILTER_TOOLS:
        result = [m for m in result if m.has_tools]
    elif capability == FILTER_VISION:
        result = [m for m in result if m.has_vision]
    elif capability == FILTER_BOTH:
        result = [m for m in result if m.has_tools and m.has_vision]

    return result


def sort_models(models: List[Model], column: str, reverse: bool = False) -> List[Model]:
    """Trie une liste de modèles selon une colonne."""
    key_funcs = {
        "tools": lambda m: m.has_tools,
        "vision": lambda m: m.has_vision,
        "name": lambda m: m.name.lower(),
        "context": lambda m: m.context_length or 0,
        "id": lambda m: m.id.lower(),
    }
    key = key_funcs.get(column, key_funcs["name"])
    return sorted(models, key=key, reverse=reverse)
