import random

import pygame

CELL_SIZE = 30
BOARD_COLUMNS = 10
BOARD_ROWS = 20
PLAY_WIDTH = BOARD_COLUMNS * CELL_SIZE
PLAY_HEIGHT = BOARD_ROWS * CELL_SIZE
SIDE_PANEL_WIDTH = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT
BACKGROUND_COLOR = (10, 10, 30)
GRID_COLOR = (40, 40, 70)
TEXT_COLOR = (230, 230, 230)

FALL_SPEED_START_MS = 500
FALL_SPEED_MIN_MS = 80
LEVEL_LINES_STEP = 10

MOVE_DOWN_EVENT = pygame.USEREVENT + 1


class Tetromino:
    def __init__(self, shape_rotations, color_rgb):
        self.shape_rotations = shape_rotations
        self.color_rgb = color_rgb
        self.rotation_index = 0
        self.position_column = BOARD_COLUMNS // 2 - 2
        self.position_row = -2

    def current_cells(self):
        return self.cells_for_rotation(self.rotation_index)

    def cells_for_rotation(self, rotation_index, offset_column=0, offset_row=0):
        cells = []
        for local_col, local_row in self.shape_rotations[rotation_index]:
            board_column = self.position_column + local_col + offset_column
            board_row = self.position_row + local_row + offset_row
            cells.append((board_column, board_row))
        return cells

    def rotated_index(self):
        return (self.rotation_index + 1) % len(self.shape_rotations)


class TetrisGame:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_COLUMNS)] for _ in range(BOARD_ROWS)]
        self.score = 0
        self.lines_cleared_total = 0
        self.level = 1
        self.fall_speed_ms = FALL_SPEED_START_MS
        self.current_piece = self.random_piece()
        self.next_piece = self.random_piece()
        self.game_over = False

    @staticmethod
    def random_piece():
        shape_definitions = get_tetromino_definitions()
        shape_rotations, color_rgb = random.choice(shape_definitions)
        return Tetromino(shape_rotations, color_rgb)

    def reset_timer_speed(self):
        level_from_lines = self.lines_cleared_total // LEVEL_LINES_STEP + 1
        self.level = level_from_lines
        speed = FALL_SPEED_START_MS * (0.85 ** (self.level - 1))
        self.fall_speed_ms = max(FALL_SPEED_MIN_MS, int(speed))
        pygame.time.set_timer(MOVE_DOWN_EVENT, self.fall_speed_ms)

    def is_valid_position(self, piece, offset_column=0, offset_row=0, rotation_index=None):
        if rotation_index is None:
            rotation_index = piece.rotation_index
        candidate_cells = piece.cells_for_rotation(
            rotation_index,
            offset_column=offset_column,
            offset_row=offset_row,
        )
        for board_column, board_row in candidate_cells:
            if board_column < 0 or board_column >= BOARD_COLUMNS:
                return False
            if board_row >= BOARD_ROWS:
                return False
            if board_row >= 0 and self.board[board_row][board_column] is not None:
                return False
        return True

    def lock_current_piece(self):
        for board_column, board_row in self.current_piece.current_cells():
            if 0 <= board_row < BOARD_ROWS:
                self.board[board_row][board_column] = self.current_piece.color_rgb
            else:
                self.game_over = True
        if not self.game_over:
            lines_cleared = self.clear_full_lines()
            if lines_cleared:
                self.lines_cleared_total += lines_cleared
                self.score += self.score_for_lines(lines_cleared)
                self.reset_timer_speed()
            self.current_piece = self.next_piece
            self.next_piece = self.random_piece()
            if not self.is_valid_position(self.current_piece):
                self.game_over = True

    def clear_full_lines(self):
        new_board = []
        cleared_count = 0
        for row_index in range(BOARD_ROWS - 1, -1, -1):
            row = self.board[row_index]
            if all(cell is not None for cell in row):
                cleared_count += 1
            else:
                new_board.insert(0, row)
        while len(new_board) < BOARD_ROWS:
            new_board.insert(0, [None for _ in range(BOARD_COLUMNS)])
        self.board = new_board
        return cleared_count

    @staticmethod
    def score_for_lines(lines_cleared):
        if lines_cleared == 1:
            return 100
        if lines_cleared == 2:
            return 300
        if lines_cleared == 3:
            return 500
        if lines_cleared >= 4:
            return 800
        return 0

    def move_current(self, delta_column, delta_row):
        if self.game_over:
            return
        if self.is_valid_position(self.current_piece, offset_column=delta_column, offset_row=delta_row):
            self.current_piece.position_column += delta_column
            self.current_piece.position_row += delta_row
        elif delta_row > 0:
            self.lock_current_piece()

    def hard_drop(self):
        if self.game_over:
            return
        while self.is_valid_position(self.current_piece, offset_row=1):
            self.current_piece.position_row += 1
        self.lock_current_piece()

    def rotate_current(self):
        if self.game_over:
            return
        new_rotation = self.current_piece.rotated_index()
        if self.is_valid_position(self.current_piece, rotation_index=new_rotation):
            self.current_piece.rotation_index = new_rotation
            return
        for offset in (-1, 1, -2, 2):
            if self.is_valid_position(self.current_piece, offset_column=offset, rotation_index=new_rotation):
                self.current_piece.position_column += offset
                self.current_piece.rotation_index = new_rotation
                return


def get_tetromino_definitions():
    cyan = (0, 240, 240)
    yellow = (240, 240, 0)
    purple = (160, 0, 240)
    green = (0, 240, 0)
    red = (240, 0, 0)
    blue = (0, 0, 240)
    orange = (240, 160, 0)

    i_shape = [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ]
    o_shape = [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ]
    t_shape = [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ]
    s_shape = [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ]
    z_shape = [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ]
    j_shape = [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ]
    l_shape = [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ]

    return [
        (i_shape, cyan),
        (o_shape, yellow),
        (t_shape, purple),
        (s_shape, green),
        (z_shape, red),
        (j_shape, blue),
        (l_shape, orange),
    ]


def draw_board(surface, game):
    surface.fill(BACKGROUND_COLOR)
    for row_index in range(BOARD_ROWS):
        for column_index in range(BOARD_COLUMNS):
            cell_color = game.board[row_index][column_index]
            if cell_color is not None:
                draw_cell(surface, column_index, row_index, cell_color)
    if not game.game_over:
        for board_column, board_row in game.current_piece.current_cells():
            if board_row >= 0:
                draw_cell(surface, board_column, board_row, game.current_piece.color_rgb)
    for row_index in range(BOARD_ROWS):
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (0, row_index * CELL_SIZE),
            (PLAY_WIDTH, row_index * CELL_SIZE),
            1,
        )
    for column_index in range(BOARD_COLUMNS + 1):
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (column_index * CELL_SIZE, 0),
            (column_index * CELL_SIZE, PLAY_HEIGHT),
            1,
        )


def draw_cell(surface, board_column, board_row, color_rgb):
    rect = pygame.Rect(
        board_column * CELL_SIZE + 1,
        board_row * CELL_SIZE + 1,
        CELL_SIZE - 2,
        CELL_SIZE - 2,
    )
    pygame.draw.rect(surface, color_rgb, rect)


def draw_side_panel(surface, game, font_main, font_small):
    panel_rect = pygame.Rect(PLAY_WIDTH, 0, SIDE_PANEL_WIDTH, PLAY_HEIGHT)
    pygame.draw.rect(surface, (20, 20, 50), panel_rect)

    score_text = font_main.render(f"Score: {game.score}", True, TEXT_COLOR)
    level_text = font_main.render(f"Level: {game.level}", True, TEXT_COLOR)
    lines_text = font_main.render(f"Lines: {game.lines_cleared_total}", True, TEXT_COLOR)
    surface.blit(score_text, (PLAY_WIDTH + 20, 30))
    surface.blit(level_text, (PLAY_WIDTH + 20, 70))
    surface.blit(lines_text, (PLAY_WIDTH + 20, 110))

    next_label = font_main.render("Next:", True, TEXT_COLOR)
    surface.blit(next_label, (PLAY_WIDTH + 20, 160))
    for board_column, board_row in game.next_piece.cells_for_rotation(0):
        preview_column = board_column - 3
        preview_row = board_row + 4
        rect = pygame.Rect(
            PLAY_WIDTH + 20 + preview_column * CELL_SIZE,
            200 + preview_row * CELL_SIZE,
            CELL_SIZE - 2,
            CELL_SIZE - 2,
        )
        pygame.draw.rect(surface, game.next_piece.color_rgb, rect)

    instructions = [
        "Setas: mover",
        "Seta cima: girar",
        "Espaço: queda",
        "Esc: sair",
    ]
    vertical_offset = 360
    for line in instructions:
        text_surface = font_small.render(line, True, TEXT_COLOR)
        surface.blit(text_surface, (PLAY_WIDTH + 20, vertical_offset))
        vertical_offset += 26

    if game.game_over:
        overlay = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        game_over_text = font_main.render("GAME OVER", True, (255, 80, 80))
        restart_text = font_small.render("Pressione R para reiniciar", True, TEXT_COLOR)
        surface.blit(
            game_over_text,
            game_over_text.get_rect(center=(PLAY_WIDTH // 2, PLAY_HEIGHT // 2 - 20)),
        )
        surface.blit(
            restart_text,
            restart_text.get_rect(center=(PLAY_WIDTH // 2, PLAY_HEIGHT // 2 + 20)),
        )


def main():
    pygame.init()
    pygame.display.set_caption("Tetris em Python - forgeCodeAgent")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font_main = pygame.font.SysFont("consolas", 24)
    font_small = pygame.font.SysFont("consolas", 18)

    game = TetrisGame()
    game.reset_timer_speed()

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == MOVE_DOWN_EVENT:
                if not game.game_over:
                    game.move_current(0, 1)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.game_over:
                    game = TetrisGame()
                    game.reset_timer_speed()
                elif not game.game_over:
                    if event.key == pygame.K_LEFT:
                        game.move_current(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move_current(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move_current(0, 1)
                    elif event.key == pygame.K_UP:
                        game.rotate_current()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()

        draw_board(screen, game)
        draw_side_panel(screen, game, font_main, font_small)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
