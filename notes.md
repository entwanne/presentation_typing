# 1. Introduction

- Antoine, président de l'AFPy et développeur Python depuis 15-20 ans
- Présentation sur le typage en Python et sur la construction d'un outil tel que mypy

# 2. Le typage en Python

- Typage fort, pas de conversions implicites
    - erreurs explicites qui surviennent au runtime

- Mais typage dynamique : le type est déduit au runtime et n'est pas connu avant l'exécution
- Il peut changer suivant les conditions
- Une variable n'a pas de type à proprement parler

- duck-typing
    - ce qu'on peut faire avec une valeur plutôt que le nom de son type
    - isinstance
    - types abstraits / interfaces pour définir un comportement (subclasshooks)

# 3. Typage statique

- Auparavant possible à l'aide de commentaires, formalisé en Python 3
    - Standardisé en 3.5 pour que les annotations correspondent toujours à des types
    - Évaluation différée en 3.14
- Outils d'analyse statique qui se sont développés suite à ça
    - Et bibliothèques qi exploitent dynamiquement ces annotations (pydantic, fastapi)

- éviter une certaine classe de bugs par analyse statique
    - détecter les incompatibilités entre types avant le runtime
    - s'assurer que toutes les branches produisent des valeurs valides / compatibles

- Annotations de types
    - Accès aux annotations depuis Python avec annotationlib
    - Ne couvre que les branches effectivement exécutées du programme
    - N'apporte pas vraiment plus de garanties par rapport au typage en Python existant (lève juste une TypeError plus tôt que prévu)
    - L'accès aux annotations est cependant utile pour d'autres usages (définition de modèles de sérialisation)

- Analyse statique : mypy
- duck-typing = typage structurel
    - Types composés (`list[int]`, `tuple[str, str]`)
    - Types génériques
    - Protocoles

# 4. Écrire un analyseur de types

- Module ast
    - AST : représentation intermédiaire entre les tokens (liste de mots) et les quads (assembleur)
    - Représente l'arborescence d'un fichier Python, les différents blocs syntaxiques
    - Pattern visiteur pour parcourir récursivement l'arbre
    - Méthodes spécialisées par type de nœud

- Analyse des nœuds de l'AST pour vérifier les types
    - Constant : valeur littérale, Name : nom de type ou nom de variable (target)
- Boilerplate pour simplifier l'usage du type-checker

# 5. Modèle objet de Python

- Types & instances : toute expression est une valeur, tout valeur a un type
- Modèle cyclique : ajout des liens explicites dans le modèle (type est une instance de type)
- Représentation dans typy :
    - classes PyObject (objet Python, possède un type), Type & Value
    - `Type.type = Type`

# 6. Expressions de types

- Assignations multiples, réassignations
    - stockage des annotations précédemment visitées
- Types concrets et expressions de types, union de types
    - Implémentation de l'union au niveau du typeur
- Absence de type pour mettre en évidence ce qui n'est pas typé ou ne possède pas de type (instruction)

- Ensemble de types permis pour une valeur : union et intersection de types selon les embranchements

# 7. Fonctions et opérations

- Gestion du contexte et du namespace
- Fonction définie par un nom, des paramètres et un retour
    - Associe les arguments de l'appel aux paramètres

- Opérateurs binaires : définition explicite des opérations permises
    - Ne pas oublier l'union de types

# 8. Types et classes

- Les types comme des fonctions
- Définition de classes : nom et bases (classes parentes)
    - vu des types comme des ensembles de valeurs autorisées
    - une classe autorise les valeurs de ses sous-classes
- Définition et appel de méthodes
    - Fonctions liées à une instance précise, reçue en premier paramètre (self)
    - En Python, tout callable peut être ainsi lié à une instance pour former une méthode (grâce aux descripteurs)
    - Méthode définie dans l'espace de nom de la classe
- Les méthodes sur les instances sont des attributs
- Les opérateurs sont des méthodes spéciales
    - Définition en dur pour simplifier notre gestion des opérateurs
    - Pourrait parcourir les fichiers .pyi de la stdlib pour créer ces données
- Opérateurs basés sur des comportements dynamiques : exécuter du code à la volée dans le typeur
    - Pour gérer l'union de types (doit renvoyer la vraie expression résultante)
    - Pour gérer le relai des arguments
- Unification des opérateurs et des appels au sein d'une même fonction

# 9. Conclusion

- Analyseur très léger mais qui couvre déjà plusieurs fonctionnalités
- Il manque :
    - Attributs
    - Autres opérateurs
    - Types composés et vérification récursive
    - Inférence de types
    - Types génériques, protocoles, Any, varargs

- Karaoké hommage à Boby Lapointe
- Support et snippets disponibles en ligne
