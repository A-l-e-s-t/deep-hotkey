"""
listen to all key presses and releases with ctypes
"""

import ctypes
import time
import json

# set all possible keys
with open('keys.json', 'r') as file:
  vk_data = json.load(file)

all_keys = []
for key_data in vk_data["virtual-key codes"]:
  all_keys.append(key_data["decimal"])
  print(f'button: {key_data["decimal"]}')
  
# all pressed buttons
pressed_keys = []

# set listener delay in ms for lower cpu usage
delay = 0.01


# listen to keyboard and mouse input
def listen_to_keys():
  while True:
    time.sleep(delay)
    for key in all_keys:
      state = ctypes.windll.user32.GetAsyncKeyState(key)
      if state:  # key is pressed
        if key not in pressed_keys:
          pressed_keys.append(key)
      else:
        if key in pressed_keys:
          pressed_keys.remove(key)
      if pressed_keys != []:
        print(f'keys: {pressed_keys}')


# start listen_key
listen_to_keys()
