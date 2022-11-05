# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 10:43:27 2022

@author: AzureRogue
"""

import random
import os
import pickle

#%% DATA I/O SUPPORT FUNCTIONS
treasury = {}
shop_inventory = {}
self_inventory = {}

def load_data():
#    global treasury
#    global shop_inventory
#    global self_inventory
    try:
        with open('data.pickle', 'rb') as file:
            treasury, shop_inventory, self_inventory = pickle.load(file)
        print('Successfully loaded data.')
    except:
        treasury = {104392361764737024: 9999}
        shop_inventory = {'Sample Item': {'price': 500, 
                                          'description': 'Just your usual item.'},
                          'Another Item': {'price': 250,
                                           'description': 'Cheaper item here.'}}
        self_inventory = {}
        print('Data failed to load - loading default test data.')
    return treasury, shop_inventory, self_inventory

def save_data():
    data_to_save = (treasury, shop_inventory, self_inventory)
    with open('data.pickle', 'wb') as file:
        pickle.dump(data_to_save, file)

#%% DABO SUPPORT FUNCTIONS
def spinWheel():
    shapes = ['circle', 'square' ,'triangle']
    counts = ['1', '2', '3']
    colors = ['red', 'green', 'blue']
    unique_shapes = ['quark-quark', 'ds9-ds9', 'ds9-ds9', 'ds9-ds9', 
                     'swirl-swirl', 'swirl-swirl', 'blackhole-blackhole',
                     'blackhole-blackhole', 'blackhole-blackhole']
    
    wheel = []
    inner_wheel = []
    
    for shape in shapes:
        for count in counts:
            for color in colors:
                item = count + '-' + color + '-' + shape
                item_2 = count + '-' + shape
                wheel.append(item)
                inner_wheel.append(item_2)
    
    wheel += unique_shapes
    inner_wheel += unique_shapes
    
    result = [random.choice(wheel), random.choice(wheel), random.choice(inner_wheel)]
    return result

def determineWinnings(result):
    uniques = ['swirl', 'quark', 'ds9', 'blackhole']
    counts = [x.split('-')[0] for x in result]
    if len([x.split('-') for x in result][1]) == 1:
        colors = [x.split('-') for x in result][1]
    else:
        colors = [x.split('-')[1] for x in result[:-1]]
    shapes = [x.split('-')[-1] for x in result]
    matches = {}
    matches['counts'] = (max(list({i:counts.count(i) for i in counts if i not in uniques}.values()) + [0]) +
                         counts.count('swirl'))
    matches['colors'] = (max(list({i:colors.count(i) for i in colors if i not in uniques}.values()) + [0]) +
                         colors.count('swirl'))
    matches['shapes'] = (max(list({i:shapes.count(i) for i in shapes if i not in uniques}.values()) + [0]) +
                         shapes.count('swirl'))
    if shapes.count('quark') == 3:
        message = 'DABO!!!'
        payout = 2000
    elif shapes.count('swirl') == 3:
        message = 'DABO!!'
        payout = 1000
    elif shapes.count('ds9') == 3:
        message = 'DABO!'
        payout = 150
    elif shapes.count('quark') == 2:
        message = 'Two Quarks!'
        payout = 5
    elif shapes.count('ds9') == 2:
        message = 'Two DS9s!'
        payout = 4
    elif matches['shapes'] == 3 and matches['colors'] == 2 and matches['counts'] == 3:
        message = 'Dabo!'
        payout = 10
    elif matches['counts'] == 3:
        message = 'Three of the same count!'
        payout = 2
    elif matches['shapes'] == 3:
        message = 'Three of the same shape!'
        payout = 1.5
    elif matches['colors'] == 2:
        message = 'Two of the same color.'
        payout = 0.2
    elif matches['counts'] == 2:
        message = 'Two of the same count.'
        payout = 0.15
    elif matches['shapes'] == 2:
        message = 'Two of the same shape.'
        payout = 0.1
    else:
        message = 'No winner this time... Try again!'
        payout = 0
    return message, payout

def verifyWager(userID, wager):
    if userID in treasury.keys():
        if treasury[userID] >= wager:
            return True
        else:
            return False
    # PROBABLY NEED ANOTHER LINE HERE FOR WHAT TO RETURN IF userID DOESN'T EXIST
    # YET

def collectWagers(wagers):
    for wager in wagers:
        treasury[wager] -= wagers[wager]

def payWinners(payout, wagers):
    for wager in wagers:
        treasury[wager] += int(wagers[wager]*payout)

def resultImages(result):
    image_folder = 'images'
    unique_shapes = ['quark-quark', 'ds9-ds9', 'ds9-ds9', 'ds9-ds9', 
                     'swirl-swirl', 'swirl-swirl']
    wheel1 = result[0]
    wheel2 = result[1]
    wheel3 = result[2]
    wheel1_file = os.path.join(image_folder, wheel1 + '.webp')
    wheel2_file = os.path.join(image_folder, wheel2 + '.webp')
    if wheel3 in unique_shapes:
        wheel3_file = os.path.join(image_folder, wheel3 + '-nc.webp')
    else:
        wheel3_file = os.path.join(image_folder, wheel3 + '.webp')
    return wheel1_file, wheel2_file, wheel3_file

#%% SHOP / ITEM SUPPORT FUNCTIONS
def collectPayment(buyer_id, item):
    if treasury[buyer_id] >= shop_inventory[item]['price']:
        treasury[buyer_id] -= shop_inventory[item]['price']
        return True
    else:
        return False

def disburseItem(buyer_id, item):
    if buyer_id in self_inventory.keys():
        self_inventory[buyer_id].append(item)
    else:
        self_inventory[buyer_id] = [item]