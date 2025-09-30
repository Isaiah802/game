import json
from cards.card import create_dice_rolls


def test_create_dice_rolls_length_and_range():
    n = 20
    rolls = create_dice_rolls(n)
    assert isinstance(rolls, list)
    assert len(rolls) == n
    for r in rolls:
        assert isinstance(r, dict)
        assert 'value' in r
        v = r['value']
        assert isinstance(v, int)
        assert 1 <= v <= 6


def test_create_dice_rolls_randomness():
    # Ensure two calls are not identical (very low chance of collision but acceptable for unit test)
    a = create_dice_rolls(10)
    b = create_dice_rolls(10)
    assert a != b or len({tuple(d['value'] for d in a), tuple(d['value'] for d in b)}) == 2
