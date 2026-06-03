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

## Lancer

```bash
python -m openrouter_explorer
```

La liste se charge automatiquement au démarrage. `F5` la recharge.

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
    __main__.py      point d'entrée
GetModelsGUI.py      lanceur de compatibilité
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
