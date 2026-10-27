a: int = 0 # OK
a = 5 # OK
a = "5" # KO

b: str
b = "" # OK
b = 0 # KO

b: str = "" # KO

c: int = 12 # OK

d: str = 12 # KO

e: int | float = 0 # OK
f: int | float = 0.1 # OK
g: int | float = '' # KO
