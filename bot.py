# ============================================================
# IMPORTS
# ============================================================

import os
import json
import re
import asyncio
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
# FILES
# ============================================================

VOUCH_FILE = "vouches.json"
TEMP_FILE = "temp_roles.json"


# ============================================================
# TEMP ROLE SETTINGS
# ============================================================

TEMP_KEEP_ROLE_IDS = [
    1541096480146853968,
    1541096476610928730
]


# ============================================================
# VOUCH DATA
# ============================================================

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
# TEMP DATA
# ============================================================

def load_temp_data():

    if not os.path.exists(TEMP_FILE):
        return {}

    try:

        with open(TEMP_FILE, "r") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):

        return {}


def save_temp_data(data):

    with open(TEMP_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ============================================================
# MEMBER RESOLVER
# ============================================================

async def get_member(ctx, value):

    if isinstance(value, discord.Member):
        return value

    value = str(value).strip()

    match = re.fullmatch(r"<@!?(\d+)>", value)

    if match:
        user_id = int(match.group(1))
    elif value.isdigit():
        user_id = int(value)
    else:
        return None

    return ctx.guild.get_member(user_id)


# ============================================================
# $ADDVOUCH @USER NUMBER
# ============================================================

@bot.command(name="addvouch")
@commands.has_permissions(manage_messages=True)
async def addvouch(ctx, member: discord.Member, amount: int = 1):

    if member.bot:
        return await ctx.send(
            "❌ You cannot add a vouch to a bot."
        )

    if amount <= 0:
        return await ctx.send(
            "❌ The number must be greater than 0."
        )

    vouches = load_vouches()
    user_id = str(member.id)

    vouches[user_id] = vouches.get(user_id, 0) + amount

    save_vouches(vouches)

    embed = discord.Embed(
        title="⭐ Vouch Added",
        description=f"Added **{amount}** vouch(s) to {member.mention}.",
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
            "❌ Usage: `$addvouch @user (number)`"
        )

    elif isinstance(error, commands.BadArgument):

        await ctx.send(
            "❌ Usage: `$addvouch @user (number)`"
        )


# ============================================================
# $REMOVEVOUCH @USER NUMBER
# ============================================================

@bot.command(name="removevouch")
@commands.has_permissions(manage_messages=True)
async def removevouch(ctx, member: discord.Member, amount: int = 1):

    if amount <= 0:
        return await ctx.send(
            "❌ The number must be greater than 0."
        )

    vouches = load_vouches()
    user_id = str(member.id)

    current = vouches.get(user_id, 0)

    if current <= 0:
        return await ctx.send(
            f"❌ {member.mention} has no vouches."
        )

    new_total = max(0, current - amount)

    vouches[user_id] = new_total

    save_vouches(vouches)

    embed = discord.Embed(
        title="🗑️ Vouch Removed",
        description=f"Removed **{amount}** vouch(s) from {member.mention}.",
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

    embed.set_thumbnail(
        url=member.display_avatar.url
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
# $VOUCHES @USER
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

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"Vouch profile • {member.display_name}"
    )

    await ctx.send(embed=embed)


# ============================================================
# $ROLE @USER @ROLE
# ============================================================

@bot.command(name="role")
@commands.has_permissions(manage_roles=True)
async def role_command(ctx, member: discord.Member, role: discord.Role):

    if role == ctx.guild.default_role:

        return await ctx.send(
            "❌ You cannot give the @everyone role."
        )

    if role >= ctx.guild.me.top_role:

        return await ctx.send(
            "❌ I cannot give that role because it is equal to or "
            "higher than my highest role."
        )

    if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:

        return await ctx.send(
            "❌ You cannot manage a role equal to or higher than "
            "your highest role."
        )

    if role in member.roles:

        return await ctx.send(
            f"❌ {member.mention} already has {role.mention}."
        )

    await member.add_roles(
        role,
        reason=f"Role command used by {ctx.author}"
    )

    await ctx.send(
        f"✅ Added {role.mention} to {member.mention}."
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
# $PROMO @USER
# ============================================================

@bot.command(name="promo")
@commands.has_permissions(manage_roles=True)
async def promo(ctx, member: discord.Member):

    if member.bot:

        return await ctx.send(
            "❌ You cannot promote a bot."
        )

    bot_top = ctx.guild.me.top_role

    manageable_roles = [
        role
        for role in ctx.guild.roles
        if role != ctx.guild.default_role
        and role < bot_top
    ]

    manageable_roles.sort(
        key=lambda r: r.position
    )

    current_manageable = [
        role
        for role in member.roles
        if role in manageable_roles
    ]

    if not current_manageable:

        next_role = (
            manageable_roles[0]
            if manageable_roles
            else None
        )

    else:

        highest_current = max(
            current_manageable,
            key=lambda r: r.position
        )

        higher_roles = [
            role
            for role in manageable_roles
            if role.position > highest_current.position
        ]

        next_role = (
            min(
                higher_roles,
                key=lambda r: r.position
            )
            if higher_roles
            else None
        )

    if next_role is None:

        return await ctx.send(
            f"❌ {member.mention} cannot be promoted any further."
        )

    if next_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:

        return await ctx.send(
            "❌ You cannot promote someone to a role equal to or "
            "higher than your highest role."
        )

    remove_roles = [
        role
        for role in current_manageable
        if role.position < next_role.position
    ]

    if remove_roles:

        await member.remove_roles(
            *remove_roles,
            reason=f"Promotion by {ctx.author}"
        )

    await member.add_roles(
        next_role,
        reason=f"Promotion by {ctx.author}"
    )

    await ctx.send(
        f"⬆️ {member.mention} has been promoted to {next_role.mention}."
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
# $DEMO @USER
# ============================================================

@bot.command(name="demo")
@commands.has_permissions(manage_roles=True)
async def demo(ctx, member: discord.Member):

    if member.bot:

        return await ctx.send(
            "❌ You cannot demote a bot."
        )

    bot_top = ctx.guild.me.top_role

    manageable_roles = [
        role
        for role in ctx.guild.roles
        if role != ctx.guild.default_role
        and role < bot_top
    ]

    manageable_roles.sort(
        key=lambda r: r.position
    )

    current_manageable = [
        role
        for role in member.roles
        if role in manageable_roles
    ]

    if not current_manageable:

        return await ctx.send(
            f"❌ {member.mention} has no manageable role to demote."
        )

    highest_current = max(
        current_manageable,
        key=lambda r: r.position
    )

    lower_roles = [
        role
        for role in manageable_roles
        if role.position < highest_current.position
    ]

    next_role = (
        max(
            lower_roles,
            key=lambda r: r.position
        )
        if lower_roles
        else None
    )

    if next_role is None:

        await member.remove_roles(
            highest_current,
            reason=f"Demotion by {ctx.author}"
        )

        return await ctx.send(
            f"⬇️ {member.mention} was demoted and "
            f"{highest_current.mention} was removed."
        )

    await member.remove_roles(
        highest_current,
        reason=f"Demotion by {ctx.author}"
    )

    if next_role != ctx.guild.default_role:

        await member.add_roles(
            next_role,
            reason=f"Demotion by {ctx.author}"
        )

    await ctx.send(
        f"⬇️ {member.mention} has been demoted to "
        f"{next_role.mention}."
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
# $W @USER
# ============================================================

@bot.command(name="w")
async def profile(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    embed = discord.Embed(
        title=f"👤 User Profile • {member.display_name}",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="👑 Username",
        value=str(member),
        inline=False
    )

    embed.add_field(
        name="🆔 ID",
        value=str(member.id),
        inline=False
    )

    if member.joined_at:

        embed.add_field(
            name="📅 Joined Guild",
            value=discord.utils.format_dt(
                member.joined_at,
                style="F"
            ),
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

    roles = [
        role.mention
        for role in reversed(member.roles)
        if role != ctx.guild.default_role
    ]

    embed.add_field(
        name=f"🎭 Roles [{len(roles)}]",
        value=", ".join(roles)
        if roles
        else "No roles",
        inline=False
    )

    permissions = member.guild_permissions

    permission_names = []

    permission_map = {
        "administrator": "Administrator",
        "manage_guild": "Manage Server",
        "manage_roles": "Manage Roles",
        "manage_channels": "Manage Channels",
        "manage_messages": "Manage Messages",
        "kick_members": "Kick Members",
        "ban_members": "Ban Members",
        "moderate_members": "Timeout Members",
        "mention_everyone": "Mention Everyone",
        "manage_nicknames": "Manage Nicknames",
        "view_audit_log": "View Audit Log"
    }

    for attribute, display_name in permission_map.items():

        if getattr(permissions, attribute, False):
            permission_names.append(display_name)

    embed.add_field(
        name="🔐 Role Permissions",
        value=", ".join(permission_names)
        if permission_names
        else "No special permissions",
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
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
# $FILL @USER
# ============================================================

@bot.command(name="fill")
@commands.has_permissions(manage_roles=True)
async def fill(ctx, member: discord.Member):

    bot_top = ctx.guild.me.top_role
    highest_member_role = member.top_role

    if highest_member_role == ctx.guild.default_role:

        return await ctx.send(
            f"❌ {member.mention} has no role to fill below."
        )

    roles_to_add = [
        role
        for role in ctx.guild.roles
        if role != ctx.guild.default_role
        and role.position < highest_member_role.position
        and role < bot_top
        and role not in member.roles
    ]

    if not roles_to_add:

        return await ctx.send(
            f"❌ There are no missing manageable roles below "
            f"{member.mention}'s highest role."
        )

    if ctx.author != ctx.guild.owner:

        roles_to_add = [
            role
            for role in roles_to_add
            if role < ctx.author.top_role
        ]

    if not roles_to_add:

        return await ctx.send(
            "❌ You cannot manage the roles below this user's highest role."
        )

    await member.add_roles(
        *roles_to_add,
        reason=f"Fill roles by {ctx.author}"
    )

    await ctx.send(
        f"✅ Filled **{len(roles_to_add)}** roles below "
        f"{member.mention}'s highest role."
    )


@fill.error
async def fill_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "❌ You need the **Manage Roles** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send(
            "❌ Usage: `$fill @user`"
        )

    elif isinstance(error, commands.BadArgument):

        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# $ROLES
# ============================================================

@bot.command(name="roles")
async def roles_command(ctx):

    roles = list(reversed(ctx.guild.roles))
    role_lines = []

    for role in roles:

        if role == ctx.guild.default_role:
            continue

        role_lines.append(
            f"{role.mention} — `{role.id}`"
        )

    if not role_lines:

        return await ctx.send(
            "❌ No roles found."
        )

    chunks = []
    current = ""

    for line in role_lines:

        if len(current) + len(line) + 1 > 4000:

            chunks.append(current)
            current = ""

        current += line + "\n"

    if current:
        chunks.append(current)

    for index, chunk in enumerate(chunks):

        embed = discord.Embed(
            title=(
                "🎭 Server Roles"
                + (
                    f" — Page {index + 1}"
                    if len(chunks) > 1
                    else ""
                )
            ),
            description=chunk,
            color=discord.Color.from_rgb(255, 20, 180)
        )

        embed.set_footer(
            text=f"{len(ctx.guild.roles) - 1} roles"
        )

        await ctx.send(embed=embed)


# ============================================================
# $SERVERINFO
# ============================================================

@bot.command(name="serverinfo")
async def serverinfo(ctx):

    guild = ctx.guild

    embed = discord.Embed(
        title=f"🌐 {guild.name}",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👑 Owner",
        value=f"<@{guild.owner_id}>",
        inline=True
    )

    embed.add_field(
        name="🆔 Server ID",
        value=str(guild.id),
        inline=True
    )

    embed.add_field(
        name="👥 Members",
        value=str(guild.member_count),
        inline=True
    )

    embed.add_field(
        name="💬 Channels",
        value=str(len(guild.channels)),
        inline=True
    )

    embed.add_field(
        name="🎭 Roles",
        value=str(len(guild.roles) - 1),
        inline=True
    )

    embed.add_field(
        name="🚀 Boost Level",
        value=str(guild.premium_tier),
        inline=True
    )

    embed.add_field(
        name="💎 Boosts",
        value=str(guild.premium_subscription_count),
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

    if guild.icon:

        embed.set_thumbnail(
            url=guild.icon.url
        )

    embed.set_footer(
        text=f"Server info • {guild.name}"
    )

    await ctx.send(embed=embed)


# ============================================================
# $TEMP
# ============================================================

@bot.command(name="temp")
@commands.has_permissions(manage_roles=True)
async def temp(ctx):

    member = ctx.author
    bot_top = ctx.guild.me.top_role

    if member.bot:

        return await ctx.send(
            "❌ You cannot temp a bot."
        )

    if member.top_role >= bot_top:

        return await ctx.send(
            "❌ I cannot manage you because your highest role "
            "is equal to or higher than my highest role."
        )

    temp_data = load_temp_data()
    user_id = str(member.id)

    if user_id in temp_data:

        return await ctx.send(
            "❌ You are already temporarily demoted."
        )

    current_roles = [
        role.id
        for role in member.roles
        if role != ctx.guild.default_role
    ]

    temp_data[user_id] = current_roles

    save_temp_data(temp_data)

    roles_to_remove = [
        role
        for role in member.roles
        if role != ctx.guild.default_role
        and role.id not in TEMP_KEEP_ROLE_IDS
        and role < bot_top
    ]

    if roles_to_remove:

        try:

            await member.remove_roles(
                *roles_to_remove,
                reason=f"Temporary role removal by {ctx.author}"
            )

        except discord.Forbidden:

            temp_data.pop(user_id, None)
            save_temp_data(temp_data)

            return await ctx.send(
                "❌ I don't have permission to remove one or more "
                "of these roles."
            )

    kept_roles = [
        role.mention
        for role in member.roles
        if role.id in TEMP_KEEP_ROLE_IDS
    ]

    embed = discord.Embed(
        title="⏸️ Temporary Demotion",
        description=(
            f"{member.mention} has been temporarily demoted."
        ),
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="🔒 Roles Kept",
        value=", ".join(kept_roles)
        if kept_roles
        else "No protected roles found",
        inline=False
    )

    embed.add_field(
        name="🗑️ Roles Removed",
        value=str(len(roles_to_remove)),
        inline=False
    )

    embed.add_field(
        name="💾 Saved Roles",
        value=f"**{len(current_roles)}** roles saved",
        inline=False
    )

    embed.add_field(
        name="👮 Action By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text="Use $canceltemp to restore your saved roles"
    )

    await ctx.send(embed=embed)


@temp.error
async def temp_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "❌ You need the **Manage Roles** permission "
            "to use `$temp`."
        )


# ============================================================
# $CANCELTEMP
# ============================================================

@bot.command(name="canceltemp")
async def canceltemp(ctx):

    allowed_role_ids = [
        1541096480146853968,
        1541096476610928730
    ]

    has_temp_permission = any(
        role.id in allowed_role_ids
        for role in ctx.author.roles
    )

    if not has_temp_permission:

        return await ctx.send(
            "❌ You need one of the required roles to use "
            "`$canceltemp`."
        )

    if not ctx.guild.me.guild_permissions.manage_roles:

        return await ctx.send(
            "❌ I need the **Manage Roles** permission to "
            "restore roles."
        )

    member = ctx.author
    user_id = str(member.id)

    temp_data = load_temp_data()

    if user_id not in temp_data:

        return await ctx.send(
            f"❌ No saved roles were found for {member.mention}."
        )

    saved_role_ids = temp_data[user_id]

    restored_roles = []
    skipped_roles = []

    for role_id in saved_role_ids:

        role = ctx.guild.get_role(role_id)

        if role is None:
            continue

        if role == ctx.guild.default_role:
            continue

        if role >= ctx.guild.me.top_role:

            skipped_roles.append(role)
            continue

        if role not in member.roles:

            restored_roles.append(role)

    if restored_roles:

        try:

            await member.add_roles(
                *restored_roles,
                reason=f"Temporary demotion cancelled by {ctx.author}"
            )

        except discord.Forbidden:

            return await ctx.send(
                "❌ I don't have permission to restore one or more roles."
            )

    del temp_data[user_id]
    save_temp_data(temp_data)

    embed = discord.Embed(
        title="▶️ Temporary Demotion Cancelled",
        description=(
            f"Successfully restored the saved roles for "
            f"{member.mention}."
        ),
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="🔄 Roles Restored",
        value=f"**{len(restored_roles)}**",
        inline=False
    )

    if skipped_roles:

        embed.add_field(
            name="⚠️ Roles Skipped",
            value=(
                f"**{len(skipped_roles)}** "
                "(above my highest role)"
            ),
            inline=False
        )

    embed.add_field(
        name="👮 Cancelled By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text="Temporary demotion cancelled"
    )

    await ctx.send(embed=embed)


# ============================================================
# $TO @USER TIME
# Supports:
# s = seconds
# m = minutes
# h = hours
# d = days
#
# Examples:
# $to @user 10m
# $to @user 1h
# $to @user 30s
# $to @user 2d
# ============================================================

@bot.command(name="to")
@commands.has_permissions(moderate_members=True)
async def timeout_command(ctx, member: discord.Member, duration: str):

    if member == ctx.author:

        return await ctx.send(
            "❌ You cannot timeout yourself."
        )

    if member == ctx.guild.owner:

        return await ctx.send(
            "❌ You cannot timeout the server owner."
        )

    match = re.fullmatch(
        r"(\d+)(s|m|h|d)",
        duration.lower()
    )

    if not match:

        return await ctx.send(
            "❌ Invalid time.\n"
            "Use `s`, `m`, `h`, or `d`.\n\n"
            "Examples:\n"
            "`$to @user 30s`\n"
            "`$to @user 10m`\n"
            "`$to @user 1h`\n"
            "`$to @user 2d`"
        )

    amount = int(match.group(1))
    unit = match.group(2)

    multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400
    }

    seconds = amount * multipliers[unit]

    if seconds > 28 * 24 * 60 * 60:

        return await ctx.send(
            "❌ Discord only allows timeouts up to **28 days**."
        )

    if member.top_role >= ctx.guild.me.top_role:

        return await ctx.send(
            "❌ I cannot timeout this member because their "
            "highest role is equal to or higher than mine."
        )

    try:

        await member.timeout(
            discord.utils.utcnow() + discord.timedelta(seconds=seconds),
            reason=f"Timeout by {ctx.author}"
        )

    except AttributeError:

        import datetime

        await member.timeout(
            datetime.timedelta(seconds=seconds),
            reason=f"Timeout by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I don't have permission to timeout this member."
        )

    await ctx.send(
        f"🔇 {member.mention} has been timed out for **{duration}**."
    )


@timeout_command.error
async def timeout_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "❌ You need the **Timeout Members** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send(
            "❌ Usage: `$to @user (time)`"
        )

    elif isinstance(error, commands.BadArgument):

        await ctx.send(
            "❌ Usage: `$to @user (time)`"
        )


# ============================================================
# $UNTO @USER
# ============================================================

@bot.command(name="unto")
@commands.has_permissions(moderate_members=True)
async def unto(ctx, member: discord.Member):

    try:

        await member.timeout(
            None,
            reason=f"Timeout removed by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I don't have permission to remove this timeout."
        )

    await ctx.send(
        f"🔊 Timeout removed from {member.mention}."
    )


# ============================================================
# $BAN @USER OR ID
# ============================================================

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_command(ctx, target):

    member = await get_member(ctx, target)

    if member is None:

        try:
            user = await bot.fetch_user(int(target))
        except (ValueError, discord.NotFound, discord.HTTPException):
            return await ctx.send(
                "❌ Please provide a valid user mention or ID."
            )

        try:

            await ctx.guild.ban(
                user,
                reason=f"Banned by {ctx.author}"
            )

        except discord.Forbidden:

            return await ctx.send(
                "❌ I don't have permission to ban this user."
            )

        return await ctx.send(
            f"🔨 Banned **{user}**."
        )

    if member == ctx.guild.owner:

        return await ctx.send(
            "❌ You cannot ban the server owner."
        )

    if member.top_role >= ctx.guild.me.top_role:

        return await ctx.send(
            "❌ I cannot ban this member because their role "
            "is equal to or higher than mine."
        )

    try:

        await ctx.guild.ban(
            member,
            reason=f"Banned by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I don't have permission to ban this member."
        )

    await ctx.send(
        f"🔨 Banned {member.mention}."
    )


# ============================================================
# $UNBAN USER ID
# ============================================================

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban_command(ctx, user_id: int):

    try:

        user = await bot.fetch_user(user_id)

        await ctx.guild.unban(
            user,
            reason=f"Unbanned by {ctx.author}"
        )

    except discord.NotFound:

        return await ctx.send(
            "❌ That user is not banned or the ID is invalid."
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I don't have permission to unban users."
        )

    await ctx.send(
        f"✅ Unbanned **{user}**."
    )


# ============================================================
# $KICK @USER OR ID
# ============================================================

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_command(ctx, target):

    member = await get_member(ctx, target)

    if member is None:

        return await ctx.send(
            "❌ The user must be in the server. "
            "Use a mention or user ID."
        )

    if member == ctx.guild.owner:

        return await ctx.send(
            "❌ You cannot kick the server owner."
        )

    if member.top_role >= ctx.guild.me.top_role:

        return await ctx.send(
            "❌ I cannot kick this member because their "
            "highest role is equal to or higher than mine."
        )

    try:

        await member.kick(
            reason=f"Kicked by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I don't have permission to kick this member."
        )

    await ctx.send(
        f"👢 Kicked {member.mention}."
    )


# ============================================================
# $PURGE NUMBER
# ============================================================

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge_command(ctx, amount: int):

    if amount <= 0:

        return await ctx.send(
            "❌ The number must be greater than 0."
        )

    if amount > 100:

        return await ctx.send(
            "❌ You can purge a maximum of **100 messages** at once."
        )

    try:

        deleted = await ctx.channel.purge(
            limit=amount + 1
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I don't have permission to delete messages here."
        )

    count = max(0, len(deleted) - 1)

    message = await ctx.send(
        f"🧹 Deleted **{count}** message(s)."
    )

    await asyncio.sleep(3)

    try:
        await message.delete()
    except discord.NotFound:
        pass


# ============================================================
# TICKET HELPER
# ============================================================

def is_ticket_channel(ctx):

    if not isinstance(ctx.channel, discord.TextChannel):
        return False

    name = ctx.channel.name.lower()

    return (
        "ticket" in name
        or "ticket-" in name
    )


# ============================================================
# $CLAIM
# ============================================================

@bot.command(name="claim")
@commands.has_permissions(manage_channels=True)
async def claim_ticket(ctx):

    if not is_ticket_channel(ctx):

        return await ctx.send(
            "❌ This command can only be used inside a ticket."
        )

    middleman_role = discord.utils.find(
        lambda r: "middleman" in r.name.lower(),
        ctx.guild.roles
    )

    if middleman_role is None:

        return await ctx.send(
            "❌ I couldn't find a Middleman role."
        )

    await ctx.channel.set_permissions(
        middleman_role,
        view_channel=False
    )

    await ctx.channel.set_permissions(
        ctx.author,
        view_channel=True,
        send_messages=True,
        read_message_history=True
    )

    await ctx.send(
        f"🎫 {ctx.author.mention} has claimed this ticket."
    )


# ============================================================
# $UNCLAIM
# ============================================================

@bot.command(name="unclaim")
@commands.has_permissions(manage_channels=True)
async def unclaim_ticket(ctx):

    if not is_ticket_channel(ctx):

        return await ctx.send(
            "❌ This command can only be used inside a ticket."
        )

    middleman_role = discord.utils.find(
        lambda r: "middleman" in r.name.lower(),
        ctx.guild.roles
    )

    if middleman_role is None:

        return await ctx.send(
            "❌ I couldn't find a Middleman role."
        )

    await ctx.channel.set_permissions(
        middleman_role,
        view_channel=True,
        send_messages=True,
        read_message_history=True
    )

    await ctx.channel.set_permissions(
        ctx.author,
        overwrite=None
    )

    await ctx.send(
        f"🔓 {ctx.author.mention} has unclaimed this ticket."
    )


# ============================================================
# $TRANSFERTICKET @USER OR ID
# ============================================================

@bot.command(name="transferticket")
@commands.has_permissions(manage_channels=True)
async def transferticket(ctx, target):

    if not is_ticket_channel(ctx):

        return await ctx.send(
            "❌ This command can only be used inside a ticket."
        )

    member = await get_member(ctx, target)

    if member is None:

        return await ctx.send(
            "❌ Please mention a valid server member or use their ID."
        )

    await ctx.channel.set_permissions(
        member,
        view_channel=True,
        send_messages=True,
        read_message_history=True
    )

    await ctx.send(
        f"🎫 Ticket transferred to {member.mention}."
    )


# ============================================================
# $TRANSFERROLES @USER
# ============================================================

@bot.command(name="transferroles")
@commands.has_permissions(manage_roles=True)
async def transferroles(ctx, target):

    member = await get_member(ctx, target)

    if member is None:

        return await ctx.send(
            "❌ Please mention a valid server member or use their ID."
        )

    source = ctx.author

    roles_to_transfer = [
        role
        for role in source.roles
        if role != ctx.guild.default_role
        and role < ctx.guild.me.top_role
        and role < ctx.author.top_role
    ]

    if not roles_to_transfer:

        return await ctx.send(
            "❌ You have no transferable roles."
        )

    added = []

    for role in roles_to_transfer:

        if role >= member.top_role and role >= ctx.guild.me.top_role:
            continue

        if role not in member.roles:

            try:

                await member.add_roles(
                    role,
                    reason=f"Role transfer by {ctx.author}"
                )

                added.append(role)

            except discord.Forbidden:
                pass

    await ctx.send(
        f"🔄 Transferred **{len(added)}** role(s) to {member.mention}."
    )


# ============================================================
# $ADD USER
# ============================================================

@bot.command(name="add")
@commands.has_permissions(manage_channels=True)
async def add_ticket_member(ctx, target):

    if not is_ticket_channel(ctx):

        return await ctx.send(
            "❌ This command can only be used inside a ticket."
        )

    member = await get_member(ctx, target)

    if member is None:

        return await ctx.send(
            "❌ Please mention a valid server member or use their ID."
        )

    await ctx.channel.set_permissions(
        member,
        view_channel=True,
        send_messages=True,
        read_message_history=True
    )

    await ctx.send(
        f"✅ Added {member.mention} to this ticket."
    )


# ============================================================
# $BACKUP
# ============================================================

BACKUP_FILE = "server_backup.json"


@bot.command(name="backup")
@commands.has_permissions(administrator=True)
async def backup_command(ctx):

    guild = ctx.guild

    backup = {
        "guild_name": guild.name,
        "roles": [],
        "categories": [],
        "channels": []
    }

    # --------------------------------------------------------
    # ROLES
    # --------------------------------------------------------

    for role in guild.roles:

        if role == guild.default_role:
            continue

        backup["roles"].append({
            "name": role.name,
            "permissions": role.permissions.value,
            "color": role.color.value,
            "hoist": role.hoist,
            "mentionable": role.mentionable
        })

    # --------------------------------------------------------
    # CATEGORIES
    # --------------------------------------------------------

    for category in guild.categories:

        backup["categories"].append({
            "name": category.name,
            "position": category.position
        })

    # --------------------------------------------------------
    # CHANNELS
    # --------------------------------------------------------

    for channel in guild.channels:

        if isinstance(channel, discord.CategoryChannel):

            continue

        data = {
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position,
            "category": channel.category.name
            if channel.category
            else None
        }

        if isinstance(channel, discord.TextChannel):

            data["topic"] = channel.topic
            data["slowmode_delay"] = channel.slowmode_delay
            data["nsfw"] = channel.nsfw

        elif isinstance(channel, discord.VoiceChannel):

            data["bitrate"] = channel.bitrate
            data["user_limit"] = channel.user_limit

        backup["channels"].append(data)

    with open(BACKUP_FILE, "w") as f:

        json.dump(
            backup,
            f,
            indent=4
        )

    await ctx.send(
        f"✅ Server backup created.\n"
        f"📁 `{BACKUP_FILE}`"
    )


# ============================================================
# $RESTORE
# ============================================================

@bot.command(name="restore")
@commands.has_permissions(administrator=True)
async def restore_command(ctx):

    if not os.path.exists(BACKUP_FILE):

        return await ctx.send(
            "❌ No server backup was found."
        )

    try:

        with open(BACKUP_FILE, "r") as f:

            backup = json.load(f)

    except (json.JSONDecodeError, OSError):

        return await ctx.send(
            "❌ The backup file is invalid."
        )

    await ctx.send(
        "⚠️ **Server restore started.**\n"
        "This will recreate missing roles and channels from "
        "the saved backup."
    )

    # --------------------------------------------------------
    # RESTORE ROLES
    # --------------------------------------------------------

    existing_roles = {
        role.name: role
        for role in ctx.guild.roles
    }

    created_roles = 0

    for role_data in backup.get("roles", []):

        if role_data["name"] in existing_roles:
            continue

        try:

            await ctx.guild.create_role(
                name=role_data["name"],
                permissions=discord.Permissions(
                    role_data["permissions"]
                ),
                colour=discord.Colour(
                    role_data["color"]
                ),
                hoist=role_data["hoist"],
                mentionable=role_data["mentionable"],
                reason="Server backup restore"
            )

            created_roles += 1

        except discord.Forbidden:

            pass

    # --------------------------------------------------------
    # RESTORE CATEGORIES
    # --------------------------------------------------------

    existing_categories = {
        category.name: category
        for category in ctx.guild.categories
    }

    created_categories = 0

    for category_data in backup.get("categories", []):

        if category_data["name"] in existing_categories:
            continue

        try:

            category = await ctx.guild.create_category(
                category_data["name"],
                reason="Server backup restore"
            )

            existing_categories[category.name] = category
            created_categories += 1

        except discord.Forbidden:

            pass

    # --------------------------------------------------------
    # RESTORE CHANNELS
    # --------------------------------------------------------

    existing_channels = {
        channel.name
        for channel in ctx.guild.channels
    }

    created_channels = 0

    for channel_data in backup.get("channels", []):

        name = channel_data["name"]

        if name in existing_channels:
            continue

        category = None

        category_name = channel_data.get("category")

        if category_name:

            category = existing_categories.get(
                category_name
            )

        try:

            if channel_data["type"] == "text":

                await ctx.guild.create_text_channel(
                    name,
                    category=category,
                    topic=channel_data.get("topic"),
                    slowmode_delay=channel_data.get(
                        "slowmode_delay",
                        0
                    ),
                    nsfw=channel_data.get(
                        "nsfw",
                        False
                    ),
                    reason="Server backup restore"
                )

                created_channels += 1

            elif channel_data["type"] == "voice":

                await ctx.guild.create_voice_channel(
                    name,
                    category=category,
                    bitrate=channel_data.get(
                        "bitrate"
                    ),
                    user_limit=channel_data.get(
                        "user_limit",
                        0
                    ),
                    reason="Server backup restore"
                )

                created_channels += 1

        except (discord.Forbidden, discord.HTTPException):

            pass

    await ctx.send(
        "✅ **Server restore finished.**\n\n"
        f"🎭 Roles created: **{created_roles}**\n"
        f"📁 Categories created: **{created_categories}**\n"
        f"💬 Channels created: **{created_channels}**"
    )


# ============================================================
# $HELP
# ============================================================

bot.remove_command("help")


@bot.command(name="help")
async def help_command(ctx):

    embed = discord.Embed(
        title="📖 Bot Commands",
        description=(
            "Here are all available commands.\n"
            "Commands requiring permissions can only be used "
            "by members with the required permissions."
        ),
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="⭐ Vouch Commands",
        value=(
            "`$addvouch @user (number)` — Add vouches\n"
            "`$removevouch @user (number)` — Remove vouches\n"
            "`$vouches @user` — Check vouches"
        ),
        inline=False
    )

    embed.add_field(
        name="🎭 Role Commands",
        value=(
            "`$role @user @role` — Give a role\n"
            "`$promo @user` — Promote a user\n"
            "`$demo @user` — Demote a user\n"
            "`$fill @user` — Fill missing roles\n"
            "`$roles` — Show server roles"
        ),
        inline=False
    )

    embed.add_field(
        name="⏸️ Temporary Role Commands",
        value=(
            "`$temp` — Temporarily remove roles\n"
            "`$canceltemp` — Restore saved roles"
        ),
        inline=False
    )

    embed.add_field(
        name="👤 User / Server Commands",
        value=(
            "`$w @user` — View user profile\n"
            "`$serverinfo` — View server information"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Moderation Commands",
        value=(
            "`$to @user (time)` — Timeout a member\n"
            "`$unto @user` — Remove timeout\n"
            "`$ban @user / ID` — Ban a member\n"
            "`$unban (user ID)` — Unban a member\n"
            "`$kick @user / ID` — Kick a member\n"
            "`$purge (number)` — Delete messages"
        ),
        inline=False
    )

    embed.add_field(
        name="🎫 Ticket Commands",
        value=(
            "`$claim` — Claim current ticket\n"
            "`$unclaim` — Unclaim current ticket\n"
            "`$transferticket @user / ID` — Transfer ticket\n"
            "`$transferroles @user` — Transfer roles\n"
            "`$add @user / ID` — Add member to ticket"
        ),
        inline=False
    )

    embed.add_field(
        name="💾 Server Backup",
        value=(
            "`$backup` — Create server backup\n"
            "`$restore` — Restore server backup"
        ),
        inline=False
    )

    embed.set_thumbnail(
        url=(
            ctx.guild.icon.url
            if ctx.guild and ctx.guild.icon
            else discord.Embed.Empty
        )
    )

    embed.set_footer(
        text=f"Requested by {ctx.author.display_name}"
    )

    await ctx.send(embed=embed)


# ============================================================
# GLOBAL COMMAND ERROR HANDLER
# ============================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):

        return await ctx.send(
            "❌ You don't have permission to use this command."
        )

    if isinstance(error, commands.MissingRequiredArgument):

        return await ctx.send(
            "❌ Missing required argument. Use `$help` to see usage."
        )

    if isinstance(error, commands.BadArgument):

        return await ctx.send(
            "❌ Invalid argument. Use `$help` to see the correct format."
        )

    if isinstance(error, commands.CommandInvokeError):

        original = error.original

        print(
            f"❌ Error in command `{ctx.command}`: {original}"
        )

        return await ctx.send(
            "❌ An error occurred while running this command."
        )

    print(
        f"❌ Unhandled command error: {error}"
    )


# ============================================================
# START BOT
# ============================================================

@bot.event
async def on_ready():

    print(
        f"✅ Logged in as {bot.user}"
    )

    print(
        f"✅ Bot is running in {len(bot.guilds)} server(s)"
    )


# ============================================================
# RUN BOT
# ============================================================

bot.run(TOKEN)
