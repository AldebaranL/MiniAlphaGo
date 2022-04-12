# 导入随机包
import random


class RandomPlayer:
    """
    随机玩家, 随机返回一个合法落子位置
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.color = color

    def random_choice(self, board):
        """
        从合法落子位置中随机选一个落子位置
        :param board: 棋盘
        :return: 随机合法落子位置, e.g. 'A1'
        """
        # 用 list() 方法获取所有合法落子位置坐标列表
        action_list = list(board.get_legal_actions(self.color))

        # 如果 action_list 为空，则返回 None,否则从中选取一个随机元素，即合法的落子坐标
        if len(action_list) == 0:
            return None
        else:
            return random.choice(action_list)

    def get_move(self, board):
        """
        根据当前棋盘状态获取最佳落子位置
        :param board: 棋盘
        :return: action 最佳落子位置, e.g. 'A1'
        """
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))
        action = self.random_choice(board)
        return action

class HumanPlayer:
    """
    人类玩家
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.color = color

    def get_move(self, board):
        """
        根据当前棋盘输入人类合法落子位置
        :param board: 棋盘
        :return: 人类下棋落子位置
        """
        # 如果 self.color 是黑棋 "X",则 player 是 "黑棋"，否则是 "白棋"
        if self.color == "X":
            player = "黑棋"
        else:
            player = "白棋"

        # 人类玩家输入落子位置，如果输入 'Q', 则返回 'Q'并结束比赛。
        # 如果人类玩家输入棋盘位置，e.g. 'A1'，
        # 首先判断输入是否正确，然后再判断是否符合黑白棋规则的落子位置
        while True:
            action = input(
                "请'{}-{}'方输入一个合法的坐标(e.g. 'D3'，若不想进行，请务必输入'Q'结束游戏。): ".format(player,
                                                                             self.color))

            # 如果人类玩家输入 Q 则表示想结束比赛
            if action == "Q" or action == 'q':
                return "Q"
            else:
                row, col = action[1].upper(), action[0].upper()

                # 检查人类输入是否正确
                if row in '12345678' and col in 'ABCDEFGH':
                    # 检查人类输入是否为符合规则的可落子位置
                    if action in board.get_legal_actions(self.color):
                        return action
                else:
                    print("你的输入不合法，请重新输入!")

import copy
import math
import random


def reverse_color(color):
    #反转当前节点颜色
    return 'O' if color == 'X' else 'X'


class Node:
    #蒙特卡洛树的结点类
    def __init__(self, board, color, parent=None, action=None):
        self.visit = 0
        self.reward = 0.0
        self.board = board
        self.children = []
        self.parent = parent
        self.action = action
        self.color = color

    def add_child(self, new_board, action):
        #扩展当前节点的子节点
        child_node = Node(new_board, parent=self, action=action, color=reverse_color(self.color))
        self.children.append(child_node)

    def if_fully_expanded(self):
        #判断当前节点是否被完全扩展
        cnt_max = len(list(self.board.get_legal_actions(self.color)))
        # print("cnt_max = ",cnt_max)
        cnt_now = len(self.children)
        # print("cnt_now = ", cnt_now)
        if (cnt_max <= cnt_now):
            return True
        else:
            return False

def random_pick(some_list, probabilities):
    x = random.uniform(0,1)
    cumulative_probability = 0.0
    sum=0.0
    for i in probabilities:
        sum+=i
    for item, item_probability in zip(some_list, probabilities):
         cumulative_probability += item_probability
         if x < cumulative_probability/sum:
               break
    return item

def choose_action(actions):
    '''    attemp1=['A1','A7','H1','H8']
    attemp2r=['A2','H2','H6','B1','G1','B7','G7','A6']
    attemp3 = ['A3', 'H3', 'H5', 'C1', 'F1', 'C7', 'F7', 'A5']
    if 'A1' in actions:'''
    col=random_pick(['A','H','B','G','C','F','D','E'],[10,10,5,5,2,2,1,1])
    row = random_pick(['1', '8', '2', '7', '3', '6', '4', '5'], [10, 10, 5, 5, 2, 2, 1, 1])
    return str(col+row)

class AIPlayer:
    """
    AI 玩家
    """
    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.color = color
        self.C = 0.01 #UCB1超参数C
        self.MaxT = 100 #最大迭代次数
        self.root = None

    def if_terminal(self, state):
        # to see the game is terminal or not
        action_black = list(state.get_legal_actions('X'))
        action_white = list(state.get_legal_actions('O'))
        if (len(action_white) == 0 and len(action_black) == 0):
            return True
        else:
            return False

    def back_propagate(self, node, reward):
        #反向更新
        while (node is not None):
            node.visit += 1
            if self.color == 'X':
                node.reward += reward
            else:
                node.reward -= reward
            node = node.parent

    def reward_function(self, board):
        '''
        reward计算函数
        若胜利则奖励100分，附加胜利子数，失败则减，平局奖励为0
        除100使之与探索量的量级接近
        '''
        winner, diff = board.get_winner()
        if winner == 2:
            return 0
        elif winner == 0:
            return (100 + diff) /100.0
        else:
            return (-100 - diff) /100.0

    def if_terminal(self, board):
        # to see a state is terminal or not
        action_black = list(board.get_legal_actions('X'))
        action_white = list(board.get_legal_actions('O'))
        if (len(action_white) == 0 and len(action_black) == 0):
            return True
        else:
            return False

    def stimulate_policy(self, node):
        #模拟
        board = copy.deepcopy(node.board)
        color = copy.deepcopy(node.color)
        cnt = 0
        while not self.if_terminal(board):
            #若未结束，则随机下至结束
            actions = list(board.get_legal_actions(color))
            if (len(actions) != 0):
                action = random.choice(actions)
                board._move(action, color)
            color = reverse_color(color)
        return self.reward_function(board)

    def distanceFromCenter(self,node):
        x,y = node.board.board_num(node.action)
        return math.sqrt(abs(x-3.5)**2+abs(y-3.5)**2)
    def ucb(self, node):
        #选择当前孩子中ucb值最大的，并返回
        max = -float('inf')
        max_set = []
        for c in node.children:
            exploit = c.reward / c.visit
            explore = math.sqrt(2.0 * math.log(node.visit) / float(c.visit))
            uct_score = exploit + self.C * explore

            if (uct_score == max):
                max_set.append(c)
            elif (uct_score > max):
                max_set = [c]
                max = uct_score

        if (len(max_set) == 0):
            print("max_set is empty")
            print(len(node.children))
            # node.board.display()
            return node.parent
        else:
            return random.choice(max_set)
    def ucb1(self, node):
        #选择当前孩子中ucb值最大的，并返回
        max = -float('inf')
        max_set = []
        for c in node.children:
            exploit = c.reward / c.visit
            explore = math.sqrt(2.0 * math.log(node.visit) / float(c.visit))
            uct_score = exploit + self.C * explore #+0.2 * self.distanceFromCenter(c)

            if (uct_score == max):
                max_set.append(c)
            elif (uct_score > max):
                max_set = [c]
                max = uct_score

        if (len(max_set) == 0):
            print("max_set is empty")
            print(len(node.children))
            # node.board.display()
            return node.parent
        else:
            return random.choice(max_set)

    def expand(self, node):
        #扩展当前搜索树
        '''actions_available = list(node.board.get_legal_actions(node.color))
        actions_already = [c.action for c in node.children]
        if(len(actions_available)==0):
            return node.parent
        action = random.choice(actions_available)
        while action in actions_already:
            action=random.choice(actions_available)'''
        #'''
        actions_available = list(node.board.get_legal_actions(node.color))
        if (len(actions_available) == 0):
            return node.parent
        actions_already = [c.action for c in node.children]
        action = choose_action(actions_available)
        while action not in actions_available or action in actions_already:
            action = choose_action(actions_available)
        #'''
        # print(action)
        new_state = copy.deepcopy(node.board)
        new_state._move(action, node.color)
        # new_state.display()
        node.add_child(new_state, action=action)
        return node.children[-1]

    def select_policy(self, node):
        #选择并扩展
        while (not self.if_terminal(node.board)):
            if (len(list(node.board.get_legal_actions(node.color))) == 0):
                return node
            elif (not node.if_fully_expanded()):
                # print("need to expand")
                new_node = self.expand(node)
                # print("end of expand")
                return new_node
            else:
                # print("fully expaned")
                # node.state.display()
                # print(len(node.children))
                # print(list(node.state.get_legal_actions(node.color)))
                node = self.ucb1(node)
        return node

    def MCTS_search(self, root):
        #蒙特卡洛树搜索
        # print("root state :")
        # root.state.display()
        for t in range(self.MaxT):
            leave = self.select_policy(root)#选择
            # print("leave state:")
            # leave.state.display()
            rewards = self.stimulate_policy(leave)#模拟
            self.back_propagate(leave, rewards)#反向更新
        # print("root state :")
        # root.state.display()
        return self.ucb1(root).action

    def get_move(self, board):
        """
        根据当前棋盘状态获取最佳落子位置
        :param board: 棋盘
        :return: action 最佳落子位置, e.g. 'A1'
        """
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        #print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))

        # -----------------请实现你的算法代码--------------------------------------
        root_board = copy.deepcopy(board)
        root = Node(board=root_board, color=self.color)
        action = self.MCTS_search(root)
        # ------------------------------------------------------------------------
        return action

class Node2:
    def __init__(self,state,color,parent = None,action = None):
        self.visit = 0
        self.blackwin = 0
        self.whitewin = 0
        self.reward = 0.0
        self.state = state
        self.children = []
        self.parent = parent
        self.action = action
        self.color = color

    def add_child(self,new_state,action,color):
        child_node = Node2(new_state,parent=self,action = action,color=color)
        self.children.append(child_node)

    def if_fully_expanded(self):
        cnt_max = len(list(self.state.get_legal_actions(self.color)))
        #print("cnt_max = ",cnt_max)
        cnt_now = len(self.children)
       # print("cnt_now = ", cnt_now)
        if(cnt_max <= cnt_now):
            return True
        else:
            return False
class AIPlayer2:
    """
    AI 玩家
    """

    def __init__(self, color,C):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """
        self.C=C
        self.color = color
    def if_terminal(self,state):
        # to see a state is terminal or not
        action_black = list(state.get_legal_actions('X'))
        action_white = list(state.get_legal_actions('O'))
        if(len(action_white) == 0 and len(action_black) == 0):
            return True
        else:
            return False

    def back_propagate(self,node,blackw,whitew):
        while(node is not None):
            node.visit+=1
            node.blackwin+=blackw
            node.whitewin+=whitew
            node = node.parent
        return 0

    def reverse_color(self,color):
        if(color == 'X'):
            return 'O'
        else:
            return 'X'

    def stimulate_policy(self,node):
        board = copy.deepcopy(node.state)
        color = copy.deepcopy(node.color)
        cnt = 0
        while not self.if_terminal(board):
            actions = list(node.state.get_legal_actions(color))
            if(len(actions)==0):
                #no way to go
                color = self.reverse_color(color)
            else:
                #have ways to go
                action = random.choice(actions)
                board._move(action,color)
                color = self.reverse_color(color)
            cnt+=1
            if cnt>20:
                break
        return board.count('X'),board.count('O')


    def ucb(self,node):
        max = -float('inf')
        max_set=[]
        for c in node.children:
            exploit = 0
            if c.color == 'O':
                exploit = c.blackwin/(c.blackwin+c.whitewin)
            else:
                exploit = c.whitewin/(c.blackwin+c.whitewin)
            explore = math.sqrt(2.0*math.log(node.visit)/float(c.visit))
            uct_score = exploit+self.C*explore
            if(uct_score==max):
                max_set.append(c)
            elif(uct_score>max):
                max_set=[c]
                max = uct_score
        if(len(max_set)==0):

           # node.state.display()
            return node.parent
        else:
            return random.choice(max_set)

    def expand(self,node):
        actions_available = list(node.state.get_legal_actions(node.color))
        actions_already = [c.action for c in node.children]
        if(len(actions_available)==0):
            return node.parent
        action = random.choice(actions_available)
        while action in actions_already:
            action=random.choice(actions_available)
        new_state = copy.deepcopy(node.state)
        new_state._move(action,node.color)
        #new_state.display()
        new_color = self.reverse_color(node.color)
        node.add_child(new_state,action = action,color= new_color)
        return node.children[-1]

    def select_policy(self,node):
        while(not self.if_terminal(node.state)):
            if(len(list(node.state.get_legal_actions(node.color)))==0):
                return node
            elif(not node.if_fully_expanded()):
               # print("need to expand")
                new_node = self.expand(node)
               # print("end of expand")
                return new_node
            else:
                #print("fully expaned")
               # node.state.display()
                node = self.ucb(node)
        return node

    def MCTS_search(self,root,maxt = 100):
        #print("root state :")
        #root.state.display()
        for t in range(maxt):
            #print("$$$$$$$$$$$$$$t = ",t)
            leave = self.select_policy(root)
            #print("leave state:")
            #leave.state.display()
            blackwin,whitewin = self.stimulate_policy(leave)
            self.back_propagate(leave,blackw=blackwin,whitew=whitewin)
        #print("root state :")
        #root.state.display()
        return self.ucb(root).action

    def get_move(self, board):
        """
        根据当前棋盘状态获取最佳落子位置
        :param board: 棋盘
        :return: action 最佳落子位置, e.g. 'A1'
        """
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))

        # -----------------请实现你的算法代码--------------------------------------
        action = None
        root_board = copy.deepcopy(board)
        root = Node2(state=root_board,color=self.color)
        action = self.MCTS_search(root)

        # ------------------------------------------------------------------------

        return action