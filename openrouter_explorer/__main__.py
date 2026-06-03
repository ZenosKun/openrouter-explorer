"""Point d'entrée : python -m openrouter_explorer."""

from .ui import OpenRouterModelsGUI


def main():
    app = OpenRouterModelsGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
