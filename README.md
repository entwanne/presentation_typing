# Écrire un analyseur de types en Python

Conférence présentée à la PyConFr 2026.

> Après un tour d'horizon des annotations de types en Python & des types génériques, nous verrons comment mettre en place une analyse dynamique de ceux-ci dans un programme Python, puis comment écrire un analyseur statique de types tel que mypy.

Le support est disponible à l'adresse <https://entwanne.github.io/presentation_typing/>.  
L'analyseur statique final est proposé dans [le dossier `typy`](https://github.com/entwanne/presentation_typing/tree/master/typy).

## Support de présentation

Le support de présentation utilise [`lucina`](https://pypi.org/project/lucina/), un outil permettant de générer un notebook Jupyter à partir de fichiers Markdown.
C'est ensuite le plugin rise qui est utilisé pour rendre une présentation Reveal.js à partir de ce notebook, afin d'avoir une présentation interactive.

L'environnement de travail peut alors être installé à l'aide de la commande shell `pip install -r requirements`.

`make run` permet ensuite de générer et démarrer la présentation.

Différents exports (notebook, reveal, PDF) sont présentés sur la branche [exports](https://github.com/entwanne/presentation_typing/tree/exports).
