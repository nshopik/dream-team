from decimal import ROUND_HALF_UP, Decimal

from export import build_stats


def shown(value):
    """The win rate as the stats page shows it."""
    return str(Decimal(str(value)).quantize(Decimal('0.01'), ROUND_HALF_UP))


def test_win_rate_shown_to_two_places():
    games = [{'won': True}] * 149 + [{'won': False}] * 51
    stats = build_stats(games)
    assert stats['win_rate'] == 0.745
    assert shown(stats['win_rate']) == '0.75'
