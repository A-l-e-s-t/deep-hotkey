import keyboard
import pyautogui
import ctypes
import time
import random

time.sleep(3)


def switch_language():
	# press down left windows
	pyautogui.keyDown('winleft')
	keyboard.press('space')
	time.sleep(0.01)
	keyboard.release('space')
	pyautogui.keyUp('winleft')


error_chance = 0.03

all_non_cyrillic_letters = ['.', ',', '!', ';', '[', ']',
														'{', '}', '<', '>', '/', '\\', '|', '\'', '\"',
														'`', '~', '@', '#', '$', '^', '&', '*',]

words_to_press = '''
Кістки, зуби, кігті, відбитки ступень і шкіри, пір'я, яйця та гнізда... Це ще не повний перелік закам'янілостей, що лишилися після динозаврів. Кожен пункт із цього списку є безцінним джерелом інформації. Найбільший знайдений закам'янілий слід сягав майже 1,25 м завдовжки. Він належав рослиноїдному зауроподу. Найбільший трипалий слід м'ясоїдного динозавра довжиною 85 см був полишений тиранозавром рексом.
'''[1:-1]


for word in words_to_press:
	for letter in word:
		# generate random float number between 0.1 and 0.9
		random_float = random.uniform(0, 0.42)
		# random_float = random.uniform(0, 0.1)
		time.sleep(random_float)
		print(letter)

		random_chance = random.random()
		# print(random_chance)
		if random_chance < error_chance:
			# generate random float number between 0.1 and 0.9
			random_float = random.uniform(0.1, 0.5)
			time.sleep(random_float)
			press_key = letter
			while press_key == letter:
				print(press_key == letter)
				# press random key from ukrainian alfabet
				press_key = random.choice('абвгґдеєжзиіїйклмнопрстуфхцчшщьюя')
			print(press_key)
			keyboard.press_and_release(press_key)

		# if leter is higer case, lover case it and simulate pres with shift
		if letter.isupper():
			letter = letter.lower()
			keyboard.press_and_release(f'shift+{letter}')
		elif letter in all_non_cyrillic_letters:
			switch_language()
			if letter == '.':
				ctypes.windll.user32.keybd_event(0xBE, 0, 0, 0)
			elif letter == ',':
				ctypes.windll.user32.keybd_event(0xBC, 0, 0, 0)
			elif letter == '\'':
				ctypes.windll.user32.keybd_event(0xDE, 0, 0, 0)
			elif letter == '"':
				pyautogui.keyDown('shift')
				ctypes.windll.user32.keybd_event(0xDE, 0, 0, 0)
				pyautogui.keyUp('shift')
			elif letter == '!':
				keyboard.press_and_release('shift+1')
			elif letter == '?':
				keyboard.press_and_release('shift+/')
			elif letter == ':':
				keyboard.press_and_release('shift+;')
			elif letter == ';':
				ctypes.windll.user32.keybd_event(0xBA, 0, 0, 0)
			elif letter == '(':
				ctypes.windll.user32.keybd_event(0xA1, 0, 0, 0)
			elif letter == ')':
				ctypes.windll.user32.keybd_event(0xA2, 0, 0, 0)
			elif letter == '[':
				ctypes.windll.user32.keybd_event(0xDB, 0, 0, 0)
			elif letter == ']':
				ctypes.windll.user32.keybd_event(0xDD, 0, 0, 0)
			elif letter == '{':
				ctypes.windll.user32.keybd_event(0xDB, 0, 0, 0)
			elif letter == '}':
				ctypes.windll.user32.keybd_event(0xDD, 0, 0, 0)
			elif letter == '<':
				ctypes.windll.user32.keybd_event(0xBC, 0, 0, 0)
			elif letter == '>':
				ctypes.windll.user32.keybd_event(0xBE, 0, 0, 0)
			elif letter == '-':
				ctypes.windll.user32.keybd_event(0xBD, 0, 0, 0)
			elif letter == '+':
				ctypes.windll.user32.keybd_event(0xBB, 0, 0, 0)
			elif letter == '=':
				ctypes.windll.user32.keybd_event(0xBB, 0, 0, 0)
			elif letter == '/':
				ctypes.windll.user32.keybd_event(0xBF, 0, 0, 0)
			else:
				keyboard.press_and_release(letter)


			switch_language()
		else:

			if letter == '№':
				keyboard.press_and_release('shift+3')
			elif letter == '%':
				ctypes.windll.user32.keybd_event(0xA0, 0, 0, 0)  # Press the shift key
				ctypes.windll.user32.keybd_event(0x35, 0, 0, 0)  # Press the 5 key
				ctypes.windll.user32.keybd_event(0x35, 0, 0x0002, 0)  # Release the 5 key
				ctypes.windll.user32.keybd_event(0xA0, 0, 0x0002, 0)  # Release the shift key
			elif letter == ':':
				keyboard.press_and_release('shift+6')
			elif letter == '?':
				keyboard.press_and_release('shift+7')
			elif letter == '(':
				keyboard.press_and_release('shift+9')
			elif letter == ')':
				keyboard.press_and_release('shift+0')
			elif letter == '_':
				ctypes.windll.user32.keybd_event(0xA0, 0, 0, 0)  # Press the shift key
				ctypes.windll.user32.keybd_event(0xBD, 0, 0, 0)  # Press the 5 key
				ctypes.windll.user32.keybd_event(0xBD, 0, 0x0002, 0)  # Release the 5 key
				ctypes.windll.user32.keybd_event(0xA0, 0, 0x0002, 0)  # Release the shift key
			elif letter == '+':
				keyboard.press_and_release('shift+=')
			else:
				keyboard.press_and_release(letter)
