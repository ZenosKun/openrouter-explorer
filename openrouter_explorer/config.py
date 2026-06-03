"""Constantes de configuration et thème de l'application."""

API_URL = "https://openrouter.ai/api/v1/models"
REQUEST_TIMEOUT = 15

WINDOW_TITLE = "OpenRouter Free Models Explorer"
WINDOW_SIZE = "1320x860"
WINDOW_MIN_SIZE = (1040, 680)

FONT = "Segoe UI"

# Options du filtre de capacités
FILTER_ALL = "All Models"
FILTER_TOOLS = "With Tools"
FILTER_VISION = "With Vision"
FILTER_BOTH = "Tools + Vision"
FILTER_OPTIONS = [FILTER_ALL, FILTER_TOOLS, FILTER_VISION, FILTER_BOTH]

# Palette sombre et sobre (alignée sur le thème "dark" de CustomTkinter)
COLORS = {
    "bg":           "#1a1b1e",
    "surface":      "#25262b",
    "surface_2":    "#2c2e33",
    "border":       "#373a40",
    "accent":       "#4c6ef5",
    "accent_hover": "#5c7cfa",
    "success":      "#2f9e44",
    "warning":      "#f08c00",
    "danger":       "#e03131",
    "text":         "#e9ecef",
    "text_muted":   "#909296",
    "row_alt":      "#202124",
    "cyan":         "#15aabf",
    "violet":       "#9775fa",
}
