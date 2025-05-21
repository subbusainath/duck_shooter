import pygame
import sys
import math
import random
import os
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Duck Shooter")

# Create assets directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), "assets"), exist_ok=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Game states
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3
    HIGH_SCORES = 4

# Weapon types
class WeaponType(Enum):
    GUN = 0
    KNIFE = 1
    STONE = 2
    BOW = 3

# Duck types
class DuckType(Enum):
    NORMAL = 0
    FAST = 1
    ARMORED = 2
    GOLDEN = 3

# Power-up types
class PowerUpType(Enum):
    RAPID_FIRE = 0
    DOUBLE_DAMAGE = 1
    SLOW_MOTION = 2
    MULTI_SHOT = 3

# Game variables
score = 0
high_scores = [0, 0, 0, 0, 0]  # Top 5 high scores
current_weapon = WeaponType.GUN
game_state = GameState.MENU
clock = pygame.time.Clock()
FPS = 60
level = 1
ducks_killed = 0
ducks_needed_for_next_level = 10
time_remaining = 60  # seconds
difficulty = 1  # 1=easy, 2=medium, 3=hard

# Load fonts
font_large = pygame.font.SysFont('Arial', 48, bold=True)
font_medium = pygame.font.SysFont('Arial', 32)
font_small = pygame.font.SysFont('Arial', 24)

# Sound effects dictionary
sounds = {}

# Create programmatic assets
def create_placeholder_image(width, height, color):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(color)
    return surface

# Create duck image
def create_duck_image(duck_type, width, height):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Base duck color based on type
    if duck_type == DuckType.NORMAL:
        body_color = (139, 69, 19)  # Brown
        head_color = (165, 42, 42)  # Brown-red
    elif duck_type == DuckType.FAST:
        body_color = (0, 0, 255)  # Blue
        head_color = (0, 0, 200)  # Dark blue
    elif duck_type == DuckType.ARMORED:
        body_color = (169, 169, 169)  # Dark gray
        head_color = (105, 105, 105)  # Darker gray
    elif duck_type == DuckType.GOLDEN:
        body_color = GOLD
        head_color = ORANGE
    
    # Draw duck body (oval)
    pygame.draw.ellipse(surface, body_color, (0, height//4, width*3//4, height*2//3))
    
    # Draw duck head (circle)
    pygame.draw.circle(surface, head_color, (width*3//4, height//3), height//4)
    
    # Draw beak (triangle)
    pygame.draw.polygon(surface, ORANGE, [
        (width*3//4 + height//4, height//3),
        (width, height//3 - height//8),
        (width, height//3 + height//8)
    ])
    
    # Draw eye
    pygame.draw.circle(surface, BLACK, (width*3//4 + height//8, height//3 - height//8), height//12)
    
    # Draw wing
    pygame.draw.ellipse(surface, body_color, (width//4, height//2, width//3, height//3))
    
    return surface

# Create crosshair image
def create_crosshair_image(size):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw outer circle
    pygame.draw.circle(surface, RED, (size//2, size//2), size//2 - 2, 2)
    
    # Draw inner circle
    pygame.draw.circle(surface, RED, (size//2, size//2), size//8, 1)
    
    # Draw crosshair lines
    pygame.draw.line(surface, RED, (size//2, 0), (size//2, size//2 - size//6), 2)
    pygame.draw.line(surface, RED, (size//2, size//2 + size//6), (size//2, size), 2)
    pygame.draw.line(surface, RED, (0, size//2), (size//2 - size//6, size//2), 2)
    pygame.draw.line(surface, RED, (size//2 + size//6, size//2), (size, size//2), 2)
    
    return surface

# Create weapon images
def create_weapon_image(weapon_type):
    if weapon_type == WeaponType.GUN:
        surface = pygame.Surface((50, 20), pygame.SRCALPHA)
        # Draw gun barrel
        pygame.draw.rect(surface, (50, 50, 50), (0, 5, 40, 10))
        # Draw gun handle
        pygame.draw.rect(surface, (101, 67, 33), (30, 15, 10, 15))
        return surface
        
    elif weapon_type == WeaponType.KNIFE:
        surface = pygame.Surface((40, 15), pygame.SRCALPHA)
        # Draw knife blade
        pygame.draw.polygon(surface, (192, 192, 192), [(0, 5), (30, 0), (30, 15), (0, 10)])
        # Draw knife handle
        pygame.draw.rect(surface, (101, 67, 33), (30, 3, 10, 9))
        return surface
        
    elif weapon_type == WeaponType.STONE:
        surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        # Draw stone (irregular circle)
        pygame.draw.circle(surface, (100, 100, 100), (10, 10), 10)
        # Add some texture
        pygame.draw.circle(surface, (80, 80, 80), (7, 7), 3)
        pygame.draw.circle(surface, (120, 120, 120), (13, 13), 2)
        return surface
        
    elif weapon_type == WeaponType.BOW:
        surface = pygame.Surface((45, 45), pygame.SRCALPHA)
        # Draw bow arc
        pygame.draw.arc(surface, (139, 69, 19), (0, 0, 40, 45), math.pi/2, 3*math.pi/2, 3)
        # Draw bow string
        pygame.draw.line(surface, WHITE, (5, 0), (5, 45), 1)
        return surface

# Create projectile images
def create_projectile_image(weapon_type):
    if weapon_type == WeaponType.GUN:
        surface = pygame.Surface((10, 5), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 255, 0), (0, 0, 10, 5))
        return surface
        
    elif weapon_type == WeaponType.KNIFE:
        surface = pygame.Surface((15, 8), pygame.SRCALPHA)
        pygame.draw.polygon(surface, (192, 192, 192), [(0, 4), (15, 0), (15, 8), (0, 4)])
        return surface
        
    elif weapon_type == WeaponType.STONE:
        surface = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(surface, (100, 100, 100), (6, 6), 6)
        return surface
        
    elif weapon_type == WeaponType.BOW:
        surface = pygame.Surface((20, 5), pygame.SRCALPHA)
        # Draw arrow shaft
        pygame.draw.rect(surface, (139, 69, 19), (0, 2, 15, 1))
        # Draw arrow head
        pygame.draw.polygon(surface, (192, 192, 192), [(15, 0), (20, 2.5), (15, 5)])
        # Draw arrow feathers
        pygame.draw.polygon(surface, (255, 255, 255), [(0, 0), (5, 2), (0, 2)])
        pygame.draw.polygon(surface, (255, 255, 255), [(0, 5), (5, 3), (0, 3)])
        return surface

# Create power-up images
def create_powerup_image(powerup_type):
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    if powerup_type == PowerUpType.RAPID_FIRE:
        color = RED
        # Draw lightning bolt
        pygame.draw.polygon(surface, color, [(15, 0), (5, 15), (15, 15), (15, 30), (25, 15), (15, 15)])
    elif powerup_type == PowerUpType.DOUBLE_DAMAGE:
        color = ORANGE
        # Draw X symbol
        pygame.draw.line(surface, color, (5, 5), (25, 25), 4)
        pygame.draw.line(surface, color, (25, 5), (5, 25), 4)
    elif powerup_type == PowerUpType.SLOW_MOTION:
        color = BLUE
        # Draw clock
        pygame.draw.circle(surface, color, (15, 15), 12, 2)
        pygame.draw.line(surface, color, (15, 15), (15, 7), 2)
        pygame.draw.line(surface, color, (15, 15), (20, 15), 2)
    elif powerup_type == PowerUpType.MULTI_SHOT:
        color = PURPLE
        # Draw three bullets
        pygame.draw.rect(surface, color, (10, 5, 10, 5))
        pygame.draw.rect(surface, color, (5, 13, 10, 5))
        pygame.draw.rect(surface, color, (15, 13, 10, 5))
        pygame.draw.rect(surface, color, (10, 21, 10, 5))
    
    # Draw circle around power-up
    pygame.draw.circle(surface, color, (15, 15), 14, 2)
    
    return surface

# Create background image
def create_background_image():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Sky gradient
    for y in range(SCREEN_HEIGHT - 100):
        # Calculate color based on height (darker blue at top, lighter at bottom)
        blue_val = min(255, 100 + int(y * 0.2))
        surface.fill((100, 149, blue_val), (0, y, SCREEN_WIDTH, 1))
    
    # Ground
    pygame.draw.rect(surface, GREEN, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
    
    # Sun
    pygame.draw.circle(surface, (255, 255, 200), (100, 100), 50)
    
    # Clouds
    for i in range(5):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(50, 200)
        size = random.randint(30, 80)
        for j in range(5):
            cloud_x = x + random.randint(-size, size)
            cloud_y = y + random.randint(-size//2, size//2)
            pygame.draw.circle(surface, (240, 240, 240), (cloud_x, cloud_y), size//2)
    
    # Trees
    for i in range(10):
        x = random.randint(0, SCREEN_WIDTH)
        y = SCREEN_HEIGHT - 100
        trunk_height = random.randint(30, 60)
        trunk_width = trunk_height // 3
        # Draw trunk
        pygame.draw.rect(surface, (101, 67, 33), (x, y - trunk_height, trunk_width, trunk_height))
        # Draw foliage
        foliage_size = trunk_width * 3
        pygame.draw.circle(surface, (0, 100, 0), (x + trunk_width//2, y - trunk_height - foliage_size//2), foliage_size)
    
    return surface

# Create sound effects
def create_sound_effects():
    global sounds
    
    try:
        import numpy
        
        # Create a simple beep sound for shooting
        def create_beep_sound(frequency, duration, volume=0.5):
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
            max_sample = 2**(16 - 1) - 1
            
            for s in range(n_samples):
                t = float(s) / sample_rate
                buf[s][0] = int(max_sample * volume * math.sin(2 * math.pi * frequency * t))
                buf[s][1] = int(max_sample * volume * math.sin(2 * math.pi * frequency * t))
                
            return pygame.mixer.Sound(buffer=buf)
        
        # Create sound effects
        sounds["gun_shoot"] = create_beep_sound(440, 0.1)  # A4 note
        sounds["knife_throw"] = create_beep_sound(330, 0.2)  # E4 note
        sounds["stone_throw"] = create_beep_sound(220, 0.3)  # A3 note
        sounds["bow_shoot"] = create_beep_sound(587, 0.15)  # D5 note
        sounds["duck_hit"] = create_beep_sound(880, 0.05)  # A5 note
        sounds["duck_die"] = create_beep_sound(220, 0.5, 0.7)  # A3 note, longer
        sounds["powerup"] = create_beep_sound(660, 0.2, 0.8)  # E5 note
        sounds["level_up"] = create_beep_sound(880, 0.5, 0.8)  # A5 note, longer
        
    except ImportError:
        print("NumPy not available, sound effects disabled")
        # Create empty sounds as fallback
        empty_sound = pygame.mixer.Sound(buffer=bytearray(44100))  # 1 second of silence
        for sound_name in ["gun_shoot", "knife_throw", "stone_throw", "bow_shoot", 
                          "duck_hit", "duck_die", "powerup", "level_up"]:
            sounds[sound_name] = empty_sound

# Weapon class
class Weapon:
    def __init__(self, weapon_type):
        self.type = weapon_type
        self.cooldown = 0
        self.max_cooldown = 30  # Default cooldown frames
        self.damage = 1  # Default damage
        self.projectile_speed = 15  # Default projectile speed
        self.image = None
        self.projectile_image = None
        self.ammo = -1  # -1 means unlimited ammo
        self.sound = None
        
        # Set weapon-specific properties
        if weapon_type == WeaponType.GUN:
            self.max_cooldown = 20
            self.damage = 2
            self.projectile_speed = 20
            self.image = create_weapon_image(weapon_type)
            self.projectile_image = create_projectile_image(weapon_type)
            self.ammo = 30
            self.sound = sounds.get("gun_shoot")
        elif weapon_type == WeaponType.KNIFE:
            self.max_cooldown = 15
            self.damage = 3
            self.projectile_speed = 12
            self.image = create_weapon_image(weapon_type)
            self.projectile_image = create_projectile_image(weapon_type)
            self.ammo = 15
            self.sound = sounds.get("knife_throw")
        elif weapon_type == WeaponType.STONE:
            self.max_cooldown = 25
            self.damage = 1
            self.projectile_speed = 10
            self.image = create_weapon_image(weapon_type)
            self.projectile_image = create_projectile_image(weapon_type)
            self.ammo = 20
            self.sound = sounds.get("stone_throw")
        elif weapon_type == WeaponType.BOW:
            self.max_cooldown = 40
            self.damage = 4
            self.projectile_speed = 18
            self.image = create_weapon_image(weapon_type)
            self.projectile_image = create_projectile_image(weapon_type)
            self.ammo = 10
            self.sound = sounds.get("bow_shoot")
    
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def can_shoot(self):
        return self.cooldown == 0 and (self.ammo > 0 or self.ammo == -1)
    
    def shoot(self):
        if self.can_shoot():
            self.cooldown = self.max_cooldown
            if self.ammo > 0:
                self.ammo -= 1
            if self.sound:
                self.sound.play()
            return True
        return False

# Projectile class
class Projectile:
    def __init__(self, x, y, target_x, target_y, weapon):
        self.x = x
        self.y = y
        self.weapon = weapon
        self.speed = weapon.projectile_speed
        self.damage = weapon.damage
        self.image = weapon.projectile_image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        self.dx = (dx / distance) * self.speed if distance > 0 else 0
        self.dy = (dy / distance) * self.speed if distance > 0 else 0
        
        # Calculate rotation angle for the projectile image
        self.angle = math.degrees(math.atan2(-dy, dx))
        
        # For multi-shot power-up
        self.is_multi_shot = False
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
    
    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rect = rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(rotated_image, rect)
    
    def is_out_of_bounds(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)

# Duck class
class Duck:
    def __init__(self, duck_type=DuckType.NORMAL):
        self.duck_type = duck_type
        self.width = 60
        self.height = 40
        self.image = create_duck_image(duck_type, self.width, self.height)
        self.hit_sound = sounds.get("duck_hit")
        self.die_sound = sounds.get("duck_die")
        
        # Set duck-specific properties
        if duck_type == DuckType.NORMAL:
            self.health = 5
            self.score_value = 10
            self.speed_multiplier = 1.0
        elif duck_type == DuckType.FAST:
            self.health = 3
            self.score_value = 15
            self.speed_multiplier = 1.8
        elif duck_type == DuckType.ARMORED:
            self.health = 10
            self.score_value = 20
            self.speed_multiplier = 0.7
        elif duck_type == DuckType.GOLDEN:
            self.health = 1
            self.score_value = 50
            self.speed_multiplier = 2.2
            
        self.reset()
    
    def reset(self):
        # Start from either left or right side
        self.direction = random.choice([-1, 1])  # -1 for left to right, 1 for right to left
        
        if self.direction == -1:
            self.x = SCREEN_WIDTH + self.width
        else:
            self.x = -self.width
            
        self.y = random.randint(100, SCREEN_HEIGHT - 200)
        base_speed = random.uniform(2, 5)
        self.speed_x = base_speed * self.direction * self.speed_multiplier
        self.speed_y = random.uniform(-1, 1) * self.speed_multiplier
        
        # Animation variables
        self.flap_timer = 0
        self.flap_direction = 1
        self.flap_speed = 0.2
        self.flap_offset = 0
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off top and bottom edges
        if self.y <= 50 or self.y >= SCREEN_HEIGHT - 150:
            self.speed_y *= -1
        
        # Check if duck has gone off screen
        if (self.direction == -1 and self.x < -self.width) or \
           (self.direction == 1 and self.x > SCREEN_WIDTH + self.width):
            self.reset()
            
        # Update wing flapping animation
        self.flap_timer += self.flap_speed
        self.flap_offset = math.sin(self.flap_timer) * 5
    
    def draw(self, surface):
        # Create a copy of the image for animation
        image_copy = self.image.copy()
        
        # Draw wing with flapping animation
        wing_y_offset = self.height//2 + self.flap_offset
        pygame.draw.ellipse(image_copy, (139, 69, 19) if self.duck_type == DuckType.NORMAL else 
                           (0, 0, 255) if self.duck_type == DuckType.FAST else
                           (169, 169, 169) if self.duck_type == DuckType.ARMORED else
                           GOLD, 
                           (self.width//4, wing_y_offset, self.width//3, self.height//3))
        
        # Flip the image based on direction
        if self.direction == -1:
            flipped_image = pygame.transform.flip(image_copy, True, False)
            surface.blit(flipped_image, (self.x, self.y))
        else:
            surface.blit(image_copy, (self.x, self.y))
    
    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            if self.die_sound:
                self.die_sound.play()
            return True
        else:
            if self.hit_sound:
                self.hit_sound.play()
            return False
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# PowerUp class
class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.width = 30
        self.height = 30
        self.image = create_powerup_image(powerup_type)
        self.speed_y = 2
        self.active_time = 10 * FPS  # 10 seconds
        self.sound = sounds.get("powerup")
    
    def update(self):
        self.y += self.speed_y
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
    
    def is_out_of_bounds(self):
        return self.y > SCREEN_HEIGHT
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def activate(self):
        if self.sound:
            self.sound.play()
        return self.type, self.active_time

# Player/Crosshair class
class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.crosshair_size = 30
        self.crosshair_image = create_crosshair_image(self.crosshair_size)
        
        self.weapons = {
            WeaponType.GUN: Weapon(WeaponType.GUN),
            WeaponType.KNIFE: Weapon(WeaponType.KNIFE),
            WeaponType.STONE: Weapon(WeaponType.STONE),
            WeaponType.BOW: Weapon(WeaponType.BOW)
        }
        self.current_weapon = self.weapons[WeaponType.GUN]
        
        # Power-up effects
        self.active_powerups = {}  # {PowerUpType: remaining_time}
        self.damage_multiplier = 1.0
        self.cooldown_multiplier = 1.0
    
    def update(self):
        # Update position to mouse position
        self.x, self.y = pygame.mouse.get_pos()
        
        # Update current weapon
        self.current_weapon.update()
        
        # Update power-ups
        for powerup_type in list(self.active_powerups.keys()):
            self.active_powerups[powerup_type] -= 1
            if self.active_powerups[powerup_type] <= 0:
                self.deactivate_powerup(powerup_type)
    
    def draw(self, surface):
        # Draw crosshair
        rect = self.crosshair_image.get_rect(center=(self.x, self.y))
        surface.blit(self.crosshair_image, rect)
        
        # Draw current weapon at bottom of screen
        weapon_rect = self.current_weapon.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        surface.blit(self.current_weapon.image, weapon_rect)
        
        # Draw ammo count
        if self.current_weapon.ammo >= 0:
            ammo_text = font_small.render(f"Ammo: {self.current_weapon.ammo}", True, WHITE)
            surface.blit(ammo_text, (SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT - 50))
        
        # Draw active power-ups
        x_offset = SCREEN_WIDTH - 150
        for powerup_type, time_left in self.active_powerups.items():
            powerup_image = create_powerup_image(powerup_type)
            surface.blit(powerup_image, (x_offset, 60))
            time_text = font_small.render(f"{time_left // FPS}s", True, WHITE)
            surface.blit(time_text, (x_offset + 35, 65))
            x_offset += 70
    
    def shoot(self):
        if self.current_weapon.can_shoot():
            self.current_weapon.shoot()
            
            # Create projectile
            projectile = Projectile(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, self.x, self.y, self.current_weapon)
            
            # Apply power-up effects
            if PowerUpType.DOUBLE_DAMAGE in self.active_powerups:
                projectile.damage *= 2
                
            # Multi-shot power-up
            if PowerUpType.MULTI_SHOT in self.active_powerups:
                return [
                    projectile,
                    Projectile(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, self.x + 30, self.y - 30, self.current_weapon),
                    Projectile(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, self.x - 30, self.y - 30, self.current_weapon)
                ]
            
            return [projectile]
        return []
    
    def change_weapon(self, weapon_type):
        self.current_weapon = self.weapons[weapon_type]
    
    def activate_powerup(self, powerup_type, duration):
        self.active_powerups[powerup_type] = duration
        
        # Apply immediate effects
        if powerup_type == PowerUpType.RAPID_FIRE:
            for weapon in self.weapons.values():
                weapon.max_cooldown = max(5, int(weapon.max_cooldown * 0.5))
        
    def deactivate_powerup(self, powerup_type):
        if powerup_type in self.active_powerups:
            del self.active_powerups[powerup_type]
            
            # Revert effects
            if powerup_type == PowerUpType.RAPID_FIRE:
                # Reset weapon cooldowns to original values
                self.weapons[WeaponType.GUN].max_cooldown = 20
                self.weapons[WeaponType.KNIFE].max_cooldown = 15
                self.weapons[WeaponType.STONE].max_cooldown = 25
                self.weapons[WeaponType.BOW].max_cooldown = 40

# UI class for modern interface
class UI:
    def __init__(self):
        self.weapon_buttons = [
            {"type": WeaponType.GUN, "rect": pygame.Rect(50, SCREEN_HEIGHT - 80, 100, 60), "text": "Gun"},
            {"type": WeaponType.KNIFE, "rect": pygame.Rect(170, SCREEN_HEIGHT - 80, 100, 60), "text": "Knife"},
            {"type": WeaponType.STONE, "rect": pygame.Rect(290, SCREEN_HEIGHT - 80, 100, 60), "text": "Stone"},
            {"type": WeaponType.BOW, "rect": pygame.Rect(410, SCREEN_HEIGHT - 80, 100, 60), "text": "Bow"}
        ]
        
        # Create background
        self.background = create_background_image()
        
        # Menu animations
        self.menu_duck_x = -100
        self.menu_duck_y = 300
        self.menu_duck_speed = 3
        self.menu_duck_image = create_duck_image(DuckType.NORMAL, 80, 60)
    
    def draw_menu(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))
        
        # Draw animated duck
        self.menu_duck_x += self.menu_duck_speed
        if self.menu_duck_x > SCREEN_WIDTH + 100:
            self.menu_duck_x = -100
        surface.blit(self.menu_duck_image, (self.menu_duck_x, self.menu_duck_y))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        surface.blit(overlay, (0, 0))
        
        # Draw title with shadow
        title_shadow = font_large.render("DUCK SHOOTER", True, BLACK)
        title_text = font_large.render("DUCK SHOOTER", True, GOLD)
        surface.blit(title_shadow, (SCREEN_WIDTH//2 - title_text.get_width()//2 + 3, 203))
        surface.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 200))
        
        # Draw start button with hover effect
        mouse_pos = pygame.mouse.get_pos()
        start_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 60)
        button_color = (0, 180, 0) if start_button.collidepoint(mouse_pos) else GREEN
        pygame.draw.rect(surface, button_color, start_button, border_radius=15)
        pygame.draw.rect(surface, WHITE, start_button, 2, border_radius=15)  # White border
        
        start_text = font_medium.render("START", True, WHITE)
        surface.blit(start_text, (start_button.centerx - start_text.get_width()//2, start_button.centery - start_text.get_height()//2))
        
        # Draw difficulty buttons
        diff_text = font_medium.render("Difficulty:", True, WHITE)
        surface.blit(diff_text, (SCREEN_WIDTH//2 - diff_text.get_width()//2, 450))
        
        diff_buttons = []
        diff_labels = ["Easy", "Medium", "Hard"]
        button_width = 120
        total_width = button_width * 3 + 20 * 2  # 3 buttons with 20px spacing
        start_x = SCREEN_WIDTH//2 - total_width//2
        
        for i, label in enumerate(diff_labels):
            diff_button = pygame.Rect(start_x + i * (button_width + 20), 500, button_width, 50)
            is_selected = difficulty == i + 1
            is_hovered = diff_button.collidepoint(mouse_pos)
            
            if is_selected:
                button_color = GOLD if is_hovered else ORANGE
            else:
                button_color = (100, 100, 100) if is_hovered else GRAY
                
            pygame.draw.rect(surface, button_color, diff_button, border_radius=10)
            pygame.draw.rect(surface, WHITE, diff_button, 2, border_radius=10)  # White border
            
            diff_label = font_small.render(label, True, WHITE)
            surface.blit(diff_label, (diff_button.centerx - diff_label.get_width()//2, 
                                     diff_button.centery - diff_label.get_height()//2))
            diff_buttons.append((diff_button, i + 1))
        
        # Draw instructions
        instructions = [
            "- Shoot ducks with different weapons",
            "- Collect power-ups for special abilities",
            "- Complete levels by shooting enough ducks",
            "- Beat the high score!"
        ]
        
        for i, instruction in enumerate(instructions):
            instr_text = font_small.render(instruction, True, WHITE)
            surface.blit(instr_text, (SCREEN_WIDTH//2 - instr_text.get_width()//2, 600 + i * 30))
        
        return start_button, diff_buttons
    
    def draw_game_over(self, surface, score):
        # Draw background with overlay
        surface.blit(self.background, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        surface.blit(overlay, (0, 0))
        
        # Draw game over text with shadow
        game_over_shadow = font_large.render("GAME OVER", True, BLACK)
        game_over_text = font_large.render("GAME OVER", True, RED)
        surface.blit(game_over_shadow, (SCREEN_WIDTH//2 - game_over_text.get_width()//2 + 3, 153))
        surface.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 150))
        
        # Draw score
        score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
        surface.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 250))
        
        # Draw high scores
        high_score_title = font_medium.render("High Scores", True, GOLD)
        surface.blit(high_score_title, (SCREEN_WIDTH//2 - high_score_title.get_width()//2, 300))
        
        for i, hs in enumerate(high_scores):
            hs_text = font_small.render(f"{i+1}. {hs}", True, WHITE)
            surface.blit(hs_text, (SCREEN_WIDTH//2 - 50, 350 + i * 30))
        
        # Draw restart button with hover effect
        mouse_pos = pygame.mouse.get_pos()
        restart_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 550, 200, 60)
        button_color = (0, 180, 0) if restart_button.collidepoint(mouse_pos) else GREEN
        pygame.draw.rect(surface, button_color, restart_button, border_radius=15)
        pygame.draw.rect(surface, WHITE, restart_button, 2, border_radius=15)  # White border
        
        restart_text = font_medium.render("RESTART", True, WHITE)
        surface.blit(restart_text, (restart_button.centerx - restart_text.get_width()//2, 
                                  restart_button.centery - restart_text.get_height()//2))
        
        # Draw menu button
        menu_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 630, 200, 60)
        button_color = (0, 0, 180) if menu_button.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(surface, button_color, menu_button, border_radius=15)
        pygame.draw.rect(surface, WHITE, menu_button, 2, border_radius=15)  # White border
        
        menu_text = font_medium.render("MENU", True, WHITE)
        surface.blit(menu_text, (menu_button.centerx - menu_text.get_width()//2, 
                               menu_button.centery - menu_text.get_height()//2))
        
        return restart_button, menu_button
    
    def draw_pause_menu(self, surface):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        surface.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = font_large.render("PAUSED", True, WHITE)
        surface.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 200))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Resume button
        resume_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 60)
        button_color = (0, 180, 0) if resume_button.collidepoint(mouse_pos) else GREEN
        pygame.draw.rect(surface, button_color, resume_button, border_radius=15)
        pygame.draw.rect(surface, WHITE, resume_button, 2, border_radius=15)
        
        resume_text = font_medium.render("RESUME", True, WHITE)
        surface.blit(resume_text, (resume_button.centerx - resume_text.get_width()//2, 
                                 resume_button.centery - resume_text.get_height()//2))
        
        # Menu button
        menu_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 380, 200, 60)
        button_color = (0, 0, 180) if menu_button.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(surface, button_color, menu_button, border_radius=15)
        pygame.draw.rect(surface, WHITE, menu_button, 2, border_radius=15)
        
        menu_text = font_medium.render("MENU", True, WHITE)
        surface.blit(menu_text, (menu_button.centerx - menu_text.get_width()//2, 
                               menu_button.centery - menu_text.get_height()//2))
        
        return resume_button, menu_button
    
    def draw_hud(self, surface, score, player, level, ducks_killed, ducks_needed, time_remaining):
        # Draw top bar
        pygame.draw.rect(surface, (50, 50, 50, 200), (0, 0, SCREEN_WIDTH, 50))
        
        # Draw score
        score_text = font_medium.render(f"Score: {score}", True, WHITE)
        surface.blit(score_text, (20, 10))
        
        # Draw level
        level_text = font_medium.render(f"Level: {level}", True, WHITE)
        surface.blit(level_text, (200, 10))
        
        # Draw ducks progress
        progress_text = font_medium.render(f"Ducks: {ducks_killed}/{ducks_needed}", True, WHITE)
        surface.blit(progress_text, (350, 10))
        
        # Draw time remaining
        time_text = font_medium.render(f"Time: {time_remaining}", True, WHITE)
        surface.blit(time_text, (550, 10))
        
        # Draw weapon selection buttons
        for button in self.weapon_buttons:
            color = GREEN if button["type"] == player.current_weapon.type else GRAY
            
            # Check if weapon has ammo
            if player.weapons[button["type"]].ammo == 0:
                color = RED  # No ammo
            
            pygame.draw.rect(surface, color, button["rect"], border_radius=10)
            pygame.draw.rect(surface, WHITE, button["rect"], 2, border_radius=10)  # White border
            
            text = font_small.render(button["text"], True, WHITE)
            surface.blit(text, (button["rect"].centerx - text.get_width()//2, 
                               button["rect"].centery - text.get_height()//2))
            
            # Draw ammo count
            ammo = player.weapons[button["type"]].ammo
            if ammo >= 0:
                ammo_text = font_small.render(f"{ammo}", True, WHITE)
                surface.blit(ammo_text, (button["rect"].right - ammo_text.get_width() - 5, 
                                       button["rect"].bottom - ammo_text.get_height() - 5))
    
    def check_weapon_button_click(self, pos):
        for button in self.weapon_buttons:
            if button["rect"].collidepoint(pos):
                return button["type"]
        return None

# Game initialization
def init_game():
    global score, game_state, level, ducks_killed, ducks_needed_for_next_level, time_remaining
    
    score = 0
    game_state = GameState.PLAYING
    level = 1
    ducks_killed = 0
    ducks_needed_for_next_level = 10 * level
    time_remaining = 60  # seconds
    
    player = Player()
    
    # Create ducks based on difficulty and level
    ducks = []
    num_ducks = 3 + (level - 1) + difficulty
    
    for i in range(num_ducks):
        # Add different duck types based on level and difficulty
        if level >= 3 and random.random() < 0.2:
            ducks.append(Duck(DuckType.GOLDEN))
        elif level >= 2 and random.random() < 0.3:
            ducks.append(Duck(DuckType.FAST))
        elif level >= 2 and random.random() < 0.3:
            ducks.append(Duck(DuckType.ARMORED))
        else:
            ducks.append(Duck(DuckType.NORMAL))
    
    projectiles = []
    powerups = []
    ui = UI()
    
    # Timer for power-up spawning
    powerup_timer = random.randint(FPS * 10, FPS * 20)  # 10-20 seconds
    
    # Timer for game time
    game_timer = 0
    
    return player, ducks, projectiles, powerups, ui, powerup_timer, game_timer

# Main game loop
def main():
    global score, game_state, current_weapon, high_scores, level, ducks_killed
    global ducks_needed_for_next_level, time_remaining, difficulty
    
    # Try to create sound effects
    try:
        create_sound_effects()
    except Exception as e:
        print(f"Could not create sound effects: {e}")
    
    player, ducks, projectiles, powerups, ui, powerup_timer, game_timer = init_game()
    
    running = True
    while running:
        # Handle game state
        if game_state == GameState.MENU:
            screen.fill(BLUE)
            start_button, diff_buttons = ui.draw_menu(screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check start button
                    if start_button.collidepoint(mouse_pos):
                        player, ducks, projectiles, powerups, ui, powerup_timer, game_timer = init_game()
                    
                    # Check difficulty buttons
                    for button, diff_level in diff_buttons:
                        if button.collidepoint(mouse_pos):
                            difficulty = diff_level
        
        elif game_state == GameState.PLAYING:
            # Draw background
            screen.blit(ui.background, (0, 0))
            
            # Update game timer
            game_timer += 1
            if game_timer % FPS == 0:  # Every second
                time_remaining -= 1
                if time_remaining <= 0:
                    game_state = GameState.GAME_OVER
                    # Update high scores
                    if score > min(high_scores):
                        high_scores.append(score)
                        high_scores.sort(reverse=True)
                        high_scores = high_scores[:5]  # Keep only top 5
            
            # Update power-up timer
            powerup_timer -= 1
            if powerup_timer <= 0:
                # Spawn a power-up
                powerup_type = random.choice(list(PowerUpType))
                x = random.randint(50, SCREEN_WIDTH - 50)
                powerups.append(PowerUp(x, 0, powerup_type))
                powerup_timer = random.randint(FPS * 10, FPS * 20)  # 10-20 seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameState.PAUSED
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if weapon button was clicked
                    weapon_type = ui.check_weapon_button_click(event.pos)
                    if weapon_type:
                        if player.weapons[weapon_type].ammo != 0:  # Only switch if ammo available
                            player.change_weapon(weapon_type)
                    else:
                        # Shoot
                        new_projectiles = player.shoot()
                        projectiles.extend(new_projectiles)
            
            # Update player
            player.update()
            
            # Update ducks
            for duck in ducks:
                duck.update()
                duck.draw(screen)
            
            # Update projectiles
            for proj in projectiles[:]:
                proj.update()
                proj.draw(screen)
                
                # Check for collisions with ducks
                for duck in ducks[:]:
                    if duck.get_rect().collidepoint(proj.x, proj.y):
                        if duck.hit(proj.damage):
                            score += duck.score_value
                            ducks_killed += 1
                            
                            # Check for level up
                            if ducks_killed >= ducks_needed_for_next_level:
                                level += 1
                                ducks_killed = 0
                                ducks_needed_for_next_level = 10 * level
                                time_remaining += 30  # Add time for next level
                                
                                # Play level up sound
                                if "level_up" in sounds:
                                    sounds["level_up"].play()
                                
                                # Spawn new ducks based on new level
                                ducks.remove(duck)
                                num_new_ducks = 3 + (level - 1) + difficulty
                                for i in range(num_new_ducks):
                                    if level >= 3 and random.random() < 0.2:
                                        ducks.append(Duck(DuckType.GOLDEN))
                                    elif level >= 2 and random.random() < 0.3:
                                        ducks.append(Duck(DuckType.FAST))
                                    elif level >= 2 and random.random() < 0.3:
                                        ducks.append(Duck(DuckType.ARMORED))
                                    else:
                                        ducks.append(Duck(DuckType.NORMAL))
                            else:
                                # Just replace the duck
                                ducks.remove(duck)
                                
                                # Determine duck type based on level
                                if level >= 3 and random.random() < 0.2:
                                    ducks.append(Duck(DuckType.GOLDEN))
                                elif level >= 2 and random.random() < 0.3:
                                    ducks.append(Duck(DuckType.FAST))
                                elif level >= 2 and random.random() < 0.3:
                                    ducks.append(Duck(DuckType.ARMORED))
                                else:
                                    ducks.append(Duck(DuckType.NORMAL))
                        
                        # Remove projectile after hit
                        if proj in projectiles:
                            projectiles.remove(proj)
                        break
                
                # Remove projectiles that are out of bounds
                if proj in projectiles and proj.is_out_of_bounds():
                    projectiles.remove(proj)
            
            # Update power-ups
            for powerup in powerups[:]:
                powerup.update()
                powerup.draw(screen)
                
                # Check for collision with player's crosshair
                if powerup.get_rect().collidepoint(player.x, player.y):
                    powerup_type, duration = powerup.activate()
                    player.activate_powerup(powerup_type, duration)
                    powerups.remove(powerup)
                
                # Remove power-ups that are out of bounds
                if powerup.is_out_of_bounds():
                    powerups.remove(powerup)
            
            # Draw player
            player.draw(screen)
            
            # Draw UI
            ui.draw_hud(screen, score, player, level, ducks_killed, ducks_needed_for_next_level, time_remaining)
        
        elif game_state == GameState.GAME_OVER:
            restart_button, menu_button = ui.draw_game_over(screen, score)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if restart_button.collidepoint(mouse_pos):
                        player, ducks, projectiles, powerups, ui, powerup_timer, game_timer = init_game()
                    elif menu_button.collidepoint(mouse_pos):
                        game_state = GameState.MENU
        
        elif game_state == GameState.PAUSED:
            resume_button, menu_button = ui.draw_pause_menu(screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameState.PLAYING
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if resume_button.collidepoint(mouse_pos):
                        game_state = GameState.PLAYING
                    elif menu_button.collidepoint(mouse_pos):
                        game_state = GameState.MENU
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()