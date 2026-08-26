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
# ============================================================

@bot.command(name="addvouch")
@commands.has_permissions(manage_messages=True)
async def addvouch(ctx, member: discord.Member, amount: int):

    if member.bot:
        return await ctx.send("❌ You cannot add vouches to a bot.")

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
        description=f"Successfully added **{amount}** vouch(es) to {member.mention}.",
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

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Vouch profile • {member.display_name}")

    await ctx.send(embed=embed)


@addvouch.error
async def addvouch_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Messages** permission.")

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
# ============================================================

@bot.command(name="removevouch")
@commands.has_permissions(manage_messages=True)
async def removevouch(ctx, member: discord.Member, amount: int):

    if member.bot:
        return await ctx.send("❌ You cannot remove vouches from a bot.")

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
        description=f"Successfully removed **{amount}** vouch(es) from {member.mention}.",
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

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Vouch profile • {member.display_name}")

    await ctx.send(embed=embed)


@removevouch.error
async def removevouch_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Messages** permission.")

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
    embed.set_footer(text=f"Vouch profile • {member.display_name}")

    await ctx.send(embed=embed)


@vouches_command.error
async def vouches_error(ctx, error):

    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid member.")


# ============================================================
# $ROLE
# Usage: $role @user @role
# ============================================================

@bot.command(name="role")
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def role_command(ctx, member: discord.Member, role: discord.Role):

    if role.is_default():
        return await ctx.send("❌ You cannot assign the @everyone role.")

    if role.managed:
        return await ctx.send(
            "❌ You cannot manually assign a managed/integration role."
        )

    if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send(
            "❌ You cannot assign a role equal to or higher than your highest role."
        )

    if role >= ctx.guild.me.top_role:
        return await ctx.send(
            "❌ My highest role must be higher than the role you're assigning."
        )

    if role in member.roles:
        return await ctx.send(
            f"❌ {member.mention} already has {role.mention}."
        )

    try:
        await member.add_roles(
            role,
            reason=f"Role added by {ctx.author}"
        )

        embed = discord.Embed(
            title="✅ Role Added",
            description=f"{role.mention} has been added to {member.mention}.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👤 User",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="🎭 Role",
            value=role.mention,
            inline=True
        )

        embed.add_field(
            name="👮 Added By",
            value=ctx.author.mention,
            inline=False
        )

        embed.set_footer(text="ℳinstrea MM service")

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to give this role.")

    except discord.HTTPException:
        await ctx.send("❌ Discord rejected the role change.")


@role_command.error
async def role_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Roles** permission.")

    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need the **Manage Roles** permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$role @user @role`")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Usage: `$role @user @role`")


# ============================================================
# $PROMO
# Usage: $promo @user
# Promotes by ONE role
# ============================================================

@bot.command(name="promo")
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def promo(ctx, member: discord.Member):

    if member == ctx.author:
        return await ctx.send("❌ You cannot promote yourself.")

    if member == ctx.guild.owner:
        return await ctx.send("❌ You cannot promote the server owner.")

    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send(
            "❌ You cannot promote someone with an equal or higher role."
        )

    bot_role = ctx.guild.me.top_role

    manageable_roles = [
        role for role in ctx.guild.roles
        if role != ctx.guild.default_role
        and not role.managed
        and role < bot_role
    ]

    manageable_roles.sort(key=lambda r: r.position)

    current_role = member.top_role

    next_roles = [
        role for role in manageable_roles
        if role.position > current_role.position
    ]

    if not next_roles:
        return await ctx.send(
            "❌ There is no higher role available to promote this user."
        )

    next_role = next_roles[0]

    try:
        await member.add_roles(
            next_role,
            reason=f"Promoted by {ctx.author}"
        )

        embed = discord.Embed(
            title="⬆️ Member Promoted",
            description=f"{member.mention} has been promoted by **one role**.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👤 User",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="🎭 New Role",
            value=next_role.mention,
            inline=True
        )

        embed.add_field(
            name="👮 Promoted By",
            value=ctx.author.mention,
            inline=False
        )

        embed.set_footer(text="ℳinstrea MM service")

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "❌ I cannot give that role. Make sure my bot role is higher."
        )

    except discord.HTTPException:
        await ctx.send("❌ Discord rejected the promotion.")


@promo.error
async def promo_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Roles** permission.")

    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need the **Manage Roles** permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$promo @user`")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid member.")


# ============================================================
# $DEMO
# Usage: $demo @user
# Demotes by ONE role
# ============================================================

@bot.command(name="demo")
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def demo(ctx, member: discord.Member):

    if member == ctx.author:
        return await ctx.send("❌ You cannot demote yourself.")

    if member == ctx.guild.owner:
        return await ctx.send("❌ You cannot demote the server owner.")

    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send(
            "❌ You cannot demote someone with an equal or higher role."
        )

    bot_role = ctx.guild.me.top_role

    manageable_roles = [
        role for role in ctx.guild.roles
        if role != ctx.guild.default_role
        and not role.managed
        and role < bot_role
    ]

    manageable_roles.sort(key=lambda r: r.position)

    current_role = member.top_role

    previous_roles = [
        role for role in manageable_roles
        if role.position < current_role.position
    ]

    if not previous_roles:
        return await ctx.send(
            "❌ There is no lower role available to demote this user."
        )

    previous_role = previous_roles[-1]

    try:
        if current_role != ctx.guild.default_role:
            await member.remove_roles(
                current_role,
                reason=f"Demoted by {ctx.author}"
            )

        if previous_role != ctx.guild.default_role:
            await member.add_roles(
                previous_role,
                reason=f"Demoted by {ctx.author}"
            )

        embed = discord.Embed(
            title="⬇️ Member Demoted",
            description=f"{member.mention} has been demoted by **one role**.",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="👤 User",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="🎭 Previous Role",
            value=current_role.mention,
            inline=True
        )

        embed.add_field(
            name="🎭 New Role",
            value=previous_role.mention,
            inline=True
        )

        embed.add_field(
            name="👮 Demoted By",
            value=ctx.author.mention,
            inline=False
        )

        embed.set_footer(text="ℳinstrea MM service")

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "❌ I cannot change that user's roles. Make sure my bot role is higher."
        )

    except discord.HTTPException:
        await ctx.send("❌ Discord rejected the role change.")


@demo.error
async def demo_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Roles** permission.")

    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I need the **Manage Roles** permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$demo @user`")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid member.")


# ============================================================
# START BOT
# ============================================================

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"✅ Bot is running in {len(bot.guilds)} server(s)")


bot.run(TOKEN)
