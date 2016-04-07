input_path = './1/input.txt'
output_path = './next_state.txt'
log_writer = open('./traverse_log.txt', 'w')
trace_state = open('./trace_state.txt', 'w')


import copy
import sys
import os

def get_config(input_path):
    fh = open(input_path, 'r')
    for i, line in enumerate(fh.readlines()):
        if i == 0:
            taskno = int(line)
        if taskno is not 4:
            if i == 1:
                player = line[0]
            elif i == 2:
                depth = int(line)
            if i > 2:
                return dict(taskno=taskno, player=player, depth=depth)
        else:
            if i == 1:
                player = line[0]
            elif i == 2:
                algo = int(line)
            elif i == 3:
                depth = int(line)
            elif i == 4:
                player2 = line[0]
            elif i == 5:
                algo2 = int(line)
            elif i == 6:
                depth2 = int(line)
            if i > 6:
                return dict(taskno=taskno, player=player,  player2=player2, depth=depth, depth2=depth2, algo=algo, algo2=algo2)


def get_nuts(taskno, input_path):
    nuts = [[0 for x in range(5)] for x in range(5)]
    if taskno is 4:
        shift = 7
    if taskno is not 4:
        shift = 3
    fh = open(input_path, 'r')
    for i, line in enumerate(fh.readlines()):
        if i >= (shift + 0) and i < (shift + 5):
            tmp = line.split()
            for index in range(5):
                nuts[i - shift][index] = int(tmp[index])
        else:
            pass
    return nuts


def get_board_matrix(taskno, input_path):
    board = [[0 for x in range(5)] for x in range(5)]
    if taskno is 4:
        shift = 12
    if taskno is not 4:
        shift = 8
    fh = open(input_path, 'r')
    for i, line in enumerate(fh.readlines()):
        if i >= (shift + 0) and i < (shift + 5):
            for index in range(5):
                board[i - shift][index] = line[index]
        else:
            pass
    return board


def opponent(player):
    if player == 'X':
        return 'O'
    else:
        return 'X'


def get_matrix_coordinate(coordinate):
    if coordinate[1] == 0:
        str = 'A'
    elif coordinate[1] == 1:
        str = 'B'
    elif coordinate[1] == 2:
        str = 'C'
    elif coordinate[1] == 3:
        str = 'D'
    elif coordinate[1] == 4:
        str = 'E'
    if coordinate[0] == 0:
        return str + '1'
    elif coordinate[0] == 1:
        return str + '2'
    elif coordinate[0] == 2:
        return str + '3'
    elif coordinate[0] == 3:
        return str + '4'
    elif coordinate[0] == 4:
        return str + '5'


def can_raid(board, coordinate, player):
    if not board[coordinate[0]][coordinate[1]] == '*':
        return False
    if coordinate[0] > 0 and board[coordinate[0] - 1][coordinate[1]] == player:
        return True
    if coordinate[0] < 4 and board[coordinate[0] + 1][coordinate[1]] == player:
        return True
    if coordinate[1] > 0 and board[coordinate[0]][coordinate[1] - 1] == player:
        return  True
    if coordinate[1] < 4 and board[coordinate[0]][coordinate[1] + 1] == player:
        return  True
    else:
        return False


def can_sneak(board, coordinate, player):
    if not board[coordinate[0]][coordinate[1]] == '*':
        return False
    if can_raid(board, coordinate, player):
        return False
    else:
        return True


def sneak(board, coordinate, player):
    board[coordinate[0]][coordinate[1]] = player


def raid(board, coordinate, player):
    board[coordinate[0]][coordinate[1]] = player
    if coordinate[0] > 0 and board[coordinate[0] - 1][coordinate[1]] == opponent(player):
        board[coordinate[0]-1][coordinate[1]] = player
    if coordinate[0] < 4 and board[coordinate[0] + 1][coordinate[1]] == opponent(player):
        board[coordinate[0]+1][coordinate[1]] = player
    if coordinate[1] > 0 and board[coordinate[0]][coordinate[1] - 1] == opponent(player):
        board[coordinate[0]][coordinate[1] - 1] = player
    if coordinate[1] < 4 and board[coordinate[0]][coordinate[1] + 1] == opponent(player):
        board[coordinate[0]][coordinate[1] + 1] = player


def print_trace_state(board):
    for i in range(5):
        for j in range(5):
            trace_state.write(board[i][j])
        trace_state.write('\r\n')


def output(board, path):
    fout = open(path, 'w')
    for i in range(5):
        for j in range(5):
            fout.write(board[i][j])
        if i == 4:
            break
        fout.write('\r\n')
    fout.close()


def change_to_infinity(input):
    if input == 1000:
        return str('Infinity')
    if input == -1000:
        return str('-Infinity')
    else:
        return str(input)

def vacancy_exist(board):
    for i in range(5):
        for j in range(5):
            if board[i][j] == '*':
                return True
    return False


class chess_board:
    def __init__(self, input_path):
        self.config = get_config(input_path)
        taskno = self.config['taskno']
        self.nuts_distribute = get_nuts(taskno, input_path) #a matrix of integers representing the nuts number
        self.board = get_board_matrix(taskno, input_path) #a matrix of 'x' 'o' '*'
        # self.pieces = parse_board(self.board)
        self.best_matrix = [[-1000 for x in range(5)] for x in range(5)]
        self.pruning_best_matrix = [[-1000 for x in range(5)] for x in range(5)]

    def get_board(self):
        return copy.deepcopy(self.board)

    def update_board(self, board):
        self.board = copy.deepcopy(board)

    def compute_E(self, board, player):
        player_value = 0
        opponent_value = 0
        for i in range(5):
            for j in range(5):
                if board[i][j] == player:
                    player_value += self.nuts_distribute[i][j]
                elif board[i][j] == opponent(player):
                    opponent_value += self.nuts_distribute[i][j]
        return (player_value - opponent_value)

    def bfs_explore(self, board, player):
        l = list()
        for i in range(5):
            for j in range(5):
                if can_raid(board, (i, j), player):
                    tmp_board = copy.deepcopy(board)
                    raid(tmp_board, (i, j), player)
                    e = self.compute_E(tmp_board, player)
                    l.append(((i, j), e))
                elif can_sneak(board, (i, j), player):
                    tmp_board = copy.deepcopy(board)
                    sneak(tmp_board, (i, j), player)
                    e = self.compute_E(tmp_board, player)
                    l.append(((i, j), e))
        return l

    def bfs_next(self, board, player):
        l = self.bfs_explore(board, player)
        max_e = -1000
        max_piece = None
        for element in l:
            if element[1] > max_e:
                max_e = element[1]
                max_piece = element[0]
        return (max_e, max_piece)


    def minimax(self, board, player, depth):
        log_writer.write('Node,Depth,Value')
        # self.best_matrix = [[-1000 for x in range(5)] for x in range(5)]
        coordinates = list()
        return self.minimax_helper(board, 0, depth, player, player, coordinates)
        # print(coordinate_value)
        # for i in range(5):
        #     for j in range(5):
        #         if self.best_matrix[i][j] == coordinate_value:
        #             return (coordinate_value, (i, j))

    def minimax_helper(self, board, depth, end_depth, player, starter, coordinates):
        if depth == end_depth or not vacancy_exist(board):
            current_e = self.compute_E(board, starter)
            #print(get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(current_e))
            log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(current_e))
            return (current_e, copy.deepcopy(coordinates[0]))

        if player == starter:

            if len(coordinates) == 0:
                #print('root' + ',' + str(depth) + ',' + '-Infinity')
                log_writer.write('\r\n' + 'root' + ',' + str(depth) + ',' + '-Infinity')
            elif len(coordinates) > 0:
                #print(get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + '-Infinity')
                log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + '-Infinity')

            max_value = -1000
            for i in range(5):
                for j in range(5):

                    tmp_board = copy.deepcopy(board)
                    if can_raid(tmp_board, (i, j), player) or can_sneak(tmp_board, (i, j), player):
                        coordinates.append((i, j))
                        if can_raid(tmp_board, (i, j), player):
                            raid(tmp_board, (i, j), player)
                        elif can_sneak(tmp_board, (i, j), player):
                            sneak(tmp_board, (i, j), player)
                        value_and_piece = self.minimax_helper(tmp_board, depth+1, end_depth, opponent(player), starter, coordinates)
                        value = value_and_piece[0]
                        if value > max_value:
                            max_value = value;
                            max_piece = value_and_piece[1]
                        del coordinates[-1]

                        #print(max_piece, max_value)
                        if len(coordinates) == 0:
                           # print('root' + ',' + str(depth) + ',' + str(max_value))
                            log_writer.write('\r\n' + 'root' + ',' + str(depth) + ',' + str(max_value))
                        elif len(coordinates) > 0:
                           # print(get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(max_value))
                            log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(max_value))

                        self.best_matrix[i][j] = value
            # print(self.best_matrix)
            return (max_value, max_piece)

        if not player == starter:

            if len(coordinates) == 0:
               # print('root' + ',' + str(depth) + ',' + 'Infinity')
                log_writer.write('\r\n' + 'root' + ',' + str(depth) + ',' + 'Infinity')
            elif len(coordinates) > 0:
               # print(get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + 'Infinity')
                log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + 'Infinity')

            min_value = 1000
            for i in range(5):
                for j in range(5):
                    tmp_board = copy.deepcopy(board)
                    if can_raid(tmp_board, (i, j), player) or can_sneak(tmp_board, (i, j), player):
                        coordinates.append((i, j))
                        if can_raid(tmp_board, (i, j), player):
                            raid(tmp_board, (i, j), player)
                        elif can_sneak(tmp_board, (i, j), player):
                            sneak(tmp_board, (i, j), player)
                        value_and_piece = self.minimax_helper(tmp_board, depth+1, end_depth, opponent(player), starter, coordinates)
                        value = value_and_piece[0]
                        if value < min_value:
                            min_value = value
                            min_piece = value_and_piece[1]
                        del coordinates[-1]

                      #  print(min_piece, min_value)
                        if len(coordinates) == 0:
                           # print('root' + ',' + str(depth) + ',' + str(min_value))
                            log_writer('\r\n' + 'root' + ',' + str(depth) + ',' + str(min_value))
                        elif len(coordinates) > 0:
                           # print(get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(min_value))
                            log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(min_value))


            return (min_value, min_piece)

    def pruning(self, board, player, depth):
        log_writer.write('Node,Depth,Value,Alpha,Beta')
        # self.pruning_best_matrix = [[-1000 for x in range(5)] for x in range(5)]
        coordinates = list()
        return self.pruning_helper(board, 0, depth, player, -1000, 1000, player, coordinates)
        # print(coordinate_value)
        # for i in range(5):
        #     for j in range(5):
        #         if self.pruning_best_matrix[i][j] == coordinate_value:
        #             return (coordinate_value, (i, j))

    def pruning_helper(self, board, depth, end_depth, player, Alpha, Beta, starter, coordinates):
        if depth == end_depth or not vacancy_exist(board):
            current_e = self.compute_E(board, starter)
           # print(get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(current_e) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
            log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(current_e) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
            return (current_e, coordinates[0])

        if player == starter:

            if len(coordinates) == 0:
               # print('root' + ',' + str(depth) + ',' + '-Infinity' + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                log_writer.write('\r\n' + 'root' + ',' + str(depth) + ',' + '-Infinity' + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
            elif len(coordinates) > 0:
               # print(get_matrix_coordinate(coordinates[0]) + ',' + str(depth) + ',' + '-Infinity' + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + '-Infinity' + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))

            max_value = -1000
            for i in range(5):
                for j in range(5):

                    tmp_board = copy.deepcopy(board)
                    if can_raid(tmp_board, (i, j), player) or can_sneak(tmp_board, (i, j), player):
                        coordinates.append((i, j))
                        if can_raid(tmp_board, (i, j), player):
                            raid(tmp_board, (i, j), player)
                        elif can_sneak(tmp_board, (i, j), player):
                            sneak(tmp_board, (i, j), player)
                        value_and_piece = self.pruning_helper(tmp_board, depth+1, end_depth, opponent(player), Alpha, Beta, starter, coordinates)
                        value = value_and_piece[0]
                        if value > max_value:
                            max_value = value
                            max_piece = value_and_piece[1]
                        # max_value = max(max_value, value)
                        tmp_Alpha = max(Alpha, max_value)
                        del coordinates[-1]

                        if tmp_Alpha >= Beta:
                            if len(coordinates) == 0:
                               # print('root' + ',' + str(depth) + ',' + str(max_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                log_writer.write('\r\n' + 'root' + ',' + str(depth) + ',' + str(max_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                            elif len(coordinates) > 0:
                               # print(get_matrix_coordinate(coordinates[0]) + ',' + str(depth) + ',' + str(max_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(max_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                            Alpha = tmp_Alpha

                        else:
                            Alpha = tmp_Alpha
                            if len(coordinates) == 0:
                              #  print('root' + ',' + str(depth) + ',' + str(max_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                log_writer.write('\r\n' + 'root' + ',' + str(depth) + ',' + str(max_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                            elif len(coordinates) > 0:
                               # print(get_matrix_coordinate(coordinates[0]) + ',' + str(depth) + ',' + str(max_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(max_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))

                        if Beta <= Alpha:
                            break
                if Beta <= Alpha:
                    break


            # print(self.best_matrix)
            return (max_value, max_piece)

        if not player == starter:

            if len(coordinates) == 0:
               # print('root' + ',' + str(depth) + ',' + 'Infinity' + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                log_writer.write('\r\n' + 'root' + ',' + str(depth) + ',' + 'Infinity' + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
            elif len(coordinates) > 0:
               # print(get_matrix_coordinate(coordinates[0]) + ',' + str(depth) + ',' + 'Infinity' + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + 'Infinity' + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))

            min_value = 1000
            for i in range(5):
                for j in range(5):
                    tmp_board = copy.deepcopy(board)
                    if can_raid(tmp_board, (i, j), player) or can_sneak(tmp_board, (i, j), player):
                        coordinates.append((i, j))
                        if can_raid(tmp_board, (i, j), player):
                            raid(tmp_board, (i, j), player)
                        elif can_sneak(tmp_board, (i, j), player):
                            sneak(tmp_board, (i, j), player)
                        value_and_piece = self.pruning_helper(tmp_board, depth+1, end_depth, opponent(player),Alpha, Beta, starter, coordinates)
                        value = value_and_piece[0]
                        if value < min_value:
                            min_value = value
                            min_piece = value_and_piece[1]
                        # min_value = min(min_value, value)
                        tmp_Beta = min(Beta, min_value)
                        del coordinates[-1]

                        # if len(coordinates) == 0:
                        #     print('root' + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                        #     log_writer('\r\n' + 'root' + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                        # elif len(coordinates) > 0:
                        #     print(get_matrix_coordinate(coordinates[0]) + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                        #     log_writer.write('\r\n' + get_matrix_coordinate(coordinates[0]) + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))


                        if tmp_Beta <= Alpha:
                            if len(coordinates) == 0:
                               # print('root' + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                log_writer('\r\n' + 'root' + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                            elif len(coordinates) > 0:
                               # print(get_matrix_coordinate(coordinates[0]) + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                Beta = tmp_Beta

                        else:
                            Beta = tmp_Beta

                            if len(coordinates) == 0:
                               # print('root' + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                log_writer('\r\n' + 'root' + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                            elif len(coordinates) > 0:
                               # print(get_matrix_coordinate(coordinates[0]) + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))
                                log_writer.write('\r\n' + get_matrix_coordinate(coordinates[-1]) + ',' + str(depth) + ',' + str(min_value) + ',' + change_to_infinity(Alpha) + ',' + change_to_infinity(Beta))

                        if Beta <= Alpha:
                            # log_writer.write("-")
                            break
                if Beta <= Alpha:
                    break

            return (min_value, min_piece)

    def algo_selecter(self, algo_no, board, player, depth):
        if algo_no == 1:
            return self.bfs_next(board, player)
        elif algo_no == 2:
            return self.minimax(board, player, depth)
        elif algo_no == 3:
            return self.pruning(board, player, depth)


def main():
    file_input = sys.argv[-1]
    input_path = file_input
    board = chess_board(input_path)
    if board.config['taskno'] == 1:
        next_coordinate = board.bfs_next(board.get_board(), board.config['player'])[1]
       # print(next_coordinate)
        new_board = board.get_board()
        if can_raid(new_board, next_coordinate, board.config['player']):
            raid(new_board, next_coordinate, board.config['player'])
        elif can_sneak(new_board, next_coordinate, board.config['player']):
            sneak(new_board, next_coordinate, board.config['player'])
        output(new_board, output_path)

    # if board.config['taskno'] == 2:
    #     next_coordinate_value = board.minimax(board.board, board.config['player'])
    #     next_coordinate = next_coordinate_value[1]
    #     new_board = board.get_board()
    #     if can_raid(new_board, next_coordinate, board.config['player']):
    #         raid(new_board, next_coordinate, board.config['player'])
    #     elif can_sneak(new_board, next_coordinate, board.config['player']):
    #         sneak(new_board, next_coordinate, board.config['player'])
    #     output(new_board, output_path)
    if board.config['taskno'] == 2:
        next_coordinate = board.minimax(board.board, board.config['player'], board.config['depth'])[1]
      #  print(next_coordinate)
        new_board = board.get_board()
        if can_raid(new_board, next_coordinate, board.config['player']):
            raid(new_board, next_coordinate, board.config['player'])
        elif can_sneak(new_board, next_coordinate, board.config['player']):
            sneak(new_board, next_coordinate, board.config['player'])
        output(new_board, output_path)

    if board.config['taskno'] == 3:
        next_coordinate_value = board.pruning(board.board, board.config['player'], board.config['depth'])
        next_coordinate = next_coordinate_value[1]
        new_board = board.get_board()
        if can_raid(new_board, next_coordinate, board.config['player']):
            raid(new_board, next_coordinate, board.config['player'])
        elif can_sneak(new_board, next_coordinate, board.config['player']):
            sneak(new_board, next_coordinate, board.config['player'])
        output(new_board, output_path)

    if board.config['taskno'] == 4:

        curr_board = board.get_board()

        while vacancy_exist(curr_board):
            next_coordinate = board.algo_selecter(board.config['algo'], curr_board, board.config['player'], board.config['depth'])[1]
           # print(next_coordinate)
            if can_raid(curr_board, next_coordinate, board.config['player']):
                raid(curr_board, next_coordinate, board.config['player'])
            elif can_sneak(curr_board, next_coordinate, board.config['player']):
                sneak(curr_board, next_coordinate, board.config['player'])
            board.update_board(curr_board)
            print_trace_state(curr_board)

            if not vacancy_exist(curr_board):
                break

            print(curr_board)
            next_coordinate = board.algo_selecter(board.config['algo2'], curr_board, board.config['player2'], board.config['depth2'])[1]
          #  print(next_coordinate)
            if can_raid(curr_board, next_coordinate, board.config['player2']):
                raid(curr_board, next_coordinate, board.config['player2'])
            elif can_sneak(curr_board, next_coordinate, board.config['player2']):
                sneak(curr_board, next_coordinate, board.config['player2'])
            else:
                raise('mitake')
            board.update_board(curr_board)
            print_trace_state(curr_board)

           # print(curr_board)

        trace_state.close()
        log_writer.close()

        #handle with the empty line in the end of './trace_state.txt'
        with open('./trace_state.txt', 'rb+') as filehandle:
            filehandle.seek(-1, os.SEEK_END)
            filehandle.truncate()
            filehandle.seek(-1, os.SEEK_END)
            filehandle.truncate()

if __name__ == "__main__": main()
