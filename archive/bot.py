# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 17:10:51 2022

TODO: I think Dabo is done - pending feedback from Night Shift.
- Need to either figure out Mee6 integration for currency OR add custom
shop etc.
- Try out personal_inventory = {user: [items]} and treasury management for items
and latinum to use our own bot instead of Mee6
- Ask Night Shift about item expiration dates, maybe?
- Add background tasks for saving treasury, self_inventory every n minutes
-- Alternatively, just save after every round of Dabo / every purchase / every interaction?
- Consider making $my-inventory and $balance DM replies?

- Do another sweep of this and backroom to look for errors that will arise with
an ID that doesn't exist in the dictionaries yet.

- Fix $buy not playing well with other functions adding users to treasury dictionary

@author: AzureRogue
"""

#%% Imports and Function Definitions

import nest_asyncio
nest_asyncio.apply()

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import random
from backroom import *

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='$', intents=intents)

dabo = False
wagers = {}

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening,
                                  name='Faith of the Heart'))
    print(f'{bot.user.name} has connected to Discord!')

#%% Dabo

dabo_min = 10
dabo_max = 1000
dabo_duration = 10

@bot.command(name='dabo')
async def dabo(ctx):
    global dabo
    global wagers
    intro = discord.Embed(
        title = 'Play Some Dabo!',
        description = 'A game of Dabo is about to begin...',
        color = discord.Color.blue())
    intro.add_field(
        name = 'How to Play', value = 'Use the command \"$Wager ' +
        '<integer>\" to bid <integer> <:mee6Coins:1017715720961925150> ' +
        'gold pressed latinum on the next spin!', inline = False)
    intro.add_field(
        name = 'Rules of the Game', value = 'Your wager must be ' +
        'at least ' + str(dabo_min) + ' and at most ' + str(dabo_max) +
        ' <:mee6Coins:1017715720961925150> to enter the game.\n' + 
        'Everyone wins or loses together, so ask the Blessed ' +
        'Exchequer for good luck!', inline = False)
    intro.set_footer(text = 'The tables will close in ' + str(dabo_duration) +
                     ' seconds.')
    dabo = True
    await ctx.send(embed=intro)
    await asyncio.sleep(dabo_duration)
    closed = discord.Embed(
        description = 'Betting is now closed! Play again next time!',
        color = discord.Color.red())
    dabo = False
    await ctx.send(embed=closed)
    collectWagers(wagers)
    result = spinWheel()
    delay = discord.Embed(
        description = 'Collecting wagers and spinning the wheel!',
        color = discord.Color.dark_gray())
    await ctx.send(embed=delay)
    message, payout = determineWinnings(result)
    await asyncio.sleep(random.randint(4,6))
    wheel1, wheel2, wheel3 = resultImages(result)
    await ctx.send(file = discord.File(wheel1))
    await asyncio.sleep(random.randint(2,4))
    await ctx.send(file = discord.File(wheel2))
    await asyncio.sleep(random.randint(5,7))
    await ctx.send(file = discord.File(wheel3))
    await asyncio.sleep(1)
    if payout > 1:
        pay_color = discord.Color.gold()
    elif payout > 0:
        pay_color = discord.Color.light_grey()
    else:
        pay_color = discord.Color.dark_red()
    result = discord.Embed(title = message, color = pay_color,
                           description = 'The payout for this round is ' + 
                           str(payout) + 'x your wagers.')
    result.set_footer(text = 'Thank you for playing!')
    await ctx.send(embed=result)
    payWinners(payout, wagers)
    wagers = {}

@bot.command(name='wager')
async def wager(ctx, wager: int):
    global wagers
    if dabo == True:
        user = ctx.author.nick
        if dabo_min <= wager <= dabo_max:
            if verifyWager(ctx.author.id, wager):
                wagers[ctx.author.id] = wager
                message = (user + ', you wagered ' + str(wager) + 
                           ' <:mee6Coins:1017715720961925150> latinum. Good luck!')
                result_color = discord.Color.blue()
            else:
                message = ('Sorry, ' + user + 
                           ', you do not have enough latinum to make that wager...')
                result_color = discord.Color.red()
        else:
            message = ('Your bet has not been place. Bets must be at least ' 
                       + str(dabo_min) + ' and no more than '
                       + str(dabo_max) + '.')
            result_color = discord.Color.red()
    else:
        message = 'Sorry, the tables are closed at the moment.'
        result_color = discord.Color.light_gray()
    wager_result = discord.Embed(description = message, color = result_color)
    await ctx.send(embed=wager_result)

#%% Latinum and Item Management

@bot.command(name='balance')
async def check_balance(ctx):
    user_id = ctx.author.id
    if user_id not in treasury.keys():
        treasury[user_id] = 0
    balance = treasury[user_id]
    user = ctx.author.nick
    message = (user + ', your current balance is: ' + str(balance) + 
               ' <:mee6Coins:1017715720961925150>.')
    response = discord.Embed(description = message, color = discord.Color.dark_gold())
    await ctx.send(embed=response)

@bot.command(name='shop-inventory')
async def inventory(ctx):
    message = discord.Embed(title = 'Shop Inventory',
                              description = 'Check out the amazing offerings below, ' +
                              'then use the command $buy "Item Name" to ' +
                              'purchase as many items as you can afford.\n' +
                              '----------',
                              color = discord.Color.blue())
    for item in shop_inventory:
        item_name = item + ': ' + str(shop_inventory[item]['price']) + ' <:mee6Coins:1017715720961925150>'
        item_description = shop_inventory[item]['description']
        message.add_field(name=item_name, value=item_description, inline=False)
    message.set_footer(text = 'Remember: all sales are final!')
    await ctx.send(embed=message)

@bot.command(name='my-inventory')
async def my_inventory(ctx):
    buyer = ctx.author.nick
    buyer_id = ctx.author.id
    buy_color = discord.Color.light_grey()
    if buyer_id in self_inventory.keys():
        message = discord.Embed(title = buyer + '\'s Inventory',
                                description = 'Here are your currently owned items. ' +
                                'Use some command Azure has not created yet to use your '+ 
                                'items.', color = buy_color)
        for item in self_inventory[buyer_id]:
            item_name = item
            item_description = shop_inventory[item]['description']
            message.add_field(name=item_name, value=item_description, inline=False)
    else:
        message = discord.Embed(title = buyer + '\'s Inventory',
                               description = 'You do not have any items yet.' +
                               'Use the command $buy "Item Name" to start spending ' +
                               'your <:mee6Coins:1017715720961925150>.')
    await ctx.send(embed=message)

@bot.command(name='buy')
async def buy_item(ctx, item):
    if item in shop_inventory:
        buyer = ctx.author.nick
        buyer_id = ctx.author.id
        buy_color = discord.Color.light_grey()
        if buyer_id not in treasury.keys():
            treasury[buyer_id] = 0
        if collectPayment(buyer_id, item):
            buy_message = buyer + ' has purchased ' + item + '.'
            disburseItem(buyer_id, item)
        else:
            buy_message = ('Sorry, ' + buyer + ', you do not have enough <:mee6Coins:1017715720961925150>' +
                           ' to make this purchase.')            
        message = discord.Embed(description = buy_message, color = buy_color)
        await ctx.send(embed=message)

#%% RUN BOT, RUN
treasury, shop_inventory, self_inventory = load_data()
bot.run(token)