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
            "❌ I cannot give that role because it is equal to or higher "
            "than my highest role."
        )

    if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send(
            "❌ You cannot manage a role equal to or higher than your "
            "highest role."
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
            "❌ You cannot promote someone to a role equal to or higher "
            "than your highest role."
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

        await ctx.send(
            embed=embed
        )


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

    await ctx.send(
        embed=embed
    )


# ============================================================
# $TEMP
# ============================================================
# $temp has NO @user.
#
# It temps the person who runs $temp.
#
# The 2 protected roles remain.
#
# ALL original roles are saved.
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

    # --------------------------------------------------------
    # SAVE ALL ORIGINAL ROLES
    # --------------------------------------------------------

    current_roles = [
        role.id
        for role in member.roles
        if role != ctx.guild.default_role
    ]

    temp_data[user_id] = current_roles
    save_temp_data(temp_data)

    # --------------------------------------------------------
    # REMOVE ALL MANAGEABLE ROLES
    # EXCEPT THE 2 PROTECTED ROLES
    # --------------------------------------------------------

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
                "of these roles. Make sure my bot role is above them."
            )

    # --------------------------------------------------------
    # GET KEPT ROLES
    # --------------------------------------------------------

    kept_roles = [
        role.mention
        for role in member.roles
        if role.id in TEMP_KEEP_ROLE_IDS
    ]

    # --------------------------------------------------------
    # EMBED
    # --------------------------------------------------------

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

    await ctx.send(
        embed=embed
    )


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
# $canceltemp has NO @user.
#
# It restores the saved roles of the person who runs it.
#
# The user only needs ONE of these 2 roles:
#
# 1541096480146853968
# 1541096476610928730
#
# The user does NOT need Manage Roles.
#
# The BOT must have Manage Roles.
# ============================================================

@bot.command(name="canceltemp")
async def canceltemp(ctx):

    # --------------------------------------------------------
    # REQUIRED ROLE IDS
    # --------------------------------------------------------

    allowed_role_ids = [
        1541096480146853968,
        1541096476610928730
    ]

    # --------------------------------------------------------
    # CHECK USER'S ROLES
    # --------------------------------------------------------

    has_temp_permission = any(
        role.id in allowed_role_ids
        for role in ctx.author.roles
    )

    if not has_temp_permission:

        return await ctx.send(
            "❌ You need one of the required roles to use "
            "`$canceltemp`."
        )

    # --------------------------------------------------------
    # CHECK BOT MANAGE ROLES
    # --------------------------------------------------------

    if not ctx.guild.me.guild_permissions.manage_roles:

        return await ctx.send(
            "❌ I need the **Manage Roles** permission to "
            "restore roles."
        )

    # --------------------------------------------------------
    # TARGET = PERSON USING $CANCELTEMP
    # --------------------------------------------------------

    member = ctx.author
    user_id = str(member.id)

    # --------------------------------------------------------
    # LOAD SAVED DATA
    # --------------------------------------------------------

    temp_data = load_temp_data()

    if user_id not in temp_data:

        return await ctx.send(
            f"❌ No saved roles were found for {member.mention}."
        )

    saved_role_ids = temp_data[user_id]

    restored_roles = []
    skipped_roles = []

    # --------------------------------------------------------
    # FIND ROLES TO RESTORE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RESTORE ROLES
    # --------------------------------------------------------

    if restored_roles:

        try:

            await member.add_roles(
                *restored_roles,
                reason=(
                    f"Temporary demotion cancelled by "
                    f"{ctx.author}"
                )
            )

        except discord.Forbidden:

            return await ctx.send(
                "❌ I don't have permission to restore one or "
                "more roles. Make sure my bot role is above "
                "the roles it needs to restore."
            )

    # --------------------------------------------------------
    # DELETE SAVED TEMP DATA
    # --------------------------------------------------------

    del temp_data[user_id]
    save_temp_data(temp_data)

    # --------------------------------------------------------
    # EMBED
    # --------------------------------------------------------

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

    await ctx.send(
        embed=embed
    )


@canceltemp.error
async def canceltemp_error(ctx, error):

    if isinstance(error, commands.BadArgument):

        await ctx.send(
            "❌ Invalid command format."
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
