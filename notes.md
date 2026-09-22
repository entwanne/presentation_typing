1. Le typage en Python

- Typage fort mais dynamique
- duck-typing
    - isinstance, types abstraits

2. Typage statique

- Annotations de types
    - Accès aux annotations depuis Python
- Analyse statique : mypy
- duck-typing = typage structurel
    - Types composés (`list[int]`, `tuple[str, str]`)
    - Types génériques
    - Protocoles

3. Écrire un analyseur de types
3.1. Analyse statique

- Module `ast`, `ast.parse` et `NodeVisitor`
    - méthodes `visit_XXX`
- Construction par itération du premier POC (eda75a7)
- Boilerplate Python pour en faire un programme CLI (9c2bf3a)
- Tests (d58a8c8)

3.2. Modèle objet de Python

- Types & instances, type_model_schema.svg
- Représentation dans typy (4615492 + ecf13d2) :
    - classes PyObject (objet Python, possède un type), Type & Value
    - `Type.type = Type`

3.3. Expressions de types

- Assignations multiples (f6fbbc6)
- Types concrets et expressions de types (e254edf), union de types (4c62f7e)

3.4. Espaces de noms

- Gestion du curseur et du contexte (f992ff2)
- Gestion du namespace (2faecd7)

3.5. Fonctions et opérations

- Définitions de fonctions et appels (399892f)
- Opérateurs binaires (54e88ff)

3.6. Types

- Les types comme des fonctions (ffb6fe3)
- Définition de classes (dd20d54)
- Appel de méthodes (8f63bea)
- Opérateurs (6d3c775)
- Définition de méthodes (ed3690f)

3.7. Ce qu'il manque

- Autres opérations
- Types composés et vérification récursive
- Types génériques, protocoles, Any, arguments variadiques

4. T'as typé ton Python

- Karaoké

5. Conclusion / questions
