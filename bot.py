# ============================================================
# IMPORTS / TOKEN
# ============================================================

import os
import json
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set")


# ============================================================
# VOUCH SYSTEM
# ============================================================

VOUCH_FILE = "vouches.json"


def load_vouches():
    if not os.path.exists(VOUCH_FILE):
        return {}

    try:
        with open(VOUCH_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_vouches(data):
    with open(VOUCH_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ============================================================
# $ADDVOUCH
# ============================================================

@bot.command(name="addvouch")
@commands.has_permissions(manage_messages=True)
async def addvouch(ctx, member: discord.Member):

    if member.bot:
        return await ctx.send("❌ You cannot add a vouch to a bot.")

    vouches = load_vouches()
    user_id = str(member.id)

    if user_id not in vouches:
        vouches[user_id] = 0

    vouches[user_id] += 1
    save_vouches(vouches)

    embed = discord.Embed(
        title="⭐ Vouch Added",
        description=f"A vouch has been added to {member.mention}.",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="⭐ Total Vouches",
        value=f"**{vouches[user_id]}**",
        inline=False
    )

    embed.add_field(
        name="👮 Added By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text=f"Vouch profile • {member.display_name}"
    )

    await ctx.send(embed=embed)


@addvouch.error
async def addvouch_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You need the **Manage Messages** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Usage: `$addvouch @user`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# $VOUCHES
# ============================================================

@bot.command(name="vouches")
async def vouches_command(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    vouches = load_vouches()
    count = vouches.get(str(member.id), 0)

    embed = discord.Embed(
        title="⭐ Vouches",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="⭐ Total Vouches",
        value=f"**{count}**",
        inline=False
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text=f"Vouch profile • {member.display_name}"
    )

    await ctx.send(embed=embed)


@vouches_command.error
async def vouches_error(ctx, error):

    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid member.")


# ============================================================
# START BOT
# ============================================================

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"✅ Bot is running in {len(bot.guilds)} server(s)")


bot.run(TOKEN)
