import pygame
import sys
import os
import asyncio

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
PLAYER_SPEED = 4
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cute Cat")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)

DIALOGUE_BG = (50, 50, 50, 200)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

def load_image(path):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

cat_anim = [
    load_image(os.path.join("assets", "Cat", "idle.png")),
    load_image(os.path.join("assets", "Cat", "0.png")),
    load_image(os.path.join("assets", "Cat", "1.png"))
]

cat_food = [
    load_image(os.path.join("assets", "catfood0.png")),
    load_image(os.path.join("assets", "catfood1.png"))
]

collectible_images = {
    'fish': cat_food[0],
    'fishbone': load_image(os.path.join("assets", "fishbone.png")),
    'dogbone': load_image(os.path.join("assets", "dogbone.png")),
    'chicken': load_image(os.path.join("assets", "chickenfood.png"))
}

tile_images = {
    'X': load_image(os.path.join("assets", "map", "wall.png")),
    'W': load_image(os.path.join("assets", "map", "water.png")),
    'I': load_image(os.path.join("assets", "map", "ice.png")),
    'P': load_image(os.path.join("assets", "map", "path.png"))
}

MAZE = [
    "XXXXXXXXXXXXXXXXXXXXXXXXX",
    "XPPPPPPPPPPPPXXXPPPPPPPPX",
    "XPPPPPIIIIIXPXPPPPPPPPPPX",
    "XPPPPPXPPPPXPXXPPXXXPPPXX",
    "XWPPPXXPPPPXPXXPPPPPPPPPX",
    "XWPPPXXPPPPXPPPPPPPPPPPPX",
    "XWWWWWWWWPPXPPPPPPPPPPPPX",
    "XPPPPPPPPPPXPPWPWWWPPPPPX",
    "XPPPPPPPPPPXPPWPPPPPPPPPX",
    "XPPPPPPPPPPXPPWPPXXXXPPPXX",
    "XPPPPPPPPPPXPPPPPPPPPPPPX",
    "XIIIIIIIIIXPPPPPPPPXXXPPX",
    "XXXXXXXXXXXXXXXXXXXXXXXXX",
]

class Player:
    def __init__(self):
        self.rect = pygame.Rect(3*TILE_SIZE, 1*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1)
        self.anim_index = 0
        self.anim_timer = 0
        self.facing_left = False
        self.inventory = {
            'fish': 0,
            'fishbone': 0,
            'dogbone': 0,
            'chicken': 0
        }

    def draw(self, screen):
        current_image = cat_anim[self.anim_index]
        if self.facing_left:
            current_image = pygame.transform.flip(current_image, True, False)
        screen.blit(current_image, self.rect.topleft)

class NPC:
    def __init__(self, x, y, image_path, npc_type):
        self.rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1)
        self.image = load_image(image_path)
        self.dialogue_state = 0
        self.quest_complete = False
        self.npc_type = npc_type
        
        if npc_type == "pitbull":
            self.dialogues = {
                0: {
                    "text": ["Woof! Hey cat!", "I need help collecting fish bones."],
                    "options": ["Tell me more", "Not now"],
                    "next": [1, None],
                    "required": {"fishbone": 3}
                },
                1: {
                    "text": ["I need 3 fish bones.", "Can you help me find them?"],
                    "options": ["I'll help", "Maybe later"],
                    "next": [2, None]
                },
                2: {
                    "text": ["Great! Look around the map.", "They're scattered everywhere!"],
                    "options": ["Got it!", "Wait..."],
                    "next": [None, None]
                }
            }
        elif npc_type == "poodle":
            self.dialogues = {
                0: {
                    "text": ["Hello kitty!", "Could you find some dog bones for me?"],
                    "options": ["Sure!", "Not now"],
                    "next": [1, None],
                    "required": {"dogbone": 2}
                },
                1: {
                    "text": ["I need 2 dog bones.", "They're somewhere around here."],
                    "options": ["I'll look", "Later"],
                    "next": [2, None]
                },
                2: {
                    "text": ["Thank you! Happy hunting!", "Be careful near the water!"],
                    "options": ["Will do!", "Okay"],
                    "next": [None, None]
                }
            }
        elif npc_type == "chick":
            self.dialogues = {
                0: {
                    "text": ["Cheep cheep!", "Have you seen my chicken feed?"],
                    "options": ["I can help!", "Not now"],
                    "next": [1, None],
                    "required": {"chicken": 4}
                },
                1: {
                    "text": ["I need 4 bags of feed.", "The wind scattered them!"],
                    "options": ["I'll find them", "Maybe later"],
                    "next": [2, None]
                },
                2: {
                    "text": ["You're so kind!", "I'll wait here."],
                    "options": ["No problem!", "See you soon"],
                    "next": [None, None]
                }
            }

    def interact(self, player_inventory):
        if pygame.Rect.colliderect(self.rect.inflate(TILE_SIZE*2, TILE_SIZE*2), player.rect):
            if not self.quest_complete:
                current_dialogue = self.dialogues.get(0)
                if current_dialogue and "required" in current_dialogue:
                    required_items = current_dialogue["required"]
                    for item, amount in required_items.items():
                        if player_inventory[item] >= amount:
                            self.quest_complete = True
                            self.dialogue_state = 3
                            self.dialogues[3] = {
                                "text": [f"You found all the {item}s!", "Thank you so much!"],
                                "options": ["You're welcome!", "No problem!"],
                                "next": [None, None]
                            }
            return True
        return False

class Collectible:
    def __init__(self, x, y, item_type):
        self.rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1)
        self.item_type = item_type
        self.image = collectible_images[item_type]

def check_collision(rect):
    left = rect.left // TILE_SIZE
    right = rect.right // TILE_SIZE
    top = rect.top // TILE_SIZE
    bottom = rect.bottom // TILE_SIZE
    
    for y in range(top, bottom+1):
        for x in range(left, right+1):
            if 0 <= y < len(MAZE) and 0 <= x < len(MAZE[y]):
                if MAZE[y][x] in ['X', 'W']:
                    return True
    return False

def handle_dialogue(key):
    global in_dialogue, selected_option, current_npc
    current_dialogue = current_npc.dialogues.get(current_npc.dialogue_state)
    if not current_dialogue:
        in_dialogue = False
        return

    if key == pygame.K_UP:
        selected_option = 0
    elif key == pygame.K_DOWN:
        selected_option = 1
    elif key == pygame.K_RETURN:
        next_state = current_dialogue["next"][selected_option]
        if next_state is not None:
            current_npc.dialogue_state = next_state
        else:
            in_dialogue = False

def draw_dialogue():
    current_dialogue = current_npc.dialogues.get(current_npc.dialogue_state)
    if not current_dialogue:
        return

    dialogue_height = 200
    dialogue_surface = pygame.Surface((SCREEN_WIDTH, dialogue_height), pygame.SRCALPHA)
    dialogue_surface.fill((0, 0, 0, 180))
    
    y_offset = 20
    for line in current_dialogue["text"]:
        text = font.render(line, True, WHITE)
        dialogue_surface.blit(text, (20, y_offset))
        y_offset += 40
    
    for i, option in enumerate(current_dialogue["options"]):
        color = GREEN if i == selected_option else WHITE
        text = font.render(f"{'>' if i == selected_option else ' '} {option}", True, color)
        dialogue_surface.blit(text, (20, y_offset + i*40))
    
    screen.blit(dialogue_surface, (0, SCREEN_HEIGHT - dialogue_height))

def draw_inventory():
    inventory_text = [
        f"Fish Bones: {player.inventory['fishbone']}",
        f"Dog Bones: {player.inventory['dogbone']}",
        f"Chicken Feed: {player.inventory['chicken']}"
    ]
    for i, text in enumerate(inventory_text):
        text_surface = font.render(text, True, WHITE)
        screen.blit(text_surface, (10, 10 + i*30))

player = Player()
npcs = [
    NPC(15, 7, os.path.join("assets", "pitbull.png"), "pitbull"),
    NPC(8, 3, os.path.join("assets", "poodle.png"), "poodle"),
    NPC(18, 10, os.path.join("assets", "chick.png"), "chick")
]

collectibles = [
    Collectible(5, 3, "fishbone"),
    Collectible(8, 7, "fishbone"),
    Collectible(12, 5, "fishbone"),
    Collectible(14, 2, "dogbone"),
    Collectible(17, 8, "dogbone"),
    Collectible(6, 9, "chicken"),
    Collectible(10, 4, "chicken"),
    Collectible(13, 6, "chicken"),
    Collectible(16, 3, "chicken")
]

in_dialogue = False
selected_option = 0
current_npc = None

os.environ['SDL_VIDEO_CENTERED'] = '1'

async def main():
    while True:
        await asyncio.sleep(0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_e:
                    for npc in npcs:
                        if npc.interact(player.inventory):
                            global in_dialogue, selected_option, current_npc
                            in_dialogue = True
                            selected_option = 0
                            current_npc = npc
                            break
                elif in_dialogue:
                    handle_dialogue(event.key)

        if not in_dialogue:
            dx, dy = 0, 0
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -PLAYER_SPEED
                player.facing_left = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = PLAYER_SPEED
                player.facing_left = False
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = PLAYER_SPEED

            if dx != 0 or dy != 0:
                player.anim_timer += 1
                if player.anim_timer % 10 == 0:
                    player.anim_index = 2 if player.anim_index == 1 else 1
            else:
                player.anim_index = 0

            if dx != 0 or dy != 0:
                player.rect.x += dx
                if check_collision(player.rect):
                    player.rect.x -= dx
                
                player.rect.y += dy
                if check_collision(player.rect):
                    player.rect.y -= dy

        for collectible in collectibles[:]:
            if player.rect.colliderect(collectible.rect):
                player.inventory[collectible.item_type] += 1
                collectibles.remove(collectible)

        screen.fill(BLACK)
        
        for y, row in enumerate(MAZE):
            for x, char in enumerate(row):
                if char in tile_images:
                    screen.blit(tile_images[char], (x*TILE_SIZE, y*TILE_SIZE))
        
        for collectible in collectibles:
            screen.blit(collectible.image, collectible.rect)
        
        player.draw(screen)
        for npc in npcs:
            screen.blit(npc.image, npc.rect)
        
        draw_inventory()
        if in_dialogue:
            draw_dialogue()

        pygame.display.flip()
        clock.tick(60)

asyncio.run(main())