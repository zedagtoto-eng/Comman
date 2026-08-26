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
# TICKET SETTINGS
# ============================================================

TICKET_CATEGORY_ID = 1541096510102437911


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
# TICKET CHECK
# ============================================================

def is_ticket_channel(channel):

    return (
        channel.category is not None
        and channel.category.id == TICKET_CATEGORY_ID
    )


# ============================================================
# GET MEMBER
# ============================================================

async def get_member_from_input(ctx, user_input):

    try:

        return await commands.MemberConverter().convert(
            ctx,
            user_input
        )

    except commands.BadArgument:
        pass

    try:

        user_id = int(user_input)

        return ctx.guild.get_member(user_id)

    except (ValueError, TypeError):

        return None


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
        description=(
            f"Added **{amount}** vouch(s) to "
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

    elif isinstance(
        error,
        (
            commands.MissingRequiredArgument,
            commands.BadArgument
        )
    ):

        await ctx.send(
            "❌ Usage: `$addvouch @user (number)`"
        )


# ============================================================
# $REMOVEVOUCH @USER NUMBER
# ============================================================

@bot.command(name="removevouch")
@commands.has_permissions(manage_messages=True)
async def removevouch(
    ctx,
    member: discord.Member,
    amount: int = 1
):

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

    new_total = max(
        0,
        current - amount
    )

    vouches[user_id] = new_total

    save_vouches(vouches)

    embed = discord.Embed(
        title="🗑️ Vouch Removed",
        description=(
            f"Removed **{amount}** vouch(s) from "
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

    elif isinstance(
        error,
        (
            commands.MissingRequiredArgument,
            commands.BadArgument
        )
    ):

        await ctx.send(
            "❌ Usage: `$removevouch @user (number)`"
        )


# ============================================================
# $VOUCHES @USER
# ============================================================

@bot.command(name="vouches")
async def vouches_command(
    ctx,
    member: discord.Member = None
):

    if member is None:
        member = ctx.author

    vouches = load_vouches()

    count = vouches.get(
        str(member.id),
        0
    )

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
async def role_command(
    ctx,
    member: discord.Member,
    role: discord.Role
):

    if role == ctx.guild.default_role:

        return await ctx.send(
            "❌ You cannot give the @everyone role."
        )

    if role >= ctx.guild.me.top_role:

        return await ctx.send(
            "❌ I cannot give that role because it is equal "
            "to or higher than my highest role."
        )

    if (
        role >= ctx.author.top_role
        and ctx.author != ctx.guild.owner
    ):

        return await ctx.send(
            "❌ You cannot manage a role equal to or higher "
            "than your highest role."
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

    elif isinstance(
        error,
        (
            commands.MissingRequiredArgument,
            commands.BadArgument
        )
    ):

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
        if (
            role != ctx.guild.default_role
            and role < bot_top
        )
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

    if (
        next_role >= ctx.author.top_role
        and ctx.author != ctx.guild.owner
    ):

        return await ctx.send(
            "❌ You cannot promote someone to a role equal "
            "to or higher than your highest role."
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
        f"⬆️ {member.mention} has been promoted to "
        f"{next_role.mention}."
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
        if (
            role != ctx.guild.default_role
            and role < bot_top
        )
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
            f"❌ {member.mention} has no manageable role "
            f"to demote."
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
async def profile(
    ctx,
    member: discord.Member = None
):

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
        value=(
            ", ".join(roles)
            if roles
            else "No roles"
        ),
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

        if getattr(
            permissions,
            attribute,
            False
        ):

            permission_names.append(
                display_name
            )

    embed.add_field(
        name="🔐 Role Permissions",
        value=(
            ", ".join(permission_names)
            if permission_names
            else "No special permissions"
        ),
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
# $FILL
# ============================================================
# Gives the person using $fill all missing roles that:
#
# 1. Are below their highest role
# 2. Are below the bot's highest role
# 3. Are not @everyone
# 4. They don't already have
#
# Usage:
# $fill
# ============================================================

@bot.command(name="fill")
@commands.has_permissions(manage_roles=True)
async def fill(ctx):

    member = ctx.author
    guild = ctx.guild
    bot_member = guild.me

    if member.bot:

        return await ctx.send(
            "❌ You cannot use `$fill` on a bot."
        )

    bot_top = bot_member.top_role
    member_top = member.top_role

    # --------------------------------------------------------
    # USER MUST HAVE A ROLE
    # --------------------------------------------------------

    if member_top == guild.default_role:

        return await ctx.send(
            f"❌ {member.mention} has no role to fill below."
        )

    # --------------------------------------------------------
    # FIND ALL MISSING MANAGEABLE ROLES
    # --------------------------------------------------------

    roles_to_add = []

    for role in guild.roles:

        # Never add @everyone.
        if role == guild.default_role:
            continue

        # Don't add roles the user already has.
        if role in member.roles:
            continue

        # Role must be below user's highest role.
        if role.position >= member_top.position:
            continue

        # Bot must be able to manage the role.
        if role.position >= bot_top.position:
            continue

        roles_to_add.append(role)

    # --------------------------------------------------------
    # NO MISSING ROLES
    # --------------------------------------------------------

    if not roles_to_add:

        return await ctx.send(
            f"❌ {member.mention} already has all manageable "
            f"roles below their highest role."
        )

    # Lowest role first.
    roles_to_add.sort(
        key=lambda role: role.position
    )

    # --------------------------------------------------------
    # ADD ROLES
    # --------------------------------------------------------

    try:

        await member.add_roles(
            *roles_to_add,
            reason=f"$fill used by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I don't have permission to add one or more "
            "of these roles. Make sure my bot role is above "
            "the roles it needs to manage."
        )

    except discord.HTTPException as error:

        return await ctx.send(
            f"❌ Discord rejected the role update: `{error}`"
        )

    # --------------------------------------------------------
    # SUCCESS EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title="🎭 Roles Filled",
        description=(
            f"Successfully filled the missing roles for "
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
        name="➕ Roles Added",
        value=f"**{len(roles_to_add)}**",
        inline=False
    )

    embed.add_field(
        name="👑 Highest Role",
        value=member_top.mention,
        inline=False
    )

    embed.add_field(
        name="👮 Filled By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text="Role fill system"
    )

    await ctx.send(embed=embed)


@fill.error
async def fill_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "❌ You need the **Manage Roles** permission "
            "to use `$fill`."
        )


# ============================================================
# $ROLES
# ============================================================

@bot.command(name="roles")
async def roles_command(ctx):

    roles = list(
        reversed(ctx.guild.roles)
    )

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
    # REMOVE MANAGEABLE ROLES EXCEPT PROTECTED
    # --------------------------------------------------------

    roles_to_remove = [
        role
        for role in member.roles
        if (
            role != ctx.guild.default_role
            and role.id not in TEMP_KEEP_ROLE_IDS
            and role < bot_top
        )
    ]

    if roles_to_remove:

        try:

            await member.remove_roles(
                *roles_to_remove,
                reason=f"Temporary role removal by {ctx.author}"
            )

        except discord.Forbidden:

            temp_data.pop(
                user_id,
                None
            )

            save_temp_data(temp_data)

            return await ctx.send(
                "❌ I don't have permission to remove one or "
                "more of these roles."
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
        value=(
            ", ".join(kept_roles)
            if kept_roles
            else "No protected roles found"
        ),
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
            f"❌ No saved roles were found for "
            f"{member.mention}."
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
                reason=(
                    f"Temporary demotion cancelled by "
                    f"{ctx.author}"
                )
            )

        except discord.Forbidden:

            return await ctx.send(
                "❌ I don't have permission to restore one "
                "or more roles."
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
# $CLAIM
# ============================================================

@bot.command(name="claim")
@commands.has_permissions(manage_channels=True)
async def claim(ctx):

    if not is_ticket_channel(ctx.channel):

        return await ctx.send(
            "❌ This command can only be used in a ticket."
        )

    topic = ctx.channel.topic or ""

    claimed_id = 0

    if "claimed=" in topic:

        try:

            claimed_id = int(
                topic.split("claimed=")[1]
                .split(";")[0]
            )

        except (ValueError, IndexError):

            claimed_id = 0

    if claimed_id != 0:

        claimed_member = ctx.guild.get_member(
            claimed_id
        )

        if claimed_member:

            return await ctx.send(
                f"❌ This ticket is already claimed by "
                f"{claimed_member.mention}."
            )

    owner_id = 0

    if "owner=" in topic:

        try:

            owner_id = int(
                topic.split("owner=")[1]
                .split(";")[0]
            )

        except (ValueError, IndexError):

            owner_id = 0

    new_topic = (
        f"owner={owner_id};"
        f"claimed={ctx.author.id}"
    )

    try:

        await ctx.channel.edit(
            topic=new_topic,
            reason=f"Ticket claimed by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I need **Manage Channels** permission."
        )

    middleman_role = discord.utils.find(
        lambda role: role.name.lower() == "middleman",
        ctx.guild.roles
    )

    if middleman_role:

        try:

            await ctx.channel.set_permissions(
                middleman_role,
                view_channel=False,
                reason=f"Ticket claimed by {ctx.author}"
            )

        except discord.Forbidden:
            pass

    try:

        await ctx.channel.set_permissions(
            ctx.author,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            reason=f"Ticket claimed by {ctx.author}"
        )

    except discord.Forbidden:
        pass

    embed = discord.Embed(
        title="🎫 Ticket Claimed",
        description=(
            f"🔒 This ticket has been claimed by "
            f"{ctx.author.mention}."
        ),
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👮 Claimed By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_footer(
        text="Use $unclaim to release this ticket."
    )

    await ctx.send(embed=embed)


# ============================================================
# $UNCLAIM
# ============================================================

@bot.command(name="unclaim")
@commands.has_permissions(manage_channels=True)
async def unclaim(ctx):

    if not is_ticket_channel(ctx.channel):

        return await ctx.send(
            "❌ This command can only be used in a ticket."
        )

    topic = ctx.channel.topic or ""

    owner_id = 0

    if "owner=" in topic:

        try:

            owner_id = int(
                topic.split("owner=")[1]
                .split(";")[0]
            )

        except (ValueError, IndexError):

            owner_id = 0

    claimed_id = 0

    if "claimed=" in topic:

        try:

            claimed_id = int(
                topic.split("claimed=")[1]
                .split(";")[0]
            )

        except (ValueError, IndexError):

            claimed_id = 0

    if claimed_id == 0:

        return await ctx.send(
            "❌ This ticket is not claimed."
        )

    new_topic = (
        f"owner={owner_id};"
        f"claimed=0"
    )

    try:

        await ctx.channel.edit(
            topic=new_topic,
            reason=f"Ticket unclaimed by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I need **Manage Channels** permission."
        )

    middleman_role = discord.utils.find(
        lambda role: role.name.lower() == "middleman",
        ctx.guild.roles
    )

    if middleman_role:

        try:

            await ctx.channel.set_permissions(
                middleman_role,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                reason=f"Ticket unclaimed by {ctx.author}"
            )

        except discord.Forbidden:
            pass

    claimed_member = ctx.guild.get_member(
        claimed_id
    )

    if claimed_member:

        try:

            await ctx.channel.set_permissions(
                claimed_member,
                overwrite=None,
                reason="Ticket unclaimed"
            )

        except discord.Forbidden:
            pass

    embed = discord.Embed(
        title="🔓 Ticket Unclaimed",
        description=(
            f"{ctx.author.mention} has unclaimed this ticket."
        ),
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="📂 Status",
        value="Available to Middlemen",
        inline=False
    )

    embed.set_footer(
        text="Use $claim to claim this ticket."
    )

    await ctx.send(embed=embed)


# ============================================================
# $TRANSFERTICKET @USER OR USER ID
# ============================================================

@bot.command(name="transferticket")
@commands.has_permissions(manage_channels=True)
async def transferticket(
    ctx,
    user_input: str
):

    if not is_ticket_channel(ctx.channel):

        return await ctx.send(
            "❌ This command can only be used in a ticket."
        )

    member = await get_member_from_input(
        ctx,
        user_input
    )

    if member is None:

        return await ctx.send(
            "❌ I couldn't find that member.\n"
            "Use: `$transferticket @user` or "
            "`$transferticket userID`"
        )

    if member.bot:

        return await ctx.send(
            "❌ You cannot transfer a ticket to a bot."
        )

    topic = ctx.channel.topic or ""

    owner_id = 0

    if "owner=" in topic:

        try:

            owner_id = int(
                topic.split("owner=")[1]
                .split(";")[0]
            )

        except (ValueError, IndexError):

            owner_id = 0

    claimed_id = 0

    if "claimed=" in topic:

        try:

            claimed_id = int(
                topic.split("claimed=")[1]
                .split(";")[0]
            )

        except (ValueError, IndexError):

            claimed_id = 0

    new_topic = (
        f"owner={owner_id};"
        f"claimed={member.id}"
    )

    try:

        await ctx.channel.edit(
            topic=new_topic,
            reason=(
                f"Ticket transferred from "
                f"{ctx.author} to {member}"
            )
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I need **Manage Channels** permission."
        )

    if (
        claimed_id
        and claimed_id != member.id
    ):

        old_claimer = ctx.guild.get_member(
            claimed_id
        )

        if old_claimer:

            try:

                await ctx.channel.set_permissions(
                    old_claimer,
                    overwrite=None,
                    reason="Ticket transferred"
                )

            except discord.Forbidden:
                pass

    middleman_role = discord.utils.find(
        lambda role: role.name.lower() == "middleman",
        ctx.guild.roles
    )

    if middleman_role:

        try:

            await ctx.channel.set_permissions(
                middleman_role,
                view_channel=False,
                reason="Ticket transferred"
            )

        except discord.Forbidden:
            pass

    try:

        await ctx.channel.set_permissions(
            member,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            reason="Ticket transferred"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I couldn't give the new user access."
        )

    embed = discord.Embed(
        title="🔄 Ticket Transferred",
        description=(
            f"🎫 This ticket has been transferred to "
            f"{member.mention}."
        ),
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 New Ticket Holder",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="👮 Transferred By",
        value=ctx.author.mention,
        inline=False
    )

    await ctx.send(embed=embed)


@transferticket.error
async def transferticket_error(ctx, error):

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "❌ Usage: `$transferticket @user` or "
            "`$transferticket userID`"
        )


# ============================================================
# $ADD @USER OR USER ID
# ============================================================

@bot.command(name="add")
@commands.has_permissions(manage_channels=True)
async def add_user(
    ctx,
    user_input: str
):

    if not is_ticket_channel(ctx.channel):

        return await ctx.send(
            "❌ This command can only be used in a ticket."
        )

    member = await get_member_from_input(
        ctx,
        user_input
    )

    if member is None:

        return await ctx.send(
            "❌ I couldn't find that member.\n"
            "Use: `$add @user` or `$add userID`"
        )

    if member.bot:

        return await ctx.send(
            "❌ You cannot add a bot to the ticket."
        )

    permissions = ctx.channel.permissions_for(
        member
    )

    if permissions.view_channel:

        return await ctx.send(
            f"❌ {member.mention} already has access "
            f"to this ticket."
        )

    try:

        await ctx.channel.set_permissions(
            member,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            reason=f"Added to ticket by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "❌ I need **Manage Channels** permission "
            "to add people to tickets."
        )

    embed = discord.Embed(
        title="👤 Member Added",
        description=(
            f"{member.mention} has been added to this ticket."
        ),
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.add_field(
        name="👤 Added Member",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="👮 Added By",
        value=ctx.author.mention,
        inline=False
    )

    await ctx.send(embed=embed)


@add_user.error
async def add_user_error(ctx, error):

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "❌ Usage: `$add @user` or `$add userID`"
        )

    elif isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "❌ You need the **Manage Channels** permission."
        )


# ============================================================
# BOT READY
# ============================================================

@bot.event
async def on_ready():

    print(
        f"✅ Logged in as {bot.user}"
    )

    print(
        f"✅ Bot is running in "
        f"{len(bot.guilds)} server(s)"
    )


# ============================================================
# RUN BOT
# ============================================================

bot.run(TOKEN)
