# tic-tac-toe-like-game-AI
1. The game board is a 5x5 grid representing territories the squirrel
warriors will trample.
2. Each player takes turns as in chess or tictactoe.
That is, the first player takes a move, then the second player, then back to the first player 
and so forth.
3. Each square has a fixed point value between 1 and 99, based upon its yield of nuts.
4. The values of the squares can be changed for each game, but remain constant within a game.
5. The objective of the game for each player is to score the most points, i.e. the total point
value of all his or her occupied squares. Thus, one wants to capture the squares worth the
most points.
6. The game ends when all the squares are occupied, because no more moves are left.
7. On each turn, a player can make one of two moves:
Raid – You can take over any unoccupied square that is adjacent to one of your current pieces
(horizontally or vertically, but not diagonally). You place a new piece in the taken over square.
Also, any enemy pieces adjacent to your new piece (horizontally or vertically, but not diagonally)
are conquered and replaced by your own pieces. You can Raid a square even if there are no
enemy pieces adjacent to it to be conquered. Once you have made this move, your turn is over.

Sneak – You can take any unoccupied square on the board that is not next to your existing
pieces. This will create a new piece on the board. Unlike Raid which is an aggressive move,
Sneak is a covert operation, so it won’t conquer any enemy pieces. It simply allows one to place
a piece at an unoccupied square that is not reachable by Raid.

8. Any unoccupied square can be taken with either Raid or Sneak, but they are
mutuallyexclusive.
If the square is horizontally or vertically adjacent to an existing selfowned
piece, it’s a Raid. Otherwise it’s a Sneak.
9. Anytime adjacency is checked (e.g. Raid validity, conquering enemy pieces), it's always
checking vertical and horizontal neighbors, but never diagonal. In other words, a diagonal
neighbor is never considered adjacent.
