from uno_game.game.game_engine import GameManager
cases = [[4,5,6],[1,1,1],[2,2,2],[1,2,3],[1,4,5],[2,3,6],[1,5,5],[2,4,5]]
for c in cases:
    res = GameManager._calculate_score(c.copy())
    print(c, '->', res)
