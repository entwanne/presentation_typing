a: int = 3 + int('5') # OK
b: str = str(3) + '5' # OK

b = str(3) + int('5') # KO
