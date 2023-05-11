# from . import config as c
import time
import ctypes
import threading
import json
import os
import inspect


class Hotkey:
	"""
	This class is used to listen to keys and execute functions when hotkeys are pressed
	"""

	def __init__(self):
		# config
		self.listener_ticks = -1  # -1 to skip first loop iteration
		self.last_prsd_keys = []  # last pressed keys
		self.prsd_keys = []  # pressed keys
		self.stop_listening = True
		self.hotkeys = {}  # all hotkeys with their data
		self.listen_delay = 0.01  # delay between all keys check
		self.print_prsd_keys = False  # print pressed keys

		"""
		List of Virtual Key Codes: https://cherrytree.at/misc/vk.htm
		"""

		# define and convert path using pathlib
		module_dir = os.path.dirname(os.path.abspath(__file__))
		with open(os.path.join(module_dir, 'keys.json'), 'r') as file:
			keys_data = json.load(file)
		self.vk_data = keys_data["virtual-key codes"]

		# set all possible keys
		self.keys_name = []
		for key_data in self.vk_data:
			self.keys_name.append(key_data["name"])
		self.keys_num = []  # numeric
		for key_data in self.vk_data:
			self.keys_num.append(key_data["numeric"])
		self.keys_dec = []  # decimal
		for key_data in self.vk_data:
			self.keys_dec.append(key_data["decimal"])

		# release key RETURN to avoid possible unwanted key presses
		ctypes.windll.user32.keybd_event(0x13, 0, 2, 0)

	def start(self):
		self.thread = threading.Thread(target=self.run)
		self.stop_listening = False
		self.thread.start()

	def stop(self):
		self.stop_listening = True  # flag to stop listening to keys
		self.thread.join()  # wait for thread to finish

	def run(self):
		while True:
			self.listener_ticks += 1

			if self.stop_listening:
				break

			time.sleep(self.listen_delay)

			self.time_now = time.time()

			self._handle_keys()

			# skip first loop iteration, because ctypes detects previously pressed keys
			if self.listener_ticks < 0:
				continue

			if self.last_prsd_keys != self.prsd_keys:
				self.last_prsd_keys = self.prsd_keys.copy()
				self._handle_hotkeys()

			self._auto_update_hotkeys()

	def _handle_keys(self):
		for key in self.keys_dec:
			prsd_key_dict = self._find_subset(key, self.prsd_keys, 'dec')
			key_state = ctypes.windll.user32.GetAsyncKeyState(key)
			if key_state:
				if prsd_key_dict:
					prsd_key_dict["prsd_for"] = time.time() - prsd_key_dict["prsd_time"]
				else:
					key_data = self._find_subset(key, self.vk_data, 'dec')
					self.prsd_keys.append({
						'name': key_data["name"],
						'numeric': key_data["numeric"],
						'decimal': key_data["decimal"],
						'description': key_data["description"],
						'prsd_time': time.time(),
						'prsd_for': 0
					})
			elif prsd_key_dict:
				self.prsd_keys.remove(prsd_key_dict)

		self.prsd_keys_name = []
		for prsd_key in self.prsd_keys:
			self.prsd_keys_name.append(prsd_key["name"])

		if self.prsd_keys and self.print_prsd_keys:
			prsd_keys_to_print = []

			for prsd_key in self.prsd_keys:
				prsd_keys_to_print.append([
					prsd_key["name"][3:],  # remove "VK_" from name
					round(prsd_key["prsd_for"], 3)
				])

			print(f'Prsd keys: {prsd_keys_to_print}')

	def _handle_hotkeys(self):
		for hotkey in self.hotkeys.keys():
			wanted = self.hotkeys[hotkey]["wanted"]
			unwanted = self.hotkeys[hotkey]["unwanted"]
			order = self.hotkeys[hotkey]["order"]

			# check if wanted keys are pressed including order
			if order:
				if unwanted is None:
					# check if wanted keys are pressed in the same order
					state = wanted == [key for key in self.prsd_keys_name if wanted[0] in self.prsd_keys_name and
					                   wanted[-1] in self.prsd_keys_name and
					                   self.prsd_keys_name.index(wanted[0]) <= self.prsd_keys_name.index(
						key) <= self.prsd_keys_name.index(wanted[-1])]
				elif unwanted == 'all':
					# check if wanted keys are pressed in order and all unwanted keys are not pressed
					state = wanted == self.prsd_keys_name
				else:
					# check if wanted keys are pressed in order and unwanted keys are not pressed
					state = (wanted[0] in self.prsd_keys_name and wanted[-1] in self.prsd_keys_name and
					         all(self.prsd_keys_name.index(wanted[0]) <= self.prsd_keys_name.index(
						         key) <= self.prsd_keys_name.index(
						         wanted[-1]) for key in self.prsd_keys_name)
					         ) and not any(key in self.prsd_keys_name for key in unwanted)
			else:
				if unwanted is None:
					# check if wanted keys are pressed
					state = all(key in self.prsd_keys_name for key in wanted)
				elif unwanted == 'all':
					state = all(key in self.prsd_keys_name for key in wanted) and not any(
						key not in wanted or key in self.keys_dec for key in self.prsd_keys_name)
				else:
					# check if wanted keys are pressed and unwanted keys are not pressed
					state = all(key in self.prsd_keys_name for key in wanted) and not any(
						key in self.prsd_keys_name for key in unwanted)

			# print(f'state: {state}, self.prsd_keys_name: {self.prsd_keys_name}, wanted: {wanted}, unwanted: {unwanted}, order: {order}')

			# if hotkey is triggered for the first time
			if state and not self.hotkeys[hotkey]["triggered"]:
				print(f'Hotkey "{hotkey}" is set as triggered, hotkey: {self.hotkeys[hotkey]}, prsd_keys: {self.prsd_keys_name}')
				self.hotkeys[hotkey]["triggered"] = True
				self.hotkeys[hotkey]["trigger_time"] = self.time_now
				if not self.hotkeys[hotkey]["on_release"] and self.hotkeys[hotkey]["triggered_for"] < self.hotkeys[hotkey]["timeout"]:
					self.hotkeys[hotkey]["trigger_callback"] = True
			# if not triggered for the first time
			elif not state and self.hotkeys[hotkey]["triggered"]:
				print(f'Hotkey "{hotkey}" is set as untriggered, hotkey: {self.hotkeys[hotkey]}, prsd_keys: {self.prsd_keys_name}')
				if self.hotkeys[hotkey]["on_release"] and self.hotkeys[hotkey]["triggered_for"] < self.hotkeys[hotkey]["timeout"]:
					self.hotkeys[hotkey]["trigger_callback"] = True
				self._untrigger_hotkey(hotkey)

	def _auto_update_hotkeys(self):
		for hotkey in self.hotkeys.keys():
			if self.hotkeys[hotkey]["triggered"] and self.hotkeys[hotkey]["active"]:
				self.hotkeys[hotkey]["triggered_for"] = self.time_now - self.hotkeys[hotkey]["trigger_time"]
				if self.hotkeys[hotkey]["triggered_for"] > self.hotkeys[hotkey]["timeout"]:
					self._untrigger_hotkey(hotkey)
					self.hotkeys[hotkey]["trigger_callback"] = False

			if self.hotkeys[hotkey]["trigger_callback"] and self.hotkeys[hotkey]["thread"] != 'main':
				print(f'Calling callback for hotkey "{self.hotkeys[hotkey]}"')
				self.hotkeys[hotkey]["trigger_callback"] = False
				if self.hotkeys[hotkey]["thread"] == 'run':
					self.hotkeys[hotkey]["callback"]()
				elif self.hotkeys[hotkey]["thread"] == 'new':
					threading.Thread(target=self.hotkeys[hotkey]["callback"]).start()


	def update_manual_hotkeys(self, hotkeys=None):
		"""
		Manually check hotkeys in manual_check_hotkeys
		:param hotkeys: list of hotkeys to check, if None all hotkeys will be checked
		:return:
		"""

		if hotkeys in [None, 'all', '*']:
			hotkeys = self.hotkeys.keys()
		elif not isinstance(hotkeys, (list, tuple)):
			raise ValueError('Hotkeys must be list or tuple')

		for hotkey in hotkeys:
			if hotkey not in self.hotkeys:
				raise ValueError(f'Hotkey "{hotkey}" not found')
			elif not self.hotkeys[hotkey]["active"] or self.hotkeys[hotkey]["thread"] != 'main':
				continue

			if self.hotkeys[hotkey]["trigger_callback"]:
				print(f'Calling callback for hotkey "{self.hotkeys[hotkey]}"')
				self.hotkeys[hotkey]["trigger_callback"] = False
				self.hotkeys[hotkey]["callback"]()

	def _find_subset(self, value, data, by_type=None):
		"""
		Find subset of dict in list of dicts
		:param value: value to find
		:param data: list of dicts
		:return: found dict, else False
		"""

		if by_type == 'num':
			by_type = 'numeric'
		elif by_type == 'dec':
			by_type = 'decimal'
		elif by_type == 'desc':
			by_type = 'description'

		if by_type in ['name', 'numeric', 'decimal', 'description']:
			for item in data:
				if value == item[by_type]:
					return item
		else:
			for item in data:
				if value == item["name"]:
					return item
				elif str(value) == item["numeric"]:
					return item
				elif value == item["decimal"]:
					return item
				elif value == item["description"]:
					return item

		return False

	def rename(self, arg, to_type='name'):
		"""
		Rename keys in given list to their names from keys database
		:param arg: list of keys to rename
		:return: list of renamed args
		"""

		if arg is None:
			return None
		elif arg == 'all':
			return 'all'
		elif not isinstance(arg, (list, tuple)):
			arg = [arg]

		if to_type == 'num':
			to_type = 'numeric'
		elif to_type == 'dec':
			to_type = 'decimal'
		elif to_type == 'desc':
			to_type = 'description'

		if to_type not in ['name', 'numeric', 'decimal', 'description']:
			raise ValueError(f'Unknown type "{to_type}", must be "name", "num", "dec" or "desc"')

		for key in arg:
			# find key in keys database
			found = self._find_subset(key, self.vk_data)
			if found:
				arg[arg.index(key)] = found[to_type]
			else:
				# if key is name with "VK_" at the beginning
				found_without_vk = self._find_subset(f'VK_{key}', self.vk_data)
				if found_without_vk:
					arg[arg.index(key)] = found_without_vk[to_type]
				else:
					raise ValueError(f'Key "{key}" is not found in keys database')
		return arg

	def set_hotkey(self, name, wanted=None, unwanted=None, callback=None, order=False,
	               on_release=False, timeout=None, thread='main', active=True):
		"""
		Add hotkey to hotkeys dict
		:param name: name of hotkey
		:param wanted: list of wanted keys that must be pressed to trigger hotkey
		:param unwanted: list of unwanted keys, if 'all', all keys are unwanted
		:param order: if True, wanted keys must be pressed in order
		:param on_release: if True, hotkey is triggered on key release
		:param timeout: timeout in seconds, if None, infinite timeout
		:param callback: function to call when hotkey is triggered
		:param thread: thread to call callback in: 'main', 'run', 'new'
		:param active: if True, hotkey is active
		:param triggered: if True, hotkey is triggered
		"""

		if not isinstance(wanted, (list, tuple)):
			raise ValueError('Wanted keys must be list or tuple')

		if timeout in [None, False, -1]:
			timeout = float('inf')

		if name in ['all', '*']:
			raise ValueError('Hotkey name can not be "all" or "*"')
		elif not isinstance(name, str):
			raise ValueError('Hotkey name must be string')

		wanted = self.rename(wanted)
		unwanted = self.rename(unwanted)

		# overwriting new arguments
		if name in self.hotkeys.keys():
			argspec = inspect.getfullargspec(self.set_hotkey)
			defaults = dict(zip(argspec.args[::-1], argspec.defaults[::-1]))
			default_args = dict(sorted(defaults.items()))
			# filter out arguments in given_args that are not in defaults
			given_args = {k: v for k, v in locals().items() if k in defaults}
			given_args = dict(sorted(given_args.items()))
			
			for arg in defaults:
				if given_args[arg] != defaults[arg]:
					self.hotkeys[name][arg] = given_args[arg]
					print(f'Updating "{arg}" for hotkey "{name}"')
		else:
			self.hotkeys[name] = {
				'wanted': wanted,
				'unwanted': unwanted,
				'order': order,
				'on_release': on_release,
				'timeout': timeout,  # counting when hotkey is triggered
				'callback': callback,  # use lambda
				'thread': thread,
				'active': active,
				'trigger_time': 0,  # self.time_now
				'triggered_for': 0,  # self.time_now - self.hotkeys[name]["trigger_time"]
				'triggered': False,  # conditions: trigger_condition, timeout
				'trigger_callback': False  # True only when triggers for first time
			}

	def _untrigger_hotkey(self, name):
		print(f'_untrigger_hotkey: {name}')
		self.hotkeys[name]["triggered"] = False
		self.hotkeys[name]["trigger_time"] = 0