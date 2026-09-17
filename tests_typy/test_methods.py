def test_assignment(typy, sample):
    typy.run_path(sample)
    assert [str(e) for e in typy.errors] == [
        f'Assignment error on {sample}::11: Trying to assign value of type int to variable c annotated with str',
        f'Assignment error on {sample}::14: Trying to assign value of type str to variable e annotated with int',
        f'Call error on {sample}::15: cannot call pouet with arg types int',
        f'Error on {sample}::17: Unknown attribute tutu on object of type A',
    ]
