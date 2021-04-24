import discord
import random
from discord.ext import commands
import sqlite3
import asyncio

CREATOR = 834857950216323072
USER_NAME = ""
link_group = 'https://discord.gg/AkPYyJYYT4'
MONEY = 0
INFO = open("info.txt", "r", encoding='utf-8').read()
HI = open("hello.txt", "r", encoding='utf-8').read()
RULE = open("rule.txt", "r", encoding='utf-8').read()
RULE_BOMB = open("rule_bomb.txt", "r", encoding='utf-8').read()
SHOP = open("shop.txt", "r", encoding='utf-8').read()
TOKEN = "ODM0ODU3OTUwMjE2MzIzMDcy.YIHADg.n-bdqxT5sGWb-5ApTJyaxSeiRco"
MENU_CASINO = False
START = True
MENU_MINES = False
bot = commands.Bot(intents=discord.Intents.all(), command_prefix='!')
con = sqlite3.connect("player.sqlite")
cur = con.cursor()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=discord.Embed(description=f'{HI}', color=0xc00c0c))
    elif isinstance(error, commands.BadArgument):
        await ctx.send(embed=discord.Embed(description=f'Неверный ввод данных :information_source:', color=0xc00c0c))


@bot.event
async def on_ready():
    global MONEY
    while True:
        game = discord.Game("!information")
        await bot.change_presence(activity=game)
        await asyncio.sleep(86400)
        cur.execute(f"""UPDATE money
                        SET euros = euros + 250""")
        con.commit()
        MONEY += 250


@bot.command(name='information')
async def info(message):
    if MENU_MINES is True:
        await message.channel.send(f'```{RULE_BOMB}```')
    elif MENU_CASINO is True:
        await message.channel.send(f'```{RULE}```')
    else:
        await message.channel.send(f'```{INFO}```')


class Start(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='casino')
    async def casino(self, message):
        global MENU_CASINO, START, MONEY, USER_NAME
        if MENU_CASINO is False:
            d = 0
            a = cur.execute(f"""SELECT discord_id FROM money""").fetchall()
            for i in range(len(a)):
                c = str(a[i][0][0:-5]) + str(a[i][0][-5:])
                if c == str(message.author):
                    MONEY = cur.execute(f"""SELECT euros FROM money
                        WHERE discord_id = '{message.author}'""").fetchall()[0][0]
                    d = 1
            if d == 0:
                cur.execute(f"""INSERT INTO money VALUES('{message.author}',250, 0)""")
                con.commit()
                MONEY = 250
            await message.channel.send(
                f">>> Привет, это режим казино, сейчас твой счёт составляет: {MONEY} :euro:"
                f"\nЕсли хотите начать игру напишите !start, чтобы выйти напишите !exit")
            USER_NAME = message.author
            MENU_CASINO = True
            START = True
            bot.add_cog(Casino(bot))


class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='start')
    async def start(self, message):
        global START
        if MENU_CASINO is True and START is True:
            START = False
            await message.channel.send(f'```Поехали! Сейчас я расскажу вкратце в чём суть! \n{RULE}```')
            bot.add_cog(Play(bot))

    @commands.command(name='exit')
    async def exit(self, message):
        global MENU_CASINO
        if MENU_CASINO is True:
            await message.channel.send(f'`Вы вышли из режима казино!`')
            cur.execute(f"""UPDATE money
                            SET euros = {MONEY}
                            WHERE discord_id = '{message.author}'""")
            con.commit()
            MENU_CASINO = False


class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dice')
    async def dice(self, ctx, percent=0, bet=0):
        global MONEY
        number = 10000
        if percent > 95 and bet > MONEY or bet > MONEY and percent < 1:
            await ctx.channel.send(embed=discord.Embed(
                description=f'Введите шансы от 1% до 95% и другую сумму, так как у вас недостаточно средств :euro:!',
                color=0xccc))
        elif percent > 95 and bet < 100 or bet > 10000 or percent < 1 and bet < 100 or bet > 10000:
            await ctx.channel.send(embed=discord.Embed(
                description=f'Введите шансы от 1% до 95% и ставку от 100 до 10000 :euro:!', color=0xccc))
        elif percent > 95 or percent < 1:
            await ctx.channel.send(embed=discord.Embed(
                description=f'Введите шансы от 1% до 95%!', color=0xccc))
        elif bet < 100 or bet > 10000:
            await ctx.channel.send(embed=discord.Embed(
                description=f'Введите ставку от 100 до 10000 :euro:!', color=0xccc))
        elif bet > MONEY:
            await ctx.channel.send(embed=discord.Embed(
                description=f'У вас недостаточно средств :euro:!', color=0xccc))
        else:
            if bet >= 100 and bet <= 10000 and bet <= MONEY:
                a = random.randint(1, 10000)
                if a < percent * 100:
                    MONEY += round(100 / percent * bet)
                    await ctx.channel.send(embed=discord.Embed(
                        description=f'Вы выиграли {round(100 / percent * bet)} :euro:! Выпало число {a}!',
                        color=0xcc00c))
                else:
                    MONEY -= bet
                    await ctx.channel.send(embed=discord.Embed(
                        description=f'Вы проиграли {bet} :euro:! Выпало число {a}!', color=0xc00c0c))

    @commands.command(name='shop')
    async def shop(self, message):
        await message.channel.send(f'```{SHOP}```')
        bot.add_cog(Shop(bot))

    @commands.command(name='coin')
    async def coin(self, ctx, coin='', bet=0):
        global MONEY
        if bet >= 250 and bet <= 1000000 and bet <= MONEY and coin == "орёл" or coin == "решка":
            if coin == 'орёл':
                coin_game = random.choices([coin, 'решка'], weights=[50, 50])[0]
            elif coin == 'решка':
                coin_game = random.choices([coin, 'орёл'], weights=[50, 50])[0]
            if coin == coin_game:
                MONEY += bet
                if coin == "орёл":
                    await ctx.channel.send(embed=discord.Embed(
                        description=f'Вы выиграли {bet} :euro:! Выпал {coin_game} :coin:!',
                        color=0xcc00c))
                else:
                    await ctx.channel.send(embed=discord.Embed(
                        description=f'Вы выиграли {bet} :euro:! Выпал {coin_game} :coin:!',
                        color=0xcc00c))
            else:
                MONEY -= bet
                if coin == "орёл":
                    await ctx.channel.send(embed=discord.Embed(
                        description=f'Вы проиграли {bet} :euro:! Выпал {coin_game} :coin:!',
                        color=0xc00c0c))
                else:
                    await ctx.channel.send(embed=discord.Embed(
                        description=f'Вы проиграли {bet} :euro:! Выпал {coin_game} :coin:!',
                        color=0xc00c0c))
        elif (bet < 250 and coin != "орёл" and coin != "решка") or (
                bet > 1000000 and coin != "орёл" and coin != "решка"):
            await ctx.channel.send(
                embed=discord.Embed(description=f'Выберите орёл или решку :coin: и ставки от 250 до 1000000 :euro:!',
                                    color=0xccc))
        elif bet > MONEY and coin != "орёл" and coin != "решка":
            await ctx.channel.send(
                embed=discord.Embed(description=f'Выберите орёл или решку :coin: и у вас недостаточно средств :euro:!',
                                    color=0xccc))
        elif (bet < 250 and coin == "орёл" or coin == "решка") or (bet > 1000000 and coin == "орёл" or coin == "решка"):
            await ctx.channel.send(embed=discord.Embed(description=f'Ставки от 250 до 1000000 :euro:!', color=0xccc))
        elif bet > MONEY:
            await ctx.channel.send(embed=discord.Embed(description=f'Недостаточно средств :euro:!', color=0xccc))
        else:
            await ctx.channel.send(embed=discord.Embed(description=f'Выберите орёл или решку :coin:!', color=0xccc))

    @commands.command(name='mines')
    async def mines(self, ctx):
        await ctx.channel.send(embed=discord.Embed(
            description=f'Введите !play, а затем количество бомб от 3 до 20 :boom: и вашу ставку :euro:!',
            color=0x8b4513))
        bot.add_cog(Mine(bot))

    @commands.command(name='balance')
    async def balance(self, ctx):
        await ctx.channel.send(embed=discord.Embed(
            description=f'Ваш баланс: {MONEY} :euro:!', color=0xdaa520))

    @commands.command(name='get_euros')
    async def get_euro(self, ctx):
        await ctx.channel.send(embed=discord.Embed(
            description=f'Ваш баланс на данный момент: {MONEY} :euro:!'
                        f'\nПодпишитесь на группу и получите 500 :euro:! Для этого надо написать !group'
                        f'\nТакже каждый день в 12:00 каждому игроку выдаётся 250 :euro:!',
            color=0xdaa520))

    @commands.command(name='group')
    async def get_group(self, ctx):
        await ctx.channel.send(embed=discord.Embed(
            description=f'Ссылка на группу {link_group}, когда подпишитесь напишите !ok', color=0xdaa520))

    @commands.command(name='ok')
    async def ok(self, ctx):
        global MONEY
        a = cur.execute(f"""SELECT group_ds FROM money""").fetchall()
        c = cur.execute(f"""SELECT discord_id FROM money""").fetchall()
        r = 0
        for i in range(len(a)):
            b = a[i][0]
            d = c[i][0]
            if b == 1 and str(USER_NAME) == str(d):
                await ctx.channel.send(embed=discord.Embed(
                    description=f"Вы уже подписаны!", color=0xdaa520))
                r = 1
        if r != 1:
            for guild in bot.guilds:
                for member in guild.members:
                    if str(member) == str(USER_NAME):
                        cur.execute(f"""UPDATE money SET group_ds = 1 WHERE discord_id = '{str(USER_NAME)}'""")
                        con.commit()
                        a = cur.execute(f"""SELECT group_ds FROM money""").fetchall()
                        c = cur.execute(f"""SELECT discord_id FROM money""").fetchall()
            for i in range(len(a)):
                b = a[i][0]
                d = c[i][0]
                print(b, d)
                if b == 0 and str(d) == str(USER_NAME):
                    await ctx.channel.send(embed=discord.Embed(
                        description=f"Вы не подписались, попробуйте ещё раз!", color=0xdaa520))
                elif b == 1 and str(d) == str(USER_NAME):
                    await ctx.channel.send(embed=discord.Embed(
                        description=f"Вы подписались, награда скоро придёт :euro:!", color=0xdaa520))
                    MONEY += 500


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='curator')
    async def curator(self, ctx):
        global MONEY
        if MONEY < 10000000:
            await ctx.channel.send(embed=discord.Embed(
                description=f'У вас недостаточно средств :euro:!', color=0xccc))
        else:
            roles = open('add_role.txt', 'w')
            roles.write(f'Выдать роль куратора {USER_NAME}')
            roles.close()
            await ctx.channel.send(embed=discord.Embed(
                description=f'Вы приобрели роль куратора, вам её должен выдать создатель в течение 24 часов!',
                color=0xcc00c))
            MONEY -= 10000000

    @commands.command(name='admin')
    async def admin(self, ctx):
        global MONEY
        if MONEY < 1000000:
            await ctx.channel.send(embed=discord.Embed(
                description=f'У вас недостаточно средств :euro:!', color=0xccc))
        else:
            roles = open('add_role.txt', 'w')
            roles.write(f'Выдать роль администратора {USER_NAME}')
            roles.close()
            await ctx.channel.send(embed=discord.Embed(
                description=f'Вы приобрели роль администратора, вам её должен выдать создатель в течение 24 часов!',
                color=0xcc00c))
            MONEY -= 1000000

    @commands.command(name='jun_adm')
    async def jun_adm(self, ctx):
        global MONEY
        if MONEY < 600000:
            await ctx.channel.send(embed=discord.Embed(
                description=f'У вас недостаточно средств :euro:!', color=0xccc))
        else:
            roles = open('add_role.txt', 'w')
            roles.write(f'Выдать роль младшего администратора {USER_NAME}')
            roles.close()
            await ctx.channel.send(embed=discord.Embed(
                description=f'Вы приобрели роль младшего администратора, вам её должен выдать создатель в течение 24 часов!',
                color=0xcc00c))
            MONEY -= 600000

    @commands.command(name='moderator')
    async def moderator(self, ctx):
        global MONEY
        if MONEY < 500000:
            await ctx.channel.send(embed=discord.Embed(
                description=f'У вас недостаточно средств :euro:!', color=0xccc))
        else:
            roles = open('add_role.txt', 'w')
            roles.write(f'Выдать роль модератора {USER_NAME}')
            roles.close()
            await ctx.channel.send(embed=discord.Embed(
                description=f'Вы приобрели роль модератора, вам её должен выдать создатель в течение 24 часов!',
                color=0xcc00c))
            MONEY -= 500000

    @commands.command(name='jun_mod')
    async def jun_mod(self, ctx):
        global MONEY
        if MONEY < 300000:
            await ctx.channel.send(embed=discord.Embed(
                description=f'У вас недостаточно средств :euro:!', color=0xccc))
        else:
            roles = open('add_role.txt', 'w')
            roles.write(f'Выдать роль младшего модератора {USER_NAME}')
            roles.close()
            await ctx.channel.send(embed=discord.Embed(
                description=f'Вы приобрели роль младшего модератора, вам её должен выдать создатель в течение 24 часов!',
                color=0xcc00c))
            MONEY -= 300000

    @commands.command(name='vip')
    async def vip(self, ctx):
        global MONEY
        if MONEY < 100000:
            await ctx.channel.send(embed=discord.Embed(
                description=f'У вас недостаточно средств :euro:!', color=0xccc))
        else:
            roles = open('add_role.txt', 'w')
            roles.write(f'Выдать роль vip {USER_NAME}')
            roles.close()
            await ctx.channel.send(embed=discord.Embed(
                description=f'Вы приобрели роль vip, вам её должен выдать создатель в течение 24 часов!',
                color=0xcc00c))
            MONEY -= 100000


class Mine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.a = []
        self.bet = 0
        self.mines = 0

    @commands.command(name='play')
    async def start_play(self, ctx, mines=0, bet=0):
        global MENU_MINES
        if MENU_MINES is False:
            self.a = [['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''],
                      ['', '', '', '', '']]
            if mines > 20 and bet > MONEY or mines < 3 and bet > MONEY:
                await ctx.channel.send(embed=discord.Embed(
                    description=f'Введите количество мин от 3 до 20 :boom: и у вас не хватает средств :euro:!',
                    color=0xccc))
            elif (mines > 20 and bet < 100 or mines > 20 and bet > 100000000) or (
                    mines < 3 and bet < 100 or mines < 3 and bet > 100000000):
                await ctx.channel.send(embed=discord.Embed(
                    description=f'Введите количество мин от 3 до 20 :boom: и ставку от 100 до 100000000 :euro:!',
                    color=0xccc))
            elif mines > 20 or mines < 3:
                await ctx.channel.send(embed=discord.Embed(
                    description=f'Введите количество мин от 3 до 20 :boom:!',
                    color=0xccc))
            elif bet < 100 or bet > 100000000:
                await ctx.channel.send(embed=discord.Embed(
                    description=f'Введите ставку от 100 до 100000000 :euro:!',
                    color=0xccc))
            elif bet > MONEY:
                await ctx.channel.send(embed=discord.Embed(
                    description=f'У вас недостаточно средств :euro:!',
                    color=0xccc))
            else:
                self.bet = bet
                self.mines = mines
                l = list(range(0, 25))
                random.shuffle(l)
                for i in range(self.mines):
                    self.a[l[i] // 5][l[i] - (l[i] // 5 * 5)] = ":boom:"
                for j in range(5):
                    for h in range(5):
                        if self.a[j][h] != ":boom:":
                            self.a[j][h] = ":gem:"
                await ctx.channel.send(f':brown_square: ' * 5)
                await ctx.channel.send(f':brown_square: ' * 5)
                await ctx.channel.send(f':brown_square: ' * 5)
                await ctx.channel.send(f':brown_square: ' * 5)
                await ctx.channel.send(f':brown_square: ' * 5)
                await ctx.channel.send(embed=discord.Embed(
                    description=f'Введите !choose, а затем столбец и строчку поля!', color=0xcc00c))
                MENU_MINES = True

    @commands.command(name='choose')
    async def choose(self, ctx, y=0, x=0):
        global MONEY, MENU_MINES
        if y < 1 or x > 5 or x < 1 or y > 5:
            await ctx.channel.send(embed=discord.Embed(
                description=f'Неверные координаты!', color=0xccc))
        else:
            for k in range(5):
                h = self.a[k][0] + self.a[k][1] + self.a[k][2] + self.a[k][3] + self.a[k][4]
                await ctx.channel.send(h)
            if self.a[int(x) - 1][int(y) - 1] == ':boom:':
                await ctx.channel.send(embed=discord.Embed(
                    description=f'Вы проиграли {self.bet} :euro:!', color=0xc00c0c))
                MONEY -= self.bet
            elif self.a[int(x) - 1][int(y) - 1] == ':gem:':
                await ctx.channel.send(embed=discord.Embed(
                    description=f'Вы выиграли {round(self.bet * self.mines / 25)} :euro:!', color=0xcc00c))
                MONEY += round(self.bet * self.mines / 25)
            MENU_MINES = False


bot.add_cog(Start(bot))
bot.run(TOKEN)
