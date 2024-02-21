import pygame, sys, random, os, math, platform

from pygame.version import PygameVersion

class Player(pygame.sprite.Sprite):
	velocity = 0 # Used for movement
	speed = 3 # Speed the player can move
	is_dead = False
	base_images = [pygame.image.load("Textures/Player.png"), pygame.image.load("Textures/PlayerWalk1.png"), pygame.image.load("Textures/PlayerWalk2.png"), pygame.image.load("Textures/PlayerDead.png")]
	animation = 0
	flipped = False

	floor_position: int

	def __init__(self): # The __init()__ function is called when the object is first created
		super().__init__() # This wierd looking line just calls the __init()__ function on the parent class (in this case pygame.sprite.Sprite)
		#                    It lets us work with sprite attributes, such as image or rect.

		self.image = self.base_images[0] # Scaling the image & applying it to the sprite
		self.rect = self.image.get_rect() # Getting a rect from the image. This allows the sprite to be positioned, and check for collisions
		self.rect.x = 100
		self.floor_position = screen_height - self.rect.height - 16
		self.rect.y = self.floor_position

	def update(self, *args, **kwargs):
		# Move the player
		if not self.is_dead:
			self.rect.x += self.velocity

		# Making sure the player stays within the screen edges
		if not self.rect.x <= screen_width - self.rect.width:
			self.rect.x = screen_width - self.rect.width
		elif not self.rect.x >= 0:
			self.rect.x = 0

		if not self.is_dead:
			if self.velocity < 0:
				self.flipped = True
			elif self.velocity > 0:
				self.flipped = False

		if frame % 10 == 0 and not self.velocity == 0 and not self.is_dead:
			self.animation += 1

			foot_step = pygame.mixer.Sound(random.choice(["Sounds/FootStep.wav"]))
			foot_step.set_volume(random.uniform(0.15, 0.25))
			foot_step.play()

			if self.animation > 2:
				self.animation = 1
		elif self.is_dead:
			self.animation = 3
		elif self.velocity == 0:
			self.animation = 0

		self.image = pygame.transform.flip(self.base_images[self.animation], self.flipped, False)

	def die(self):
		global frame, high_score
		pygame.mixer.Sound("Sounds/Death.wav").play()

		for i in range(random.randrange(6, 11)):
			blood = Particle(
				image="Textures/Blood.png",
				x_pos=int((self.rect.x + self.rect.width / 2) + random.randrange(-6, 6)),
				y_pos=int((self.rect.y + self.rect.height / 2) + random.randrange(-4, 0)),
				x_speed=random.choice([-1, 1,]),
				y_speed=random.uniform(-3.0, -1.0),
				persistant=True
			)
			game.particles.add(blood)

		if self.is_dead:
			if self.rect.y < self.floor_position + 3:
				self.rect.y += 1
			return

		self.is_dead = True
		menus.append("death")

		frame = 1
		game.show_died_text = True

		if game.score > high_score:
			high_score = game.score

			print("--- SAVING DATA ---")
			if not os.path.exists(save_data_path):
				os.makedirs(save_data_path)
				print(f"Created dir at {save_data_path}")

			print(f"Found directory at {save_data_path}, writing save file...")

			with open(f"{save_data_path}highscore.txt", "w") as file:
				file.write(str(high_score))

				print(f"Saved high score of {high_score} to {save_data_path}highscore.txt")

			game.show_new_high_score_text =  True


class Pillar(pygame.sprite.Sprite):
	move_direction = 1 # Dictates if the pillar is moving up or down. 1 == up, -1 == down
	upper_limit: int # The y position where the pillar is just barely not visible off the top of the screen.
					 # Gets defined in __init__()
	speed = 5 # Move speed
	has_hit_player = False

	def __init__(self, position: int):
		super().__init__()
		global show_warning

		self.image = pygame.image.load("Textures/Boot1.png")
		self.rect = self.image.get_rect()
		rect_x_positions = [0, 64, 64*2, 64*3, 64*4]
		self.rect.x = rect_x_positions[position]
		self.upper_limit = -self.image.get_height() # Define upper limit
		self.rect.y = round(self.upper_limit * random.uniform(1.5, 2.0))

		show_warning = True

	def update(self, *args, **kwargs):
		global show_warning

		self.rect.y += self.move_direction * self.speed # Move the pillar up or down, dependent on the current move direction

		if not self.rect.y <= self.upper_limit:
				show_warning = False

		if show_warning:
			main_screen.blit(pygame.image.load("Textures/Warning.png"), (self.rect.x, 18))

		if self.rect.y >= -16 and self.move_direction == 1: # Change move direction to be up (-1) when the pillar reaches the ground
			self.rect.y = -16
			self.move_direction = -1

			pygame.mixer.Sound(random.choice(["Sounds/Stomp.wav", "Sounds/Stomp1.wav"])).play()
			screen_shake.shake()

			for i in range(random.randrange(7, 13)):
				pebble = Particle(
					image="Textures/Pebble.png",
					x_pos=int((self.rect.x + self.rect.width / 2) + random.randrange(-32, 32)),
					y_pos=int(self.rect.height - 17 + random.randrange(-6, 0)),
					x_speed=random.choice([-1, 1,]),
					y_speed=random.uniform(-4.0, -2.0),
					persistant=False
				)
				game.particles.add(pebble)

		elif self.rect.y <= self.upper_limit and self.move_direction == -1: # Delete this pillar when it comes back up from the ground
			self.kill()

		# Detect for collisions with the player
		# Currently, the player just gets deleted when this happens.
		if self.rect.colliderect(game.player.rect) and not self.has_hit_player and self.move_direction == 1:
			game.player.die()
			self.has_hit_player = True


class Particle(pygame.sprite.Sprite):
	x_speed: float
	y_speed: float
	persistant: bool

	def __init__(self, image: str, x_pos: int, y_pos: int, x_speed: int, y_speed: float, persistant: bool):
		super().__init__()

		self.image = pygame.image.load(image)
		self.rect = self.image.get_rect()
		self.rect.x = x_pos
		self.rect.y = y_pos

		self.x_speed = x_speed
		self.y_speed = y_speed
		self.persistant = persistant

	def update(self, *args, **kwargs):
		if self.rect.y >= screen_height - 18:
			if self.persistant:
				self.rect.y = screen_height - 18
			else:
				self.kill()

			return

		self.rect.x += int(self.x_speed)
		self.rect.y += int(self.y_speed)

		self.y_speed += 0.1

		if int(self.y_speed) == 0:
			self.y_speed = 1


class ScreenShake():
	strength: int
	length: int
	speed: int
	shake_timer = 99999

	x_shake = 0
	y_shake = 0

	def __init__(self, strength: int, length: int, speed: int):
		self.strength = strength
		self.length = length
		self.speed = speed

	def tick(self):
		if self.shake_timer <= self.length:
			if frame / self.speed == round(frame / self.speed):
				self.x_shake = random.choice([-self.strength, self.strength])
				self.y_shake = random.choice([-self.strength, self.strength])

			self.shake_timer += 1
		else:
			self.x_shake = 0
			self.y_shake = 0

	def shake(self):
		self.shake_timer = 0


class Button(pygame.sprite.Sprite):
	label = None
	label_rect = None
	texture = None
	hover_texture = None
	press_texture = None

	just_pressed = False

	def __init__(self, label: str, texture: str, hover_texture: str, press_texture: str, position: tuple):
		super().__init__()

		self.label = font.render(label, False, (0, 0, 0))
		self.label_rect = self.label.get_rect()

		self.texture = pygame.image.load(texture)
		self.hover_texture = pygame.image.load(hover_texture)
		self.press_texture = pygame.image.load(press_texture)

		self.image = self.texture
		self.rect = self.image.get_rect()

		self.rect.x = position[0]
		self.rect.y = position[1]

	def is_mouse_in_bounds(self):
		if (self.rect.x <= mouse_x <= self.rect.x + self.rect.width) and (self.rect.y <= mouse_y <= self.rect.y + self.rect.height):
			return True
		else:
			return False

	def update(self, *args, **kwargs):
		global mouse_just_up

		self.just_pressed = False
		self.image = self.texture

		if self.is_mouse_in_bounds():
			if mouse_down:
				self.image = self.press_texture
			else:
				self.image = self.hover_texture

			if mouse_just_up:
				self.just_pressed = True
				mouse_just_up = False

				select = pygame.mixer.Sound("Sounds/Select.wav")
				select.set_volume(0.6)
				select.play()


		self.image.blit(self.label, (self.rect.width / 2 - self.label_rect.width / 2, -2))


class GameState():
	def reset(self):
		self.level_change_timer = 0
		self.current_level = 0
		self.pillar_spawn_timer = 0

		self.show_warning = False # Part of the logic that decides when to show the exclamation marks on the top of the screen.

		# Sprites & sprite groups
		# All sprites must be part of some group so they can be drawn with <group>.draw(screen)
		# If you only intend to have one sprite in a group, use a GroupSingle() instead of a Group()
		self.player = Player()

		self.player_group = pygame.sprite.GroupSingle()
		self.player_group.add(self.player)

		self.pillars = pygame.sprite.Group()

		self.particles = pygame.sprite.Group()

		self.score = -10

		self.show_died_text = False

		self.show_new_high_score_text = False


def generate_pillars():

	if not game.player.is_dead:
		game.score += 10

	# Minimum amount of pillars to spawn
	min_pillars = level_attrubutes[game.current_level][1]
	# Max amount of pillars to spawn
	max_pillars = level_attrubutes[game.current_level][2]

	# Setup empty list of pillars
	pillars_positions = [False, False, False, False, False]

	# There is a one-in-3 change to spawn a pillar directly above the player
	player_grid_pos = math.floor(game.player.rect.x / 64)
	if random.randrange(0, 3) == 0:
		pillars_positions[player_grid_pos] = True
		game.pillars.add(Pillar(position=player_grid_pos))

	# Makes it so an extra pillar is not spawned if one was placed above the player
	pillar_amount = random.randrange(min_pillars, max_pillars + 1)
	if len(game.pillars.sprites()) > 0:
		if pillar_amount == 1:
			return

		pillar_amount -= 1

	# Place pillars in random spots
	for i in range(pillar_amount):
		pillar_pos = random.randrange(0, 5)

		# Select a new position until the selected position is not already filled
		while pillars_positions[pillar_pos]:
			pillar_pos = random.randrange(0, 5)

		pillars_positions[pillar_pos] = True
		game.pillars.add(Pillar(position=pillar_pos))


pygame.init()
pygame.mixer.init()

main_screen = pygame.Surface((320, 180)) # The surface to put all graphics on, aspect ratio is 16:9
resizing_screen = pygame.Surface((320, 180)) # To resize the screen, the main_screen is blitted onto here, and then this is resized and blitted onto the window.

window_display = pygame.Window(title="STOMP!", size=(640, 360), resizable=True, allow_high_dpi=True)
window = window_display.get_surface()
is_fullscreen = False
clock = pygame.time.Clock() # Used for setting a constant frame rate

mouse_pos_division = 0

background_color = [25, 40, 25]
background_image = pygame.image.load("Textures/GreenBg.png")
main_menu_bg_y = 0
main_menu_bg_y_change_direction = 1
screen_width = main_screen.get_width()
screen_height = main_screen.get_height()

# Get the path for save data
save_data_path = "~/hwGames/Stomp/" # save data will be put directly into the user folder if the user's system cannot be determined
if platform.system() == "Darwin": # "Darwin" indicates the system is MacOS
	save_data_path = os.path.expanduser("~/Library/hwGames/Stomp/") # This just expands "~" into an absolute path for the user's home directory
	window_display.set_icon(pygame.image.load("Textures/Icons/Mac.png"))
elif platform.system() == "Windows": # Obviously "Windows" indicates the system is, well, windows (duh)
	save_data_path = os.path.expanduser("~\\AppData\\Local\\hwGames\\Stomp\\")
	window_display.set_icon(pygame.image.load("Textures/Icons/Windows.png"))

print("--- LOADING DATA ---")
# Open the high score file in read mode ('r')
if os.path.exists(f"{save_data_path}highscore.txt"):
	with open(f"{save_data_path}highscore.txt", "r") as file:
		# Read the entire content of the file
		high_score = int(file.read())
		print(f"Read high score from {save_data_path}highscore.txt as {high_score}")
else:
	high_score = 0 # The player's high score
	print("No save data found, high score set to 0")

level_attrubutes = [ # Attrubutes of each level, listed in the format [time between pillar spawns, min amount of pillars per spawn, max amount of pillars per spawn]
	[150, 1, 2],
	[140, 1, 2],
	[140, 1, 3],
	[130, 1, 3],
	[130, 1, 4],
	[120, 1, 4],
	[110, 2, 4],
	[110, 3, 4],
	[110, 4, 4],
	[100, 4, 4],
	[90, 4, 4],
	[80, 4, 4]
]
time_between_levels = 1200 # Amount of frames before changing levels. Levels indicate how many pillars can spawn at once, and how often.

font = pygame.font.Font("PixelCowboy.ttf", 16)

mouse_x = 0
mouse_y = 0
mouse_down = False
mouse_just_down = False
mouse_just_up = True

# Tells the game which menus to render
# game -> playing the game
# death -> death screen
# menu -> main menu screen
menus = ["menu"]

# Sprites & sprite groups
# All sprites must be part of some group so they can be drawn with <group>.draw(screen)
# If you only intend to have one sprite in a group, use a GroupSingle() instead of a Group()
button_width = pygame.image.load("Textures/Button.png").get_width()
button_height = pygame.image.load("Textures/Button.png").get_height()

respawn_button = Button(
	label="Retry",
	texture="Textures/Button.png",
	hover_texture="Textures/ButtonHover.png",
	press_texture="Textures/ButtonPress.png",
	position=(screen_width / 2 - button_width / 2, screen_height / 2 - button_height / 2 - 10)
)

back_to_menu_button = Button(
	label="Main Menu",
	texture="Textures/Button.png",
	hover_texture="Textures/ButtonHover.png",
	press_texture="Textures/ButtonPress.png",
	position=(screen_width / 2 - button_width / 2, screen_height / 2 - button_height / 2 + 10)
)

death_screen = pygame.sprite.Group()
death_screen.add(respawn_button)
death_screen.add(back_to_menu_button)

death_screen_bg = pygame.image.load("Textures/DeathScreenBg.png")

start_button = Button(
	label="Play!",
	texture="Textures/Button.png",
	hover_texture="Textures/ButtonHover.png",
	press_texture="Textures/ButtonPress.png",
	position=(screen_width / 2 - button_width / 2, screen_height / 2 - button_height / 2 + 55)
)

quit_button = Button(
	label="Quit Game",
	texture="Textures/Button.png",
	hover_texture="Textures/ButtonHover.png",
	press_texture="Textures/ButtonPress.png",
	position=(screen_width / 2 - button_width / 2, screen_height / 2 - button_height / 2 + 75)
)

main_menu = pygame.sprite.Group()
main_menu.add(start_button)
main_menu.add(quit_button)

logo = pygame.image.load("Textures/Logo.png")

# GAME STATE OBJECT
game = GameState()
game.reset()

frame = 0

# Init screenshake object
screen_shake = ScreenShake(strength=1, length=10, speed=2)

while True:
	mouse_just_down = False
	mouse_just_up = False

	# Main event loop
	for event in pygame.event.get():
		# Check for window getting closed
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

		# Check for keys getting pushed down
		if event.type == pygame.KEYDOWN:
			# Player movement
			if event.key == pygame.K_a:
				game.player.velocity -= game.player.speed
			elif event.key == pygame.K_d:
				game.player.velocity += game.player.speed
			elif event.key == pygame.K_F11:
				if is_fullscreen:
					window_display.set_windowed()
					is_fullscreen = False
				else:
					window_display.set_fullscreen()
					is_fullscreen = True

		# Check for keys getting unpushed
		if event.type == pygame.KEYUP:
			# Player movement
			if event.key == pygame.K_a:
				game.player.velocity += game.player.speed
			elif event.key == pygame.K_d:
				game.player.velocity -= game.player.speed

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == pygame.BUTTON_LEFT:
				mouse_down = True
				mouse_just_down = True

		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == pygame.BUTTON_LEFT:
				mouse_down = False
				mouse_just_up = True

	main_screen.fill(background_color) # Fills the background in

	if "game" in menus:
		main_screen.blit(background_image, (0, 0))

		# Update & render the player
		game.player_group.update()
		game.player_group.draw(main_screen)

		game.pillars.update()
		game.pillars.draw(main_screen)

		# Pillar spawning logic
		game.pillar_spawn_timer += 1
		game.level_change_timer += 1

		# Changing level
		if game.level_change_timer >= time_between_levels:
			if not game.current_level == len(level_attrubutes) - 1:
				game.current_level += 1

			game.level_change_timer = 0

		# Spawning a group of pillars
		if game.pillar_spawn_timer >= level_attrubutes[game.current_level][0]:
			if len(game.pillars.sprites()) == 0:
				generate_pillars()
				game.pillar_spawn_timer = 0

				pygame.mixer.Sound("Sounds/Spawn.wav").play()

		# Particle rendering & updating
		game.particles.update()
		game.particles.draw(main_screen)

		# Tick screen shake
		screen_shake.tick()

		# Render ground texture
		resizing_screen.blit(pygame.image.load("Textures/Bg.png"), (0, 0))
		main_screen.blit(pygame.image.load("Textures/Bg.png"), (0, 0))


	# Blit the screen onto the resizable surface
	resizing_screen.blit(main_screen, (0, 0))
	resizing_screen.blit(main_screen, (screen_shake.x_shake, screen_shake.y_shake))

	if "game" in menus:
		if game.show_died_text:
			text = "GAME OVER"
		elif game.score >= 0:
			text = f"Score: {game.score}"
		else:
			text = "Score: 0"

		if game.player.is_dead:
			color = (214, 43, 36)
		else:
			color = (255, 255, 255)

		score_text = font.render(text, False, color)
		resizing_screen.blit(score_text, (screen_width / 2 - score_text.get_width() / 2, 0))

		if game.show_new_high_score_text:
			new_high_score_text = font.render("New High Score!", False, (255, 255, 255))
			resizing_screen.blit(new_high_score_text, (screen_width / 2 - new_high_score_text.get_width() / 2, 16))

		if frame % 60 == 0 and game.player.is_dead:
			if game.show_died_text:
				game.show_died_text = False
			else:
				game.show_died_text = True

	if "death" in menus:
		resizing_screen.blit(death_screen_bg, (screen_width / 2 - death_screen_bg.get_width() / 2, screen_height / 2 - death_screen_bg.get_height() / 2))
		main_screen.blit(background_image, (0, 0))

		# Check for button input
		death_screen.update()
		death_screen.draw(resizing_screen)

		if respawn_button.just_pressed:
			menus = ["game"]
			game.reset()

			frame = 0

		if back_to_menu_button.just_pressed:
			menus = ["menu"]

			frame = 0

	if "menu" in menus:
		if frame % 30 == 0:
			main_menu_bg_y += main_menu_bg_y_change_direction

			if main_menu_bg_y == 0:
				main_menu_bg_y_change_direction = 1
			elif main_menu_bg_y == 6:
				main_menu_bg_y_change_direction = -1

		resizing_screen.blit(background_image, (0, main_menu_bg_y))
		resizing_screen.blit(logo, (screen_width / 2 - logo.get_width() / 2, screen_height / 2 - logo.get_height() + 15))

		# Check for button input
		main_menu.update()
		main_menu.draw(resizing_screen)

		if start_button.just_pressed:
			menus = ["game"]
			game.reset()

			frame = 0

		if quit_button.just_pressed:
			pygame.quit()
			sys.exit()

		# Render high score text
		score_text = font.render(f"High Score: {high_score}", False, (255, 255, 255))
		resizing_screen.blit(score_text, (screen_width / 2 - score_text.get_width() / 2, 107))

	# Resize the window properly
	window.fill([0, 0, 0])
	screen_scaled = None

	if window.get_height() * (16 / 9) < window.get_width():
		screen_scaled = pygame.transform.scale(resizing_screen, [window.get_height() * (16 / 9), window.get_height()])
	else:
		screen_scaled = pygame.transform.scale(resizing_screen, [window.get_width(), window.get_width() * (9 / 16)])

	screen_position = ((window.get_width() - screen_scaled.get_width()) / 2, (window.get_height() - screen_scaled.get_height()) / 2)

	window.blit(screen_scaled, screen_position)

	# On hidpi displays, some values need to be divided by 2 when calculating relative mouse positions.
	# This code finds out wether or not the user is using a hidpi display, and sets the division value accordingly.
	# This only ever gets called on the first iteration of the game loop.
	if mouse_pos_division == 0:
		x_ratio_test = screen_scaled.get_width() / screen_width / 2
		mouse_x_test = (639 - screen_position[0] / 2) / x_ratio_test

		if mouse_x_test == 639:
			mouse_pos_division = 1
		else:
			mouse_pos_division = 2

	# Calculate relative mouse position
	x_ratio = screen_scaled.get_width() / screen_width / mouse_pos_division
	y_ratio = screen_scaled.get_height() / screen_height / mouse_pos_division
	mouse_x = (pygame.mouse.get_pos()[0] - screen_position[0] / mouse_pos_division) / x_ratio
	mouse_y = (pygame.mouse.get_pos()[1] - screen_position[1] / mouse_pos_division) / y_ratio

	# Refresh the window at a rate of 60hz
	frame += 1
	if frame > 999999: # Just to make sure the frame val doesn't get too high, and excede the integer limit or something silly like that
		frame = 0

	window_display.flip()
	clock.tick(60)
