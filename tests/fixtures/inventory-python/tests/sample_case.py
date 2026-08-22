from sample import Parser


def test_parse() -> None:
    assert Parser().parse(" x ") == "x"


def test_empty() -> None:
    with pytest.raises(ValueError):
        Parser().parse("", strict=True)
