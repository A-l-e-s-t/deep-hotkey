"""
listen to keyborad input, then convert it to VK code for creating hotkeys
"""

import config as c
import utils as u
import threading


# set all possible keys
all_keys = []
for key_data in c.vk_data:
  all_keys.append(key_data["decimal"])
  # print(f'button: {key_data["decimal"]}')


# all pressed buttons
pressed_keys = []

# set listener delay in ms for lower cpu usage
delay = 0.01


# listen to keyboard and mouse input with threading
def listen_key(key):
  while True:
    state = c.ctypes.windll.user32.GetAsyncKeyState(key)
    if state:  # key is pressed
      pressed_key = u.is_subset(key, pressed_keys, 'dec')
      if pressed_key:
        # update time_pressed in pressed_keys
        differance = c.time.time() - pressed_key["press_time"]
        pressed_key["pressed_for"] = round(differance, 5)
      else:  # key is pressed for the first time
        key_data = u.is_subset(key, c.vk_data, 'decimal')
        # append dict to pressed_keys that contains pressed_key's info
        pressed_keys.append({
          "name": key_data["name"],
          "numeric": key_data["numeric"],
          "decimal": key_data["decimal"],
          "description": key_data["description"],
          "press_time": c.time.time(),
          "pressed_for": 0,
        })
    elif not state and u.is_subset(key, pressed_keys, 'dec'):  # key is released
      # remove pressed_key from pressed_keys
      pressed_keys.remove(u.is_subset(key, pressed_keys, 'dec'))


# start listen_key in threading
for key in all_keys:
  threading.Thread(target=listen_key, args=(key,)).start()

# press and release key 0x13 using ctypes to avoid possible unwanted key presses
c.ctypes.windll.user32.keybd_event(0x13, 0, 2, 0)


# print pressed keys in infinite loop with threading
def print_pressed_keys():
  while True:
    if pressed_keys != []:
      # print name, decimal, pressed_for from pressed_keys
      pressed_key_list = []
      for pressed_key in pressed_keys:
        pressed_key_list.append(f'name: {pressed_key["name"]}, dec: {pressed_key["decimal"]}, time: {pressed_key["pressed_for"]}')
      print(f'Keys: {pressed_key_list}')
      c.time.sleep(delay)


# start print_pressed_keys in threading
threading.Thread(target=print_pressed_keys).start()
