# Le typage en Python

## Le typage en Python

- Typage fort
    - Lève des exceptions en cas d'incompatibilités
    - Évite les conversions implicites

```python
5 + 2
```

```python
'5' + '2'
```

```python
5 + '2'
```


## Le typage en Python

- Mais typage dynamique
    - Le type est déduit au _runtime_

```python
value = int(x) if (x := input()) else None
print(value, type(value))
```

---

- Il est lié à une valeur, pas une variable

```python
value = 5
type(value)
```

```python
value = '5'
type(value)
```

## Duck-typing 🦆

- Duck-typing : on s'intéresse à l'interface, pas au type
    - « si ça marche comme un canard et fait coin-coin, on peut le considérer comme un canard »

---

- Une fonction n'a pas besoin de connaître le type d'un argument, seulement de savoir qu'il sera compatible

```python
max([1, 2, 3])
```

```python
max(range(10))
```

```python
import random
max(random.randint(1, 10) for _ in range(10))
```

## Duck-typing 🦆

- Python fournit une fonction `isinstance` pour savoir si une valeur est d'un certain type

```python
isinstance([1, 2, 3], list)
```

```python
isinstance(range(10), list)
```

```python
isinstance('abcdef', list)
```

## Duck-typing 🦆

- Qui fonctionne aussi avec des types abstraits

```python
from collections.abc import Iterable
isinstance([1, 2, 3], Iterable)
```

```python
isinstance(range(10), Iterable)
```

```python
isinstance('abcdef', Iterable)
```

---

- Cela grâce à des mécanismes de _subclass-hooks_ qui ne seront pas abordés ici
    - On retient simplement que le type `Iterable` est abstrait et définit une interface
    - Direction le module `abc` si vous voulez en savoir plus
