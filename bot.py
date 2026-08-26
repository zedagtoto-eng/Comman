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
# Usage: $addvouch @user 5
# ============================================================

@bot.command(name="addvouch")
@commands.has_permissions(manage_messages=True)
async def addvouch(ctx, member: discord.Member, amount: int = 1):

    if member.bot:
        return await ctx.send("❌ You cannot add a vouch to a bot.")

    if amount <= 0:
        return await ctx.send("❌ The number must be greater than 0.")

    if amount > 1000:
        return await ctx.send(
            "❌ You cannot add more than **1000** vouches at once."
        )

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
    embed.set_footer(text=f"Vouch profile • {member.display_name}")

    await ctx.send(embed=embed)


@addvouch.error
async def addvouch_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Messages** permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$addvouch @user (number)`")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Usage: `$addvouch @user (number)`")


# ============================================================
# $REMOVEVOUCH
# Usage: $removevouch @user 2
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
    embed.set_footer(text=f"Vouch profile • {member.display_name}")

    await ctx.send(embed=embed)


@removevouch.error
async def removevouch_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Messages** permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$removevouch @user (number)`")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Usage: `$removevouch @user (number)`")


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
async def role_command(ctx, member: discord.Member, role: discord.Role):

    if role.is_default():
        return await ctx.send("❌ You cannot give the @everyone role.")

    if role.managed:
        return await ctx.send("❌ You cannot manually assign a managed role.")

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
            value=f"{role.mention}\n`{role.id}`",
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=ctx.author.mention,
            inline=False
        )

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to give that role.")


@role_command.error
async def role_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Roles** permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$role @user @role`")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Usage: `$role @user @role`")


# ============================================================
# $PROMO
# Usage: $promo @user
# ============================================================

@bot.command(name="promo")
@commands.has_permissions(manage_roles=True)
async def promo(ctx, member: discord.Member):

    bot_top = ctx.guild.me.top_role

    roles = sorted(
        [
            r for r in ctx.guild.roles
            if not r.is_default()
            and not r.managed
            and r < bot_top
        ],
        key=lambda r: r.position
    )

    higher_roles = [
        r for r in roles
        if r.position > member.top_role.position
    ]

    if not higher_roles:
        return await ctx.send(
            "❌ There is no higher role I can give this user."
        )

    next_role = higher_roles[0]

    if (
        next_role >= ctx.author.top_role
        and ctx.author != ctx.guild.owner
    ):
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
            value=f"{next_role.mention}\n`{next_role.id}`",
            inline=False
        )

        embed.add_field(
            name="👮 Promoted By",
            value=ctx.author.mention,
            inline=False
        )

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to give that role.")


@promo.error
async def promo_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need the **Manage Roles** permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$promo @user`")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid member.")


# ============================================================
# $DEMO
# Usage: $demo @user
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

    if (
        current_role >= ctx.author.top_role
        and ctx.author != ctx.guild.owner
    ):
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
            value=f"{current_role.mention}\n`{current_role.id}`",
            inline=False
        )

        embed.add_field(
            name="🎭 New Role",
            value=(
                f"{new_role.mention}\n`{new_role.id}`"
                if new_role
                else "No lower role"
            ),
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
        await ctx.send("❌ You need the **Manage Roles** permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$demo @user`")

    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid member.")


# ============================================================
# $W
# Usage: $w @user
# ============================================================

@bot.command(name="w")
async def profile(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    # --------------------------------------------------------
    # ROLES WITH IDS
    # --------------------------------------------------------

    roles = [
        f"{role.mention} (`{role.id}`)"
        for role in reversed(member.roles)
        if not role.is_default()
    ]

    role_text = ", ".join(roles) if roles else "No roles"

    if len(role_text) > 1024:
        role_text = role_text[:1020] + "..."

    # --------------------------------------------------------
    # KEY PERMISSIONS
    # --------------------------------------------------------

    permissions = []

    permission_names = {
        "administrator": "Administrator",
        "manage_guild": "Manage Server",
        "manage_roles": "Manage Roles",
        "manage_channels": "Manage Channels",
        "manage_messages": "Manage Messages",
        "manage_webhooks": "Manage Webhooks",
        "manage_nicknames": "Manage Nicknames",
        "kick_members": "Kick Members",
        "ban_members": "Ban Members",
        "moderate_members": "Timeout Members",
        "mention_everyone": "Mention Everyone",
        "view_audit_log": "View Audit Log",
        "manage_threads": "Manage Threads",
        "manage_events": "Manage Events"
    }

    for permission, name in permission_names.items():

        if getattr(member.guild_permissions, permission, False):
            permissions.append(name)

    permissions_text = (
        ", ".join(permissions)
        if permissions
        else "No key permissions"
    )

    if len(permissions_text) > 1024:
        permissions_text = permissions_text[:1020] + "..."

    # --------------------------------------------------------
    # PROFILE EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title=f"👤 {member.display_name}",
        color=discord.Color.from_rgb(255, 20, 180)
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.add_field(
        name="👤 User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="👑 Username",
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
        value=(
            discord.utils.format_dt(
                member.joined_at,
                style="F"
            )
            if member.joined_at
            else "Unknown"
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

    embed.add_field(
        name=f"🎭 Roles [{len(member.roles) - 1}]",
        value=role_text,
        inline=False
    )

    embed.add_field(
        name="🔑 Key Permissions",
        value=permissions_text,
        inline=False
    )

    embed.set_footer(
        text=f"User profile • {member.display_name}"
    )

    await ctx.send(embed=embed)


@profile.error
async def profile_error(ctx, error):

    if isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid member.")


# ============================================================
# $FILL
# Usage: $fill
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

    role_text = ", ".join(
        f"{role.mention} (`{role.id}`)"
        for role in added
    )

    if len(role_text) > 4000:
        role_text = role_text[:3990] + "..."

    embed = discord.Embed(
        title="🎭 Roles Filled",
        description=(
            f"{ctx.author.mention}, the available roles below "
            "your highest role have been added."
        ),
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
# $ROLES
# Usage: $roles
# ============================================================

@bot.command(name="roles")
async def roles_command(ctx):

    roles = [
        role
        for role in reversed(ctx.guild.roles)
        if not role.is_default()
    ]

    if not roles:
        return await ctx.send(
            "❌ This server has no custom roles."
        )

    lines = [
        f"{role.mention} — `{role.id}`"
        for role in roles
    ]

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
            title=(
                "🎭 Server Roles"
                + (
                    f" • {index + 1}/{len(chunks)}"
                    if len(chunks) > 1
                    else ""
                )
            ),
            description=chunk,
            color=discord.Color.from_rgb(255, 20, 180)
        )

        embed.set_footer(
            text=f"{len(ctx.guild.roles) - 1} custom role(s)"
        )

        await ctx.send(embed=embed)


# ============================================================
# $SERVERINFO
# Usage: $serverinfo
# ============================================================

@bot.command(name="serverinfo")
async def serverinfo(ctx):

    guild = ctx.guild

    humans = sum(
        1
        for member in guild.members
        if not member.bot
    )

    bots = sum(
        1
        for member in guild.members
        if member.bot
    )

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
        value=f"**{len(guild.text_channels)}**",
        inline=True
    )

    embed.add_field(
        name="🔊 Voice Channels",
        value=f"**{len(guild.voice_channels)}**",
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
# TEMP ROLE STORAGE
# ============================================================

TEMP_FILE = "temp_roles.json"

# ============================================================
# PUT THE TWO ROLE IDS THAT SHOULD STAY DURING $TEMP HERE
# ============================================================

TEMP_KEEP_ROLE_IDS = [
    0,  # First role
    0   # Second role
]


def load_temp_roles():

    if not os.path.exists(TEMP_FILE):
        return {}

    try:
        with open(TEMP_FILE, "r") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return {}


def save_temp_roles(data):

    with open(TEMP_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ============================================================
# $TEMP
# Usage: $temp @user
#
# Removes all removable roles except the 2 protected roles.
# Saves the old roles so $canceltemp can restore them.
# ============================================================

@bot.command(name="temp")
@commands.has_permissions(manage_roles=True)
async def temp(ctx, member: discord.Member):

    if member.id == ctx.author.id:
        return await ctx.send(
            "❌ You cannot use this command on yourself."
        )

    if member.id == ctx.guild.owner_id:
        return await ctx.send(
            "❌ You cannot temp the server owner."
        )

    if member.top_role >= ctx.guild.me.top_role:
        return await ctx.send(
            "❌ I cannot modify this user because their highest role "
            "is equal to or higher than my highest role."
        )

    temp_data = load_temp_roles()
    user_id = str(member.id)

    # --------------------------------------------------------
    # SAVE CURRENT ROLES
    # --------------------------------------------------------

    original_roles = []

    for role in member.roles:

        if role.is_default():
            continue

        if role < ctx.guild.me.top_role:
            original_roles.append(role.id)

    temp_data[user_id] = original_roles
    save_temp_roles(temp_data)

    # --------------------------------------------------------
    # FIND ROLES TO REMOVE
    # --------------------------------------------------------

    roles_to_remove = []

    for role in member.roles:

        if role.is_default():
            continue

        if role.id in TEMP_KEEP_ROLE_IDS:
            continue

        if role >= ctx.guild.me.top_role:
            continue

        roles_to_remove.append(role)

    if not roles_to_remove:
        return await ctx.send(
            f"❌ {member.mention} has no removable roles."
        )

    try:

        await member.remove_roles(
            *roles_to_remove,
            reason=f"Temp command used by {ctx.author}"
        )

        kept_roles = []

        for role_id in TEMP_KEEP_ROLE_IDS:1541096480146853968 1541096476610928730

            role = ctx.guild.get_role(role_id)

            if role:
                kept_roles.append(
                    f"{role.mention} (`{role.id}`)"
                )

        embed = discord.Embed(
            title="🧹 User Temped",
            description=f"{member.mention}'s roles have been cleared.",
            color=discord.Color.from_rgb(255, 20, 180)
        )

        embed.add_field(
            name="👤 User",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="🗑️ Roles Removed",
            value=str(len(roles_to_remove)),
            inline=True
        )

        embed.add_field(
            name="🔒 Roles Kept",
            value=", ".join(kept_roles) if kept_roles else "None",
            inline=False
        )

        embed.add_field(
            name="👮 Staff",
            value=ctx.author.mention,
            inline=False
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text=f"Temp • {member.display_name}"
        )

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "❌ I don't have permission to remove these roles."
        )


@temp.error
async def temp_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You need the **Manage Roles** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Usage: `$temp @user`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# $CANCELTEMP
# Usage: $canceltemp @user
#
# Restores all roles saved by $temp.
# ============================================================

@bot.command(name="canceltemp")
@commands.has_permissions(manage_roles=True)
async def canceltemp(ctx, member: discord.Member):

    temp_data = load_temp_roles()
    user_id = str(member.id)

    if user_id not in temp_data:
        return await ctx.send(
            f"❌ {member.mention} does not have a saved temp role history."
        )

    original_role_ids = temp_data[user_id]

    roles_to_restore = []

    for role_id in original_role_ids:

        role = ctx.guild.get_role(role_id)

        if role is None:
            continue

        if role.is_default():
            continue

        if role >= ctx.guild.me.top_role:
            continue

        if role not in member.roles:
            roles_to_restore.append(role)

    try:

        if roles_to_restore:

            await member.add_roles(
                *roles_to_restore,
                reason=f"Cancel temp command used by {ctx.author}"
            )

        # Delete saved history after restoration
        del temp_data[user_id]
        save_temp_roles(temp_data)

        restored_text = ", ".join(
            f"{role.mention} (`{role.id}`)"
            for role in roles_to_restore
        )

        if not restored_text:
            restored_text = "No additional roles needed restoration."

        if len(restored_text) > 4000:
            restored_text = restored_text[:3990] + "..."

        embed = discord.Embed(
            title="✅ Temp Cancelled",
            description=f"{member.mention}'s previous roles have been restored.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👤 User",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="🔄 Roles Restored",
            value=str(len(roles_to_restore)),
            inline=True
        )

        embed.add_field(
            name="🎭 Restored Roles",
            value=restored_text,
            inline=False
        )

        embed.add_field(
            name="👮 Staff",
            value=ctx.author.mention,
            inline=False
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text=f"Temp cancelled • {member.display_name}"
        )

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "❌ I don't have permission to restore one or more roles."
        )


@canceltemp.error
async def canceltemp_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You need the **Manage Roles** permission."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Usage: `$canceltemp @user`"
        )

    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Please mention a valid member."
        )


# ============================================================
# GENERAL ERROR HANDLER
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
            f"❌ Missing argument. Use `{ctx.prefix}{ctx.command.name} ...`."
        )
        return

    if isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Invalid argument. Please mention the correct user or role."
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
