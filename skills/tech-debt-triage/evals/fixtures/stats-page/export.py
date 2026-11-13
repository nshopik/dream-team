"""Writes stats.json, which index.html shows."""
import json


def build_stats(games):
    wins = sum(g['won'] for g in games)
    return {'games': len(games), 'win_rate': wins / len(games)}


if __name__ == '__main__':
    with open('games.json') as f:
        games = json.load(f)
    with open('stats.json', 'w') as f:
        json.dump(build_stats(games), f)
