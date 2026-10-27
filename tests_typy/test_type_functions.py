def test_operations(typy, sample):
    typy.run_path(sample)
    assert [str(e) for e in typy.errors] == [
        f'Expression error on {sample}::4: Incompatible operation Add for values of types str and int',
    ]
