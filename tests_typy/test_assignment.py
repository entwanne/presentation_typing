from typy import Typy


def test_assignment():
    sample = 'tests_typy/samples/assignment.py'
    typy = Typy()

    typy.run_path(sample)
    assert [str(e) for e in typy.errors] == [
        f'Assignment error on {sample}::3: Trying to assign value of type str to variable a annotated with int',
        f'Assignment error on {sample}::7: Trying to assign value of type int to variable b annotated with str',
        f'Error on {sample}::9: b variable already defined',
        f'Assignment error on {sample}::13: Trying to assign value of type int to variable d annotated with str',
        f'Assignment error on {sample}::17: Trying to assign value of type str to variable g annotated with (int | float)',
    ]
