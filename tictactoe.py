import os
import random

# ─── Constants ────────────────────────────────────────────────────────────────

WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
    [0, 4, 8], [2, 4, 6],             # diagonals
]

# ─── Display ──────────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def cell_str(board, idx, win_line=None, hint=None):
    val = board[idx]
    if val == "X":
        return "\033[91mX\033[0m"   # red
    if val == "O":
        return "\033[94mO\033[0m"   # blue
    if hint == idx:
        return "\033[93m·\033[0m"   # yellow dot for hint
    return "\033[90m·\033[0m"       # dark dot for empty

def print_board(board, win_line=None, hint=None, scores=None):
    clear()
    print("\n  ╔═══════════════╗")
    print("  ║  TIC  TAC  TOE ║")
    print("  ╚═══════════════╝\n")

    if scores:
        x, o, d = scores["X"], scores["O"], scores["D"]
        print(f"  \033[91mX:{x}\033[0m  Draw:{d}  \033[94mO:{o}\033[0m\n")

    def row(a, b, c):
        return f"  {cell_str(board,a,win_line,hint)}  │  {cell_str(board,b,win_line,hint)}  │  {cell_str(board,c,win_line,hint)}"

    print("     1     2     3")
    print("  ┌─────┬─────┬─────┐")
    print(f"1 │  {cell_str(board,0,win_line,hint)}  │  {cell_str(board,1,win_line,hint)}  │  {cell_str(board,2,win_line,hint)}  │")
    print("  ├─────┼─────┼─────┤")
    print(f"2 │  {cell_str(board,3,win_line,hint)}  │  {cell_str(board,4,win_line,hint)}  │  {cell_str(board,5,win_line,hint)}  │")
    print("  ├─────┼─────┼─────┤")
    print(f"3 │  {cell_str(board,6,win_line,hint)}  │  {cell_str(board,7,win_line,hint)}  │  {cell_str(board,8,win_line,hint)}  │")
    print("  └─────┴─────┴─────┘")
    print("  Enter row,col (e.g. 1,2) │ h=hint │ q=quit\n")

# ─── Game Logic ───────────────────────────────────────────────────────────────

def check_winner(board):
    """Returns (winner, winning_line) or (None, None)."""
    for line in WIN_LINES:
        a, b, c = line
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], line
    if all(cell != " " for cell in board):
        return "D", []
    return None, None

def empty_cells(board):
    return [i for i, v in enumerate(board) if v == " "]

# ─── Minimax with Alpha-Beta Pruning ──────────────────────────────────────────

def minimax(board, depth, is_max, ai_side, human_side, alpha=-float("inf"), beta=float("inf")):
    winner, _ = check_winner(board)
    if winner == ai_side:
        return 10 - depth
    if winner == human_side:
        return depth - 10
    if winner == "D":
        return 0

    moves = empty_cells(board)
    if is_max:
        best = -float("inf")
        for m in moves:
            board[m] = ai_side
            score = minimax(board, depth + 1, False, ai_side, human_side, alpha, beta)
            board[m] = " "
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = float("inf")
        for m in moves:
            board[m] = human_side
            score = minimax(board, depth + 1, True, ai_side, human_side, alpha, beta)
            board[m] = " "
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

def get_best_move(board, ai_side, human_side, difficulty):
    moves = empty_cells(board)
    if difficulty == "easy" and random.random() < 0.6:
        return random.choice(moves)
    if difficulty == "medium" and random.random() < 0.25:
        return random.choice(moves)

    best_score = -float("inf")
    best_move = moves[0]
    for m in moves:
        board[m] = ai_side
        score = minimax(board, 0, False, ai_side, human_side, -float("inf"), float("inf"))
        board[m] = " "
        if score > best_score:
            best_score = score
            best_move = m
    return best_move

# ─── Input Helpers ────────────────────────────────────────────────────────────

def get_move(board):
    """Prompt human for a move. Returns cell index, 'h' for hint, or 'q' to quit."""
    while True:
        raw = input("  Your move: ").strip().lower()
        if raw == "q":
            return "q"
        if raw == "h":
            return "h"
        try:
            parts = raw.replace(" ", "").split(",")
            row, col = int(parts[0]) - 1, int(parts[1]) - 1
            idx = row * 3 + col
            if 0 <= idx <= 8 and board[idx] == " ":
                return idx
            print("  \033[91mCell taken or out of range. Try again.\033[0m")
        except (ValueError, IndexError):
            print("  \033[91mInvalid input. Use row,col like 2,3\033[0m")

def choose_option(prompt, options):
    """Simple menu picker."""
    while True:
        print(f"\n  {prompt}")
        for key, label in options:
            print(f"    [{key}] {label}")
        choice = input("  → ").strip().lower()
        for key, label in options:
            if choice == key:
                return key
        print("  \033[91mInvalid choice.\033[0m")

# ─── Main Game Loop ───────────────────────────────────────────────────────────

def play_round(mode, difficulty, human_side, scores):
    board = [" "] * 9
    ai_side = "O" if human_side == "X" else "X"
    current = "X"  # X always goes first
    hint = None

    # AI opens if human plays O
    if mode == "ai" and human_side == "O":
        move = get_best_move(board, ai_side, human_side, difficulty)
        board[move] = ai_side
        current = "O"

    while True:
        print_board(board, hint=hint, scores=scores)
        hint = None

        winner, win_line = check_winner(board)
        if winner:
            print_board(board, win_line=win_line, scores=scores)
            if winner == "D":
                print("  ══ It's a draw! ══\n")
                scores["D"] += 1
            elif mode == "ai":
                if winner == human_side:
                    print(f"  🎉 You win as {human_side}!\n")
                else:
                    print(f"  🤖 AI wins!\n")
                scores[winner] += 1
            else:
                print(f"  🏆 Player {winner} wins!\n")
                scores[winner] += 1
            return

        if mode == "ai" and current == ai_side:
            print(f"  \033[94mAI ({ai_side}) is thinking...\033[0m")
            move = get_best_move(board, ai_side, human_side, difficulty)
            board[move] = ai_side
            current = human_side
        else:
            label = f"Your move ({human_side})" if mode == "ai" else f"Player {current}'s move"
            print(f"  {label}")
            action = get_move(board)
            if action == "q":
                print("\n  Thanks for playing!\n")
                raise SystemExit
            if action == "h":
                if mode == "ai":
                    hint = get_best_move(board, human_side, ai_side, "hard")
                    print(f"  \033[93mHint: best move is row {hint//3+1}, col {hint%3+1}\033[0m")
                else:
                    print("  Hints only available in AI mode.")
                continue
            board[action] = current
            current = ai_side if mode == "ai" else ("O" if current == "X" else "X")


def main():
    scores = {"X": 0, "O": 0, "D": 0}

    clear()
    print("\n  ╔═══════════════╗")
    print("  ║  TIC  TAC  TOE ║")
    print("  ╚═══════════════╝")

    mode = choose_option("Game mode:", [("1", "vs AI"), ("2", "2 Players")])
    mode = "ai" if mode == "1" else "2p"

    difficulty = "hard"
    human_side = "X"

    if mode == "ai":
        diff_choice = choose_option("Difficulty:", [("1", "Easy"), ("2", "Medium"), ("3", "Hard")])
        difficulty = {"1": "easy", "2": "medium", "3": "hard"}[diff_choice]

        side_choice = choose_option("Play as:", [("x", "X — goes first"), ("o", "O — goes second")])
        human_side = side_choice.upper()

    while True:
        play_round(mode, difficulty, human_side, scores)
        again = input("  Play again? [y/n]: ").strip().lower()
        if again != "y":
            print("\n  Final scores:")
            print(f"    X: {scores['X']}  |  Draw: {scores['D']}  |  O: {scores['O']}\n")
            print("  Thanks for playing!\n")
            break

if __name__ == "__main__":
    main()
