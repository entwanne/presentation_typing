def test_custom(typy, sample):
    typy.run_path(sample)
    assert [str(e) for e in typy.errors] == [
        f'Assignment error on {sample}::5: Trying to assign value of type A to variable b annotated with int',
        f'Assignment error on {sample}::7: Trying to assign value of type int to variable c annotated with A',
        f'Assignment error on {sample}::16: Trying to assign value of type str to variable g annotated with (A | int)',
        f'Assignment error on {sample}::19: Trying to assign value of type A to variable i annotated with (D | int)',
        f'Assignment error on {sample}::22: Trying to assign value of type str to variable l annotated with (D | int)',
    ]
