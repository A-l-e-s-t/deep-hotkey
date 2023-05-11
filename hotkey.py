import config as c
import utils
import time
import ctypes
import threading


# i should make it detect capslock, numlock, scrolllock, etc. and add them to pressed keys list

# listen to keyboard and mouse (only buttons) input and check if hotkeys are triggered
def keys_listener():
    # skip first loop iteration, as ctypes detects keys before this function is called
    c.listener_ticks = -1  # default start counter number

    c.last_prsd_keys = None  # list of last pressed keys (opimisation)
    while not c.stop_listening:
        if c.listen_to_keys:
            time.sleep(c.listen_delay)  # delay to avoid unnecessary CPU usage

            # check what keys are pressed
            for key in c.all_keys:  # go through all possible keys
                state = ctypes.windll.user32.GetAsyncKeyState(key)  # get key state (pressed or not)
                if c.listener_ticks == 0:  # if it's first loop tick
                    continue  # skip all code below until the next loop iteration
                prsd_key_dict = utils.find_subset(key, c.prsd_keys)  # find pressed key in pressed keys list
                if state:  # if key is pressed
                    if prsd_key_dict:  # key is already in pressed keys
                        # update time_pressed in pressed_keys
                        differance = time.time() - prsd_key_dict['prsd_time']
                        prsd_key_dict['prsd_for'] = differance
                    else:  # key is pressed for the first time
                        key_data = utils.find_subset(key, c.vk_data)  # find key in database
                        c.prsd_keys.append({  # append dict to pressed_keys that contains pressed_key's info
                            'name': key_data['name'],
                            'numeric': key_data['numeric'],
                            'decimal': key_data['decimal'],
                            'description': key_data['description'],
                            'prsd_time': c.time.time(),
                            'prsd_for': 0,
                        })
                elif prsd_key_dict:  # if key is not pressed and was pressed before
                    c.prsd_keys.remove(utils.find_subset(key, c.prsd_keys))  # remove released key from pressed keys

            # check hotkeys if last pressed keys are not the same as the last pressed keys
            if c.last_prsd_keys != c.prsd_keys:
                check_hotkeys()  # check what hotkeys are triggered
                c.last_prsd_keys = c.prsd_keys.copy()  # copy pressed keys to last pressed keys

            if c.prsd_keys != [] and c.print_prsd_keys:  # if print_prsd_keys is True
                prsd_keys_to_print = []  # list of pressed keys to print
                for prsd_key in c.prsd_keys:  # append pressed keys modified properties to list
                    prsd_keys_to_print.append([
                        prsd_key['name'][3:],  # remove "VK_" from name
                        round(prsd_key['prsd_for'], 3)  # round to 3 decimal places
                    ])  # other properties are skipped
                print(f'Prsd keys: {prsd_keys_to_print}')  # print name, decimal, pressed_for from pressed_keys

        c.listener_ticks += 1  # add 1 to listener_ticks


def check_hotkeys():
    prsd = []  # pressed keys
    for prsd_key in c.prsd_keys:
        prsd.append(prsd_key['name'])  # add pressed key name to list

    print(f'prsd: {prsd}')

    for hotkey in c.hotkeys:  # go through all hotkeys created by user
        if c.hotkeys[hotkey]['active']:  # if hotkey is set to active
            # convert pressed keys dict to list

            wanted = c.hotkeys[hotkey]['wanted']  # get wanted from hotkey
            print(f'check_hotkeys, wanted: {wanted}')
            unwanted = c.hotkeys[hotkey]['unwanted']  # get unwanted from hotkey
            print(f'check_hotkeys, unwanted: {unwanted}')
            order = c.hotkeys[hotkey]['order']  # get order from hotkey

            # print(f'prsd: {prsd}, wanted: {wanted}, unwanted: {unwanted}, order: {order}, triggered: {c.hotkeys[hotkey]["triggered"]}')

            # check if hotkey is triggered
            if order:  # check if pressed keys are in the same order as wanted keys
                if unwanted is None:  # check if unwanted is None
                    prsd_in_wanned = [True if key in wanted else False for key in
                                      prsd]  # convert pressed keys to bool list (True if key is in wanted keys)
                    keys_len = len(wanted)  # get wanted keys length
                    triggered = any([True] * 3 == prsd[i:i + 3] for i in
                                    range(len(prsd) - 2))  # check if wanted keys amount True's are in a row
                    res = triggered
                elif unwanted == 'all':  # all keys are unwanted except wanted keys
                    res = triggered and len(prsd) == len(wanted)
                else:  # unwanted is not None
                    res = triggered and unwanted not in prsd
            else:  # check if pressed keys are in wanted keys without order strictness
                triggered = all(key in prsd for key in wanted)
                if unwanted is None:  # check if unwanted is None
                    res = triggered
                elif unwanted == 'all':  # all keys are unwanted except wanted keys
                    res = triggered and len(prsd) == len(wanted)
                else:  # unwanted is not None
                    res = triggered and all(key not in prsd for key in unwanted)

            # if hotkey got trigged
            if res and not c.hotkeys[hotkey]['triggered']:  # if hotkey is triggered first time
                c.hotkeys[hotkey]['triggered'] = True  # set triggered to True
                if c.hotkeys[hotkey]['func'] == 'print':  # if hotkey insted of function is set to "print"
                    print(f'Hotkey "{hotkey}" is triggered')  # print that hotkey is triggered
                elif c.hotkeys[hotkey]['func'] is not None:  # if hotkey has function
                    if type(c.hotkeys[hotkey]['args']) in [list, tuple]:  # if args is list or tuple
                        c.hotkeys[hotkey]['func'](*c.hotkeys[hotkey]['args'])  # execute function with args in list
                    elif c.hotkeys[hotkey]['args'] is None:  # if no args are given
                        c.hotkeys[hotkey]['func']()  # execute function without args
                    else:  # if only one arg is given
                        c.hotkeys[hotkey]['func'](c.hotkeys[hotkey]['args'])  # execute function with one args
            elif not res and c.hotkeys[hotkey]['triggered']:
                c.hotkeys[hotkey]['triggered'] = False  # set triggered to False


def add_hotkey(name, wanted, wanted_order=False, unwanted=None, unwanted_order=False,
               order=False, func=None, args=None, active=True, triggered=False):
    '''
    Add hotkey to hotkeys dict
    :param name: name of hotkey
    :param wanted: if None, hotkey is triggered if all pressed keys are not in unwanted keys
    :param wanted_order:
    :param unwanted:
    :param unwanted_order:
    :param order:
    :param func:
    :param args:
    :param active:
    :param triggered:
    :return:
    '''

    if name == 'all':  # check if name is 'all'
        raise ValueError('Hotkey name can not be "all"')
    elif name in c.hotkeys:  # check if name is already in hotkeys dict
        print(f'Hotkey "{name}" already exists')
    else:  # add hotkey to hotkeys dict

        print(f'add old wanted: {wanted}')
        print(f'add old unwanted: {unwanted}')

        wanted = utils.rename(wanted)  # rename wanted keys
        unwanted = utils.rename(unwanted)  # rename unwanted keys

        print(f'add new wanted: {wanted}')
        print(f'add new unwanted: {unwanted}')

        c.hotkeys[name] = {
            'wanted': wanted,
            'wanted_order': wanted_order,  # if True, wanted keys must be pressed in order
            'unwanted': unwanted,  # if None, hotkey is triggered if all wanted keys are pressed
            'unwanted_order': unwanted_order,  # if True, unwanted keys must be pressed in order, if 'all', all keys are unwanted except wanted keys
            'timeout': 0,  # if not 0, hotkey has specified time to be triggered after first key in wanted is pressed
            'suppress': False,  # if True, after hotkey trigger blocks all input in wanted keys from being sent to system/programs
            'on_press': False,  # if True, hotkey is triggered on key press
            'func': func,  # function to execute on trigger
            'args': args,  # arguments for function
            'active': active,  # if True, hotkey is tiggerable
            'triggered': triggered,  # if True, hotkey is triggered, all wanted keys are pressed and no unwanted
            'trigger_for': 0,  # if not 0, hotkey is triggered for specified time
            'half_trigger': False,  # if True, some keys are pressed wanted keys are pressed but not all
        }


def update_hotkey(name, wanted='keep', unwanted='keep', order='keep',
                  func='keep', args='keep', active='keep', triggered='keep'):
    """
    Change specified properties of hotkey (except name)

    :param name: name of hotkey
    :param wanted: list of wanted keys or single key
    :param unwanted: list of unwanted keys or single key
    :param order: if True, order of pressed keys must be the same as wanted keys
    :param func: function to execute on trigger
    :param args: arguments for function
    :param active: if True, hotkey is active and can be triggered
    :param triggered: if True, hotkey is triggered
    :return: None
    """

    all_args = []  # list of all arguments
    for key, value in locals().items():  # go through all arguments in function
        if key != 'name':  # if argument is not name
            all_args.append(value)  # add argument to list

    if name in c.hotkeys:  # if hotkey exists in hotkeys dict, modify it
        # if any argument is "keep", don't modify it
        for arg in all_args:
            print(f'arg: {arg}')
            if arg != 'keep':
                if arg in ['wanted', 'unwanted']:  # if arg is wanted or unwanted
                    c.hotkeys[name][arg] = utils.rename(arg)  # set keys to specified renamed value
                else:  # if arg is not wanted or unwanted
                    c.hotkeys[name][arg] = arg  # set arg to specified value
    else:  # raise error if hotkey is not found
        raise ValueError(f'Hotkey "{name}" is\'t found')


def remove_hotkey(name):
    if name == 'all':
        c.hotkeys = {}
    elif name in c.hotkeys:
        del c.hotkeys[name]
    else:
        raise ValueError(f'Hotkey "{name}" is\'t found')


def enable_hotkey(name):
    if name == 'all':
        for key in c.hotkeys:
            c.hotkeys[key]['enabled'] = True
    elif name in c.hotkeys:
        c.hotkeys[name]['enabled'] = True
    else:
        raise ValueError(f'Hotkey "{name}" is\'t found')


def disable_hotkey(name):
    if name == 'all':
        for key in c.hotkeys:
            c.hotkeys[key]['active'] = False
    elif name in c.hotkeys:
        c.hotkeys[name]['active'] = False
    else:
        raise ValueError(f'Hotkey "{name}" is\'t found')


def print_prsd_keys(state=True):
    """
    Print pressed keys every tik in key_listener loop (depends on set delay)
    :param state:
    :return:
    """

    c.print_prsd_keys = state


def get_pressed_keys():
    """
    Get pressed keys
    :return:
    """

    return c.prsd_keys


# check if utils.py is imported successfully
if __name__ != '__main__':
    print('hotkey.py imported successfully')
