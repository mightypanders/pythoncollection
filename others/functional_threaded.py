#!/usr/bin/env python

# Display a list of user-defined color bars;
# fill the remaining area with sparkles.
# Designed for the Unicorn pHAT.
# By tusing.


import colorsys
import math
import os
import subprocess
import sys
import threading
import time
from random import randint

import unicornhat as unicorn

# Initialization
unicorn.set_layout(unicorn.AUTO)
unicorn.rotation(0)
unicorn.brightness(0.3)  # Tune to your preferences.
width, height = unicorn.get_shape()

# Line number for where each function will begin
function_pos = {}
# Store values for multithreaded fetching functions.
function_values = {}


def main(display_function, bar_functions, time_limit=None):
	""" The main display function. Uses function_pos to assign parts of the
	display to
	bar functions and display functions.

	Args:
		display_function (func): A function intended to take up the majority
		of the HAT's
			display. Should limit display area with the use of function_pos.
		bar_functions (func): A list of single-row "bars". Again, assign
		position with the
			use of function_pos.
		time_limit (int): How long to wait before quitting (in seconds).
	"""
	if bar_functions is not None:
		for index, bar_function in enumerate(bar_functions):
			function_pos[bar_function] = width - index - 1
		if display_function is not None:
			function_pos[display_function] = width - len(bar_functions) - 1
	else:
		function_pos[display_function] = width - 1

	threads = [threading.Thread(target=function) for function in
	           function_pos.keys()]
	for thread in threads:
		thread.start()

	if time_limit is not None:
		time.sleep(time_limit)
		print("Time limit reached!")
		os._exit(3)


######################################################################
#######################                     ##########################
#######################    BAR FUNCTIONS    ##########################
#######################                     ##########################
######################################################################

#######################     INTERNET BAR    ##########################
def internet_color(update_rate=5):
	""" Color bar - tests internet connectivity. Displays white if connected;
	orange if not.

	Args:
		update_rate (int): seconds to wait before checking connectivity again
	"""
	# Ping a Google DNS server to check for internet connectivity.
	while True:
		ping_response = subprocess.Popen(
				["/bin/ping", "-c1", "-w100", "8.8.8.8"],
				stdout=subprocess.PIPE).stdout.read()
		if "1 received" in str(ping_response):
			color_bar(function_pos[internet_color], (255, 255, 255))
		else:
			color_bar(function_pos[internet_color], (255, 127, 80))
		unicorn.show()
		time.sleep(update_rate)


def color_bar(position, color):
	""" Display a single, static bar of ```color``` in ```position```.

	Args:
		position (int): the width index at which to display the bar
		color (int tuple): (R, G, B) tuple of the RGB color to be displayed
	"""
	for height_index in range(height):
		unicorn.set_pixel(position, height_index, *color)
	return


######################################################################
#######################                     ##########################
#######################  FETCHER FUNCTIONS  ##########################
#######################                     ##########################
######################################################################

def load_fetcher(update_rate=5):
	""" Get the load of the system and modify the relevant dictionary
	with the new load value.

	Args:
		update_rate (int): seconds to wait before fetching load value
	"""
	while True:
		function_values[load_fetcher] = os.getloadavg()[0]
		time.sleep(update_rate)


def random_color():
	""" Generate a random RGB color.
	Returns:
		int tuple: (R, G, B) values
	"""
	r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
	return (r, g, b)


######################################################################
#######################                     ##########################
#######################  DISPLAY FUNCTIONS  ##########################
#######################                     ##########################
######################################################################

#######################    LOAD SPARKLES    ##########################
def load_sparkles(color_function=random_color, update_rate=5):
	""" Fill the rest of the area with randomly-positioned sparkles.
	Frequency of sparkling increases with load^2 (for load>1).

	Args:
		color_function (func): Define a custom function for the
			sparkles' color, instead of a random rainbow.
		update_rate (int): How often to refresh system load value (seconds).
	"""

	def random_pixel(color_function):
		""" Generate a randomly positioned pixel with the color returned
		by color_function.

		Args:
			color_function (func): Should return a (R,G,B) color value.
		"""
		color = color_function()

		def random_position():
			""" Get the position of a random pixel bound by
			function_pos. """
			x = randint(0, function_pos[load_sparkles])
			y = randint(0, (height - 1))
			return (x, y)

		selected_pixel = random_position()

		''' Aesthetic: If the randomly generated pixel is currently lit,
		turn it off and try with a new pixel. Also works as sort of a

		population control on how many pixels will be lit. '''
		while sum(unicorn.get_pixel(*selected_pixel)) > 0:
			unicorn.set_pixel(*(selected_pixel + (0, 0, 0)))
			selected_pixel = random_position()
		unicorn.set_pixel(*(selected_pixel + color))
		return

	''' Sparkle with a frequency based off of the computer's current
	load. Fetch load value every update_rate seconds.'''
	function_values[load_fetcher] = 1
	threading.Thread(target=load_fetcher).start()
	while True:
		tick = 1
		if function_values[load_fetcher] > 1:
			tick = 1 / (function_values[load_fetcher] ** 2) if function_values[
				                                                   load_fetcher] < 12 else 1 / 144
		for i in range(int(update_rate / tick)):
			random_pixel(color_function)
			unicorn.show()
			time.sleep(tick)


#######################    LOAD RAINBOW    ##########################
def load_rainbow(update_rate=5):
	""" A minimally modified version of Pimeroni's "rainbow" example.
	Displays a moving rainbow of colors that increases with load.

	Args:
		update_rate (int): How often to update the load value (seconds).
	"""

	i = 0.0
	offset = 30
	function_values[load_fetcher] = 1
	threading.Thread(target=load_fetcher).start()
	while True:
		load_function = function_values[load_fetcher] / 10 if function_values[
			                                                      load_fetcher] <= 10 else 10
		for w in range(int(update_rate / 0.01)):
			i = i + load_function
			for y in range(4):
				for x in range(function_pos[load_rainbow]):
					r = 0  # x * 32
					g = 0  # y * 32
					xy = x + y / 4
					r = (math.cos((x + i) / 2.0) + math.cos(
							(y + i) / 2.0)) * 64.0 + 128.0
					g = (math.sin((x + i) / 1.5) + math.sin(
							(y + i) / 2.0)) * 64.0 + 128.0
					b = (math.sin((x + i) / 2.0) + math.cos(
							(y + i) / 1.5)) * 64.0 + 128.0
					r = max(0, min(255, r + offset))
					g = max(0, min(255, g + offset))
					b = max(0, min(255, b + offset))
					unicorn.set_pixel(x, y, int(r), int(g), int(b))
			unicorn.show()
			time.sleep(0.01)


#######################     LOAD MATRIX     ##########################
def load_matrix(update_rate=5):
	""" A minimally modified version of Pimeroni's "cross" example.
	Speed increases with n*load^2.

	Args:
		update_rate (int): seconds to wait before updating load value
	"""

	points = []

	class LightPoint:
		def __init__(self):
			self.direction = randint(1, 4)
			if self.direction == 1:
				self.x = randint(0, function_pos[load_matrix])
				self.y = 0
			elif self.direction == 2:
				self.x = 0
				self.y = randint(0, height - 1)
			elif self.direction == 3:
				self.x = randint(0, function_pos[load_matrix])
				self.y = height - 1
			else:
				self.x = function_pos[load_matrix] - 1
				self.y = randint(0, height - 1)
			self.colour = []
			for i in range(0, 3):
				self.colour.append(randint(100, 255))

	def update_positions():
		for point in points:
			unicorn.set_pixel(point.x, point.y, 0, 0, 0)
			if point.direction == 1:
				point.y += 1
				if point.y > height - 1:
					points.remove(point)
			elif point.direction == 2:
				point.x += 1
				if point.x > function_pos[load_matrix] - 1:
					points.remove(point)
			elif point.direction == 3:
				point.y -= 1
				if point.y < 0:
					points.remove(point)
			else:
				point.x -= 1
				if point.x < 0:
					points.remove(point)

	def plot_points():
		# unicorn.clear()
		for point in points:
			unicorn.set_pixel(point.x, point.y, point.colour[0],
			                  point.colour[1], point.colour[2])
		unicorn.show()

	function_values[load_fetcher] = 1
	threading.Thread(target=load_fetcher).start()
	tick_func = lambda load: 0.5 / (load ** 2) if load > 1 else 1 / 4
	max_points = function_pos[load_matrix] * height / 3

	while True:
		tick = tick_func(function_values[load_fetcher]) if function_values[
			                                                   load_fetcher] \
		                                                   < \
		                                                   12 else tick_func(
				12)
		for w in range(int(update_rate / tick)):
			if len(points) < max_points and randint(0, 5) > 1:
				points.append(LightPoint())
			plot_points()
			update_positions()
			time.sleep(tick)


if __name__ == "__main__":
	main(load_matrix, (internet_color,))
