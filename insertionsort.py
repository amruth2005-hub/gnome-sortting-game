import pygame
import random
import sys
import math

# --- Game Configuration ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# --- Colors ---
COLOR_BACKGROUND = (17, 24, 39)      # Dark Blue/Gray
COLOR_TEXT = (240, 240, 240)
COLOR_BLOCK = (59, 130, 246)         # Blue
COLOR_BLOCK_TEXT = (255, 255, 255)
COLOR_SORTER_BODY = (234, 179, 8)     # Amber/Yellow
COLOR_SORTER_ACCENT = (255, 255, 255)
COLOR_HIGHLIGHT_MIN = (22, 163, 74, 120)  # Green, translucent
COLOR_HIGHLIGHT_SWAP = (34, 211, 238, 120) # Cyan, translucent
COLOR_SORTED_ZONE = (22, 163, 74, 40)      # Faint Green
COLOR_UNSORTED_ZONE = (239, 68, 68, 40)     # Faint Red

# --- Game Object Settings ---
BLOCK_WIDTH = 80
BLOCK_HEIGHT = 80
SORTER_RADIUS = 25
SORTER_SPEED = 4.5

class Sorter:
    """Represents the player-controlled Sorter."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.carrying_block_value = None
        self.is_carrying = False

    def move(self):
        """Updates the Sorter's position based on keyboard input."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= SORTER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += SORTER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= SORTER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += SORTER_SPEED

        # Keep Sorter within the screen bounds
        self.x = max(SORTER_RADIUS, min(self.x, SCREEN_WIDTH - SORTER_RADIUS))
        self.y = max(SORTER_RADIUS, min(self.y, SCREEN_HEIGHT - SORTER_RADIUS))

    def draw(self, screen, font):
        """Draws the Sorter on the screen."""
        pygame.draw.circle(screen, COLOR_SORTER_BODY, (self.x, self.y), SORTER_RADIUS)
        pygame.draw.circle(screen, COLOR_SORTER_ACCENT, (self.x, self.y), SORTER_RADIUS, 3)
        # If carrying a block, draw its value inside the sorter
        if self.is_carrying:
            text_surf = font.render(str(self.carrying_block_value), True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=(self.x, self.y))
            screen.blit(text_surf, text_rect)

    def is_colliding_with(self, block):
        """Checks if the Sorter is close enough to a block to interact."""
        dist = math.hypot(self.x - block.x, self.y - block.y)
        return dist < (BLOCK_WIDTH / 2) + SORTER_RADIUS

class DataBlock:
    """Represents a single data block to be sorted."""
    def __init__(self, value, original_index, total_blocks):
        self.value = value
        self.original_index = original_index # Stays with the object to track it
        self.current_pos_index = original_index # Changes after swaps
        self.update_screen_pos(total_blocks)
        self.is_ghost = False # Is this block being "carried"?

    def update_screen_pos(self, total_blocks):
        """Calculates the x, y coordinates based on current array position."""
        spacing = SCREEN_WIDTH / (total_blocks + 1)
        self.x = int(spacing * (self.current_pos_index + 1))
        self.y = int(SCREEN_HEIGHT / 2)

    def draw(self, screen, font, is_min=False, is_swap_target=False):
        """Draws the data block and its value."""
        if self.is_ghost:
            return # Don't draw if it's being carried
        
        rect = pygame.Rect(self.x - BLOCK_WIDTH / 2, self.y - BLOCK_HEIGHT / 2, BLOCK_WIDTH, BLOCK_HEIGHT)
        
        # Draw base block
        pygame.draw.rect(screen, COLOR_BLOCK, rect, border_radius=10)
        
        # Draw highlights if necessary
        highlight_color = None
        if is_min:
            highlight_color = COLOR_HIGHLIGHT_MIN
        elif is_swap_target:
            highlight_color = COLOR_HIGHLIGHT_SWAP

        if highlight_color:
            highlight_surface = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, highlight_color, (0, 0, BLOCK_WIDTH, BLOCK_HEIGHT), border_radius=10)
            screen.blit(highlight_surface, rect.topleft)
        
        # Value Text
        text_surf = font.render(str(self.value), True, COLOR_BLOCK_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

def draw_hud(screen, title_font, text_font, objective, array, pass_idx):
    """Draws all the UI text elements."""
    # Title
    title_surf = title_font.render("Selection Sorter", True, COLOR_TEXT)
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 20))

    # Objective Panel
    pygame.draw.rect(screen, (0,0,0,150), [20, 80, SCREEN_WIDTH - 40, 80], border_radius=10)
    obj_title = text_font.render("Current Objective:", True, (234, 179, 8))
    screen.blit(obj_title, (40, 90))
    obj_text = text_font.render(objective, True, COLOR_TEXT)
    screen.blit(obj_text, (40, 120))

    # Array Display
    array_str = ' '.join([str(val) for val in array])
    arr_surf = text_font.render(f"Array State: {array_str}", True, COLOR_TEXT)
    screen.blit(arr_surf, (20, SCREEN_HEIGHT - 50))
    
    # Draw zone indicators
    if 0 < pass_idx < len(array):
        spacing = SCREEN_WIDTH / (len(array) + 1)
        split_point = spacing * (pass_idx + 0.5)
        
        # Sorted Zone
        sorted_rect = pygame.Rect(0, SCREEN_HEIGHT/2 - 70, split_point, 140)
        sorted_surface = pygame.Surface(sorted_rect.size, pygame.SRCALPHA)
        sorted_surface.fill(COLOR_SORTED_ZONE)
        screen.blit(sorted_surface, sorted_rect.topleft)
        
        # Unsorted Zone
        unsorted_rect = pygame.Rect(split_point, SCREEN_HEIGHT/2 - 70, SCREEN_WIDTH - split_point, 140)
        unsorted_surface = pygame.Surface(unsorted_rect.size, pygame.SRCALPHA)
        unsorted_surface.fill(COLOR_UNSORTED_ZONE)
        screen.blit(unsorted_surface, unsorted_rect.topleft)

def main():
    """Main function to run the game."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Selection Sorter Game")
    clock = pygame.time.Clock()

    # --- Fonts ---
    title_font = pygame.font.Font(None, 50)
    text_font = pygame.font.Font(None, 32)
    block_font = pygame.font.Font(None, 45)

    # --- Game Variables ---
    game_state = "READY"
    objective = "Press SPACE to begin sorting!"
    
    array_to_sort = []
    blocks = []
    sorter = Sorter(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
    
    # Selection Sort specific variables
    current_pass_index = 0
    min_element_index = 0

    def reset_game():
        nonlocal array_to_sort, blocks, current_pass_index, min_element_index, game_state, objective
        game_state = "READY"
        objective = "Press SPACE to begin sorting! (R to Reset)"
        
        array_to_sort = random.sample(range(10, 100), 8)
        blocks = [DataBlock(val, i, len(array_to_sort)) for i, val in enumerate(array_to_sort)]
        
        current_pass_index = 0
        min_element_index = 0
        sorter.is_carrying = False
        sorter.carrying_block_value = None
        for block in blocks: block.is_ghost = False

    def start_new_pass():
        nonlocal game_state, objective, min_element_index
        if current_pass_index >= len(array_to_sort) - 1:
            game_state = "FINISHED"
            objective = "Array sorted! Press SPACE to play again."
            return

        # Find the minimum element in the unsorted part
        min_val = array_to_sort[current_pass_index]
        min_element_index = current_pass_index
        for i in range(current_pass_index + 1, len(array_to_sort)):
            if array_to_sort[i] < min_val:
                min_val = array_to_sort[i]
                min_element_index = i
        
        objective = f"Minimum is {array_to_sort[min_element_index]}. Move to the GREEN highlighted block to pick it up."
        game_state = "MOVE_TO_MIN"

    reset_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_SPACE and game_state in ["READY", "FINISHED"]:
                    reset_game()
                    game_state = "START_PASS"

        if game_state == "START_PASS":
            start_new_pass()
            
        sorter.move()

        # --- Game Logic (State Machine based on Collision) ---
        if game_state == "MOVE_TO_MIN":
            min_block = blocks[min_element_index]
            if sorter.is_colliding_with(min_block):
                sorter.is_carrying = True
                sorter.carrying_block_value = min_block.value
                min_block.is_ghost = True
                objective = f"Block acquired! Now move to the CYAN swap target at position {current_pass_index}."
                game_state = "CARRYING_TO_SWAP"

        elif game_state == "CARRYING_TO_SWAP":
            swap_block = blocks[current_pass_index]
            if sorter.is_colliding_with(swap_block):
                # Perform the swap
                array_to_sort[current_pass_index], array_to_sort[min_element_index] = array_to_sort[min_element_index], array_to_sort[current_pass_index]
                # Update block values and visual positions
                blocks[current_pass_index].value, blocks[min_element_index].value = blocks[min_element_index].value, blocks[current_pass_index].value
                
                # Reset sorter and ghost block
                sorter.is_carrying = False
                blocks[min_element_index].is_ghost = False
                
                objective = "Swap complete! Starting next pass..."
                game_state = "SWAPPING"
                pygame.time.wait(1000) # Pause to show the result
                current_pass_index += 1
                game_state = "START_PASS"

        # --- Drawing ---
        screen.fill(COLOR_BACKGROUND)
        draw_hud(screen, title_font, text_font, objective, array_to_sort, current_pass_index)
        
        for block in blocks:
            is_min = (game_state == "MOVE_TO_MIN" and block.current_pos_index == min_element_index)
            is_swap = (game_state == "CARRYING_TO_SWAP" and block.current_pos_index == current_pass_index)
            block.draw(screen, block_font, is_min, is_swap)

        sorter.draw(screen, block_font)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
