import time
import ctypes
import threading
import json
import os
import inspect
import logging


"""
Bugs to fix:
- when triggering hotkey, it's on_released_callback is triggered with delay
"""


class Hotkey:
	"""
	This class is used to listen to keys and execute functions when hotkeys are pressed

	Example:
		def on_hotkey_1():
			print('hotkey 1 pressed')

		def on_hotkey_2():
			print('hotkey 2 pressed')

		hotkey = Hotkey()
		hotkey.set_hotkey(
			['CTRL', 'A'],
			on_press_callback=lambda: on_hotkey_1(),
			on_release_callback=lambda: print('hotkey 1 released')
		)
	"""

	def __init__(self):
		"""
		:param listener_ticks: how many times listener should be called
		:param last_prsd_keys: list of pressed keys
		:param prsd_keys: list of pressed keys
		:param stop_listening: if True, listener will stop listening
		:param hotkeys: dict of all hotkeys with their data
		:param listen_delay: delay between all keys check (in seconds)
		:param manual_hotkeys_timeouts: if hotkey is triggered, but update_manual_hotkeys() is not called in time, hotkey will be ignored (in seconds)
		:param print_prsd_keys: print pressed keys
		"""

		# config
		self.listener_ticks = -1  # -1 to skip first loop iteration
		self.last_prsd_keys = []
		self.prsd_keys = []  # pressed keys
		self.stop_listening = True
		self.hotkeys = {}  # all hotkeys with their data
		self.listen_delay = 0.01  # (sec) delay between all keys check
		self.manual_hotkeys_timeout = 1  # (sec) if hotkey is triggered, but update_manual_hotkeys() is not called in time, hotkey will be ignored
		self.print_prsd_keys = False  # print pressed keys
		self.custom_class = False

		logging.basicConfig(level='CRITICAL', format='%(module)s:%(funcName)s:%(message)s')

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

	def set_logging_level(self, level):
		"""
		Set logging level
		:param level: logging level

		Levels:
		[CRITICAL] - 50;
		[ERROR] - 40;
		[WARNING] - 30;
		[INFO] - 20;
		[DEBUG] - 10;
		[NOTSET] - 0.

		Levels can be set using numbers or strings
		"""

		logging.getLogger().setLevel(level)

	def set_custom(self, custom_class):
		"""
		Set custom class
		:param custom_class: custom class
		"""

		self.custom_class = custom_class

	def start(self):
		stop_event = threading.Event()
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
			hotkey_dict = self.hotkeys[hotkey]
			wanted = hotkey_dict["wanted"]
			unwanted = hotkey_dict["unwanted"]
			order = hotkey_dict["order"]

			# check if wanted keys are pressed including order
			if order:
				if unwanted is None:
					# check if wanted keys are pressed in the same order
					state = wanted == [
						key for key in self.prsd_keys_name if wanted[0] in self.prsd_keys_name
                        and wanted[-1] in self.prsd_keys_name
                        and self.prsd_keys_name.index(wanted[0])
                        <= self.prsd_keys_name.index(key)
                        <= self.prsd_keys_name.index(wanted[-1])
					]
				elif unwanted == 'all':
					# check if wanted keys are pressed in order and all unwanted keys are not pressed
					state = wanted == self.prsd_keys_name
				else:
					# check if wanted keys are pressed in order and unwanted keys are not pressed
					state = (
						wanted[0] in self.prsd_keys_name and wanted[-1] in self.prsd_keys_name
						and all(
							self.prsd_keys_name.index(wanted[0])
							<= self.prsd_keys_name.index(key)
							<= self.prsd_keys_name.index(wanted[-1]) for key in self.prsd_keys_name
						)
					) and not any(key in self.prsd_keys_name for key in unwanted)
			else:
				if unwanted is None:
					# check if wanted keys are pressed
					state = all(key in self.prsd_keys_name for key in wanted)
				elif unwanted == 'all':
					state = all(key in self.prsd_keys_name for key in wanted) \
					        and not any(key not in wanted or key in self.keys_dec for key in self.prsd_keys_name)
				else:
					# check if wanted keys are pressed and unwanted keys are not pressed
					state = all(key in self.prsd_keys_name for key in wanted) and \
							not any(key in self.prsd_keys_name for key in unwanted)

			logging.debug(f'state: {state}, self.prsd_keys_name: {self.prsd_keys_name}, wanted: {wanted}, unwanted: {unwanted}, order: {order}')
			logging.info(f'Hotkey "{hotkey}" state: {state}, triggered: {hotkey_dict["triggered"]}')

			if not self._check_requirements(hotkey_dict["requirements"]):
				continue

			# if hotkey is triggered for the first time and all bools in requirements are True
			if state and not hotkey_dict["triggered"]:
				if hotkey_dict["toggle"]:
					if not hotkey_dict["switched"]:
						hotkey_dict["triggered"] = True
						hotkey_dict["trigger_time"] = self.time_now
						if hotkey_dict["triggered_for"] < hotkey_dict["timeout"]:
							logging.info(f'Hotkey "{hotkey}" is set as triggered, hotkey: {hotkey_dict}, prsd_keys: {self.prsd_keys_name}')
							if hotkey_dict["on_press_callback"]:
								hotkey_dict["trigger_on_press_callback"] = True
					else:
						if hotkey_dict["triggered_for"] < hotkey_dict["timeout"]:
							logging.info(f'Hotkey "{hotkey}" is set as untriggered, hotkey: {hotkey_dict}, prsd_keys: {self.prsd_keys_name}')
							if hotkey_dict["on_release_callback"]:
								hotkey_dict["trigger_on_release_callback"] = True
								self._untrigger_hotkey(hotkey)

					hotkey_dict["switched"] = not hotkey_dict["switched"]
				else:
					logging.info(f'Hotkey "{hotkey}" is set as triggered, hotkey: {hotkey_dict}, prsd_keys: {self.prsd_keys_name}')
					hotkey_dict["triggered"] = True
					hotkey_dict["trigger_time"] = self.time_now
					if hotkey_dict["on_press_callback"] and hotkey_dict["triggered_for"] < \
							hotkey_dict["timeout"]:
						print(f'Hotkey "{hotkey}", triggered_for: {hotkey_dict["triggered_for"]}, timeout: {hotkey_dict["timeout"]}')
						hotkey_dict["trigger_on_press_callback"] = True

			# if not triggered for the first time
			elif not state and hotkey_dict["triggered"]:
				if hotkey_dict["toggle"]:
					pass
				else:
					logging.info(f'Hotkey "{hotkey}" is set as untriggered, hotkey: {hotkey_dict}, prsd_keys: {self.prsd_keys_name}')
					if hotkey_dict["on_release_callback"] and \
							hotkey_dict["triggered_for"] < hotkey_dict["timeout"]:
						hotkey_dict["trigger_on_release_callback"] = True
				self._untrigger_hotkey(hotkey)

	def _auto_update_hotkeys(self):
		for hotkey in self.hotkeys.keys():
			hotkey_dict = self.hotkeys[hotkey]

			if not hotkey_dict["active"]:
				continue

			if hotkey_dict["triggered"]:
				# print(f'Hotkey "{hotkey}" is triggered, time_now: {self.time_now}, trigger_time: {hotkey_dict["trigger_time"]}, triggered_for: {hotkey_dict["triggered_for"]}, timeout: {hotkey_dict["timeout"]}')
				hotkey_dict["triggered_for"] = self.time_now - hotkey_dict["trigger_time"]
				if hotkey_dict["triggered_for"] > hotkey_dict["timeout"] or not self._check_requirements(hotkey_dict["requirements"]):
					# print(f'Hotkey "{hotkey}" is set as untriggered because of timeout, triggered_for: {hotkey_dict["triggered_for"]}, timeout: {hotkey_dict["timeout"]}')
					self._untrigger_hotkey(hotkey)
					hotkey_dict["trigger_on_press_callback"] = False
					hotkey_dict["trigger_on_release_callback"] = False

			if hotkey_dict["thread"] == 'main':
				# if self.time_now - hotkey_dict["trigger_time"] > hotkey_dict["timeout"]:
				# 	print(f'Hotkey "{hotkey}" is set as untriggered because of maual timeout, triggered_for: {hotkey_dict["triggered_for"]}, timeout: {hotkey_dict["timeout"]}')
				# 	self._untrigger_hotkey(hotkey)
				# 	hotkey_dict["trigger_on_press_callback"] = False
				# 	hotkey_dict["trigger_on_release_callback"] = False
				continue

			if hotkey_dict["trigger_on_press_callback"]:
				logging.info(f'Calling auto on_press_callback for hotkey "{hotkey_dict}"')
				hotkey_dict["trigger_on_press_callback"] = False
				if hotkey_dict["thread"] == 'dhk':
					hotkey_dict["on_press_callback"]()
				elif hotkey_dict["thread"] == 'new':
					threading.Thread(target=hotkey_dict["on_press_callback"]).start()
			elif hotkey_dict["trigger_on_release_callback"]:
				logging.info(f'Calling auto on_release_callback for hotkey "{hotkey_dict}"')
				hotkey_dict["trigger_on_release_callback"] = False
				if hotkey_dict["thread"] == 'dhk':
					hotkey_dict["on_release_callback"]()
				elif hotkey_dict["thread"] == 'new':
					threading.Thread(target=hotkey_dict["on_release_callback"]).start()

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

		called_hotkeys = []
		for hotkey in hotkeys:
			hotkey_dict = self.hotkeys[hotkey]

			# do check because hotkey to update can be set manually, so it can be not in self.hotkeys
			if hotkey not in self.hotkeys:
				raise ValueError(f'Hotkey "{hotkey}" not found')
			elif not hotkey_dict["active"] or hotkey_dict["thread"] != 'main':
				continue

			if hotkey_dict["trigger_on_press_callback"]:
				called_hotkeys.append(hotkey)
				logging.info(f'Calling manual on_press_callback for hotkey "{hotkey_dict}"')
				hotkey_dict["trigger_on_press_callback"] = False
				hotkey_dict["on_press_callback"]()
			elif hotkey_dict["trigger_on_release_callback"]:
				called_hotkeys.append(hotkey)
				logging.info(f'Calling manual on_release_callback for hotkey "{hotkey_dict}"')
				hotkey_dict["trigger_on_release_callback"] = False
				hotkey_dict["on_release_callback"]()

		return called_hotkeys

	def _find_subset(self, value, data, by_type=None):
		"""
		Find subset of dict in list of dicts
		:param value: value to find
		:param data: list of dicts
		:param by_type: type of value to find, can be 'name', 'numeric', 'decimal', 'description'
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

	def _rename(self, arg, to_type='name'):
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

	def set_hotkey(self, name, wanted=None, unwanted=None, on_press_callback=None, on_release_callback=None,
	               toggle=False, order=False, requirements=None, timeout=None, thread='new', active=True):
		"""
		Add hotkey to hotkeys dict
		:param name: name of hotkey
		:param wanted: list of wanted keys that must be pressed to trigger hotkey
		:param unwanted: list of unwanted keys, if 'all', all keys are unwanted
		:param on_press_callback: callback to call when hotkey is triggered
		:param on_release_callback: callback to call when hotkey is untriggered
		:param toggle: if True, hotkey will call callback in switch mode, else as button
		:param order: if True, wanted keys must be pressed in order
		:param requirements: list of variables that must be True to trigger hotkey
		:param timeout: timeout in seconds, if None, infinite timeout
		:param thread: thread to call callback in: 'main', 'dhk', 'new'
		:param active: if True, hotkey can be triggered

		For on_press_callback and on_release_callback use lambda

		If thread is set to "main", to execute callback you need to call
		update_manual_hotkeys() in your main loop, thread "dhk" will call
		callback in DHK's main loop, thread "new" will call callback in
		new thread

		Timeouts start counting when hotkey is triggered, when timeout is
		reached, hotkey is untriggered even if wanted keys are still pressed
		"""

		if not isinstance(wanted, (list, tuple)):
			raise ValueError('Wanted keys must be list or tuple')

		if timeout in (None, False, -1):
			timeout = float('inf')

		if name in ('all', '*'):
			raise ValueError('Hotkey name can not be "all" or "*"')
		elif not isinstance(name, str):
			raise ValueError('Hotkey name must be string')

		wanted = self._rename(wanted)
		unwanted = self._rename(unwanted)

		# overwriting new arguments
		if name in self.hotkeys.keys():
			argspec = inspect.getfullargspec(self.set_hotkey)
			defaults = dict(zip(argspec.args[::-1], argspec.defaults[::-1]))
			default_args = dict(sorted(defaults.items()))
			given_args = {k: v for k, v in locals().items() if k in defaults}  # filter
			given_args = dict(sorted(given_args.items()))

			for arg in defaults:
				if given_args[arg] != defaults[arg]:
					self.hotkeys[name][arg] = given_args[arg]
					logging.info(f'Updating "{arg}" for hotkey "{name}"')
		else:
			self.hotkeys[name] = {
				'wanted': wanted,
				'unwanted': unwanted,
				'on_press_callback': on_press_callback,
				'on_release_callback': on_release_callback,
				'order': order,
				'requirements': requirements,
				'toggle': toggle,
				'timeout': timeout,
				'thread': thread,
				'active': active,
				'switched': False,  # only for toggle hotkeys, like capslock
				'trigger_time': 0,  # self.time_now
				'triggered_for': 0,  # self.time_now - self.hotkeys[name]["trigger_time"]
				'triggered': False,  # conditions: trigger_condition, timeout
				'trigger_on_press_callback': False,  # True only when triggers for first time
				'trigger_on_release_callback': False  # True only when triggers for first time
			}

	def _check_requirements(self, requirements):
		if requirements is None:
			return True

		dict_requirements = {}
		for key in requirements:
			if key in self.custom_class.__dict__:
				dict_requirements[key] = self.custom_class.__dict__[key]
			elif key in self.hotkeys.keys():
				dict_requirements[key] = self.hotkeys[key]["triggered"]
			else:
				dict_requirements[key] = False
		return all(dict_requirements.values())

	def _untrigger_hotkey(self, name):
		logging.info(f'_untrigger_hotkey: {name}')
		self.hotkeys[name]["triggered"] = False
		self.hotkeys[name]["trigger_time"] = 0
