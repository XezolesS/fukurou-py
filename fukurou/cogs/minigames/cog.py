import discord
from discord.ext import commands
from discord.ext.bridge import BridgeContext
from discord.ext.bridge import BridgeApplicationContext
import random

class MinigamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command()
    async def roll_the_dice(self, ctx: BridgeApplicationContext):
        dice_roll = random.randint(1, 6)
        dice_image = discord.File(f"./fukurou/resources/minigames/dice/dice_{dice_roll}.png")

        await ctx.respond(file = dice_image)
