import pygame
import random
import sys

pygame.init()

CELL = 30
COLS = 10
ROWS = 20
PANEL_W = 200
WIDTH = COLS * CELL + PANEL_W
HEIGHT = ROWS * CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Tetris")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 20)
BIG_FONT = pygame.font.SysFont("consolas", 40, bold=True)

BLACK = (0, 0, 0)
GRAY = (30, 30, 30)
WHITE = (240, 240, 240)
GRID = (50, 50, 50)

COLORS = {
    "I": (0, 255, 255),
    "O": (255, 255, 0),
    "T": (200, 0, 255),
    "S": (0, 255, 100),
    "Z": (255, 50, 100),
    "J": (80, 120, 255),
    "L": (255, 150, 0),
}

SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

STATE_MENU = "menu"
STATE_CONTROLS = "controls"
STATE_PLAYING = "playing"

def empty_board():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

def valid(cells, board):
    for x, y in cells:
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and board[y][x] is not None:
            return False
    return True

def place_piece(cells, kind, board):
    for x, y in cells:
        if y >= 0:
            board[y][x] = kind

def clear_lines(board):
    new_board = [row for row in board if any(cell is None for cell in row)]
    cleared = ROWS - len(new_board)
    while len(new_board) < ROWS:
        new_board.insert(0, [None for _ in range(COLS)])
    return new_board, cleared

def draw_grid():
    for x in range(COLS + 1):
        pygame.draw.line(screen, GRID, (x * CELL, 0), (x * CELL, HEIGHT), 1)
    for y in range(ROWS + 1):
        pygame.draw.line(screen, GRID, (0, y * CELL), (COLS * CELL, y * CELL), 1)

def draw_block(x, y, color):
    rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

def draw_board(board):
    for y in range(ROWS):
        for x in range(COLS):
            kind = board[y][x]
            if kind:
                draw_block(x, y, COLORS[kind])

def draw_piece(cells, kind):
    for x, y in cells:
        if y >= 0:
            draw_block(x, y, COLORS[kind])

def draw_next_piece(next_kind):
    screen.blit(FONT.render("Next:", True, WHITE), (COLS * CELL + 20, 240))
    cells = SHAPES[next_kind][0]
    for cx, cy in cells:
        x = COLS * CELL + 60 + cx
        y = 280 + cy
        rect = pygame.Rect(x * (CELL // 2), y * (CELL // 2), CELL // 2, CELL // 2)
        pygame.draw.rect(screen, COLORS[next_kind], rect)

def run_game():
    board = empty_board()
    kinds = list(SHAPES.keys())
    current_kind = random.choice(kinds)
    next_kind = random.choice(kinds)

    x, y = 3, -2
    rot = 0
    score = 0

    fall_timer = 0
    fall_speed = 500
    game_over = False

    def get_cells(px, py, r):
        shape = SHAPES[current_kind][r % len(SHAPES[current_kind])]
        return [(px + cx, py + cy) for cx, cy in shape]

    while True:
        dt = clock.tick(60)
        fall_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

                if game_over:
                    if event.key == pygame.K_r:
                        return "restart"
                    continue

                if event.key == pygame.K_LEFT:
                    if valid(get_cells(x - 1, y, rot), board):
                        x -= 1
                if event.key == pygame.K_RIGHT:
                    if valid(get_cells(x + 1, y, rot), board):
                        x += 1
                if event.key == pygame.K_DOWN:
                    if valid(get_cells(x, y + 1, rot), board):
                        y += 1
                if event.key == pygame.K_UP:
                    new_rot = rot + 1
                    if valid(get_cells(x, y, new_rot), board):
                        rot = new_rot
                if event.key == pygame.K_SPACE:
                    while valid(get_cells(x, y + 1, rot), board):
                        y += 1

        if not game_over and fall_timer >= fall_speed:
            fall_timer = 0
            if valid(get_cells(x, y + 1, rot), board):
                y += 1
            else:
                place_piece(get_cells(x, y, rot), current_kind, board)
                board, cleared = clear_lines(board)
                score += cleared * 100

                current_kind = next_kind
                next_kind = random.choice(kinds)
                x, y, rot = 3, -2, 0

                if not valid(get_cells(x, y, rot), board):
                    game_over = True

        screen.fill(BLACK)

        pygame.draw.rect(screen, GRAY, (0, 0, COLS * CELL, HEIGHT))
        draw_grid()
        draw_board(board)

        if not game_over:
            draw_piece(get_cells(x, y, rot), current_kind)

        pygame.draw.rect(screen, (20, 20, 40), (COLS * CELL, 0, PANEL_W, HEIGHT))
        screen.blit(FONT.render(f"Score: {score}", True, WHITE), (COLS * CELL + 20, 60))
        draw_next_piece(next_kind)

        if game_over:
            text1 = BIG_FONT.render("GAME OVER", True, WHITE)
            text2 = FONT.render("Press R to restart", True, WHITE)
            screen.blit(text1, (40, HEIGHT // 2 - 60))
            screen.blit(text2, (60, HEIGHT // 2))

        pygame.display.flip()

def draw_menu(selected):
    screen.fill(BLACK)
    title = BIG_FONT.render("TETRIS", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

    options = ["PLAY", "CONTROLS", "QUIT"]
    y = 250
    for i, opt in enumerate(options):
        col = (0, 255, 255) if i == selected else WHITE
        txt = FONT.render(opt, True, col)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))
        y += 50

    hint = FONT.render("Use ↑/↓ and ENTER", True, WHITE)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 450))
    pygame.display.flip()

def draw_controls():
    screen.fill(BLACK)
    title = BIG_FONT.render("CONTROLS", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    lines = [
        "← / →  Move",
        "↓      Soft Drop",
        "↑      Rotate",
        "SPACE  Hard Drop",
        "",
        "ESC    Back to Menu",
        "",
        "Press BACKSPACE to return"
    ]

    y = 180
    for line in lines:
        txt = FONT.render(line, True, WHITE)
        screen.blit(txt, (120, y))
        y += 35

    pygame.display.flip()

def main():
    state = STATE_MENU
    selected = 0

    while True:
        if state == STATE_MENU:
            draw_menu(selected)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % 3
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % 3
                    if event.key == pygame.K_RETURN:
                        if selected == 0:
                            state = STATE_PLAYING
                        elif selected == 1:
                            state = STATE_CONTROLS
                        elif selected == 2:
                            pygame.quit()
                            sys.exit()

        elif state == STATE_CONTROLS:
            draw_controls()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_BACKSPACE, pygame.K_ESCAPE):
                        state = STATE_MENU

        elif state == STATE_PLAYING:
            result = run_game()
            if result == "quit":
                pygame.quit()
                sys.exit()
            if result == "restart":
                state = STATE_PLAYING
            else:
                state = STATE_MENU

if __name__ == "__main__":
    main()
