import pygame
import random
import sys
import math

# --- Game Configuration ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# --- Colors ---
COLOR_BACKGROUND = (26, 77, 46)  # Dark Green
COLOR_TEXT = (240, 240, 240)
COLOR_POT_BODY = (139, 69, 19)   # Brown
COLOR_POT_RIM = (160, 82, 45)    # Sienna
COLOR_HIGHLIGHT_CURRENT = (255, 255, 0, 100) # Yellow, translucent
COLOR_HIGHLIGHT_COMPARE = (0, 255, 255, 100) # Cyan, translucent
COLOR_GNOME_HAT = (255, 0, 0)      # Red
COLOR_GNOME_BODY = (0, 0, 255)     # Blue

# --- Game Object Settings ---
POT_RADIUS = 35
GNOME_RADIUS = 20
GNOME_SPEED = 4

class Gnome:
    """Represents the player character, the gnome."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        """Updates the gnome's position based on keyboard input."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= GNOME_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += GNOME_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= GNOME_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += GNOME_SPEED

        # Keep gnome within the screen bounds
        self.x = max(GNOME_RADIUS, min(self.x, SCREEN_WIDTH - GNOME_RADIUS))
        self.y = max(GNOME_RADIUS, min(self.y, SCREEN_HEIGHT - GNOME_RADIUS))

    def draw(self, screen):
        """Draws the gnome on the screen."""
        # Body
        pygame.draw.circle(screen, COLOR_GNOME_BODY, (self.x, self.y + 5), GNOME_RADIUS)
        # Hat
        hat_points = [(self.x, self.y - 30), (self.x - 20, self.y), (self.x + 20, self.y)]
        pygame.draw.polygon(screen, COLOR_GNOME_HAT, hat_points)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y - 30), 5) # Hat bobble

    def is_colliding_with(self, pot):
        """Checks if the gnome is close enough to a pot to interact."""
        dist = math.hypot(self.x - pot.x, self.y - pot.y)
        return dist < POT_RADIUS + GNOME_RADIUS

class FlowerPot:
    """Represents a single flower pot to be sorted."""
    def __init__(self, value, pos_index, total_pots):
        self.value = value
        self.pos_index = pos_index
        self.update_screen_pos(total_pots)

    def update_screen_pos(self, total_pots):
        """Calculates the x, y coordinates on the screen based on array position."""
        spacing = SCREEN_WIDTH / (total_pots + 1)
        self.x = int(spacing * (self.pos_index + 1))
        self.y = int(SCREEN_HEIGHT / 2)

    def draw(self, screen, font, is_current=False, is_compare=False):
        """Draws the flower pot and its value."""
        # Draw highlights if necessary
        if is_current or is_compare:
            highlight_surface = pygame.Surface((POT_RADIUS * 2, POT_RADIUS * 2), pygame.SRCALPHA)
            color = COLOR_HIGHLIGHT_CURRENT if is_current else COLOR_HIGHLIGHT_COMPARE
            pygame.draw.circle(highlight_surface, color, (POT_RADIUS, POT_RADIUS), POT_RADIUS)
            screen.blit(highlight_surface, (self.x - POT_RADIUS, self.y - POT_RADIUS))
        
        # Pot Body
        pygame.draw.rect(screen, COLOR_POT_BODY, (self.x - 25, self.y - 15, 50, 40))
        # Pot Rim
        pygame.draw.rect(screen, COLOR_POT_RIM, (self.x - 30, self.y - 25, 60, 10))
        
        # Value Text
        text_surf = font.render(str(self.value), True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=(self.x, self.y + 5))
        screen.blit(text_surf, text_rect)

def draw_hud(screen, title_font, text_font, objective, array, index, game_state):
    """Draws all the UI text elements."""
    # Title
    title_surf = title_font.render("Gnome Sorter: The Garden Gauntlet", True, COLOR_TEXT)
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 20))

    # Objective Panel
    pygame.draw.rect(screen, (0,0,0,150), [20, 80, SCREEN_WIDTH - 40, 80], border_radius=10)
    obj_title = text_font.render("Current Objective:", True, (255, 255, 0))
    screen.blit(obj_title, (40, 90))
    obj_text = text_font.render(objective, True, COLOR_TEXT)
    screen.blit(obj_text, (40, 120))

    # Array Display
    array_str = ' '.join([f"[{val}]" if i == index or i == index-1 else str(val) for i, val in enumerate(array)])
    arr_surf = text_font.render(f"Array: {array_str}", True, COLOR_TEXT)
    screen.blit(arr_surf, (20, SCREEN_HEIGHT - 80))

    # Game State Display
    state_surf = text_font.render(f"Algorithm State: {game_state}", True, COLOR_TEXT)
    screen.blit(state_surf, (20, SCREEN_HEIGHT - 50))

def main():
    """Main function to run the game."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Gnome Sorter Game")
    clock = pygame.time.Clock()

    # --- Fonts ---
    title_font = pygame.font.Font(None, 50)
    text_font = pygame.font.Font(None, 32)
    pot_font = pygame.font.Font(None, 40)

    # --- Game Variables ---
    game_data = {
        "state": "READY",
        "objective": "Press SPACE to start sorting the flower pots!",
        "array_to_sort": [],
        "pots": [],
        "sort_index": 0
    }
    gnome = Gnome(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

    def reset_game():
        """Resets the game to its initial state."""
        nonlocal game_data
        game_data["state"] = "READY"
        game_data["objective"] = "Press SPACE to start sorting! (R to reset)"
        
        # Generate a new random array
        game_data["array_to_sort"] = random.sample(range(10, 100), 8)
        game_data["pots"] = [FlowerPot(val, i, len(game_data["array_to_sort"])) for i, val in enumerate(game_data["array_to_sort"])]
        game_data["sort_index"] = 1 # Gnome sort starts by comparing index 1 and 0

    # Initialize game for the first time
    reset_game()

    # --- Main Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_SPACE:
                    if game_data["state"] == "READY":
                        game_data["state"] = "MOVING_TO_COMPARE"
                    elif game_data["state"] == "SWAP_PROMPT":
                        # Perform the swap
                        game_data["array_to_sort"][game_data["sort_index"]], game_data["array_to_sort"][game_data["sort_index"] - 1] = game_data["array_to_sort"][game_data["sort_index"] - 1], game_data["array_to_sort"][game_data["sort_index"]]
                        game_data["pots"][game_data["sort_index"]].value, game_data["pots"][game_data["sort_index"]-1].value = game_data["pots"][game_data["sort_index"]-1].value, game_data["pots"][game_data["sort_index"]].value
                        
                        # Move index back
                        game_data["sort_index"] = max(1, game_data["sort_index"] - 1)
                        game_data["state"] = "MOVING_TO_COMPARE"
                    elif game_data["state"] == "ADVANCE_PROMPT":
                        # Move index forward
                        game_data["sort_index"] += 1
                        if game_data["sort_index"] >= len(game_data["array_to_sort"]):
                            game_data["state"] = "FINISHED"
                        else:
                            game_data["state"] = "MOVING_TO_COMPARE"
                    elif game_data["state"] == "FINISHED":
                         reset_game()
        
        # --- Game Logic (State Machine) ---
        if game_data["state"] == "MOVING_TO_COMPARE":
            game_data["objective"] = f"Move the gnome to pot {game_data['sort_index']} to compare it with the previous one."
            target_pot = game_data["pots"][game_data["sort_index"]]
            if gnome.is_colliding_with(target_pot):
                # Comparison logic of Gnome Sort
                if game_data["array_to_sort"][game_data["sort_index"]] < game_data["array_to_sort"][game_data["sort_index"] - 1]:
                    game_data["objective"] = f"{game_data['array_to_sort'][game_data['sort_index']]} < {game_data['array_to_sort'][game_data['sort_index']-1]}. Out of order! Press SPACE to SWAP."
                    game_data["state"] = "SWAP_PROMPT"
                else:
                    game_data["objective"] = f"{game_data['array_to_sort'][game_data['sort_index']]} >= {game_data['array_to_sort'][game_data['sort_index']-1]}. In order! Press SPACE to ADVANCE."
                    game_data["state"] = "ADVANCE_PROMPT"
        
        elif game_data["state"] == "FINISHED":
            game_data["objective"] = "All pots sorted! Press SPACE to play again."

        # --- Update ---
        if game_data["state"] not in ["READY", "FINISHED"]:
            gnome.move()

        # --- Drawing ---
        screen.fill(COLOR_BACKGROUND)
        
        # Draw pots with appropriate highlights
        for i, pot in enumerate(game_data["pots"]):
            is_current = (game_data["state"] != "READY" and i == game_data["sort_index"])
            is_compare = (game_data["state"] != "READY" and i == game_data["sort_index"] - 1)
            pot.draw(screen, pot_font, is_current, is_compare)

        gnome.draw(screen)
        draw_hud(screen, title_font, text_font, game_data["objective"], game_data["array_to_sort"], game_data["sort_index"], game_data["state"])

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
