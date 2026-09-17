def func() -> int:
    return 0

a: int = func() # OK
b: str = func() # KO

def addition(a: int, b: int) -> int:
    return a + b

addition(3, 5) # OK
addition(3, '5') # KO
addition('3', '5') # KO
