def test_operations(typy, sample):
    typy.run_path(sample)
    assert [str(e) for e in typy.errors] == [
        f'Expression error on {sample}::3: Incompatible operation Add for values of types int and str',
        f'Assignment error on {sample}::6: Trying to assign value of type int to variable b annotated with str',
    ]
