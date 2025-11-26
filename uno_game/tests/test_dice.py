import json
## card.py removed; update or remove dice tests as needed


def test_create_dice_rolls_length_and_range():
    n = 20
        pytest.skip("create_dice_rolls removed; 3D dice roller is now used externally.")
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
        pytest.skip("create_dice_rolls removed; 3D dice roller is now used externally.")
    assert a != b or len({tuple(d['value'] for d in a), tuple(d['value'] for d in b)}) == 2
