# OpenRouter Free Models Explorer

Une petite application de bureau pour parcourir les modèles gratuits d'OpenRouter
sans avoir à fouiller la doc ou l'API à la main. On cherche, on filtre par
capacités (outils / vision), on trie, et on exporte la sélection en JSON.

L'interface est faite avec CustomTkinter (thème sombre).

## Pourquoi

OpenRouter expose des dizaines de modèles, dont une bonne partie gratuits, mais
leur catalogue n'est pas pratique à filtrer quand on cherche un modèle précis
avec du function calling ou de la vision. Cet outil interroge directement
l'endpoint `/models`, ne garde que ceux dont tous les prix sont à zéro, et
affiche le tout dans un tableau triable.

## Installation

Il faut Python 3.10 ou plus récent.

```bash
git clone https://github.com/ZenosKun/openrouter-explorer.git
cd openrouter-explorer
pip install -r requirements.txt
```

Sur Linux, Tkinter n'est pas toujours fourni avec Python. Si le lancement
échoue avec une erreur du type `ModuleNotFoundError: No module named 'tkinter'`,
installez-le via le gestionnaire de paquets :

```bash
# Debian / Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

L'application tourne sous Windows, Linux et macOS. La police s'adapte
automatiquement au système.

## Lancer

```bash
python -m openrouter_explorer
```

La liste se charge automatiquement au démarrage. `F5` la recharge.

## Créer un exécutable autonome

Pour distribuer l'application à des gens qui n'ont pas Python, on peut la
packager en un seul fichier exécutable avec PyInstaller. Des scripts prêts à
l'emploi s'en chargent :

```bash
# Windows : double-clique sur build_exe.bat, ou en terminal :
build_exe.bat

# Linux / macOS :
bash build_exe.sh
```

Le résultat apparaît dans le dossier `dist/` (`OpenRouterExplorer.exe` sous
Windows, `OpenRouterExplorer` sous Linux/macOS).

Deux points à savoir :

- **Pas de compilation croisée.** PyInstaller génère un exécutable pour le
  système sur lequel il tourne. Pour fournir à la fois une version Windows et
  une version Linux, il faut lancer le build une fois sur chaque OS.
- Le fichier `OpenRouterExplorer.spec` embarque automatiquement les ressources
  de CustomTkinter (thèmes, polices). Sans ça l'exécutable planterait au
  démarrage, donc évitez de lancer PyInstaller à la main sans ce `.spec`.

## Utilisation

- **Recherche** : tape une partie du nom ou de l'ID du modèle.
- **Filtre** : All Models / With Tools / With Vision / Tools + Vision.
- **Tri** : clique sur un en-tête de colonne (un deuxième clic inverse l'ordre).
- **Détails** : double-clic sur une ligne, ou clic droit > View Details.
- **Copier l'ID** : clic droit > Copy ID.
- **Export** : le bouton *Export* enregistre la liste filtrée en JSON ;
  clic droit > Export Selected n'enregistre que les lignes sélectionnées.

## Structure du projet

```
openrouter_explorer/
    config.py        constantes, URL de l'API, palette de couleurs
    models.py        dataclass Model + fonctions de filtre/tri (sans UI)
    api.py           appel réseau et parsing des modèles gratuits
    ui/
        app.py       fenêtre principale
        details.py   fenêtre de détails d'un modèle
    __main__.py      point d'entrée du module
run.py               script de lancement (utilisé aussi pour le build)
```

La logique métier (`models.py`, `api.py`) ne dépend pas de Tkinter, ce qui la
rend testable indépendamment de l'interface.

## Notes

- Un modèle est considéré « gratuit » quand tous les champs de prix renseignés
  valent zéro. Si OpenRouter change le format de `pricing`, c'est la fonction
  `_is_free` dans `api.py` qu'il faudra ajuster.
- Le tableau utilise `ttk.Treeview` (CustomTkinter n'a pas de widget tableau),
  restylé pour rester cohérent avec le reste de l'interface.

## Licence

MIT. Voir [LICENSE](LICENSE).
