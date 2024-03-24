from calebwilliams import validate_input
from pytest import raises


def test_valid_input():
    inputs = [
        [(1, 2, 3), (2, 3, 4), (3, 4, 5)],
        [(1, 2, 5), (2, 3, 4), (3, 4, 3)],
    ]
    for input in inputs:
        try:
            validate_input(input)
        except Exception as e:
            assert False, f"Valid input raised exception {e}."

        assert True


def test_non_list_input():
    for input in [42, "not a list"]:
        with raises(ValueError, match=r"Input must be a list"):
            validate_input(input)


def test_too_short_input():
    for input in [[], [(1, 2, 3)]]:
        with raises(
            ValueError, match=r"Input list must have at least two elements."
        ):
            validate_input(input)


def test_non_3_tuple_input():
    with raises(ValueError, match=r"not enough values to unpack"):
        validate_input([(1, 2, 3), (2, 1)])


def test_negative_buy_in():
    with raises(ValueError, match=r"All buy-ins must be positive"):
        validate_input([(-1, 2, 4), (0, 3, 6)])


def test_negative_payout():
    with raises(ValueError, match=r"Found a negative net payout"):
        validate_input([(1, 2, 4), (4, 3, 6)])


def test_nonmonotonic_probabilities():
    inputs = [
        [(1, 2, 3), (2, 3, 5), (3, 4, 4)],
        [(1, 2, 3), (2, 3, 1), (3, 4, 2)],
    ]
    for input in inputs:
        with raises(
            ValueError,
            match=r"Probabilities must either always increase or always decrease",
        ):
            validate_input(input)
