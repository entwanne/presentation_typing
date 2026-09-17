def test_functions(typy, sample):
    typy.run_path(sample)
    assert [str(e) for e in typy.errors] == [
        f'Assignment error on {sample}::5: Trying to assign value of type int to variable b annotated with str',
        f'Call error on {sample}::11: cannot call addition with arg types int, str',
        f'Call error on {sample}::12: cannot call addition with arg types str, str',
    ]
