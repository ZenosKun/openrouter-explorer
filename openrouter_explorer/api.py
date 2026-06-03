"""Accès à l'API OpenRouter et filtrage des modèles gratuits."""

from __future__ import annotations

from typing import List

import requests

from .config import API_URL, REQUEST_TIMEOUT
from .models import Model


class OpenRouterError(Exception):
    """Erreur levée lorsque la récupération des modèles échoue."""


def _is_free(pricing: dict) -> bool:
    """Retourne True si tous les prix renseignés valent zéro."""
    if not pricing:
        return False
    return all(
        float(price) == 0
        for price in pricing.values()
        if price is not None and price != ""
    )


def fetch_free_models(url: str = API_URL,
                      timeout: int = REQUEST_TIMEOUT) -> List[Model]:
    """Récupère et retourne la liste des modèles gratuits d'OpenRouter.

    Lève OpenRouterError en cas de problème réseau ou de réponse invalide.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise OpenRouterError(f"Network error: {exc}") from exc
    except ValueError as exc:  # JSON invalide
        raise OpenRouterError(f"Invalid JSON response: {exc}") from exc

    free_models: List[Model] = []
    for raw in data.get("data", []):
        if _is_free(raw.get("pricing", {})):
            free_models.append(Model.from_api(raw))
    return free_models
