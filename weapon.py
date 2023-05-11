import config as c
import utils as u

import numpy as np
import cv2
from win32api import GetSystemMetrics
from mss import mss



def capture():  # capture
    w_max = GetSystemMetrics(0)
    h_max = GetSystemMetrics(1)

    sct = mss()
    x = 810
    y = 50
    h = 300
    w = 350
    bbox = {'top': x, 'left': y, 'width': w, 'height': h}
    screen = sct.grab(bbox)
    screen_np = np.array(screen)
    while c.capture_status:
        cv2.imshow('Screencapture', screen_np)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


def hk_ctrl_pgdn():  # turn on/off capture
    if c.ctrl_status and c.key_vk == 34:
        if not c.capture_status:
            c.capture_status = True
            c.thread_func(capture)
            c.play_sound('run')
            print('Capture enable')
        else:
            c.capture_status = False
            c.play_sound('stop')
            print('Capture disable')


def hk_shift_pgdn():  # turn on/off trigger bot
    if u.hot_key(['VK_LSHIFT', 'VK_PRIOR']):
        if not c.tb_status:
            c.tb_status = True
            u.play_sound('run')
            print('Trigger bot enable')
            u.thread_func(trigger_bot)
        else:
            c.tb_status = False
            u.play_sound('stop')
            print('Trigger bot disable')


def trigger_bot():  # trigger bot
    while c.tb_status:
        u.play_sound('tik')
        print('trigger bot')
        c.time.sleep(1)
        # click mouse button using win32api
        c.win32api.mouse_event(c.win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        c.time.sleep(0.2)
        c.win32api.mouse_event(c.win32con.MOUSEEVENTF_LEFTUP, 0, 0)
