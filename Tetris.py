# Author:   Thai Duc Thien
# Date:     25.10.2025
# Purpose:  Lam cho vui ^^


import pygame
import random
import sys

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
BG_COLOR = (245, 245, 250)
GRID_BG = (220, 230, 240)
HIGHLIGHT_COLOR = (100, 255, 150)
COLORS = [
    (255, 107, 107),  # Đỏ
    (255, 195, 113),  # Cam
    (255, 234, 167),  # Vàng
    (134, 229, 134),  # Xanh lá
    (119, 221, 231),  # Xanh dương
    (162, 155, 254),  # Tím
    (255, 159, 243),  # Hồng
]

# Màu nền đặc biệt khi clear toàn bộ grid (màu sáng, không u ám)
SPECIAL_BG_COLORS = [
    (255, 240, 245),  # Hồng pastel
    (240, 255, 240),  # Xanh lá pastel
    (240, 248, 255),  # Xanh dương pastel
    (255, 250, 240),  # Cam pastel
    (248, 240, 255),  # Tím pastel
    (255, 255, 240),  # Vàng pastel
    (240, 255, 255),  # Cyan pastel
    (255, 245, 238),  # Đào pastel
]

# Cài đặt màn hình - GIỮ NGUYÊN KÍCH THƯỚC CŨ
CELL_SIZE = 45
GRID_SIZE = 8
MARGIN = 4
SCREEN_WIDTH = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN + 40
SCREEN_HEIGHT = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN + 380
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Block Blast")

# Font
title_font = pygame.font.Font(None, 48)
font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 28)
combo_font = pygame.font.Font(None, 72)

# Các brick - Phân loại theo độ khó
SHAPES_EASY = [
    [[1]],              
    [[1, 1]],           
    [[1], [1]],         
]

SHAPES_MEDIUM = [
    [[1, 1, 1]],        
    [[1], [1], [1]],    
    [[1, 1], [1, 1]],   
    [[1, 0], [1, 1]], 
    [[1, 1], [1, 0]],
    [[1, 1], [0, 1]],
    [[1, 1, 1], [1, 0, 0]],  
    [[1, 1, 1], [0, 0, 1]],
]

SHAPES_HARD = [
    [[1, 1, 1, 1]],    
    [[1], [1], [1], [1]],  
    [[1, 1, 1], [0, 1, 0]],  
    [[0, 1, 0], [1, 1, 1]],  
    [[1, 1, 0], [0, 1, 1]],  
    [[1, 1, 1], [1, 1, 1]], 
    [[0, 1, 1], [1, 1, 0]],  
    [[1, 1, 1], [1, 0, 0], [1, 0, 0]],  
    [[1, 1, 1], [0, 0, 1], [0, 0, 1]],
]

SHAPES_VERY_HARD = [
    [[1, 1, 1, 1, 1]],        
    [[1], [1], [1], [1], [1]],    
    [[1, 0], [0, 1]],   
    [[0, 1], [1, 0]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1]],  
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    [[0, 0, 1], [0, 1, 0], [1, 0, 0]],
]

# Gộp tất cả shapes
ALL_SHAPES = {
    'easy': SHAPES_EASY,
    'medium': SHAPES_MEDIUM,
    'hard': SHAPES_HARD,
    'very_hard': SHAPES_VERY_HARD
}

# Hiệu ứng combo
COMBO_MESSAGES = {
    2: ("NICE!", (100, 200, 255)),
    3: ("GREAT!", (255, 200, 50)),
    4: ("EXCELLENT!", (255, 100, 255)),
    5: ("AMAZING!", (255, 50, 50)),
    6: ("INCREDIBLE!", (150, 50, 255)),
}

class ComboEffect:
    """Class để quản lý hiệu ứng combo"""
    def __init__(self, message, color, x, y):
        self.message = message
        self.color = color
        self.x = x
        self.y = y
        self.alpha = 255
        self.scale = 0.5
        self.lifetime = 90
        self.age = 0
    
    def update(self):
        self.age += 1
        if self.age < 15:
            self.scale = 0.5 + (self.age / 15) * 0.5
        elif self.age > 60:
            self.alpha = max(0, 255 - (self.age - 60) * 8.5)
        
        self.y -= 0.5
    
    def is_expired(self):
        return self.age >= self.lifetime
    
    def draw(self, screen):
        if self.alpha > 0:
            font_size = int(72 * self.scale)
            dynamic_font = pygame.font.Font(None, font_size)
            text = dynamic_font.render(self.message, True, self.color)
            
            text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            text_surface.fill((255, 255, 255, 0))
            text_surface.blit(text, (0, 0))
            text_surface.set_alpha(int(self.alpha))
            
            shadow_offset = 3
            shadow_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            shadow_text = dynamic_font.render(self.message, True, (0, 0, 0))
            shadow_surface.blit(shadow_text, (0, 0))
            shadow_surface.set_alpha(int(self.alpha * 0.5))
            
            text_rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
            shadow_rect = shadow_surface.get_rect(center=(int(self.x) + shadow_offset, 
                                                          int(self.y) + shadow_offset))
            
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)

class BlockBlastGame:
    def __init__(self, highest_score=0):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        # self.initialize_random_blocks()
        self.score = 0
        self.highest_score = highest_score
        self.available_pieces = []
        self.dragging_piece = None
        self.dragging_index = -1
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.preview_pos = None
        self.can_place_preview = False
        self.highlighted_lines = {'rows': [], 'cols': []}
        self.consecutive_hard_pieces = 0  
        self.grid_fullness = 0.0
        self.combo_effects = []
        self.current_bg_color = BG_COLOR  
        self.generate_new_pieces()
    
    def initialize_random_blocks(self):
        """Tạo các ô gạch ngẫu nhiên khi bắt đầu game"""
        num_blocks = random.randint(10, 15)
        all_positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        selected_positions = random.sample(all_positions, num_blocks)
        
        for row, col in selected_positions:
            self.grid[row][col] = random.choice(COLORS)
    
    def is_grid_empty(self):
        """Kiểm tra xem grid có hoàn toàn trống không"""
        for row in self.grid:
            for cell in row:
                if cell != 0:
                    return False
        return True
    
    def change_background_color(self):
        """Đổi màu nền thành màu ngẫu nhiên sáng"""
        self.current_bg_color = random.choice(SPECIAL_BG_COLORS)
        # Thêm hiệu ứng đặc biệt khi clear toàn bộ
        effect = ComboEffect("PERFECT CLEAR!", (255, 215, 0), 
                           SCREEN_WIDTH // 2, 250)
        self.combo_effects.append(effect)
        # Thưởng điểm bonus
        self.score += 100
    
    def add_combo_effect(self, lines_cleared):
        """Thêm hiệu ứng combo dựa trên số hàng/cột bị xóa"""
        if lines_cleared >= 2 and lines_cleared in COMBO_MESSAGES:
            message, color = COMBO_MESSAGES.get(lines_cleared, COMBO_MESSAGES[6])
            center_x = SCREEN_WIDTH // 2
            center_y = 250
            effect = ComboEffect(message, color, center_x, center_y)
            self.combo_effects.append(effect)
        elif lines_cleared > 6:
            effect = ComboEffect("LEGENDARY!", (255, 215, 0), 
                               SCREEN_WIDTH // 2, 250)
            self.combo_effects.append(effect)
    
    def update_combo_effects(self):
        """Cập nhật và loại bỏ hiệu ứng đã hết hạn"""
        for effect in self.combo_effects[:]:
            effect.update()
            if effect.is_expired():
                self.combo_effects.remove(effect)
    
    def draw_combo_effects(self):
        """Vẽ tất cả hiệu ứng combo"""
        for effect in self.combo_effects:
            effect.draw(screen)
        
    def calculate_grid_fullness(self):
        """Tính % ô đã bị lấp trên grid"""
        filled = sum(1 for row in self.grid for cell in row if cell != 0)
        total = GRID_SIZE * GRID_SIZE
        self.grid_fullness = filled / total
        
    def get_shape_size(self, shape):
        """Đếm số ô của một khối"""
        return sum(sum(row) for row in shape)   
    
    def generate_balanced_pieces(self):
        pieces = []
        self.calculate_grid_fullness()
        
        if self.grid_fullness < 0.7:
            difficulty_weights = {
                'easy': 5, 'medium': 20, 'hard': 40, 'very_hard': 35
            }
        elif self.grid_fullness < 0.9:
            difficulty_weights = {
                'easy': 7, 'medium': 25, 'hard': 38, 'very_hard': 30
            }
        else:
            difficulty_weights = {
                'easy': 13, 'medium': 35, 'hard': 35, 'very_hard': 17
            }
        
        if self.consecutive_hard_pieces >= 2:
            difficulty_weights['easy'] += 20
            difficulty_weights['medium'] += 10
            difficulty_weights['hard'] = max(10, difficulty_weights['hard'] - 15)
            difficulty_weights['very_hard'] = max(5, difficulty_weights['very_hard'] - 5)
        
        total_size = 0
        hard_count = 0
        
        for i in range(3):
            difficulties = list(difficulty_weights.keys())
            weights = list(difficulty_weights.values())
            difficulty = random.choices(difficulties, weights=weights, k=1)[0]
            
            if difficulty == 'very_hard' and hard_count >= 1:
                difficulty = random.choice(['medium', 'hard'])
            
            shape = random.choice(ALL_SHAPES[difficulty])
            color = random.choice(COLORS)
            
            shape_size = self.get_shape_size(shape)
            total_size += shape_size
            if difficulty in ['hard', 'very_hard']:
                hard_count += 1
            
            pieces.append({
                'shape': shape,
                'color': color,
                'difficulty': difficulty,
                'size': shape_size
            })
        
        has_small_piece = any(p['difficulty'] in ['easy', 'medium'] for p in pieces)
        if not has_small_piece:
            pieces[2] = {
                'shape': random.choice(SHAPES_EASY + SHAPES_MEDIUM),
                'color': random.choice(COLORS),
                'difficulty': 'easy',
                'size': self.get_shape_size(pieces[2]['shape'])
            }
        
        self.consecutive_hard_pieces = hard_count
        
        return pieces
    
    def generate_new_pieces(self):
        """Tạo 3 khối mới""" 
        if not self.available_pieces:
            self.available_pieces = self.generate_balanced_pieces()
    
    def can_place(self, shape, row, col):
        """Kiểm tra có thể đặt khối ko"""
        for r, row_data in enumerate(shape):
            for c, cell in enumerate(row_data):
                if cell:
                    new_r, new_c = row + r, col + c
                    if new_r < 0 or new_r >= GRID_SIZE or new_c < 0 or new_c >= GRID_SIZE:
                        return False
                    if self.grid[new_r][new_c]:
                        return False
        return True
    
    def get_lines_to_clear_if_placed(self, shape, row, col):
        """Tính toán các hàng/cột sẽ bị xóa nếu đặt khối tại vị trí này"""
        temp_grid = [row[:] for row in self.grid]
        
        for r, row_data in enumerate(shape):
            for c, cell in enumerate(row_data):
                if cell:
                    temp_grid[row + r][col + c] = 1
        
        rows_to_clear = []
        cols_to_clear = []
        
        for r in range(GRID_SIZE):
            if all(temp_grid[r]):
                rows_to_clear.append(r)
        
        for c in range(GRID_SIZE):
            if all(temp_grid[r][c] for r in range(GRID_SIZE)):
                cols_to_clear.append(c)
        
        return {'rows': rows_to_clear, 'cols': cols_to_clear}
    
    def place_piece(self, shape, color, row, col):
        """Đặt khối lên bảng"""
        for r, row_data in enumerate(shape):
            for c, cell in enumerate(row_data):
                if cell:
                    self.grid[row + r][col + c] = color
        self.check_and_clear_lines()
    
    def check_and_clear_lines(self):
        """Kiểm tra và xóa hàng/cột đầy"""
        rows_to_clear = []
        cols_to_clear = []
        
        for r in range(GRID_SIZE):
            if all(self.grid[r]):
                rows_to_clear.append(r)
        
        for c in range(GRID_SIZE):
            if all(self.grid[r][c] for r in range(GRID_SIZE)):
                cols_to_clear.append(c)
        
        for r in rows_to_clear:
            self.grid[r] = [0] * GRID_SIZE
            self.score += 10
        
        for c in cols_to_clear:
            for r in range(GRID_SIZE):
                self.grid[r][c] = 0
            self.score += 10
        
        total_cleared = len(rows_to_clear) + len(cols_to_clear)
        if total_cleared > 1:
            self.score += total_cleared * 5
        
        # Thêm hiệu ứng combo
        if total_cleared >= 2:
            self.add_combo_effect(total_cleared)
        
        # Kiểm tra xem grid có trống hoàn toàn không
        if self.is_grid_empty():
            self.change_background_color()
    
    def has_valid_moves(self):
        """Kiểm tra còn nước đi hợp lệ ko"""
        for piece in self.available_pieces:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.can_place(piece['shape'], r, c):
                        return True
        return False
    
    def draw_grid(self):
        grid_x = (SCREEN_WIDTH - (GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN)) // 2
        grid_y = 105  
        
        pygame.draw.rect(screen, GRID_BG, 
                        (grid_x - 10, grid_y - 10, 
                         GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN + 20,
                         GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN + 20), 
                        border_radius=10)
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = grid_x + MARGIN + col * (CELL_SIZE + MARGIN)
                y = grid_y + MARGIN + row * (CELL_SIZE + MARGIN)
                
                is_highlighted = (row in self.highlighted_lines['rows'] or 
                                col in self.highlighted_lines['cols'])
                
                if self.grid[row][col]:
                    pygame.draw.rect(screen, self.grid[row][col], 
                                   (x, y, CELL_SIZE, CELL_SIZE), border_radius=5)
                    pygame.draw.rect(screen, WHITE, 
                                   (x, y, CELL_SIZE, CELL_SIZE), 2, border_radius=5)
                else:
                    pygame.draw.rect(screen, WHITE, 
                                   (x, y, CELL_SIZE, CELL_SIZE), border_radius=5)
                    pygame.draw.rect(screen, (200, 210, 220), 
                                   (x, y, CELL_SIZE, CELL_SIZE), 1, border_radius=5)
                
                if is_highlighted and self.preview_pos:
                    s = pygame.Surface((CELL_SIZE, CELL_SIZE))
                    s.set_alpha(100)
                    s.fill(HIGHLIGHT_COLOR)
                    screen.blit(s, (x, y))
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, 
                                   (x, y, CELL_SIZE, CELL_SIZE), 3, border_radius=5)
        
        if self.preview_pos and self.dragging_piece:
            preview_row, preview_col = self.preview_pos
            shape = self.dragging_piece['shape']
            color = self.dragging_piece['color']
            
            for r, row_data in enumerate(shape):
                for c, cell in enumerate(row_data):
                    if cell:
                        curr_row = preview_row + r
                        curr_col = preview_col + c
                        if 0 <= curr_row < GRID_SIZE and 0 <= curr_col < GRID_SIZE:
                            x = grid_x + MARGIN + curr_col * (CELL_SIZE + MARGIN)
                            y = grid_y + MARGIN + curr_row * (CELL_SIZE + MARGIN)
                            
                            if self.can_place_preview:
                                s = pygame.Surface((CELL_SIZE, CELL_SIZE))
                                s.set_alpha(150)
                                s.fill(color)
                                screen.blit(s, (x, y))
                                
                                pygame.draw.rect(screen, (80, 150, 255), 
                                               (x, y, CELL_SIZE, CELL_SIZE), 3, border_radius=5)
                            else:
                                s = pygame.Surface((CELL_SIZE, CELL_SIZE))
                                s.set_alpha(100)
                                s.fill((255, 100, 100))
                                screen.blit(s, (x, y))
                                
                                pygame.draw.rect(screen, (255, 50, 50), 
                                               (x, y, CELL_SIZE, CELL_SIZE), 3, border_radius=5)
    
    def draw_piece(self, piece, x, y, scale=1, alpha=255):
        shape = piece['shape']
        color = piece['color']
        cell_size = int(CELL_SIZE * scale)
        margin = int(MARGIN * scale)
        
        for r, row_data in enumerate(shape):
            for c, cell in enumerate(row_data):
                if cell:
                    px = x + c * (cell_size + margin)
                    py = y + r * (cell_size + margin)
                    
                    if alpha < 255:
                        s = pygame.Surface((cell_size, cell_size))
                        s.set_alpha(alpha)
                        s.fill(color)
                        screen.blit(s, (px, py))
                        pygame.draw.rect(screen, WHITE, 
                                       (px, py, cell_size, cell_size), 2, border_radius=4)
                    else:
                        pygame.draw.rect(screen, color, 
                                       (px, py, cell_size, cell_size), border_radius=4)
                        pygame.draw.rect(screen, WHITE, 
                                       (px, py, cell_size, cell_size), 2, border_radius=4)
    
    def get_piece_dimensions(self, shape):
        """Tính kích thước khối"""
        height = len(shape)
        width = max(len(row) for row in shape)
        return width, height
    
    def draw_available_pieces(self, mouse_pos):
        """Vẽ các khối có sẵn"""
        start_y = GRID_SIZE * (CELL_SIZE + MARGIN) + 155  
        
        container_width = SCREEN_WIDTH - 40
        container_x = 20
        slot_width = container_width // 3
        
        box_size = 120
        
        for i, piece in enumerate(self.available_pieces):
            if i == self.dragging_index:
                continue
            
            slot_center_x = container_x + slot_width * i + slot_width // 2
            slot_center_y = start_y + 70
            
            box_x = slot_center_x - box_size // 2
            box_y = slot_center_y - box_size // 2
            bg_rect = pygame.Rect(box_x, box_y, box_size, box_size)
            
            pygame.draw.rect(screen, WHITE, bg_rect, border_radius=12)
            
            if bg_rect.collidepoint(mouse_pos) and not self.dragging_piece:
                pygame.draw.rect(screen, (100, 150, 255), bg_rect, 4, border_radius=12)
            else:
                pygame.draw.rect(screen, (180, 190, 210), bg_rect, 2, border_radius=12)
            
            width, height = self.get_piece_dimensions(piece['shape'])
            piece_pixel_width = width * (CELL_SIZE * 0.5 + MARGIN * 0.5)
            piece_pixel_height = height * (CELL_SIZE * 0.5 + MARGIN * 0.5)
            
            piece_x = int(slot_center_x - piece_pixel_width // 2)
            piece_y = int(slot_center_y - piece_pixel_height // 2)
            
            self.draw_piece(piece, piece_x, piece_y, scale=0.5)
    
    def draw_dragging_piece(self, mouse_x, mouse_y):
        """Vẽ khối đang kéo"""
        if self.dragging_piece:
            x = mouse_x - self.drag_offset_x
            y = mouse_y - self.drag_offset_y
            self.draw_piece(self.dragging_piece, x, y, scale=0.7, alpha=200)
    
    def draw_score(self):
        """Vẽ điểm số - Layout: Title trên, Highest và Score cùng hàng dưới"""
        # BLOCK BLAST ở giữa trên cùng - phóng to
        title_font_big = pygame.font.Font(None, 56)
        title = title_font_big.render("BLOCK BLAST", True, (50, 50, 80))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title, title_rect)
        
        # Highest và Score cùng 1 hàng ở dưới
        score_font = pygame.font.Font(None, 32)
        
        # Highest bên trái
        highest_text = score_font.render(f"Highest: {self.highest_score}", True, (120, 120, 140))
        highest_rect = highest_text.get_rect(midright=(SCREEN_WIDTH // 2 - 20, 65))
        screen.blit(highest_text, highest_rect)
        
        # Score bên phải
        score_text = score_font.render(f"Score: {self.score}", True, (80, 80, 100))
        score_rect = score_text.get_rect(midleft=(SCREEN_WIDTH // 2 + 20, 65))
        screen.blit(score_text, score_rect)
    
    def draw_author(self):
        author_font = pygame.font.Font(None, 24)
        author_text = author_font.render("Author: Thai Duc Thien - 2313222", True, (100, 100, 120))
        
        author_surface = pygame.Surface(author_text.get_size(), pygame.SRCALPHA)
        author_surface.fill((255, 255, 255, 0))
        author_surface.blit(author_text, (0, 0))
        author_surface.set_alpha(180)  
        
        # Vẽ shadow mờ mờ ảo ảo
        shadow_text = author_font.render("Author: Thai Duc Thien - 2313222", True, (50, 50, 60))
        shadow_surface = pygame.Surface(shadow_text.get_size(), pygame.SRCALPHA)
        shadow_surface.fill((255, 255, 255, 0))
        shadow_surface.blit(shadow_text, (0, 0))
        shadow_surface.set_alpha(100)
        
        shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH // 2 + 1, SCREEN_HEIGHT - 14))
        author_rect = author_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))
        
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(author_surface, author_rect)
    
    def get_grid_pos_from_mouse(self, mouse_x, mouse_y):
        """Chuyển tọa độ chuột thành vị trí trên bảng dựa trên ô gần nhất"""
        grid_x = (SCREEN_WIDTH - (GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN)) // 2
        grid_y = 105  
        
        min_dist = float('inf')
        best_row, best_col = None, None
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell_x = grid_x + MARGIN + col * (CELL_SIZE + MARGIN) + CELL_SIZE // 2
                cell_y = grid_y + MARGIN + row * (CELL_SIZE + MARGIN) + CELL_SIZE // 2
                
                dist = ((mouse_x - cell_x) ** 2 + (mouse_y - cell_y) ** 2) ** 0.5
                
                if dist < min_dist:
                    min_dist = dist
                    best_row, best_col = row, col
        
        if min_dist < CELL_SIZE * 1.5:
            return best_row, best_col
        return None, None
    
    def get_piece_at_pos(self, mouse_x, mouse_y):
        """Kiểm tra click vào khối nào"""
        start_y = GRID_SIZE * (CELL_SIZE + MARGIN) + 155 
        
        container_width = SCREEN_WIDTH - 40
        container_x = 20
        slot_width = container_width // 3
        box_size = 120
        
        for i, piece in enumerate(self.available_pieces):
            slot_center_x = container_x + slot_width * i + slot_width // 2
            slot_center_y = start_y + 70
            
            box_x = slot_center_x - box_size // 2
            box_y = slot_center_y - box_size // 2
            bg_rect = pygame.Rect(box_x, box_y, box_size, box_size)
            
            if bg_rect.collidepoint(mouse_x, mouse_y):
                width, height = self.get_piece_dimensions(piece['shape'])
                piece_pixel_width = width * (CELL_SIZE * 0.5 + MARGIN * 0.5)
                piece_pixel_height = height * (CELL_SIZE * 0.5 + MARGIN * 0.5)
                
                piece_x = int(slot_center_x - piece_pixel_width // 2)
                piece_y = int(slot_center_y - piece_pixel_height // 2)
                
                return i, piece_x, piece_y
        
        return -1, 0, 0


def main():
    game = BlockBlastGame()
    clock = pygame.time.Clock()
    game_over = False
    highest_score = 0
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    if game.score > highest_score:
                        highest_score = game.score
                    game = BlockBlastGame(highest_score)
                    game_over = False
            
            if not game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    piece_index, piece_x, piece_y = game.get_piece_at_pos(*mouse_pos)
                    if piece_index != -1:
                        game.dragging_piece = game.available_pieces[piece_index]
                        game.dragging_index = piece_index
                        
                        width, height = game.get_piece_dimensions(game.dragging_piece['shape'])
                        piece_pixel_width = width * (CELL_SIZE * 0.5 + MARGIN * 0.5)
                        piece_pixel_height = height * (CELL_SIZE * 0.5 + MARGIN * 0.5)
                        
                        game.drag_offset_x = piece_pixel_width // 2
                        game.drag_offset_y = piece_pixel_height // 2
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if game.dragging_piece:
                        row, col = game.get_grid_pos_from_mouse(*mouse_pos)
                        if row is not None and game.can_place(game.dragging_piece['shape'], row, col):
                            game.place_piece(game.dragging_piece['shape'], 
                                           game.dragging_piece['color'], row, col)
                            game.available_pieces.pop(game.dragging_index)
                            game.score += len([cell for row in game.dragging_piece['shape'] 
                                             for cell in row if cell])
                            
                            if game.score > game.highest_score:
                                game.highest_score = game.score
                            if game.score > highest_score:
                                highest_score = game.score
                            
                        game.dragging_piece = None
                        game.dragging_index = -1
                        game.preview_pos = None
                        game.highlighted_lines = {'rows': [], 'cols': []}
                        
                        game.generate_new_pieces()
                        
                        if not game.has_valid_moves():
                            if game.score > highest_score:
                                highest_score = game.score
                            game_over = True
        
        # Cập nhật combo effects
        game.update_combo_effects()
        
        # Cập nhật preview khi đang kéo
        if game.dragging_piece:
            row, col = game.get_grid_pos_from_mouse(*mouse_pos)
            if row is not None:
                game.preview_pos = (row, col)
                game.can_place_preview = game.can_place(game.dragging_piece['shape'], row, col)
                
                if game.can_place_preview:
                    game.highlighted_lines = game.get_lines_to_clear_if_placed(
                        game.dragging_piece['shape'], row, col
                    )
                else:
                    game.highlighted_lines = {'rows': [], 'cols': []}
            else:
                game.preview_pos = None
                game.highlighted_lines = {'rows': [], 'cols': []}
        else:
            game.highlighted_lines = {'rows': [], 'cols': []}
        
        # Vẽ với màu nền động
        screen.fill(game.current_bg_color)
        game.draw_score()
        game.draw_grid()
        game.draw_available_pieces(mouse_pos)
        game.draw_dragging_piece(*mouse_pos)
        game.draw_combo_effects()
        game.draw_author()  
        
        # Game over
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER!", True, WHITE)
            score_text = font.render(f"Score: {game.score}", True, WHITE)
            restart_text = small_font.render("Press SPACE to restart", True, WHITE)
            
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            
            screen.blit(game_over_text, game_over_rect)
            screen.blit(score_text, score_rect)
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
