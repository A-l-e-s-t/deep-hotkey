import config as c
import threading


def thread_func(func):
	thread = threading.Thread(target=func)
	thread.start()


def find_subset(value, data, type=None):
	"""
	:param value: value to find in data
	:param data: list of dicts
	:param type: type of value to find
	:return: item from data if value is found, None if value is not found
	"""

	if type:  # find subsets of value in data by set type
		if type == 'dec':
			type = 'decimal'
		elif type == 'num':
			type = 'numeric'
		elif type == 'desc':
			type = 'description'

		for item in data:
			if value == item[type]:
				return item  # return subset of value in data
	else:  # try to find subsets in all types automatically
		for item in data:  # go through all subsets in keys dataset
			for key in item:
				if value == item[key]:
					return item  # return item if value is found in any type
			if value == item['name'][3:]:
				return item  # return item if value is equal to name without "VK_"
	return False  # subset not found


def rename(arg):
	"""
	Rename keys in given list to their names from keys database
	:param arg: list of keys to rename
	:return: list of renamed args
	"""

	# if arg is not a list or tuple, make it a list
	if type(arg) not in [list, tuple]:
		arg = [arg]

	for key in arg:
		if find_subset(key, c.vk_data):
			# rename key name
			arg[arg.index(key)] = find_subset(key, c.vk_data)['name']
		# if key is name but without "VK_" at the beginning
		elif type(key) == str and find_subset(f'VK_{key}', c.vk_data):
			arg[arg.index(key)] = find_subset(f'VK_{key}', c.vk_data)['name']
		else:  # if key is not found in database raise error
			raise ValueError(f'Key "{key}" is not found in keys database')

	return arg  # return renamed list of keys


def test(text='this is a test'):  # test
	# if hotkey(['VK_LSHIFT', 'VK_B'], unwanted=['VK_LBUTTON'], order=False):
	# play_sound('tik')
	print(f'Test start with text: {text}')


# def hk_shift_m():  # open menu
# 	if hotkey(['VK_LSHIFT', 'VK_M'], order=False):
# 		play_sound('tik')
# 		print('Start menu')
#
#
# def hk_ctrl_q():  # get mouse position and color
# 	if hotkey([162, 81], unwanted=[160]):  # [162, 81] - ctrl + q, [160] - shift
# 		play_sound('tik')
# 		# get mouse position and color using pyautogui
# 		position = list(c.pyautogui.position())
# 		x, y = [position[0], position[1]]
# 		color = c.pyautogui.pixel(x, y)
# 		print(f'Position: {position}, Color: {color}')


# def hk_sift_ctrl_q():
# 	print mouse position and color
# if c.pressed_keys == [160, 162, 81] or c.pressed_keys == [162, 160, 81]:


# check if utils.py is imported successfully
if __name__ != '__main__':
	print('utils.py imported successfully')
