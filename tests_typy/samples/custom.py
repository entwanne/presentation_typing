class A:
    pass

a: A = A() # OK
b: int = A() # KO

c: A = 0 # KO

class D(int):
    pass

d: int = D() # OK

e: A | int = A() # OK
f: A | int = 5 # OK
g: A | int = '' # KO
h: A | int = D() # OK

i: D | int = A() # KO
j: D | int = D() # OK
k: D | int = 5 # OK
l: D | int = '' # KO
