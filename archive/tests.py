# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 22:00:43 2022

@author: AzureRogue
"""

@client.command()
async def embed(ctx):
    embed=discord.Embed(
    title="Text Formatting",
        url="https://realdrewdata.medium.com/",
        description="Here are some ways to format text",
        color=discord.Color.blue())
    embed.set_author(name="RealDrewData", url="https://twitter.com/RealDrewData", icon_url="https://cdn-images-1.medium.com/fit/c/32/32/1*QVYjh50XJuOLQBeH_RZoGw.jpeg")
    #embed.set_author(name=ctx.author.display_name, url="https://twitter.com/RealDrewData", icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://i.imgur.com/axLm3p6.jpeg")
    embed.add_field(name="*Italics*", value="Surround your text in asterisks (\*)", inline=False)
    embed.add_field(name="**Bold**", value="Surround your text in double asterisks (\*\*)", inline=False)
    embed.add_field(name="__Underline__", value="Surround your text in double underscores (\_\_)", inline=False)
    embed.add_field(name="~~Strikethrough~~", value="Surround your text in double tildes (\~\~)", inline=False)
    embed.add_field(name="`Code Chunks`", value="Surround your text in backticks (\`)", inline=False)
    embed.add_field(name="Blockquotes", value="> Start your text with a greater than symbol (\>)", inline=False)
    embed.add_field(name="Secrets", value="||Surround your text with double pipes (\|\|)||", inline=False)
    embed.set_footer(text="Learn more here: realdrewdata.medium.com")
    await ctx.send(embed=embed)

# Testing out the wheel results / EV
# Odds correct / agreed for Quark Dabo / DS9 Dabo / Swirl Dabo
# Regular Dabos not counting up correctly - mine counts 1.18%, STO says 1.68%
# This is also counting special dabos atm... 
# Ah, it was mis-counting double swirls
all_results = [[x, y, z] for x in wheel for y in wheel for z in inner_wheel]
assert len(all_results) == 36*36*36
all_payouts = [determineWinnings(x) for x in all_results]
# STO Claims 88.01% EV - I get 88.295
# It seems the 2x payouts (Counts == 3) are the error here
# Look for problems with swirl or blackhole?
# Nope - getting the exact correct amount of 2x payout results - I think it's
# just a long rounding error
my_ev = sum([x[1] for x in all_payouts])/len(all_payouts)

test_results = []
for result in all_results:
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
    if matches['counts'] == 3 and (matches['colors'] < 2 or matches['shapes'] < 3):
        test_results.append(result)

'''
    uniques = ['swirl', 'quark', 'ds9'] #, 'blackhole']
    counts = [x.split('-')[0] for x in result]
    if len([x.split('-') for x in result][1]) == 1:
        colors = [x.split('-') for x in result][1]
    else:
        colors = [x.split('-')[1] for x in result[:-1]]
    shapes = [x.split('-')[-1] for x in result]
    matches = {}
    matches['counts'] = (max(list({i:counts.count(i) for i in counts if i not in uniques}.values()) + [0]) +
                         counts.count('swirl') - max([0,counts.count('blackhole')-1]))
    matches['colors'] = (max(list({i:colors.count(i) for i in colors if i not in uniques}.values()) + [0]) +
                         colors.count('swirl') - max([0,colors.count('blackhole')-1]))
    matches['shapes'] = (max(list({i:shapes.count(i) for i in shapes if i not in uniques}.values()) + [0]) +
                         shapes.count('swirl') - max([0,shapes.count('blackhole')-1]))
    if matches['counts'] == 3 and matches['colors'] < 2 and matches['shapes'] < 3:


    temporary removal to test new version
    matches['counts'] = max({i:counts.count(i) + counts.count('swirl') - 
                             max([0,(counts.count('blackhole')-1)]) for i in counts}.values())
    matches['colors'] = max({i:colors.count(i) + colors.count('swirl') - 
                             max([0,(colors.count('blackhole')-1)]) for i in colors}.values())
    matches['shapes'] = max({i:shapes.count(i) + shapes.count('swirl') - 
                             max([0,(shapes.count('blackhole')-1)]) for i in shapes}.values())


@bot.command(name='Dabo')
async def dabo(ctx):
    global dabo
    global wagers
    roles = [str(role) for role in ctx.author.roles]
    if 'Night Shift' in roles:
        wagers = {}
        await ctx.send('The Dabo table is open! Use $Wager <amount> to place your bets!')
        dabo = True
        await asyncio.sleep(10) # How long the table stays open
        await ctx.send('Betting is closed! Play again next time!')
        dabo = False
        await asyncio.sleep(2)
        await ctx.send('Collecting all the wagers now.')
        collectWagers(wagers)
        await asyncio.sleep(3)
        await ctx.send('Spinning the wheel!')
        result = spinWheel()
        message, payout = determineWinnings(result)
        await asyncio.sleep(5)
        wheel1, wheel2, wheel3 = resultImages(result)
        await ctx.send(content = 'Wheel 1', file=discord.File(wheel1))
        await asyncio.sleep(3) # For drama - maybe make it random?
        await ctx.send(content = 'Wheel 2', file=discord.File(wheel2))
        await asyncio.sleep(4) # For drama - maybe make it random?
        await ctx.send(content = 'Wheel 3', file=discord.File(wheel3))
        await asyncio.sleep(1)
        await ctx.send(message)
        await ctx.send('The payout for this round is ' + str(payout) + 'x your wagers.')
        payWinners(payout, wagers)
        await asyncio.sleep(3)
        await ctx.send('Thanks for playing!')
        wagers = {}

@bot.command(name='Wager')
async def wager(ctx, wager: int):
    global dabo
    global wagers
    if dabo == True:
        if verifyPayment(ctx.author.id, wager):
            wagers[ctx.author.id] = wager
            user = ctx.author.name
            await ctx.send(user + ', you wagered ' + str(wager) + ' latinum. Good luck!')
        else:
            await ctx.send('Sorry, ' + ctx.author.name + ', you do not have enough latinum to make that wager...')
    else:
        await ctx.send('Sorry, the tables are closed at the moment.')

@bot.command(name='CheckBalance')
async def check_balance(ctx):
    balance = treasury[ctx.author.id]
    user = ctx.author.name
    await ctx.send(user + ' your current balance is ' + str(balance) + '.')

@bot.command(name='TestDabo')
async def test_dabo(ctx, wager: int):
    result = spinWheel()
    message, payout = determineWinnings(result)
    await ctx.send(message)

@bot.command(name='UserName')
async def username(ctx):
    await ctx.send(ctx.author.id)

'''