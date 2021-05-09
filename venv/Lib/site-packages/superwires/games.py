#########################################################################
#Copyright 2013 Akif Patel
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
###########################################################################

"""Rewriting of the graphics lib in 'Python for the Absolute Beginner' book."""

import pygame
import pygame.locals
import time


screen=None
mouse=None
keyboard=None
music=None

for i in dir(pygame):
	if i.startswith('K_'):
		globals()[i]=getattr(pygame, i)

class Mouse(object):
	"""A class for controlling the mouse.

	Usually used via calls to games.init() and module variable games.mouse.

	Attributes:
		x: The x position of the mouse.
		y: The y position of the mouse.
		position: A two-element tuple containing the x and y position.
		is_visible: Whether or not mouse cursor is visible.
	"""

	def __init__(self):
		"""Initializes mouse. Usually not used directly.
		"""
		self._is_visible=True

	def get_x(self):
		return pygame.mouse.get_pos()[0]

	def set_x(self, new_x):
		pygame.mouse.set_pos([self._x, self._y])

	x=property(get_x, set_x)

	def get_y(self):
		return pygame.mouse.get_pos()[1]

	def set_y(self, new_y):
		pygame.mouse.set_pos([self._x, self._y])

	y=property(get_y, set_y)

	def get_position(self):
		return pygame.mouse.get_pos()

	def set_position(self, new_position):
		pygame.mouse.set_pos(new_position)

	position=property(get_position, set_position)

	def get_is_visible(self):
		return self._is_visible

	def set_is_visible(self, new_visibility):
		self._is_visible=new_visibility
		pygame.mouse.set_visible(self._is_visible)

	is_visible=property(get_is_visible, set_is_visible)

	def is_pressed(self, button_num):
		"""Tells if given key is pressed.

		Args:
			button_num: The button being checked to see if it is pressed.
				It's values are 0 to 2.

		Returns:
			Boolean representing whether button is pressed
		"""
		return pygame.mouse.get_pressed()[button_num]

class Keyboard(object):
	"""A class to check key states with the keyboard.

	Similar to Mouse object, this is not used directly, but via module variable
	games.keyboard and calls to games.init().
	"""
	
	def __init__(self):
		self._keys=[]
	
	def get_keys(self):
		if not screen.virtual:
			self._keys=filter(self.is_pressed, [globals()[i] for i in globals() if i.startswith("K_")])
		
		return self._keys
	
	def set_keys(self, keys):
		if not screen.virtual:
			raise AttributeError("Cannot set keys list if not in virtual mode")
		self._keys=keys
		
	keys=property(get_keys, set_keys)
	
	def is_pressed(self, key):
		"""Returns if the given key is pressed. Key constants are listed in this
		module global scope (Check end of pydoc of this module for a complete
		list of key constants)."""

		if not screen.virtual:
			return pygame.key.get_pressed()[key]

class Music(object):
	"""A class to play music in the background.

	Similar to Mouse object, this is not used directly, but via module variable
	games.music and calls to games.init().
	"""

	def load(self, filename):
		"""Loads the music from filename."""
		pygame.mixer.music.load(filename)

	def play(self, loop=0):
		"""Plays the loaded music.

		Args:
			loop: Amount of times to repeat(-1 is forever)
		"""
		pygame.mixer.music.play(loop)

	def fadeout(self, millisec):
		"""Fadesout music in the given amount of milliseconds"""
		pygame.mixer.music.fadeout(millisec)

	def stop(self):
		"""Stops music"""
		pygame.mixer.music.stop()

class Sprite(object):
	"""A Sprite object to put on the screen.

	This class is used to place objects on the screen. You can use this
	directly, make a your own subclass or use one of the subclasses made for
	you:Text, Animation, etc. Position of the object is measured by its
	center (and not its upper-left corner).

	Attributes:
		image: the image that is displayed on the screen. This is the
			image before rotating.
		angle: the amount in degrees to rotate the image.
		x: The x position of the center of the sprite.
			The x value increases moving left to right on the screen.
		y: The y position of the center of the sprite.
			The y value increases moving TOP TO BOTTOM (and not bottom to top
			as in the cartesian co-ordinate system).
		top: The y position of the top edge of the sprite.
		bottom: The y position of the bottom edge of the sprite.
		left: The x position of the left edge of the sprite.
		right: The x position of the right edge of the sprite.
		position: A two-element tuple with the x and y position of the (center
			of the) sprite.
		dx: delta x is the x velocity of the sprite.
		dy: delta y is the y velocity of the sprite.
		velocity: A two-element tuple containing the dx and dy of the sprite.
		is_collideable: Whether or not the sprite participates in collisions.
		interval: The number of frames between tick() calls.
	"""

	def __init__(self, image, angle=0, x=0, y=0, top=None,
				 bottom=None, left=None, right=None, dx=0,
				 dy=0, interval=1, is_collideable=True):
		"""Initializes Sprite with given parameters.

		Args:
			image: The image to display.
			angle: The angle to rotate by.
			x: The center x to place the sprite on.
			y: The center y to place the sprite on.
			top: The y location of the top of the sprite.
			bottom: The y location of the bottom of the sprite.
			left: The x location of the left of the sprite.
			right: The x location of  right of the sprite.
			dx: The x velocity (Delta x).
			dy: The y velocity (delta y).
			interval: The number of frames between tick() calls.
			is_collideable: Whether or not the sprite participates in collisions.
		"""

		self._angle=0
		self._x=0
		self._y=0

		self._image=image
		self.interval=interval
		self.tick_timer=interval
		self.angle=angle

		if left:
			self.left=left
		elif right:
			self.right=right
		elif x:
			self.x=x
		else:
			self.x=0

		if top:
			self.top=top
		elif bottom:
			self.bottom=bottom
		elif y:
			self.y=y
		else:
			self.y=0

		self.dx=dx
		self.dy=dy
		self._overlapping_sprites=[]
		self.is_collideable=is_collideable
		self.screen=None

	def get_image(self):
		return self._image

	def set_image(self, new_image):
		self._image=new_image
		self._rot_image=pygame.transform.rotate(self._image, -self._angle)
		self._rect=self._rot_image.get_rect()
		self._rect.centerx=self._x
		self._rect.centery=self._y

	image=property(get_image, set_image)

	def get_width(self):
		return self._rect.width

	def _set_width(self, new_width):
		raise ValueError("Can't change the width")

	width=property(get_width, _set_width)

	def get_height(self):
		return self._rect.height

	def _set_height(self, new_height):
		raise ValueError("Can't change the height")

	height=property(get_height, _set_height)

	def get_angle(self):
		return self._angle

	def set_angle(self, new_angle):
		self._angle = new_angle % 360
		self._rot_image = pygame.transform.rotate(self._image, -self._angle)
		self._rect = self._rot_image.get_rect()
		self._rect.centerx = self._x
		self._rect.centery = self._y

	angle=property(get_angle, set_angle)

	def get_x(self):
		return self._x

	def set_x(self, new_x):
		self._x=new_x
		self._rect.centerx=new_x

	x=property(get_x, set_x)

	def get_y(self):
		return self._y

	def set_y(self, new_y):
		self._y=new_y
		self._rect.centery=new_y

	y=property(get_y, set_y)

	def get_position(self):
		return (self._x, self._y)

	def set_position(self, new_position):
		self.x=new_position[0]
		self.y=new_position[1]

	position=property(get_position, set_position)

	def get_top(self):
		return self._rect.top

	def set_top(self, new_top):
		self._rect.top=new_top
		self._y=self._rect.centery

	top=property(get_top, set_top)

	def get_bottom(self):
		return self._rect.bottom

	def set_bottom(self, new_bottom):
		self._rect.bottom=new_bottom
		self._y=self._rect.centery

	bottom=property(get_bottom, set_bottom)

	def get_left(self):
		return self._rect.left

	def set_left(self, new_left):
		self._rect.left=new_left
		self._x=self._rect.centerx

	left=property(get_left, set_left)

	def get_right(self):
		return self._rect.right

	def set_right(self, new_right):
		self._rect.right=new_right
		self._x=self._rect.centerx

	right=property(get_right, set_right)

	def get_dx(self):
		return self._dx

	def set_dx(self, new_dx):
		self._dx=new_dx

	dx=property(get_dx, set_dx)

	def get_dy(self):
		return self._dy

	def set_dy(self, new_dy):
		self._dy=new_dy

	dy=property(get_dy, set_dy)

	def get_velocity(self):
		return (self._dx, self._dy)

	def set_velocity(self, new_velocity):
		self.dx=new_velocity[0]
		self.dy=new_velocity[1]

	velocity=property(get_velocity, set_velocity)

	def get_overlapping_sprites(self):
		"""Returns list of other sprites overlapping this sprite."""
		self._check_overlap()
		return self._overlapping_sprites
	
	def _set_overlapping_sprites(self, new_list):
		raise ValueError("Can't set overlapping sprites")
	
	overlapping_sprites=property(get_overlapping_sprites, _set_overlapping_sprites)
  
	def overlaps(self, other):
		"""Tells if other sprite overlaps this sprite"""
		return (self._rect.colliderect(other._rect) and self._is_collideable and
				other.is_collideable and (not self is other))

	def get_is_collideable(self):
		return self._is_collideable

	def set_is_collideable(self, new_status):
		self._is_collideable=new_status
		self._check_overlap()

	is_collideable=property(get_is_collideable,
							set_is_collideable)

	def _check_overlap(self):
		self._overlapping_sprites=[]
		if not self.is_collideable:
			return []
		for sprite in screen.all_objects:
			if self.overlaps(sprite):
				self._overlapping_sprites.append(sprite)

	def get_interval(self):
		return self._interval

	def set_interval(self, new_interval):
		self._interval=new_interval
		self.tick_timer=self._interval

	interval=property(get_interval, set_interval)

	def update(self):
		"""A function that is usually overridden.

		This is called every mainloop() cycle and does nothing by default.
		It is overridden in subclasses to do what the user wants.
		"""
		pass

	def tick(self):
		"""Similar to update() but different.

		Serves the exact same purpose as update() except it is called every
		interval frames."""
		pass


	def destroy(self):
		"""Destroys sprite."""
		if self.screen:
			self.screen.remove(self)

	def _move(self):
		self.x+=self.dx
		self.y+=self.dy

	def _draw(self):
		if self.screen:
			self.screen.buffer.blit(self._rot_image, self._rect)
			self.screen.new_dirties.append(self._rect)

	def _process_sprite(self):
		self._check_overlap()
		self._draw()
		self._move()
		self.update()
		self.tick_timer-=1
		if not self.tick_timer:
			self.tick()
			self.tick_timer=self._interval

class Text(Sprite):
	"""A Sprite which displays text.

	A GUI label with all the properties of a sprite.

	Attributes:
		value: The text to display.
		size: The height of the text in pixels.
		color: The color of the text (can be specified by using the color module
			or an RGB tuple)."""

	def __init__(self, value, size, color, angle=0, x=0,
				 y=0, top=None, bottom=None, left=None,
				 right=None, dx=0, dy=0, interval=1,
				 is_collideable=True):
		"""Initializes Text object with given parameters.

		Args:
			value: The text to display.
			size: The height of the text in pixels
			color: The color of the text.
			angle: The angle to rotate the object.
			x: The center x position where the sprite will be placed.
			y: The center y position where the sprite will be placed.
			top: The y location of the top edge of the sprite.
			bottom: The y location of the bottom edge of the sprite.
			left: The x location of the left edge of the sprite.
			right: The x location of  right edge of the sprite.
			dx: delta x is the x velocity of the sprite.
			dy: delta y is the y velocity of the sprite.
			interval: The number of frames between tick() calls.
			is_collideable: Whether or not the sprite participates in collisions.
		"""


		self._size=size
		self._color=color
		self._value=value
		pygame.font.init()
		self.font = pygame.font.Font(None, size)
		Sprite.__init__(self, self.font.render(str(value), 1, color),
						angle, x, y, top, bottom, left,
						right, dx, dy, interval, is_collideable)

	def get_value(self):
		return self._value

	def set_value(self, new_value):
		self._value=new_value
		self._make_image()

	value=property(get_value, set_value)

	def get_size(self):
		return self._size

	def set_size(self, new_size):
		self._size=new_size
		self.font=pygame.font.Font(None, self._size)
		self._make_image()

	size=property(get_size, set_size)

	def get_color(self):
		return self._color

	def set_color(self, new_color):
		self._color=new_color
		self._make_image()

	color=property(get_color, set_color)

	def _make_image(self):
		self.image=self.font.render(str(self._value), 1, self.color)

class Message(Text):
	"""An object that is displayed for a temporary period.

	A text object that disappears in a few frames and calls
	a function as it diappears. Used for things like game over message
	which disappears in few seconds and closes the program as it disappears.
	Can't override tick() as it is already used.
	"""
	def __init__(self, value, size, color, angle=0, x=0,
				 y=0, top=None, bottom=None, left=None,
				 right=None, dx=0, dy=0, lifetime=0,
				 is_collideable=True, after_death=None):
		"""Initializes Message object with given parameters.

		Args:
			value: The text to display.
			size: The height of the text in pixels
			color: The color of the text.
			angle: The angle to rotate the object.
			x: The center x position where the sprite will be placed.
			y: The center y position where the sprite will be placed.
			top: The y location of the top edge of the sprite.
			bottom: The y location of the bottom edge of the sprite.
			left: The x location of the left edge of the sprite.
			right: The x location of  right edge of the sprite.
			dx: delta x is the x velocity of the sprite.
			dy: delta y is the y velocity of the sprite.
			lifetime: The number of frames before removing self and afterwards
				calling function after_death. This args is set to interval
				attribute and as such the Message object has no lifetime attribute.
			after_death: Function to call after lifetime frames.
			is_collideable: Whether or not the sprite participates in collisions.
		"""

		Text.__init__(self, value, size, color, angle, x,
					  y, top, bottom, left, right, dx, dy,
					  lifetime, is_collideable)

		self.after_death=after_death

	def tick(self):
		self.destroy()
		if self.after_death: self.after_death()


class Animation(Sprite):
	"""A subclass of Sprite that rotates through a list of images.

	This is basically an emulation of a gif.
	As with Message, you don't get to override tick() as it is
	already being used.
	"""
	def __init__(self, images, angle=0, x=0, y=0, top=None,
				 bottom=None, left=None, right=None, dx=0, dy=0,
				 repeat_interval=1, n_repeats=0,
				 is_collideable=True):
		"""Initializes Animation with given parameters.

		Args:
			images: The list of images to display. These could be actual image
				objects from load_image() or just the filenames (Animation will load
				the images for you).
			angle: The angle to rotate the object.
			x: The center x position where the sprite will be placed.
			y: The center y position where the sprite will be placed.
			top: The y location of the top edge of the sprite.
			bottom: The y location of the bottom edge of the sprite.
			left: The x location of the left edge of the sprite.
			right: The x location of  right edge of the sprite.
			dx: delta x is the x velocity of the sprite.
			dy: delta y is the y velocity of the sprite.
			repeat_interval: The number of frames between image changes. This
				arg is set to interval attribute and as such the Animation
				object has no repeat_interval attribute.
			n_repeats: The number of times the animation is repeated before
				getting removed. If 0 then it repeats forever.
			is_collideable: Whether or not the sprite participates in collisions.
		"""
		self.images=[]
		for pic in images:
			if isinstance(pic, str):
				self.images.append(load_image(pic))
			else:
				self.sequence.append(pic)
		Sprite.__init__(self, self.images[0], angle, x, y, top,
						bottom, left, right, dx, dy,
						repeat_interval, is_collideable)
		self.n_repeats=n_repeats
		if not self.n_repeats:
			self.n_repeats-=1
		self.pos=0

	def tick(self):
		self.pos+=1
		self.pos%=len(self.images)
		self.image=self.images[self.pos]
		if not self.pos:
			self.n_repeats-=1
		if not self.n_repeats:
			self.destroy()

class Screen(object):
	"""A screen class.

	The screen to use everything with. Shouldn't make own copy.
	Use init() instead and screen instead.

	Attributes:
		background: The background image for the screen. Make
			sure it is the same size as the screen or bigger
			and it is not transparent or else Bad
			Things Happen.
		all_objects: List of all the objects on the screen.
		event_grab: A boolean for if all input events are grabbed by the
			program. Use the escape key to exit when true.
		 width: The screen's width. Can't change it.
		 height: The screen's height. Can't change it.
	"""


	def __init__(self, width, height, fps, virtual=False):
		"""Initializes screen.

		Usually, this shouldn't be directly used, rather get copy from
		games.screen after running games.init().
		"""

		self._width=width
		self._height=height
		self._fps=fps
		self.running=False
		self.virtual=virtual
		# Initialise screen
		if not virtual:
			pygame.init()
			self.screen_surf = pygame.display.set_mode((width, height))

		start=pygame.Surface((0, 0))
		if not virtual:
			start=start.convert()
		start.fill((0, 0, 0))
		self.background=start
		# Fill background
		self.buffer = pygame.Surface((width, height))
		if not self.virtual:
			self.buffer = self.buffer.convert()
		self.buffer.fill((0, 0, 0))

		self.all_objects=[]
		self.event_grab=False
		self.old_dirties=[]
		self.new_dirties=[]

	def get_width(self):
		return self._width

	def _set_width(self, new_width):
		raise ValueError("Can't change width")

	width=property(get_width, _set_width)

	def get_height(self):
		return self._height

	def _set_height(self, new_height):
		raise ValueError("Can't change height")

	height=property(get_height, _set_height)

	def get_fps(self):
		return self._fps

	def _set_fps(self, new_fps):
		raise ValueError("Can't change fps")

	fps=property(get_fps, _set_fps)

	def get_background(self):
		return self._background

	def set_background(self, new_background):
		self._background=new_background
		self._real_background=pygame.Surface((self.width, self.height))
		if not self.virtual:
			self._real_background = self._real_background.convert()
		self._real_background.fill((0, 0, 0))
		self._real_background.blit(self._background, (0, 0))

	background=property(get_background, set_background)

	def get_all_objects(self):
		return self.all_objects

	def get_event_grab(self):
		return self._event_grab

	def set_event_grab(self, new_status):
		self._event_grab=new_status
		if not self.virtual:
			pygame.event.set_grab(self.event_grab)

	event_grab=property(get_event_grab, set_event_grab)

	def add(self, sprite):
		"""Adds sprite to list of objects on screen.

		Args:
			sprite: The sprite to add.

		Raises:
			ValueError: When given object isn't a Sprite
		"""

		if isinstance(sprite, Sprite):
			self.all_objects.append(sprite)
			sprite.screen=self
		else:
			raise ValueError("Method 'add' takes Sprite objects not, "
							 +type(sprite)+".")

	def remove(self, sprite):
		"""Removes sprite from list of objects on screen.

		Args:
			sprite: The sprite to remove.
		"""

		if sprite in self.all_objects:
			self.all_objects.remove(sprite)
			sprite.screen=None

	def clear(self):
		"""Clears entire screen.

		Removes all sprites from screen, only the background will be left.
		"""
		for i in self.all_objects:
			self.remove(i)

	def mainloop(self):
		"""Starts the event loop.

		Sprites are moved, drawn, etc. The program will keep looping until
		screen.quit() is called.
		"""
		self.running=True
		# Event loop
		while self.running:
			start=time.time()
			self.old_dirties=self.new_dirties
			self.new_dirties=[]
			self.buffer.blit(self._real_background, (0, 0))
			if not self.virtual:
				for event in pygame.event.get():
					if event.type == pygame.locals.QUIT:
						self.quit()
						return
			if keyboard.is_pressed(pygame.locals.K_ESCAPE):
				self.quit()
			for sprite in self.all_objects:
				if not self.running:
					return
				sprite._process_sprite()
			if not self.running:
				return
			if not self.virtual:
				self.screen_surf.blit(self.buffer, (0, 0))
				pygame.display.update()

			delay=(1.0/self.fps)-(time.time()-start)
			if delay>0:
				time.sleep(delay)

	def quit(self):
		"""Stops mainloop()

		Raises:
			ValueError: When called without calling mainloop first.
		"""
		if self.running:
			self.running=False
			pygame.display.quit()
		else:
			raise ValueError("Can't quit while not running.")


def init(screen_width, screen_height, fps, virtual=False):
	"""Initializes screen, keyboard, mouse and music.

	Its necessary to initialize these global variables before anything is done.

	Args:
		screen_width: The desired width of the screen.
		screen_height: The desired height of the screen.
		fps: The desired Frames Per Second for the screen.
	"""
	global screen, mouse, keyboard, music

	screen=Screen(screen_width, screen_height, fps, virtual)
	mouse=Mouse()
	keyboard=Keyboard()
	music=Music()

def load_image(filename, transparent=True):
	"""Returns Image object from the file filename.

	Args:
		filename: File containing image.
		transparent: If true, all pixels with upper-right-most
			pixel color will become 100% transparent.

	Returns:
		An image object to use with Sprites, etc.
	"""
	image = pygame.image.load(filename)
	if not screen.virtual:
		image = image.convert()
	if transparent:
		colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, pygame.locals.RLEACCEL)
	return image

def scale_image(image, x_scale, y_scale=None):
	"""Scales image by the given factors.
	Args:
		x_scale: Width scaling factor.
		y_scale: Height scaling factor. If y_scale not given then uses x_scale
			as height scaling factor.

	Returns:
		A scaled copy of the image.
		***DOES NOT AFFECT ORGINAL IMAGE***
	"""
	rect=image.get_rect()
	width=rect.width*x_scale
	if y_scale:
		height=rect.height*y_scale
	else:
		height=rect.height*x_scale
	return pygame.transform.scale(image, (int(round(width)), int(round(height))))

def load_sound(filename):
	"""Returns Sound object from the file filename.

	Args:
		filename: File containing sound.

	Returns:
		A sound object to play, etc.
	"""
	return pygame.mixer.Sound(filename)
