from publist import storage


def test_generate_uid_happy_path():
    res1 = storage._generate_uid()
    res2 = storage._generate_uid()

    assert isinstance(res1, str)
    assert isinstance(res2, str)
    assert res1 != res2