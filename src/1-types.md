# Let's talk about types

### A walk inside Python type system


## Let's talk about types

- Python is strongly typed

```pycon
>>> 5 + 3
```

```pycon
>>> 5 + '3'
```


## Let's talk about types

- Python is dynamically typed
    - Types are resolved at runtime

```pycon
>>> value = int(x) if (x := input()) else None
>>> value + 1
```


## Let's talk about types

- Python is dynamically typed
    - Values are typed, not variables

```pycon
>>> obj = 42
>>> type(obj)
```

---

```pycon
>>> obj = []
>>> type(obj)
```


## Let's talk about types

- Python is duck-typed
   - Structural typing: more interested in interface than in type itself

---

```pycon
>>> max([0, 1, 2, 3])
```

---

```pycon
>>> max(range(10))
```

---

```pycon
>>> max('abcdef')
```


## Let's talk about types

- Types can be checked at runtime with `isinstance` function

```pycon
>>> isinstance([0, 1, 2, 3], list)
```

---

```pycon
>>> isinstance(range(10), list)
```

---

```pycon
>>> isinstance('abcdef', list)
```


## Let's talk about types

- This function is more powerful than you could expect

```pycon
>>> from collections.abc import Iterable
>>> isinstance([0, 1, 2, 3], Iterable)
```

---

```pycon
>>> isinstance(range(10), Iterable)
```

---

```pycon
>>> isinstance('abcdef', Iterable)
```

---

```pycon
>>> isinstance(42, Iterable)
```


## Let's talk about types

- This works with hooks and allows recognization of types by protocol

```pycon
>>> from abc import ABC
>>> class Number(ABC):
...     @classmethod
...     def __subclasshook__(cls, subcls):
...         return hasattr(subcls, '__int__')
```

---

```pycon
>>> isinstance(42, Number)
```

---

```pycon
>>> isinstance(4.2, Number)
```

---

```pycon
>>> isinstance('42', Number)
```
