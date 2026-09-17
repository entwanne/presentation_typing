from typy import Typy


def test_assignment():
    sample = 'tests_typy/samples/assignment.py'
    typy = Typy()

    typy.run_path(sample)
    assert [str(e) for e in typy.errors] == [
        f'Assignment error on {sample}::2: Trying to assign value of type str to variable b annotated with int',
        f'Assignment error on {sample}::5: Trying to assign value of type int to variable c annotated with str',
    ]
