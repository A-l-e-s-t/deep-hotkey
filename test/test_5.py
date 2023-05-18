"""
take screenshot using mss in loop and display screenshot in tkinter label
"""

import mss
import mss.tools
import tkinter as tk
import threading
import time
from PIL import Image, ImageDraw, ImageTk


def take_screen_shot():
  while True:
    with mss.mss() as sct:
      start = time.time()

      # Get information of monitor 2
      monitor_number = 1
      mon = sct.monitors[monitor_number]

      # The screen part to capture
      monitor = {
        "top": mon['width'] // 4,
        "left": mon['height'] // 4,
        "width": mon['width'] // 2,
        "height": mon['height'] // 2,
        "mon": monitor_number,
      }

      # Grab the data
      sct_img = sct.grab(monitor)

      # convert to PIL image
      pil_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

      image = ImageTk.PhotoImage(pil_img)
      label.configure(image=image)
      label.image = image

      time.sleep(0.0016)
      print(f'FPS {1 / (time.time() - start)}')


root = tk.Tk()
root.title('test')
label = tk.Label(root)
label.pack()

# start thread to take screenshot
threading.Thread(target=take_screen_shot).start()

root.mainloop()
