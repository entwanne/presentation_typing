class A:
    def test(self: A) -> int:
        return 0

    def pouet(self: A, value: str) -> str:
        return value + '!'


a: A = A() # OK
b: int = a.test() # OK
c: str = a.test() # KO

d: str = a.pouet('test') # OK
e: int = a.pouet('test') # KO
a.pouet(5) # KO

a.tutu() # KO
