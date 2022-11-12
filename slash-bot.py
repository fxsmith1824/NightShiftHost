# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 09:35:50 2022

@author: AzureRogue
"""

#%% Imports and Function Definitions

import nest_asyncio
nest_asyncio.apply()

import os
import discord
from discord.ext import commands, app_commands, tasks
from dotenv import load_dotenv
import asyncio
import random
import pickle
import datetime

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='$', intents=intents)
admin_role = 'Night Shift'

dabo = False
wagers = {}
treasury = {}
shop_inventory = {}
self_inventory = {}

latinum = '<:mee6Coins:1017715720961925150>'
starting_balance = 500

def load_data():
    try:
        with open('data.pickle', 'rb') as file:
            treasury, shop_inventory, self_inventory = pickle.load(file)
        print('Successfully loaded data.')
    except:
        treasury = {295610445824393217: 1000,
                    104392361764737024: 9999}
        shop_inventory = {'Sample Item': {'price': 500, 
                                          'description': 'Just your usual item.'},
                          'Another Item': {'price': 250,
                                           'description': 'Cheaper item here.'}}
        self_inventory = {}
        print('Data failed to load - loading default test data.')
    return treasury, shop_inventory, self_inventory

@bot.event
async def on_ready():
    save_data.start()
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening,
                                  name='Faith of the Heart'))
    print(f'{bot.user.name} has connected to Discord!')

@tasks.loop(minutes=10)
async def save_data():
    data_to_save = (treasury, shop_inventory, self_inventory)
    with open('data.pickle', 'wb') as file:
        pickle.dump(data_to_save, file)
    print('Data saved at ' + str(datetime.datetime.now()))
    print(treasury)
