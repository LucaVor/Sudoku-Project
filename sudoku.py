import sys
import pygame

from sudoku_generator import SudokuGenerator

# some basic constants for rendering purposes
WIDTH, HEIGHT = 600, 720
BOARD_SIZE = 540
GRID_SIZE = 9
CELL_SIZE = BOARD_SIZE // GRID_SIZE
BOARD_LEFT = (WIDTH - BOARD_SIZE) // 2
BOARD_TOP = 100

BG_COLOR = (20, 20, 20)
BOARD_COLOR = (35, 35, 35)
GRID_COLOR = (90, 90, 90)
BOLD_GRID_COLOR = (200, 200, 200)
GIVEN_COLOR = (160, 200, 255)
USER_COLOR = (245, 245, 245)
SKETCH_COLOR = (120, 120, 120)
SELECTED_COLOR = (200, 80, 80)
BUTTON_COLOR = (55, 55, 55)
BUTTON_BORDER = (200, 200, 200)
SUCCESS_COLOR = (80, 180, 120)
FAIL_COLOR = (200, 80, 80)

NUMBER_FONT = None
SKETCH_FONT = None
TITLE_FONT = None
BUTTON_FONT = None


class Cell:
	"""represents a single square on the board."""

	def __init__(self, value, row, col, screen, fixed):
		self.value = value
		self.row = row
		self.col = col
		self.screen = screen
		self.fixed = fixed
		self.sketched_value = 0
		self.selected = False

	def set_cell_value(self, value):
		self.value = value

	def set_sketched_value(self, value):
		self.sketched_value = value

	def draw(self):
		x = BOARD_LEFT + self.col * CELL_SIZE
		y = BOARD_TOP + self.row * CELL_SIZE
		
		rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
		pygame.draw.rect(self.screen, BOARD_COLOR, rect)
		
		if self.value:
			if self.fixed:
				value_color = GIVEN_COLOR
			else:
				value_color = USER_COLOR
			text = NUMBER_FONT.render(str(self.value), True, value_color)
			
			self.screen.blit(text, text.get_rect(center=rect.center))
			
		elif self.sketched_value:
			text = SKETCH_FONT.render(str(self.sketched_value), True, SKETCH_COLOR)
			self.screen.blit(text, (x + 5, y + 5))
			
		if self.selected:
			border_color = SELECTED_COLOR
			border_width = 2
		else:
			border_color = GRID_COLOR
			border_width = 1
		pygame.draw.rect(self.screen, border_color, rect, border_width)


class Board:
	"""manages the nine by nine grid."""

	def __init__(self, width, height, screen, difficulty):
		self.width = width
		self.height = height
		self.screen = screen
		self.difficulty = difficulty
		self.cells = []
		self.matrix = []
		self.original = []
		self.solution = []
		self.fixed_map = []
		self.selected = None
		self.build_board()

	def build_board(self):
		removed = {"easy": 30, "medium": 40, "hard": 50}[self.difficulty]
		generator = SudokuGenerator(GRID_SIZE, removed)
		generator.fill_values()
		generator.remove_cells()
		
		self.solution = []
		for solution_row in generator.solution:
			self.solution.append(solution_row[:])
			
		self.matrix = generator.get_board()
		self.original = []
		
		for original_row in self.matrix:
			self.original.append(original_row[:])
			
		self.fixed_map = []
		
		for matrix_row in self.matrix:
			fixed_row = []
			
			for value in matrix_row:
				fixed_row.append(value != 0)
				
			self.fixed_map.append(fixed_row)
			
		self.cells = []
		
		for row_idx in range(GRID_SIZE):
			row_cells = []
			
			for col_idx in range(GRID_SIZE):
				cell_value = self.matrix[row_idx][col_idx]
				cell_fixed = self.fixed_map[row_idx][col_idx]
				row_cells.append(Cell(cell_value, row_idx, col_idx, self.screen, cell_fixed))
				
			self.cells.append(row_cells)

	def draw(self):
		pygame.draw.rect(self.screen, BOARD_COLOR, pygame.Rect(BOARD_LEFT, BOARD_TOP, BOARD_SIZE, BOARD_SIZE))
		
		for row in self.cells:
			for cell in row:
				cell.draw()
				
		for line_index in range(GRID_SIZE + 1):
			if line_index % 3 == 0:
				line_width = 4
				line_color = BOLD_GRID_COLOR
			else:
				line_width = 1
				line_color = GRID_COLOR
				
			horizontal_start = (BOARD_LEFT, BOARD_TOP + line_index * CELL_SIZE)
			horizontal_end = (BOARD_LEFT + BOARD_SIZE, BOARD_TOP + line_index * CELL_SIZE)
			pygame.draw.line(self.screen, line_color, horizontal_start, horizontal_end, line_width)
			vertical_start = (BOARD_LEFT + line_index * CELL_SIZE, BOARD_TOP)
			vertical_end = (BOARD_LEFT + line_index * CELL_SIZE, BOARD_TOP + BOARD_SIZE)
			pygame.draw.line(self.screen, line_color, vertical_start, vertical_end, line_width)

	def select(self, row, col):
		if self.selected:
			self.cells[self.selected[0]][self.selected[1]].selected = False
			
		self.selected = (row, col)
		self.cells[row][col].selected = True

	def click(self, x, y):
		if not (BOARD_LEFT <= x < BOARD_LEFT + BOARD_SIZE and BOARD_TOP <= y < BOARD_TOP + BOARD_SIZE):
			return None
		
		row = (y - BOARD_TOP) // CELL_SIZE
		col = (x - BOARD_LEFT) // CELL_SIZE
		
		self.select(row, col)
		
		return row, col

	def clear(self):
		if not self.selected:
			return
		
		row, col = self.selected
		cell = self.cells[row][col]
		
		if not self.fixed_map[row][col]:
			cell.set_cell_value(0)
			cell.set_sketched_value(0)
			
			self.matrix[row][col] = 0

	def sketch(self, value):
		if not self.selected:
			return
		
		row, col = self.selected
		
		if not self.fixed_map[row][col]:
			self.cells[row][col].set_sketched_value(value)

	def place_number(self, value=None):
		if not self.selected:
			return False
		
		row, col = self.selected
		cell = self.cells[row][col]
		
		if self.fixed_map[row][col]:
			return False
		
		if value is not None:
			final_value = value
		else:
			final_value = cell.sketched_value
		
		if not final_value:
			return False
		
		cell.set_cell_value(final_value)
		cell.set_sketched_value(0)
		self.matrix[row][col] = final_value
		
		return True

	def reset_to_original(self):
		for row_idx in range(GRID_SIZE):
			for col_idx in range(GRID_SIZE):
				self.cells[row_idx][col_idx].set_cell_value(self.original[row_idx][col_idx])
				self.cells[row_idx][col_idx].set_sketched_value(0)

		self.matrix = []
		for original_row in self.original:
			self.matrix.append(original_row[:])

	def is_full(self):
		for cell_row in self.cells:
			for cell in cell_row:
				if cell.value == 0:
					return False
		return True

	def update_board(self):
		for row_idx in range(GRID_SIZE):
			for col_idx in range(GRID_SIZE):
				self.matrix[row_idx][col_idx] = self.cells[row_idx][col_idx].value

	def find_empty(self):
		for row_idx in range(GRID_SIZE):
			for col_idx in range(GRID_SIZE):
				if self.cells[row_idx][col_idx].value == 0:
					return row_idx, col_idx

		return None

	def check_board(self):
		self.update_board()
		
		return self.matrix == self.solution

	def move_selection(self, dr, dc):
		if not self.selected:
			row, col = 0, 0
		else:
			row, col = self.selected
			
		row = max(0, min(GRID_SIZE - 1, row + dr))
		col = max(0, min(GRID_SIZE - 1, col + dc))
		
		self.select(row, col)


class Button:
	"""simple clickable rectangle."""

	def __init__(self, rect, text, value):
		self.rect = pygame.Rect(rect)
		self.text = text
		self.value = value

	def draw(self, screen):
		hovered = self.rect.collidepoint(pygame.mouse.get_pos())
		
		if hovered:
			lighter_components = []
			for base_component in BUTTON_COLOR:
				lighter_components.append(min(255, base_component + 30))
				
			color = tuple(lighter_components)
		else:
			color = BUTTON_COLOR
		
		pygame.draw.rect(screen, color, self.rect)
		pygame.draw.rect(screen, BUTTON_BORDER, self.rect, 2)
		
		label = BUTTON_FONT.render(self.text, True, USER_COLOR)
		screen.blit(label, label.get_rect(center=self.rect.center))

	def contains(self, pos):
		return self.rect.collidepoint(pos)


def init_fonts():
	pygame.font.init()
	global NUMBER_FONT, SKETCH_FONT, TITLE_FONT, BUTTON_FONT
	
	NUMBER_FONT = pygame.font.SysFont(None, 48)
	SKETCH_FONT = pygame.font.SysFont(None, 24)
	TITLE_FONT = pygame.font.SysFont(None, 64)
	BUTTON_FONT = pygame.font.SysFont(None, 32)


def draw_start(screen, buttons):
	screen.fill(BG_COLOR)
	title = TITLE_FONT.render("Sudoku", True, USER_COLOR)
	
	screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))
	
	prompt = BUTTON_FONT.render("choose a difficulty", True, USER_COLOR)
	
	screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, 150)))
	
	for btn in buttons:
		btn.draw(screen)


def draw_game(screen, board, buttons):
	screen.fill(BG_COLOR)
	board.draw()
	
	for btn in buttons:
		btn.draw(screen)


def draw_end(screen, text, color, buttons):
	screen.fill(BG_COLOR)
	label = TITLE_FONT.render(text, True, color)
	screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
	
	for btn in buttons:
		btn.draw(screen)


def main():
	pygame.init()
	init_fonts()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Sudoku")
	clock = pygame.time.Clock()
	
	start_buttons = [
		Button((WIDTH // 2 - 100, 200, 200, 60), "easy", "easy"),
		Button((WIDTH // 2 - 100, 280, 200, 60), "medium", "medium"),
		Button((WIDTH // 2 - 100, 360, 200, 60), "hard", "hard"),
	]
	
	control_buttons = [
		Button((60, 660, 120, 40), "reset", "reset"),
		Button((240, 660, 120, 40), "restart", "restart"),
		Button((420, 660, 120, 40), "exit", "exit"),
	]
	
	end_buttons = [
		Button((WIDTH // 2 - 140, HEIGHT // 2, 120, 50), "restart", "restart"),
		Button((WIDTH // 2 + 20, HEIGHT // 2, 120, 50), "exit", "exit"),
	]
	
	state = "start"
	board = None
	running = True
	
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				
			elif state == "start" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				for btn in start_buttons:
					if btn.contains(event.pos):
						board = Board(BOARD_SIZE, BOARD_SIZE, screen, btn.value)
						state = "game"
						break
					
			elif state == "game":
				if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					if not board.click(*event.pos):
						for btn in control_buttons:
							if btn.contains(event.pos):
								if btn.value == "reset":
									board.reset_to_original()
									
								elif btn.value == "restart":
									state = "start"
									board = None
									
								elif btn.value == "exit":
									running = False
									
								break
							
				elif event.type == pygame.KEYDOWN:
					if pygame.K_1 <= event.key <= pygame.K_9:
						board.sketch(event.key - pygame.K_0)
						
					elif event.key == pygame.K_RETURN:
						if board.place_number() and board.is_full():
							if board.check_board():
								state = "win"
							else:
								state = "lose"
							
					elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
						board.clear()
						
					elif event.key == pygame.K_LEFT:
						board.move_selection(0, -1)
						
					elif event.key == pygame.K_RIGHT:
						board.move_selection(0, 1)
						
					elif event.key == pygame.K_UP:
						board.move_selection(-1, 0)
						
					elif event.key == pygame.K_DOWN:
						board.move_selection(1, 0)
						
			elif state in ("win", "lose") and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				for btn in end_buttons:
					if btn.contains(event.pos):
						if btn.value == "restart":
							state = "start"
							board = None
							
						else:
							running = False
							
						break
					
		if state == "start":
			draw_start(screen, start_buttons)
			
		elif state == "game":
			draw_game(screen, board, control_buttons)
			
		elif state == "win":
			draw_end(screen, "you solved it", SUCCESS_COLOR, end_buttons)
			
		else:
			draw_end(screen, "incorrect board", FAIL_COLOR, end_buttons)
			
		pygame.display.flip()
		clock.tick(60)
		
	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
