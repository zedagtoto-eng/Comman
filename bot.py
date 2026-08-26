# ============================================================
# IMPORTS
# ============================================================

import os
import json
import discord
from discord.ext import commands


# ============================================================
# TOKEN
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set")


# ============================================================
# BOT
# ============================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="$",
    intents=intents
)


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
# Usage: $addvouch @user number
# Example: $addvouch @Drei 5
# ============================================================

@bot.command(name="addvouch")
@commands.has_permissions(manage_messages=True)
async def addvouch(ctx, member: discord.Member, amount: int):

    if member.bot:
        return await ctx.send(
            "❌ You cannot add vouches to a bot."
        )

    if amount <= 0:
        return await ctx.send(
            "❌ The number of vouches must be greater than **0**."
        )

    if amount > 100:
        return await ctx.send(
            "❌ You can only add up to **100 vouches** at once."
        )

    vouches = load_vouches()
    user_id = str(member.id)

    old_count = vouches.get(user_id, 0)
    new_count = old_count + amount

    vouches[user_id] = new_count
    save_vouches(vouches)

    embed = discord.Embed(
        title="⭐ Vouches Added",
        description=(
            f"Successfully added **{amount}** vouch(es) "
            f"to {member.mention}."
        ),
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 User",
        value=f"{member.mention}\n`{member.id}`",
        inline=False
    )

    embed.add_field(
        name="⭐ Added",
        value=f"**+{amount}**",
        inline=True
    )

    embed.add_field(
        name="⭐ Total Vouches",
        value=f"**{new_count}**",
        inline=True
    )

    embed.add_field(
        name="👮 Added By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

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
            "❌ Usage: `$addvouch @user (number)`\n"
            "Example: `$addvouch @Drei 5`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Usage: `$addvouch @user (number)`\n"
            "Example: `$addvouch @Drei 5`"
        )


# ============================================================
# $REMOVEVOUCH
# Usage: $removevouch @user number
# Example: $removevouch @Drei 2
# ============================================================

@bot.command(name="removevouch")
@commands.has_permissions(manage_messages=True)
async def removevouch(ctx, member: discord.Member, amount: int):

    if member.bot:
        return await ctx.send(
            "❌ You cannot remove vouches from a bot."
        )

    if amount <= 0:
        return await ctx.send(
            "❌ The number of vouches must be greater than **0**."
        )

    if amount > 100:
        return await ctx.send(
            "❌ You can only remove up to **100 vouches** at once."
        )

    vouches = load_vouches()
    user_id = str(member.id)

    old_count = vouches.get(user_id, 0)

    if old_count == 0:
        return await ctx.send(
            f"❌ {member.mention} has **0 vouches**."
        )

    if amount > old_count:
        return await ctx.send(
            f"❌ {member.mention} only has **{old_count} vouches**."
        )

    new_count = old_count - amount

    if new_count == 0:
        vouches.pop(user_id, None)
    else:
        vouches[user_id] = new_count

    save_vouches(vouches)

    embed = discord.Embed(
        title="⭐ Vouches Removed",
        description=(
            f"Successfully removed **{amount}** vouch(es) "
            f"from {member.mention}."
        ),
        color=discord.Color.red()
    )

    embed.add_field(
        name="👤 User",
        value=f"{member.mention}\n`{member.id}`",
        inline=False
    )

    embed.add_field(
        name="⭐ Removed",
        value=f"**-{amount}**",
        inline=True
    )

    embed.add_field(
        name="⭐ Remaining Vouches",
        value=f"**{new_count}**",
        inline=True
    )

    embed.add_field(
        name="👮 Removed By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"Vouch profile • {member.display_name}"
    )

    await ctx.send(embed=embed)


@removevouch.error
async def removevouch_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You need the **Manage Messages** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Usage: `$removevouch @user (number)`\n"
            "Example: `$removevouch @Drei 2`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Usage: `$removevouch @user (number)`\n"
            "Example: `$removevouch @Drei 2`"
        )


# ============================================================
# $VOUCHES
# Usage: $vouches @user
# ============================================================

@bot.command(name="vouches")
async def vouches_command(
    ctx,
    member: discord.Member = None
):

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

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"Vouch profile • {member.display_name}"
    )

    await ctx.send(embed=embed)


@vouches_command.error
async def vouches_error(ctx, error):

    if isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# START BOT
# ============================================================

@bot.event
async def on_ready():

    print(f"✅ Logged in as {bot.user}")
    print(
        f"✅ Bot is running in "
        f"{len(bot.guilds)} server(s)"
    )


bot.run(TOKEN)
