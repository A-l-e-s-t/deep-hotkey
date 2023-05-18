# """
# write python program that reads json file "keys.json" and prints all dublicates that it found
# """
#
# import json
#
# with open('keys.json', 'r') as file:
# 	keys_data = json.load(file)
#
# vk_data = keys_data["virtual-key codes"]
#
# print(f'1: {vk_data}')
#
# all_items = []
# for item in vk_data:
# 	all_items.append(item['name'])
# 	all_items.append(item['numeric'])
# 	all_items.append(item['decimal'])
# 	all_items.append(item['description'])
#
# print(f'2: {all_items}')
#
# dublicates = []
# for item in all_items:
# 	if all_items.count(item) > 1:
# 		dublicates.append(item)
#
# print(f'3: {dublicates}')


import json
import time


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


def _find_subset(value, data):
    """
    Find subset of dict in list of dicts
    :param value: value to find
    :param data: list of dicts
    :return: found dict, else False
    """

    for item in data:
        if value == item['name']:
            return item
        elif str(value) == item['numeric']:
            return item
        elif value == item['decimal']:
            return item
        elif value == item['description']:
            return item

    return False


with open('keys.json', 'r') as file:
    keys_data = json.load(file)
vk_data = keys_data['virtual-key codes']

# utils.find_subset() took 0.4837017059326172 seconds
# _find_subset() took 0.452298641204834 seconds

value = 'VK_B'

print(f'find_subset() returned {find_subset(value, vk_data)}')
print(f'_find_subset() returned {_find_subset(value, vk_data)}')

# make 10000 loop to test performance of utils.find_subset()
now = time.time()
for i in range(10000):
    find_subset(0x41, vk_data)
print(f'utils.find_subset() took {time.time() - now} seconds')

# make 10000 loop to test performance of _find_subset()
now = time.time()
for i in range(10000):
    _find_subset("0x41", vk_data)
print(f'_find_subset() took {time.time() - now} seconds')

