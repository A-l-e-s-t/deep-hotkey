"""
get list of all windows and their position and size using win32gui
"""

import win32gui
import win32con
import win32api
import time

def get_windows():
  windows = []

  # get all windows and their position and size
  def callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
      windows.append((hwnd, win32gui.GetWindowText(hwnd), win32gui.GetWindowRect(hwnd)))

  win32gui.EnumWindows(callback, windows)

  # print windows
  for window in windows:
    print(f'window: {window}')

  return windows

# get all windows
windows = get_windows()

# print windows
for window in windows:
  print(f'window: {window}')