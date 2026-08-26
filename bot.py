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
# ADD VOUCH
# $addvouch @user 1
# ============================================================

@bot.command(name="addvouch")
@commands.has_permissions(manage_messages=True)
async def addvouch(ctx, member: discord.Member, amount: int = 1):

    if member.bot:
        return await ctx.send("❌ You cannot add a vouch to a bot.")

    if amount <= 0:
        return await ctx.send("❌ The number must be greater than 0.")

    if amount > 1000:
        return await ctx.send("❌ You cannot add more than **1000** vouches at once.")

    vouches = load_vouches()
    user_id = str(member.id)

    vouches[user_id] = vouches.get(user_id, 0) + amount
    save_vouches(vouches)

    embed = discord.Embed(
        title="⭐ Vouch Added",
        description=f"Added **{amount}** vouch(es) to {member.mention}.",
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
            "❌ Usage: `$addvouch @user (number)`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Usage: `$addvouch @user (number)`"
        )


# ============================================================
# REMOVE VOUCH
# $removevouch @user 1
# ============================================================

@bot.command(name="removevouch")
@commands.has_permissions(manage_messages=True)
async def removevouch(ctx, member: discord.Member, amount: int = 1):

    if amount <= 0:
        return await ctx.send("❌ The number must be greater than 0.")

    vouches = load_vouches()
    user_id = str(member.id)

    current = vouches.get(user_id, 0)

    if current <= 0:
        return await ctx.send(
            f"❌ {member.mention} has **0 vouches**."
        )

    removed = min(amount, current)
    new_total = current - removed

    if new_total <= 0:
        vouches.pop(user_id, None)
    else:
        vouches[user_id] = new_total

    save_vouches(vouches)

    embed = discord.Embed(
        title="🗑️ Vouch Removed",
        description=f"Removed **{removed}** vouch(es) from {member.mention}.",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="⭐ Total Vouches",
        value=f"**{new_total}**",
        inline=False
    )

    embed.add_field(
        name="👮 Removed By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(url=member.display_avatar.url)

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
            "❌ Usage: `$removevouch @user (number)`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Usage: `$removevouch @user (number)`"
        )


# ============================================================
# VOUCHES
# $vouches @user
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
        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# ROLE COMMAND
# $role @user @role
# ============================================================

@bot.command(name="role")
@commands.has_permissions(manage_roles=True)
async def role_command(ctx, member: discord.Member, role: discord.Role):

    if role.is_default():
        return await ctx.send(
            "❌ You cannot give the @everyone role."
        )

    if role.managed:
        return await ctx.send(
            "❌ You cannot manually assign a managed role."
        )

    if role >= ctx.guild.me.top_role:
        return await ctx.send(
            "❌ I cannot manage this role because it is above my highest role."
        )

    if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send(
            "❌ You cannot assign a role equal to or higher than your highest role."
        )

    if role in member.roles:
        return await ctx.send(
            f"❌ {member.mention} already has {role.mention}."
        )

    try:
        await member.add_roles(
            role,
            reason=f"Role command used by {ctx.author}"
        )

        embed = discord.Embed(
            title="🎭 Role Added",
            color=discord.Color.from_rgb(255, 20, 180)
        )

        embed.add_field(
            name="👤 User",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="🎭 Role",
            value=role.mention,
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=ctx.author.mention,
            inline=False
        )

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "❌ I don't have permission to give that role."
        )


@role_command.error
async def role_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You need the **Manage Roles** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Usage: `$role @user @role`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Usage: `$role @user @role`"
        )


# ============================================================
# PROMOTE
# $promo @user
# ============================================================

@bot.command(name="promo")
@commands.has_permissions(manage_roles=True)
async def promo(ctx, member: discord.Member):

    roles = sorted(
        [
            r for r in ctx.guild.roles
            if not r.is_default()
            and not r.managed
            and r < ctx.guild.me.top_role
        ],
        key=lambda r: r.position
    )

    current_role = member.top_role

    higher_roles = [
        r for r in roles
        if r.position > current_role.position
        and r.position < ctx.guild.me.top_role.position
    ]

    if not higher_roles:
        return await ctx.send(
            "❌ There is no higher role I can give this user."
        )

    next_role = higher_roles[0]

    if next_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send(
            "❌ You cannot promote someone to a role equal to or above your highest role."
        )

    try:
        await member.add_roles(
            next_role,
            reason=f"Promoted by {ctx.author}"
        )

        embed = discord.Embed(
            title="⬆️ User Promoted",
            description=f"{member.mention} has been promoted.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="🎭 New Role",
            value=next_role.mention,
            inline=False
        )

        embed.add_field(
            name="👮 Promoted By",
            value=ctx.author.mention,
            inline=False
        )

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "❌ I don't have permission to give that role."
        )


@promo.error
async def promo_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You need the **Manage Roles** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Usage: `$promo @user`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# DEMOTE
# $demo @user
# ============================================================

@bot.command(name="demo")
@commands.has_permissions(manage_roles=True)
async def demo(ctx, member: discord.Member):

    current_role = member.top_role

    if current_role.is_default():
        return await ctx.send(
            "❌ This user has no role to demote."
        )

    if current_role >= ctx.guild.me.top_role:
        return await ctx.send(
            "❌ I cannot remove this role because it is above my highest role."
        )

    if current_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send(
            "❌ You cannot demote someone whose role is equal to or higher than yours."
        )

    roles_below = [
        r for r in ctx.guild.roles
        if not r.is_default()
        and not r.managed
        and r.position < current_role.position
        and r.position < ctx.guild.me.top_role.position
    ]

    roles_below.sort(
        key=lambda r: r.position,
        reverse=True
    )

    try:
        await member.remove_roles(
            current_role,
            reason=f"Demoted by {ctx.author}"
        )

        new_role = roles_below[0] if roles_below else None

        if new_role:
            await member.add_roles(
                new_role,
                reason=f"Demoted by {ctx.author}"
            )

        embed = discord.Embed(
            title="⬇️ User Demoted",
            description=f"{member.mention} has been demoted.",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="❌ Removed Role",
            value=current_role.mention,
            inline=False
        )

        embed.add_field(
            name="🎭 New Role",
            value=new_role.mention if new_role else "No lower role",
            inline=False
        )

        embed.add_field(
            name="👮 Demoted By",
            value=ctx.author.mention,
            inline=False
        )

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "❌ I don't have permission to change this user's roles."
        )


@demo.error
async def demo_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You need the **Manage Roles** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Usage: `$demo @user`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# USER PROFILE
# $w @user
# ============================================================

@bot.command(name="w")
async def profile(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    roles = [
        role.mention
        for role in reversed(member.roles)
        if not role.is_default()
    ]

    role_text = ", ".join(roles) if roles else "No roles"

    if len(role_text) > 1024:
        role_text = role_text[:1020] + "..."

    embed = discord.Embed(
        title=f"👤 {member.display_name}",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(
        name="👤 User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="📛 Username",
        value=str(member),
        inline=True
    )

    embed.add_field(
        name="🆔 ID",
        value=str(member.id),
        inline=True
    )

    embed.add_field(
        name="📅 Joined Guild",
        value=discord.utils.format_dt(
            member.joined_at,
            style="F"
        ) if member.joined_at else "Unknown",
        inline=False
    )

    embed.add_field(
        name="🗓️ Account Created",
        value=discord.utils.format_dt(
            member.created_at,
            style="F"
        ),
        inline=False
    )

    embed.add_field(
        name=f"🎭 Roles [{len(member.roles) - 1}]",
        value=role_text,
        inline=False
    )

    embed.add_field(
        name="⭐ Vouches",
        value=str(load_vouches().get(str(member.id), 0)),
        inline=False
    )

    embed.set_footer(
        text=f"User profile • {member.display_name}"
    )

    await ctx.send(embed=embed)


@profile.error
async def profile_error(ctx, error):

    if isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# FILL
# $fill
#
# Gives the command user every assignable role below
# their highest role and below the bot's highest role.
# ============================================================

@bot.command(name="fill")
@commands.has_permissions(manage_roles=True)
async def fill(ctx):

    member = ctx.author
    bot_top = ctx.guild.me.top_role

    eligible_roles = [
        role for role in ctx.guild.roles
        if not role.is_default()
        and not role.managed
        and role < member.top_role
        and role < bot_top
    ]

    eligible_roles.sort(
        key=lambda r: r.position
    )

    added = []

    for role in eligible_roles:

        if role in member.roles:
            continue

        try:
            await member.add_roles(
                role,
                reason=f"Fill command used by {ctx.author}"
            )
            added.append(role)

        except discord.Forbidden:
            continue

    if not added:
        return await ctx.send(
            "❌ There are no roles below your highest role that I can add."
        )

    role_text = ", ".join(role.mention for role in added)

    if len(role_text) > 4000:
        role_text = role_text[:3990] + "..."

    embed = discord.Embed(
        title="🎭 Roles Filled",
        description=f"{ctx.author.mention}, the available roles below your highest role have been added.",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="🎭 Added Roles",
        value=role_text,
        inline=False
    )

    embed.set_footer(
        text=f"Filled {len(added)} role(s)"
    )

    await ctx.send(embed=embed)


@fill.error
async def fill_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You need the **Manage Roles** permission."
        )


# ============================================================
# ROLES
# $roles
# ============================================================

@bot.command(name="roles")
async def roles_command(ctx):

    roles = [
        role for role in reversed(ctx.guild.roles)
        if not role.is_default()
    ]

    if not roles:
        return await ctx.send(
            "❌ This server has no custom roles."
        )

    lines = []

    for role in roles:
        lines.append(
            f"{role.mention} — `Position {role.position}`"
        )

    chunks = []
    current = ""

    for line in lines:

        if len(current) + len(line) + 1 > 3900:
            chunks.append(current)
            current = ""

        current += line + "\n"

    if current:
        chunks.append(current)

    for index, chunk in enumerate(chunks):

        embed = discord.Embed(
            title=f"🎭 Server Roles"
            + (f" • {index + 1}/{len(chunks)}" if len(chunks) > 1 else ""),
            description=chunk,
            color=discord.Color.from_rgb(255, 20, 180)
        )

        embed.set_footer(
            text=f"{len(ctx.guild.roles) - 1} custom role(s)"
        )

        await ctx.send(embed=embed)


# ============================================================
# SERVER INFO
# $serverinfo
# ============================================================

@bot.command(name="serverinfo")
async def serverinfo(ctx):

    guild = ctx.guild

    humans = sum(
        1 for member in guild.members
        if not member.bot
    )

    bots = sum(
        1 for member in guild.members
        if member.bot
    )

    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)

    embed = discord.Embed(
        title=f"🏠 {guild.name}",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    if guild.icon:
        embed.set_thumbnail(
            url=guild.icon.url
        )

    embed.add_field(
        name="🆔 Server ID",
        value=str(guild.id),
        inline=False
    )

    embed.add_field(
        name="👑 Owner",
        value=f"<@{guild.owner_id}>",
        inline=True
    )

    embed.add_field(
        name="👥 Members",
        value=f"**{guild.member_count}**",
        inline=True
    )

    embed.add_field(
        name="👤 Humans",
        value=f"**{humans}**",
        inline=True
    )

    embed.add_field(
        name="🤖 Bots",
        value=f"**{bots}**",
        inline=True
    )

    embed.add_field(
        name="💬 Text Channels",
        value=f"**{text_channels}**",
        inline=True
    )

    embed.add_field(
        name="🔊 Voice Channels",
        value=f"**{voice_channels}**",
        inline=True
    )

    embed.add_field(
        name="🎭 Roles",
        value=f"**{len(guild.roles) - 1}**",
        inline=True
    )

    embed.add_field(
        name="🚀 Boost Level",
        value=f"**Level {guild.premium_tier}**",
        inline=True
    )

    embed.add_field(
        name="🚀 Boosts",
        value=f"**{guild.premium_subscription_count or 0}**",
        inline=True
    )

    embed.add_field(
        name="📅 Created",
        value=discord.utils.format_dt(
            guild.created_at,
            style="F"
        ),
        inline=False
    )

    embed.set_footer(
        text=f"Server info • {guild.name}"
    )

    await ctx.send(embed=embed)


# ============================================================
# UNKNOWN COMMAND / COMMAND ERRORS
# ============================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You do not have permission to use this command."
        )
        return

    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            "❌ I don't have the required permissions to do that."
        )
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"❌ Missing argument. Use `{ctx.prefix}{ctx.command.name} help`."
        )
        return

    if isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Invalid argument. Please mention the correct user/role."
        )
        return

    print(f"Command error: {error}")


# ============================================================
# START BOT
# ============================================================

@bot.event
async def on_ready():

    print(f"✅ Logged in as {bot.user}")
    print(f"✅ Bot is running in {len(bot.guilds)} server(s)")
    print("✅ Prefix: $")


bot.run(TOKEN)
