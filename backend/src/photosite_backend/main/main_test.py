from photosite_backend.main import return_hi


def test_return_hi():
    assert return_hi() == "hi!"
