from players import AIPlayer2,AIPlayer,HumanPlayer
# 导入黑白棋文件
from game import Game

wins=[]
diffs=[]
for i in range(1):
# 人类玩家黑棋初始化
    black_player = AIPlayer2("X",0)

# AI 玩家 白棋初始化
    white_player = AIPlayer("O")

# 游戏初始化，第一个玩家是黑棋，第二个玩家是白棋
    game = Game(black_player, white_player)

# 开始下棋
    game.run()
  #  wins.append(win)
  #  diffs.append(diff)
#print(wins)
#print(diffs)