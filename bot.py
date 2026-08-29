===================================================================
# IMPORTS
# ============================================================

import os
import io
import html
import json
import re
import asyncio
import datetime
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
BACKUP_FILE = "server_backup.json"


# ============================================================
# TICKET SETTINGS
# ============================================================

TICKET_CATEGORY_ID = 1541096510102437911

# Channel where closed-ticket transcripts are sent
# Replace 0 with your transcript channel ID.
TRANSCRIPT_CHANNEL_ID = 1541096728806039693


# ============================================================
# APPLICATION SETTINGS
# ============================================================

APPLICATION_ROLE_ID = 1541096476610928730
RESULT_CHANNEL_ID = 1541096707985637496

PINK = discord.Color.from_rgb(255, 105, 180)


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

    match = re.fullmatch(
        r"<@!?(\d+)>",
        value
    )

    if match:

        user_id = int(match.group(1))

    elif value.isdigit():

        user_id = int(value)

    else:

        return None

    return ctx.guild.get_member(user_id)


# ============================================================
# MEMBER INPUT RESOLVER
# ============================================================

async def get_member_from_input(ctx, value):

    if isinstance(value, discord.Member):
        return value

    value = str(value).strip()

    match = re.fullmatch(
        r"<@!?(\d+)>",
        value
    )

    if match:

        user_id = int(match.group(1))

        return ctx.guild.get_member(
            user_id
        )

    if value.isdigit():

        return ctx.guild.get_member(
            int(value)
        )

    value_lower = value.lower()

    for member in ctx.guild.members:

        if str(member).lower() == value_lower:

            return member

        if member.name.lower() == value_lower:

            return member

        if member.display_name.lower() == value_lower:

            return member

    return None


# ============================================================
# APPLICATION BUTTONS
# ============================================================

class ApplicationView(discord.ui.View):

    def __init__(self, member_id):

        super().__init__(timeout=120)

        self.member_id = member_id
        self.finished = False

    # ========================================================
    # ONLY THE PINGED USER CAN CLICK
    # ========================================================

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.member_id:

            await interaction.response.send_message(
                "Ã¢ÂÂ This application is not for you.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # ACCEPT
    # ========================================================

    @discord.ui.button(
        label="Accept",
        emoji="Ã¢ÂÂ",
        style=discord.ButtonStyle.success,
        custom_id="application_accept"
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.finished:

            return await interaction.response.send_message(
                "Ã¢ÂÂ This application has already been decided.",
                ephemeral=True
            )

        guild = interaction.guild

        if guild is None:

            return await interaction.response.send_message(
                "Ã¢ÂÂ This can only be used inside a server.",
                ephemeral=True
            )

        member = guild.get_member(
            self.member_id
        )

        if member is None:

            try:

                member = await guild.fetch_member(
                    self.member_id
                )

            except discord.NotFound:

                return await interaction.response.send_message(
                    "Ã¢ÂÂ User is no longer in the server.",
                    ephemeral=True
                )

        role = guild.get_role(
            APPLICATION_ROLE_ID
        )

        if role is None:

            return await interaction.response.send_message(
                "Ã¢ÂÂ Application role was not found.\n"
                "Check APPLICATION_ROLE_ID.",
                ephemeral=True
            )

        if role >= guild.me.top_role:

            return await interaction.response.send_message(
                "Ã¢ÂÂ I can't give this role.\n\n"
                "Make sure my bot's highest role is ABOVE "
                "the application role.",
                ephemeral=True
            )

        try:

            await member.add_roles(
                role,
                reason="Application accepted"
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "Ã¢ÂÂ I can't give this role.\n\n"
                "Make sure I have **Manage Roles** and "
                "my bot role is above the application role.",
                ephemeral=True
            )

        except discord.HTTPException:

            return await interaction.response.send_message(
                "Ã¢ÂÂ Discord returned an error while giving "
                "the role. Please try again.",
                ephemeral=True
            )

        self.finished = True

        for child in self.children:

            child.disabled = True

        application_embed = discord.Embed(
            title="Application Accepted",
            description=(
                f"Ã¢ÂÂ {member.mention} has been accepted "
                f"and received {role.mention}."
            ),
            color=PINK
        )

        application_embed.set_footer(
            text="Minstrea ~ MM service Ã¢ÂÂ¢ Application System"
        )

        await interaction.response.edit_message(
            embed=application_embed,
            view=self
        )

        result_channel = guild.get_channel(
            RESULT_CHANNEL_ID
        )

        if result_channel is None:

            print(
                "Ã¢ÂÂ RESULT_CHANNEL_ID is incorrect "
                "or the bot cannot see that channel."
            )

            return

        welcome_embed = discord.Embed(
            title="Ã°ÂÂÂ New Flopper!",
            description=(
                f"Congratulations {member.mention}, "
                "you're now a flopper!\n\n"

                "Ã¢ÂÂ¢ To learn about flopping or how to get rich "
                "join the main-guide channel\n\n"

                "Ã¢ÂÂ¢ To hangout with other floppers "
                "talk in the staff-chat channel\n\n"

                "Ã¢ÂÂ¢ Lastly to get a middleman for your trades "
                "do a ticket in the middleman channel"
            ),
            color=PINK
        )

        welcome_embed.set_thumbnail(
            url=member.display_avatar.url
        )

        welcome_embed.set_footer(
            text="Minstrea ~ MM service Ã¢ÂÂ¢ New Flopper"
        )

        await result_channel.send(
            content=member.mention,
            embed=welcome_embed,
            allowed_mentions=discord.AllowedMentions(
                users=True
            )
        )

    # ========================================================
    # DECLINE
    # ========================================================

    @discord.ui.button(
        label="Decline",
        emoji="Ã¢ÂÂ",
        style=discord.ButtonStyle.danger,
        custom_id="application_decline"
    )
    async def decline(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.finished:

            return await interaction.response.send_message(
                "Ã¢ÂÂ This application has already been decided.",
                ephemeral=True
            )

        guild = interaction.guild

        if guild is None:

            return await interaction.response.send_message(
                "Ã¢ÂÂ This can only be used inside a server.",
                ephemeral=True
            )

        member = guild.get_member(
            self.member_id
        )

        if member is None:

            try:

                member = await guild.fetch_member(
                    self.member_id
                )

            except discord.NotFound:

                member = interaction.user

        self.finished = True

        for child in self.children:

            child.disabled = True

        embed = discord.Embed(
            title="Application Declined",
            description=(
                f"Ã¢ÂÂ {member.mention}'s application "
                "has been declined."
            ),
            color=PINK
        )

        embed.set_footer(
            text="Minstrea ~ MM service Ã¢ÂÂ¢ Application System"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # TIMEOUT
    # ========================================================

    async def on_timeout(self):

        if self.finished:
            return

        self.finished = True

        for child in self.children:

            child.disabled = True


# ============================================================
# $TRIGGER @USER
# ============================================================

@bot.command(name="trigger")
@commands.has_permissions(manage_guild=True)
async def trigger(
    ctx,
    member: discord.Member
):

    embed = discord.Embed(
        title="Minstrea ~ MM service",
        description=(
            f"{member.mention}\n\n"

            "**Flopping Application Ã°ÂÂÂ**\n"
            "You can join a well-built system and community "
            "where you can participate in server activities "
            "and events.\n\n"

            "**What is Flopping? Ã¢ÂÂ**\n"
            "Flopping is where you participate in our "
            "community activities and events.\n\n"

            "Detailed information will be provided once "
            "you accept this application.\n\n"

            "**Flopping Offer**\n"
            "Choose whether you want to accept or decline "
            "the offer below.\n\n"

            "Ã¢ÂÂ¼Ã¯Â¸Â **Note**\n"
            "You only have two minutes to either **Accept** "
            "or **Decline** the offer presented above. "
            "Choose wisely, the clock is ticking.."
        ),
        color=PINK
    )

    embed.set_footer(
        text="Minstrea ~ MM service Ã¢ÂÂ¢ Application System"
    )

    view = ApplicationView(
        member.id
    )

    await ctx.send(
        content=member.mention,
        embed=embed,
        view=view,
        allowed_mentions=discord.AllowedMentions(
            users=True
        )
    )


@trigger.error
async def trigger_error(ctx, error):

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Usage: `$trigger @user`"
        )

    if isinstance(
        error,
        commands.MemberNotFound
    ):

        return await ctx.send(
            "Ã¢ÂÂ I couldn't find that member."
        )

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need **Manage Server** permission "
            "to use `$trigger`."
        )

    print(
        f"Ã¢ÂÂ Trigger error: "
        f"{type(error).__name__}: {error}"
    )

    await ctx.send(
        "Ã¢ÂÂ An error occurred while running `$trigger`."
    )


# ============================================================
# $ADDVOUCH @USER NUMBER
# ============================================================

@bot.command(name="addvouch")
@commands.has_permissions(manage_messages=True)
async def addvouch(
    ctx,
    member: discord.Member,
    amount: int = 1
):

    if member.bot:

        return await ctx.send(
            "Ã¢ÂÂ You cannot add a vouch to a bot."
        )

    if amount <= 0:

        return await ctx.send(
            "Ã¢ÂÂ The number must be greater than 0."
        )

    vouches = load_vouches()

    user_id = str(member.id)

    vouches[user_id] = (
        vouches.get(user_id, 0) + amount
    )

    save_vouches(vouches)

    embed = discord.Embed(
        title="Ã¢Â­Â Vouch Added",
        description=(
            f"Added **{amount}** vouch(s) to "
            f"{member.mention}."
        ),
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ¤ User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="Ã¢Â­Â Total Vouches",
        value=f"**{vouches[user_id]}**",
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ® Added By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"Vouch profile Ã¢ÂÂ¢ {member.display_name}"
    )

    await ctx.send(
        embed=embed
    )


@addvouch.error
async def addvouch_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "Ã¢ÂÂ You need the **Manage Messages** permission."
        )

    elif isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$addvouch @user (number)`"
        )

    elif isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$addvouch @user (number)`"
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
            "Ã¢ÂÂ The number must be greater than 0."
        )

    vouches = load_vouches()

    user_id = str(member.id)

    current = vouches.get(
        user_id,
        0
    )

    if current <= 0:

        return await ctx.send(
            f"Ã¢ÂÂ {member.mention} has no vouches."
        )

    new_total = max(
        0,
        current - amount
    )

    vouches[user_id] = new_total

    save_vouches(vouches)

    embed = discord.Embed(
        title="Ã°ÂÂÂÃ¯Â¸Â Vouch Removed",
        description=(
            f"Removed **{amount}** vouch(s) from "
            f"{member.mention}."
        ),
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ¤ User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="Ã¢Â­Â Total Vouches",
        value=f"**{new_total}**",
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ® Removed By",
        value=ctx.author.mention,
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    await ctx.send(
        embed=embed
    )


@removevouch.error
async def removevouch_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "Ã¢ÂÂ You need the **Manage Messages** permission."
        )

    elif isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$removevouch @user (number)`"
        )

    elif isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$removevouch @user (number)`"
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
        title="Ã¢Â­Â Vouches",
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ¤ User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="Ã¢Â­Â Total Vouches",
        value=f"**{count}**",
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"Vouch profile Ã¢ÂÂ¢ {member.display_name}"
    )

    await ctx.send(
        embed=embed
    )


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
            "Ã¢ÂÂ You cannot give the @everyone role."
        )

    if role.managed:

        return await ctx.send(
            "Ã¢ÂÂ You cannot manually assign a managed role."
        )

    if role >= ctx.guild.me.top_role:

        return await ctx.send(
            "Ã¢ÂÂ I cannot give that role because it is equal to "
            "or higher than my highest role."
        )

    if (
        role >= ctx.author.top_role
        and ctx.author != ctx.guild.owner
    ):

        return await ctx.send(
            "Ã¢ÂÂ You cannot manage a role equal to or higher "
            "than your highest role."
        )

    if role in member.roles:

        return await ctx.send(
            f"Ã¢ÂÂ {member.mention} already has {role.mention}."
        )

    try:

        await member.add_roles(
            role,
            reason=f"Role command used by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to give that role."
        )

    await ctx.send(
        f"Ã¢ÂÂ Added {role.mention} to {member.mention}."
    )


@role_command.error
async def role_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "Ã¢ÂÂ You need the **Manage Roles** permission."
        )

    elif isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$role @user @role`"
        )

    elif isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$role @user @role`"
        )


# ============================================================
# $PROMO @USER
# ============================================================

@bot.command(name="promo")
@commands.has_permissions(manage_roles=True)
async def promo(
    ctx,
    member: discord.Member
):

    if member.bot:

        return await ctx.send(
            "Ã¢ÂÂ You cannot promote a bot."
        )

    bot_top = ctx.guild.me.top_role

    manageable_roles = [
        role
        for role in ctx.guild.roles
        if role != ctx.guild.default_role
        and not role.managed
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
            f"Ã¢ÂÂ {member.mention} cannot be promoted any further."
        )

    if (
        next_role >= ctx.author.top_role
        and ctx.author != ctx.guild.owner
    ):

        return await ctx.send(
            "Ã¢ÂÂ You cannot promote someone to a role equal to "
            "or higher than your highest role."
        )

    remove_roles = [
        role
        for role in current_manageable
        if role.position < next_role.position
    ]

    try:

        if remove_roles:

            await member.remove_roles(
                *remove_roles,
                reason=f"Promotion by {ctx.author}"
            )

        await member.add_roles(
            next_role,
            reason=f"Promotion by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to manage these roles."
        )

    await ctx.send(
        f"Ã¢Â¬ÂÃ¯Â¸Â {member.mention} has been promoted to "
        f"{next_role.mention}."
    )


@promo.error
async def promo_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "Ã¢ÂÂ You need the **Manage Roles** permission."
        )

    elif isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$promo @user`"
        )

    elif isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Please mention a valid member."
        )


# ============================================================
# $DEMO @USER
# ============================================================

@bot.command(name="demo")
@commands.has_permissions(manage_roles=True)
async def demo(
    ctx,
    member: discord.Member
):

    if member.bot:

        return await ctx.send(
            "Ã¢ÂÂ You cannot demote a bot."
        )

    bot_top = ctx.guild.me.top_role

    manageable_roles = [
        role
        for role in ctx.guild.roles
        if role != ctx.guild.default_role
        and not role.managed
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
            f"Ã¢ÂÂ {member.mention} has no manageable role to demote."
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

    try:

        await member.remove_roles(
            highest_current,
            reason=f"Demotion by {ctx.author}"
        )

        if next_role is not None:

            await member.add_roles(
                next_role,
                reason=f"Demotion by {ctx.author}"
            )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to manage these roles."
        )

    if next_role is None:

        return await ctx.send(
            f"Ã¢Â¬ÂÃ¯Â¸Â {member.mention} was demoted and "
            f"{highest_current.mention} was removed."
        )

    await ctx.send(
        f"Ã¢Â¬ÂÃ¯Â¸Â {member.mention} has been demoted to "
        f"{next_role.mention}."
    )


@demo.error
async def demo_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "Ã¢ÂÂ You need the **Manage Roles** permission."
        )

    elif isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$demo @user`"
        )

    elif isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Please mention a valid member."
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
        title=f"Ã°ÂÂÂ¤ User Profile Ã¢ÂÂ¢ {member.display_name}",
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ¤ User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ Username",
        value=str(member),
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ ID",
        value=str(member.id),
        inline=False
    )

    if member.joined_at:

        embed.add_field(
            name="Ã°ÂÂÂ Joined Guild",
            value=discord.utils.format_dt(
                member.joined_at,
                style="F"
            ),
            inline=False
        )

    embed.add_field(
        name="Ã°ÂÂÂÃ¯Â¸Â Account Created",
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
        name=f"Ã°ÂÂÂ­ Roles [{len(roles)}]",
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

        if getattr(
            permissions,
            attribute,
            False
        ):

            permission_names.append(
                display_name
            )

    embed.add_field(
        name="Ã°ÂÂÂ Role Permissions",
        value=", ".join(permission_names)
        if permission_names
        else "No special permissions",
        inline=False
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"User profile Ã¢ÂÂ¢ {member.display_name}"
    )

    await ctx.send(
        embed=embed
    )


@profile.error
async def profile_error(ctx, error):

    if isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Please mention a valid member."
        )


# ============================================================
# $FILL
# ============================================================

@bot.command(name="fill")
@commands.has_permissions(manage_roles=True)
async def fill(ctx):

    member = ctx.author
    bot_member = ctx.guild.me
    bot_top = bot_member.top_role

    if not bot_member.guild_permissions.manage_roles:

        return await ctx.send(
            "Ã¢ÂÂ I need the **Manage Roles** permission."
        )

    if member.top_role == ctx.guild.default_role:

        return await ctx.send(
            "Ã¢ÂÂ You have no role to fill below."
        )

    roles_to_add = []

    for role in ctx.guild.roles:

        if role == ctx.guild.default_role:
            continue

        if role.managed:
            continue

        if role.position >= bot_top.position:
            continue

        if role.position >= member.top_role.position:
            continue

        if role in member.roles:
            continue

        if not role.is_assignable():
            continue

        roles_to_add.append(role)

    if not roles_to_add:

        return await ctx.send(
            "Ã¢ÂÂ There are no missing roles that I can assign "
            "below your highest role."
        )

    roles_to_add.sort(
        key=lambda role: role.position
    )

    try:

        await member.add_roles(
            *roles_to_add,
            reason=f"Fill roles by {ctx.author}"
        )

    except discord.Forbidden as e:

        print(
            f"Ã¢ÂÂ $fill Forbidden error: {e}"
        )

        return await ctx.send(
            "Ã¢ÂÂ Discord refused the role update. "
            "Make sure I have **Manage Roles** and my bot "
            "role is above the roles being filled."
        )

    except discord.HTTPException as e:

        print(
            f"Ã¢ÂÂ $fill HTTP error: {e}"
        )

        return await ctx.send(
            "Ã¢ÂÂ Discord returned an error while giving the roles."
        )

    except Exception as e:

        print(
            f"Ã¢ÂÂ $fill unexpected error: "
            f"{type(e).__name__}: {e}"
        )

        return await ctx.send(
            f"Ã¢ÂÂ `$fill` failed: `{type(e).__name__}`"
        )

    await ctx.send(
        f"Ã¢ÂÂ Filled **{len(roles_to_add)}** missing role(s) "
        f"for {member.mention}."
    )


@fill.error
async def fill_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need the **Manage Roles** permission."
        )

    if isinstance(
        error,
        commands.CommandInvokeError
    ):

        print(
            f"Ã¢ÂÂ $fill error: "
            f"{type(error.original).__name__}: "
            f"{error.original}"
        )

        return await ctx.send(
            f"Ã¢ÂÂ `$fill` failed: "
            f"`{type(error.original).__name__}`"
        )

    print(
        f"Ã¢ÂÂ $fill error: "
        f"{type(error).__name__}: {error}"
    )

    await ctx.send(
        "Ã¢ÂÂ An error occurred while running `$fill`."
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
            f"{role.mention} Ã¢ÂÂ `{role.id}`"
        )

    if not role_lines:

        return await ctx.send(
            "Ã¢ÂÂ No roles found."
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
                "Ã°ÂÂÂ­ Server Roles"
                + (
                    f" Ã¢ÂÂ Page {index + 1}"
                    if len(chunks) > 1
                    else ""
                )
            ),
            description=chunk,
            color=discord.Color.from_rgb(
                255,
                20,
                180
            )
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
        title=f"Ã°ÂÂÂ {guild.name}",
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ Owner",
        value=f"<@{guild.owner_id}>",
        inline=True
    )

    embed.add_field(
        name="Ã°ÂÂÂ Server ID",
        value=str(guild.id),
        inline=True
    )

    embed.add_field(
        name="Ã°ÂÂÂ¥ Members",
        value=str(guild.member_count),
        inline=True
    )

    embed.add_field(
        name="Ã°ÂÂÂ¬ Channels",
        value=str(len(guild.channels)),
        inline=True
    )

    embed.add_field(
        name="Ã°ÂÂÂ­ Roles",
        value=str(len(guild.roles) - 1),
        inline=True
    )

    embed.add_field(
        name="Ã°ÂÂÂ Boost Level",
        value=str(guild.premium_tier),
        inline=True
    )

    embed.add_field(
        name="Ã°ÂÂÂ Boosts",
        value=str(
            guild.premium_subscription_count or 0
        ),
        inline=True
    )

    embed.add_field(
        name="Ã°ÂÂÂ Created",
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
        text=f"Server info Ã¢ÂÂ¢ {guild.name}"
    )

    await ctx.send(
        embed=embed
    )


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
            "Ã¢ÂÂ You cannot temp a bot."
        )

    if member.top_role >= bot_top:

        return await ctx.send(
            "Ã¢ÂÂ I cannot manage you because your highest role "
            "is equal to or higher than my highest role."
        )

    temp_data = load_temp_data()
    user_id = str(member.id)

    if user_id in temp_data:

        return await ctx.send(
            "Ã¢ÂÂ You are already temporarily demoted."
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
        and not role.managed
        and role < bot_top
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

            save_temp_data(
                temp_data
            )

            return await ctx.send(
                "Ã¢ÂÂ I don't have permission to remove one or "
                "more of these roles."
            )

    kept_roles = [
        role.mention
        for role in member.roles
        if role.id in TEMP_KEEP_ROLE_IDS
    ]

    embed = discord.Embed(
        title="Ã¢ÂÂ¸Ã¯Â¸Â Temporary Demotion",
        description=(
            f"{member.mention} has been temporarily demoted."
        ),
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ¤ User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ Roles Kept",
        value=", ".join(kept_roles)
        if kept_roles
        else "No protected roles found",
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂÃ¯Â¸Â Roles Removed",
        value=str(
            len(roles_to_remove)
        ),
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ¾ Saved Roles",
        value=f"**{len(current_roles)}** roles saved",
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ® Action By",
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

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "Ã¢ÂÂ You need the **Manage Roles** permission "
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
            "Ã¢ÂÂ You need one of the required roles to use "
            "`$canceltemp`."
        )

    if not ctx.guild.me.guild_permissions.manage_roles:

        return await ctx.send(
            "Ã¢ÂÂ I need the **Manage Roles** permission to "
            "restore roles."
        )

    member = ctx.author
    user_id = str(member.id)

    temp_data = load_temp_data()

    if user_id not in temp_data:

        return await ctx.send(
            f"Ã¢ÂÂ No saved roles were found for "
            f"{member.mention}."
        )

    saved_role_ids = temp_data[user_id]

    restored_roles = []
    skipped_roles = []

    for role_id in saved_role_ids:

        role = ctx.guild.get_role(
            role_id
        )

        if role is None:
            continue

        if role == ctx.guild.default_role:
            continue

        if role.managed:

            skipped_roles.append(role)
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
                "Ã¢ÂÂ I don't have permission to restore one "
                "or more roles."
            )

    del temp_data[user_id]

    save_temp_data(
        temp_data
    )

    embed = discord.Embed(
        title="Ã¢ÂÂ¶Ã¯Â¸Â Temporary Demotion Cancelled",
        description=(
            f"Successfully restored the saved roles for "
            f"{member.mention}."
        ),
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ¤ User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ Roles Restored",
        value=f"**{len(restored_roles)}**",
        inline=False
    )

    if skipped_roles:

        embed.add_field(
            name="Ã¢ÂÂ Ã¯Â¸Â Roles Skipped",
            value=(
                f"**{len(skipped_roles)}** "
                "(above my highest role or managed)"
            ),
            inline=False
        )

    embed.add_field(
        name="Ã°ÂÂÂ® Cancelled By",
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


# ============================================================
# $TO @USER TIME
# ============================================================

@bot.command(name="to")
@commands.has_permissions(moderate_members=True)
async def timeout_command(
    ctx,
    member: discord.Member,
    duration: str
):

    if member == ctx.author:

        return await ctx.send(
            "Ã¢ÂÂ You cannot timeout yourself."
        )

    if member == ctx.guild.owner:

        return await ctx.send(
            "Ã¢ÂÂ You cannot timeout the server owner."
        )

    match = re.fullmatch(
        r"(\d+)(s|m|h|d)",
        duration.lower()
    )

    if not match:

        return await ctx.send(
            "Ã¢ÂÂ Invalid time.\n"
            "Use `s`, `m`, `h`, or `d`.\n\n"
            "Examples:\n"
            "`$to @user 30s`\n"
            "`$to @user 10m`\n"
            "`$to @user 1h`\n"
            "`$to @user 2d`"
        )

    amount = int(
        match.group(1)
    )

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
            "Ã¢ÂÂ Discord only allows timeouts up to **28 days**."
        )

    if member.top_role >= ctx.guild.me.top_role:

        return await ctx.send(
            "Ã¢ÂÂ I cannot timeout this member because their "
            "highest role is equal to or higher than mine."
        )

    try:

        await member.timeout(
            datetime.timedelta(
                seconds=seconds
            ),
            reason=f"Timeout by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to timeout this member."
        )

    except discord.HTTPException:

        return await ctx.send(
            "Ã¢ÂÂ Discord returned an error while applying "
            "the timeout."
        )

    await ctx.send(
        f"Ã°ÂÂÂ {member.mention} has been timed out for "
        f"**{duration}**."
    )


@timeout_command.error
async def timeout_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "Ã¢ÂÂ You need the **Timeout Members** permission."
        )

    elif isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$to @user (time)`"
        )

    elif isinstance(
        error,
        commands.BadArgument
    ):

        await ctx.send(
            "Ã¢ÂÂ Usage: `$to @user (time)`"
        )


# ============================================================
# $UNTO @USER
# ============================================================

@bot.command(name="unto")
@commands.has_permissions(moderate_members=True)
async def unto(
    ctx,
    member: discord.Member
):

    try:

        await member.timeout(
            None,
            reason=f"Timeout removed by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to remove this timeout."
        )

    await ctx.send(
        f"Ã°ÂÂÂ Timeout removed from {member.mention}."
    )


# ============================================================
# $BAN @USER OR ID
# ============================================================

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_command(
    ctx,
    target
):

    member = await get_member(
        ctx,
        target
    )

    if member is None:

        try:

            user = await bot.fetch_user(
                int(target)
            )

        except (
            ValueError,
            discord.NotFound,
            discord.HTTPException
        ):

            return await ctx.send(
                "Ã¢ÂÂ Please provide a valid user mention or ID."
            )

        try:

            await ctx.guild.ban(
                user,
                reason=f"Banned by {ctx.author}"
            )

        except discord.Forbidden:

            return await ctx.send(
                "Ã¢ÂÂ I don't have permission to ban this user."
            )

        return await ctx.send(
            f"Ã°ÂÂÂ¨ Banned **{user}**."
        )

    if member == ctx.author:

        return await ctx.send(
            "Ã¢ÂÂ You cannot ban yourself."
        )

    if member == ctx.guild.owner:

        return await ctx.send(
            "Ã¢ÂÂ You cannot ban the server owner."
        )

    if member.top_role >= ctx.guild.me.top_role:

        return await ctx.send(
            "Ã¢ÂÂ I cannot ban this member because their role "
            "is equal to or higher than mine."
        )

    try:

        await ctx.guild.ban(
            member,
            reason=f"Banned by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to ban this member."
        )

    await ctx.send(
        f"Ã°ÂÂÂ¨ Banned {member.mention}."
    )


# ============================================================
# $UNBAN USER ID
# ============================================================

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban_command(
    ctx,
    user_id: int
):

    try:

        user = await bot.fetch_user(
            user_id
        )

        await ctx.guild.unban(
            user,
            reason=f"Unbanned by {ctx.author}"
        )

    except discord.NotFound:

        return await ctx.send(
            "Ã¢ÂÂ That user is not banned or the ID is invalid."
        )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to unban users."
        )

    await ctx.send(
        f"Ã¢ÂÂ Unbanned **{user}**."
    )


# ============================================================
# $KICK @USER OR ID
# ============================================================

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_command(
    ctx,
    target
):

    member = await get_member(
        ctx,
        target
    )

    if member is None:

        return await ctx.send(
            "Ã¢ÂÂ The user must be in the server. "
            "Use a mention or user ID."
        )

    if member == ctx.author:

        return await ctx.send(
            "Ã¢ÂÂ You cannot kick yourself."
        )

    if member == ctx.guild.owner:

        return await ctx.send(
            "Ã¢ÂÂ You cannot kick the server owner."
        )

    if member.top_role >= ctx.guild.me.top_role:

        return await ctx.send(
            "Ã¢ÂÂ I cannot kick this member because their "
            "highest role is equal to or higher than mine."
        )

    try:

        await member.kick(
            reason=f"Kicked by {ctx.author}"
        )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to kick this member."
        )

    await ctx.send(
        f"Ã°ÂÂÂ¢ Kicked {member.mention}."
    )


# ============================================================
# $PURGE NUMBER
# ============================================================

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge_command(
    ctx,
    amount: int
):

    if amount <= 0:

        return await ctx.send(
            "Ã¢ÂÂ The number must be greater than 0."
        )

    if amount > 100:

        return await ctx.send(
            "Ã¢ÂÂ You can purge a maximum of **100 messages** "
            "at once."
        )

    try:

        deleted = await ctx.channel.purge(
            limit=amount + 1
        )

    except discord.Forbidden:

        return await ctx.send(
            "Ã¢ÂÂ I don't have permission to delete messages here."
        )

    count = max(
        0,
        len(deleted) - 1
    )

    message = await ctx.send(
        f"Ã°ÂÂ§Â¹ Deleted **{count}** message(s)."
    )

    await asyncio.sleep(3)

    try:

        await message.delete()

    except discord.NotFound:

        pass


# ============================================================
# TICKET HELPERS
# ============================================================

def is_ticket_channel(channel):

    if not isinstance(
        channel,
        discord.TextChannel
    ):

        return False

    # --------------------------------------------------------
    # PRIMARY CHECK:
    # TICKET CATEGORY
    # --------------------------------------------------------

    if TICKET_CATEGORY_ID:

        if channel.category_id == TICKET_CATEGORY_ID:

            return True

    # --------------------------------------------------------
    # FALLBACK:
    # TICKET CHANNEL NAME
    # --------------------------------------------------------

    name = channel.name.lower()

    return (
        name.startswith("ticket-")
        or name.startswith("ticket")
        or "ticket-" in name
    )


def get_ticket_data(channel):

    """
    Reads:

    owner=123456789;claimed=987654321

    claimed=0 means unclaimed.
    """

    owner_id = 0
    claimed_id = 0

    topic = channel.topic or ""

    # --------------------------------------------------------
    # OWNER
    # --------------------------------------------------------

    owner_match = re.search(
        r"(?:^|;)owner=(\d+)",
        topic
    )

    if owner_match:

        try:

            owner_id = int(
                owner_match.group(1)
            )

        except (
            ValueError,
            TypeError
        ):

            owner_id = 0

    # --------------------------------------------------------
    # CLAIMED
    # --------------------------------------------------------

    claimed_match = re.search(
        r"(?:^|;)claimed=(\d+)",
        topic
    )

    if claimed_match:

        try:

            claimed_id = int(
                claimed_match.group(1)
            )

        except (
            ValueError,
            TypeError
        ):

            claimed_id = 0

    return owner_id, claimed_id


async def save_ticket_data(
    channel,
    owner_id,
    claimed_id,
    reason=None
):

    topic = (
        f"owner={int(owner_id)};"
        f"claimed={int(claimed_id)}"
    )

    await channel.edit(
        topic=topic,
        reason=reason
    )


def get_middleman_role(guild):

    for role in guild.roles:

        if role.name.lower() == "middleman":

            return role

    return None


async def send_ticket_error(
    ctx,
    command_name,
    error
):

    print(
        "\n============================================================"
    )

    print(
        f"Ã¢ÂÂ ERROR IN ${command_name}"
    )

    print(
        f"Type: {type(error).__name__}"
    )

    print(
        f"Details: {error}"
    )

    print(
        "============================================================\n"
    )

    try:

        await ctx.send(
            f"Ã¢ÂÂ `${command_name}` failed:\n"
            f"`{type(error).__name__}: {error}`"
        )

    except Exception:

        pass


# ============================================================
# $CLAIM
# ============================================================

@bot.command(name="claim")
@commands.has_permissions(manage_channels=True)
async def claim(ctx):

    try:

        if not is_ticket_channel(
            ctx.channel
        ):

            return await ctx.send(
                "Ã¢ÂÂ This command can only be used in a ticket."
            )

        guild = ctx.guild

        if guild is None:

            return await ctx.send(
                "Ã¢ÂÂ This command can only be used inside a server."
            )

        # ----------------------------------------------------
        # BOT PERMISSION
        # ----------------------------------------------------

        bot_member = guild.me

        if bot_member is None:

            try:

                bot_member = await guild.fetch_member(
                    bot.user.id
                )

            except Exception:

                bot_member = None

        if bot_member is not None:

            if not bot_member.guild_permissions.manage_channels:

                return await ctx.send(
                    "Ã¢ÂÂ I need the **Manage Channels** permission."
                )

        # ----------------------------------------------------
        # GET TICKET DATA
        # ----------------------------------------------------

        owner_id, claimed_id = get_ticket_data(
            ctx.channel
        )

        # ----------------------------------------------------
        # ALREADY CLAIMED
        # ----------------------------------------------------

        if claimed_id != 0:

            claimed_member = guild.get_member(
                claimed_id
            )

            if claimed_member:

                return await ctx.send(
                    f"Ã¢ÂÂ This ticket is already claimed by "
                    f"{claimed_member.mention}."
                )

            return await ctx.send(
                "Ã¢ÂÂ This ticket is already claimed."
            )

        # ----------------------------------------------------
        # MIDDLEMAN ROLE
        # ----------------------------------------------------

        middleman_role = get_middleman_role(
            guild
        )

        # ----------------------------------------------------
        # SAVE CLAIM
        # ----------------------------------------------------

        await save_ticket_data(
            ctx.channel,
            owner_id,
            ctx.author.id,
            reason=f"Ticket claimed by {ctx.author}"
        )

        # ----------------------------------------------------
        # HIDE FROM MIDDLEMEN
        # ----------------------------------------------------

        if middleman_role:

            try:

                await ctx.channel.set_permissions(
                    middleman_role,
                    view_channel=False,
                    reason=f"Ticket claimed by {ctx.author}"
                )

            except discord.Forbidden:

                return await ctx.send(
                    "Ã¢ÂÂ I couldn't hide this ticket from "
                    "the Middleman role.\n"
                    "Check my **Manage Channels** permission."
                )

        # ----------------------------------------------------
        # GIVE CLAIMER ACCESS
        # ----------------------------------------------------

        try:

            await ctx.channel.set_permissions(
                ctx.author,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                reason=f"Ticket claimed by {ctx.author}"
            )

        except discord.Forbidden:

            return await ctx.send(
                "Ã¢ÂÂ I couldn't give you access to this ticket."
            )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="Ã°ÂÂÂ« Ticket Claimed",
            description=(
                f"Ã°ÂÂÂ This ticket has been claimed by "
                f"{ctx.author.mention}."
            ),
            color=discord.Color.from_rgb(
                255,
                20,
                180
            )
        )

        embed.add_field(
            name="Ã°ÂÂÂ® Claimed By",
            value=ctx.author.mention,
            inline=False
        )

        embed.add_field(
            name="Ã°ÂÂÂ Status",
            value="Claimed",
            inline=False
        )

        embed.set_footer(
            text="Use $unclaim to release this ticket."
        )

        await ctx.send(
            embed=embed
        )

    except (
        discord.Forbidden,
        discord.HTTPException
    ) as error:

        await send_ticket_error(
            ctx,
            "claim",
            error
        )

    except Exception as error:

        await send_ticket_error(
            ctx,
            "claim",
            error
        )


@claim.error
async def claim_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need the **Manage Channels** permission "
            "to use `$claim`."
        )

    await send_ticket_error(
        ctx,
        "claim",
        error
    )


# ============================================================
# $UNCLAIM
# ============================================================

@bot.command(name="unclaim")
@commands.has_permissions(manage_channels=True)
async def unclaim(ctx):

    try:

        if not is_ticket_channel(
            ctx.channel
        ):

            return await ctx.send(
                "Ã¢ÂÂ This command can only be used in a ticket."
            )

        guild = ctx.guild

        if guild is None:

            return await ctx.send(
                "Ã¢ÂÂ This command can only be used inside a server."
            )

        # ----------------------------------------------------
        # GET DATA
        # ----------------------------------------------------

        owner_id, claimed_id = get_ticket_data(
            ctx.channel
        )

        if claimed_id == 0:

            return await ctx.send(
                "Ã¢ÂÂ This ticket is not claimed."
            )

        # ----------------------------------------------------
        # MIDDLEMAN ROLE
        # ----------------------------------------------------

        middleman_role = get_middleman_role(
            guild
        )

        # ----------------------------------------------------
        # CLEAR CLAIM
        # ----------------------------------------------------

        await save_ticket_data(
            ctx.channel,
            owner_id,
            0,
            reason=f"Ticket unclaimed by {ctx.author}"
        )

        # ----------------------------------------------------
        # RESTORE MIDDLEMAN ACCESS
        # ----------------------------------------------------

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

                return await ctx.send(
                    "Ã¢ÂÂ I couldn't restore access for the "
                    "Middleman role."
                )

        # ----------------------------------------------------
        # REMOVE OLD CLAIMER
        # ----------------------------------------------------

        claimed_member = guild.get_member(
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

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="Ã°ÂÂÂ Ticket Unclaimed",
            description=(
                f"{ctx.author.mention} has unclaimed "
                "this ticket."
            ),
            color=discord.Color.from_rgb(
                255,
                20,
                180
            )
        )

        embed.add_field(
            name="Ã°ÂÂÂ Status",
            value="Available to Middlemen",
            inline=False
        )

        embed.set_footer(
            text="Use $claim to claim this ticket."
        )

        await ctx.send(
            embed=embed
        )

    except (
        discord.Forbidden,
        discord.HTTPException
    ) as error:

        await send_ticket_error(
            ctx,
            "unclaim",
            error
        )

    except Exception as error:

        await send_ticket_error(
            ctx,
            "unclaim",
            error
        )


@unclaim.error
async def unclaim_error(ctx, error):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need the **Manage Channels** permission "
            "to use `$unclaim`."
        )

    await send_ticket_error(
        ctx,
        "unclaim",
        error
    )


# ============================================================
# $TRANSFERTICKET @USER OR USER ID
# ============================================================

@bot.command(name="transferticket")
@commands.has_permissions(manage_channels=True)
async def transferticket(
    ctx,
    user_input: str
):

    try:

        if not is_ticket_channel(
            ctx.channel
        ):

            return await ctx.send(
                "Ã¢ÂÂ This command can only be used in a ticket."
            )

        guild = ctx.guild

        if guild is None:

            return await ctx.send(
                "Ã¢ÂÂ This command can only be used inside a server."
            )

        # ----------------------------------------------------
        # FIND USER
        # ----------------------------------------------------

        member = await get_member_from_input(
            ctx,
            user_input
        )

        if member is None:

            return await ctx.send(
                "Ã¢ÂÂ I couldn't find that member.\n\n"
                "Use:\n"
                "`$transferticket @user`\n"
                "or\n"
                "`$transferticket userID`"
            )

        if member.bot:

            return await ctx.send(
                "Ã¢ÂÂ You cannot transfer a ticket to a bot."
            )

        # ----------------------------------------------------
        # CURRENT DATA
        # ----------------------------------------------------

        owner_id, claimed_id = get_ticket_data(
            ctx.channel
        )

        # ----------------------------------------------------
        # REMOVE OLD CLAIMER
        # ----------------------------------------------------

        if (
            claimed_id != 0
            and claimed_id != member.id
        ):

            old_claimer = guild.get_member(
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

        # ----------------------------------------------------
        # MIDDLEMAN ROLE
        # ----------------------------------------------------

        middleman_role = get_middleman_role(
            guild
        )

        if middleman_role:

            try:

                await ctx.channel.set_permissions(
                    middleman_role,
                    view_channel=False,
                    reason="Ticket transferred"
                )

            except discord.Forbidden:

                return await ctx.send(
                    "Ã¢ÂÂ I couldn't update the Middleman "
                    "permissions."
                )

        # ----------------------------------------------------
        # GIVE NEW USER ACCESS
        # ----------------------------------------------------

        try:

            await ctx.channel.set_permissions(
                member,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                reason=f"Ticket transferred to {member}"
            )

        except discord.Forbidden:

            return await ctx.send(
                "Ã¢ÂÂ I couldn't give the new user access "
                "to this ticket."
            )

        # ----------------------------------------------------
        # SAVE NEW CLAIM
        # ----------------------------------------------------

        await save_ticket_data(
            ctx.channel,
            owner_id,
            member.id,
            reason=(
                f"Ticket transferred from "
                f"{ctx.author} to {member}"
            )
        )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="Ã°ÂÂÂ Ticket Transferred",
            description=(
                f"Ã°ÂÂÂ« This ticket has been transferred to "
                f"{member.mention}."
            ),
            color=discord.Color.from_rgb(
                255,
                20,
                180
            )
        )

        embed.add_field(
            name="Ã°ÂÂÂ¤ New Ticket Holder",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Ã°ÂÂÂ® Transferred By",
            value=ctx.author.mention,
            inline=False
        )

        embed.add_field(
            name="Ã°ÂÂÂ Status",
            value="Transferred / Claimed",
            inline=False
        )

        await ctx.send(
            embed=embed
        )

    except (
        discord.Forbidden,
        discord.HTTPException
    ) as error:

        await send_ticket_error(
            ctx,
            "transferticket",
            error
        )

    except Exception as error:

        await send_ticket_error(
            ctx,
            "transferticket",
            error
        )


@transferticket.error
async def transferticket_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Usage: `$transferticket @user` or "
            "`$transferticket userID`"
        )

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need the **Manage Channels** permission."
        )

    await send_ticket_error(
        ctx,
        "transferticket",
        error
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

    try:

        if not is_ticket_channel(
            ctx.channel
        ):

            return await ctx.send(
                "Ã¢ÂÂ This command can only be used in a ticket."
            )

        guild = ctx.guild

        if guild is None:

            return await ctx.send(
                "Ã¢ÂÂ This command can only be used inside a server."
            )

        # ----------------------------------------------------
        # FIND MEMBER
        # ----------------------------------------------------

        member = await get_member_from_input(
            ctx,
            user_input
        )

        if member is None:

            return await ctx.send(
                "Ã¢ÂÂ I couldn't find that member.\n\n"
                "Use:\n"
                "`$add @user`\n"
                "or\n"
                "`$add userID`"
            )

        if member.bot:

            return await ctx.send(
                "Ã¢ÂÂ You cannot add a bot to the ticket."
            )

        # ----------------------------------------------------
        # CHECK CURRENT ACCESS
        # ----------------------------------------------------

        permissions = ctx.channel.permissions_for(
            member
        )

        if permissions.view_channel:

            return await ctx.send(
                f"Ã¢ÂÂ {member.mention} already has access "
                f"to this ticket."
            )

        # ----------------------------------------------------
        # ADD USER
        # ----------------------------------------------------

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
                "Ã¢ÂÂ I need **Manage Channels** permission "
                "to add people to tickets."
            )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="Ã°ÂÂÂ¤ Member Added",
            description=(
                f"{member.mention} has been added to "
                "this ticket."
            ),
            color=discord.Color.from_rgb(
                255,
                20,
                180
            )
        )

        embed.add_field(
            name="Ã°ÂÂÂ¤ Added Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Ã°ÂÂÂ® Added By",
            value=ctx.author.mention,
            inline=False
        )

        await ctx.send(
            embed=embed
        )

    except (
        discord.Forbidden,
        discord.HTTPException
    ) as error:

        await send_ticket_error(
            ctx,
            "add",
            error
        )

    except Exception as error:

        await send_ticket_error(
            ctx,
            "add",
            error
        )


@add_user.error
async def add_user_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Usage: `$add @user` or `$add userID`"
        )

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need the **Manage Channels** permission."
        )

    await send_ticket_error(
        ctx,
        "add",
        error
    )


# ============================================================
# ============================================================
# TICKET TRANSCRIPT HELPER
# ============================================================

async def create_ticket_transcript(channel):
    """Build a plain-text transcript of the ticket."""

    lines = []

    lines.append("=" * 70)
    lines.append(f"TICKET TRANSCRIPT - #{channel.name}")
    lines.append(f"Server: {channel.guild.name}")
    lines.append(f"Channel ID: {channel.id}")
    lines.append(f"Generated: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("=" * 70)
    lines.append("")

    async for message in channel.history(limit=None, oldest_first=True):
        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        lines.append(f"[{timestamp}] {message.author} ({message.author.id})")

        if message.content:
            lines.append(message.content)
        else:
            lines.append("[No message content]")

        for attachment in message.attachments:
            lines.append(f"Attachment: {attachment.filename} - {attachment.url}")

        lines.append("-" * 70)

    if len(lines) == 6:
        lines.append("[No messages found]")

    return "\n".join(lines).encode("utf-8")


# ============================================================
# $CLOSE
# ============================================================

@bot.command(name="close")
@commands.has_permissions(manage_channels=True)
async def close_ticket(ctx):

    try:

        # ----------------------------------------------------
        # TICKET CHECK
        # ----------------------------------------------------

        if not is_ticket_channel(ctx.channel):
            return await ctx.send(
                "Ã¢ÂÂ This command can only be used in a ticket."
            )

        # ----------------------------------------------------
        # TRANSCRIPT CHANNEL CHECK
        # ----------------------------------------------------

        if not TRANSCRIPT_CHANNEL_ID:
            return await ctx.send(
                "Ã¢ÂÂ `TRANSCRIPT_CHANNEL_ID` is not configured. "
                "Set it to the channel ID where transcripts should "
                "be sent before using `$close`."
            )

        transcript_channel = ctx.guild.get_channel(
            TRANSCRIPT_CHANNEL_ID
        )

        if not isinstance(
            transcript_channel,
            discord.TextChannel
        ):
            return await ctx.send(
                "Ã¢ÂÂ The configured transcript channel was not found "
                "in this server."
            )

        # ----------------------------------------------------
        # CHECK BOT PERMISSIONS BEFORE CLOSING
        # ----------------------------------------------------

        permissions = transcript_channel.permissions_for(
            ctx.guild.me
        )

        if not permissions.view_channel:
            return await ctx.send(
                "Ã¢ÂÂ I cannot view the transcript channel."
            )

        if not permissions.send_messages:
            return await ctx.send(
                "Ã¢ÂÂ I cannot send messages in the transcript channel."
            )

        if not permissions.attach_files:
            return await ctx.send(
                "Ã¢ÂÂ I cannot upload transcript files in the "
                "transcript channel."
            )

        # ----------------------------------------------------
        # CREATE TRANSCRIPT BEFORE DELETING THE TICKET
        # ----------------------------------------------------

        try:
            transcript_bytes = await create_ticket_transcript(
                ctx.channel
            )

        except discord.Forbidden:
            return await ctx.send(
                "Ã¢ÂÂ I don't have permission to read the ticket "
                "history, so the transcript could not be created."
            )

        except discord.HTTPException as error:
            return await ctx.send(
                f"Ã¢ÂÂ Discord failed while reading the ticket: "
                f"`{error}`\nThe ticket was **not deleted**."
            )

        # ----------------------------------------------------
        # SEND TRANSCRIPT
        # ----------------------------------------------------

        channel_name = ctx.channel.name

        transcript_file = discord.File(
            io.BytesIO(transcript_bytes),
            filename=f"{channel_name}-transcript.txt"
        )

        transcript_embed = discord.Embed(
            title="Ã°ÂÂÂ Ticket Transcript",
            description=(
                f"Transcript for **#{channel_name}**\n"
                f"Closed by {ctx.author.mention}"
            ),
            color=discord.Color.from_rgb(
                255,
                20,
                180
            ),
            timestamp=datetime.datetime.now(
                datetime.timezone.utc
            )
        )

        transcript_embed.add_field(
            name="Ã°ÂÂÂ« Ticket",
            value=f"`{channel_name}`",
            inline=True
        )

        transcript_embed.add_field(
            name="Ã°ÂÂÂ® Closed By",
            value=ctx.author.mention,
            inline=True
        )

        transcript_embed.add_field(
            name="Ã°ÂÂÂ Ticket Channel ID",
            value=f"`{ctx.channel.id}`",
            inline=False
        )

        try:
            await transcript_channel.send(
                embed=transcript_embed,
                file=transcript_file
            )

        except discord.Forbidden:
            return await ctx.send(
                "Ã¢ÂÂ I could not send the transcript. "
                "The ticket was **not deleted**."
            )

        except discord.HTTPException as error:
            return await ctx.send(
                f"Ã¢ÂÂ Failed to upload the transcript: `{error}`\n"
                "The ticket was **not deleted**."
            )

        # ----------------------------------------------------
        # CONFIRM TRANSCRIPT WAS SENT, THEN CLOSE
        # ----------------------------------------------------

        closing_embed = discord.Embed(
            title="Ã°ÂÂÂ Ticket Closing",
            description=(
                f"This ticket is being closed by "
                f"{ctx.author.mention}.\n\n"
                "Ã¢ÂÂ Transcript saved successfully.\n"
                "The channel will be deleted in **5 seconds**."
            ),
            color=discord.Color.from_rgb(
                255,
                20,
                180
            )
        )

        closing_embed.add_field(
            name="Ã°ÂÂÂ« Ticket",
            value=f"`{channel_name}`",
            inline=False
        )

        closing_embed.add_field(
            name="Ã°ÂÂÂ® Closed By",
            value=ctx.author.mention,
            inline=False
        )

        await ctx.send(
            embed=closing_embed
        )

        await asyncio.sleep(5)

        # ----------------------------------------------------
        # DELETE TICKET
        # ----------------------------------------------------

        try:
            await ctx.channel.delete(
                reason=f"Ticket closed by {ctx.author}"
            )

        except discord.NotFound:
            pass

        except discord.Forbidden:
            # Transcript already exists, so tell the user if
            # deletion itself is the only thing that failed.
            try:
                await ctx.send(
                    "Ã¢ÂÂ The transcript was saved, but I don't have "
                    "permission to delete this ticket channel."
                )
            except Exception:
                pass

    except (
        discord.Forbidden,
        discord.HTTPException
    ) as error:

        await send_ticket_error(
            ctx,
            "close",
            error
        )

    except Exception as error:

        await send_ticket_error(
            ctx,
            "close",
            error
        )


@close_ticket.error
async def close_ticket_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need the **Manage Channels** permission "
            "to use `$close`."
        )

    await send_ticket_error(
        ctx,
        "close",
        error
    )


# ============================================================
# $TRANSFERROLES @USER
# ============================================================

@bot.command(name="transferroles")
@commands.has_permissions(manage_roles=True)
async def transferroles(
    ctx,
    target
):

    member = await get_member(
        ctx,
        target
    )

    if member is None:

        return await ctx.send(
            "Ã¢ÂÂ Please mention a valid server member "
            "or use their ID."
        )

    source = ctx.author

    roles_to_transfer = [
        role
        for role in source.roles
        if role != ctx.guild.default_role
        and not role.managed
        and role < ctx.guild.me.top_role
        and role < ctx.author.top_role
    ]

    if not roles_to_transfer:

        return await ctx.send(
            "Ã¢ÂÂ You have no transferable roles."
        )

    added = []

    for role in roles_to_transfer:

        if role >= ctx.guild.me.top_role:

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
        f"Ã°ÂÂÂ Transferred **{len(added)}** role(s) "
        f"to {member.mention}."
    )


# ============================================================
# $BACKUP
# ============================================================

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

    for category in guild.categories:

        backup["categories"].append({
            "name": category.name,
            "position": category.position
        })

    for channel in guild.channels:

        if isinstance(
            channel,
            discord.CategoryChannel
        ):

            continue

        data = {
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position,
            "category": (
                channel.category.name
                if channel.category
                else None
            )
        }

        if isinstance(
            channel,
            discord.TextChannel
        ):

            data["topic"] = channel.topic
            data["slowmode_delay"] = channel.slowmode_delay
            data["nsfw"] = channel.nsfw

        elif isinstance(
            channel,
            discord.VoiceChannel
        ):

            data["bitrate"] = channel.bitrate
            data["user_limit"] = channel.user_limit

        backup["channels"].append(
            data
        )

    with open(
        BACKUP_FILE,
        "w"
    ) as f:

        json.dump(
            backup,
            f,
            indent=4
        )

    await ctx.send(
        "Ã¢ÂÂ Server backup created.\n"
        f"Ã°ÂÂÂ `{BACKUP_FILE}`"
    )


# ============================================================
# $RESTORE
# ============================================================

@bot.command(name="restore")
@commands.has_permissions(administrator=True)
async def restore_command(ctx):

    if not os.path.exists(
        BACKUP_FILE
    ):

        return await ctx.send(
            "Ã¢ÂÂ No server backup was found."
        )

    try:

        with open(
            BACKUP_FILE,
            "r"
        ) as f:

            backup = json.load(f)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return await ctx.send(
            "Ã¢ÂÂ The backup file is invalid."
        )

    await ctx.send(
        "Ã¢ÂÂ Ã¯Â¸Â **Server restore started.**\n"
        "This will recreate missing roles and channels "
        "from the saved backup."
    )

    existing_roles = {
        role.name: role
        for role in ctx.guild.roles
    }

    created_roles = 0

    for role_data in backup.get(
        "roles",
        []
    ):

        if role_data["name"] in existing_roles:

            continue

        try:

            role = await ctx.guild.create_role(
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

            existing_roles[
                role.name
            ] = role

            created_roles += 1

        except discord.Forbidden:

            pass

    existing_categories = {
        category.name: category
        for category in ctx.guild.categories
    }

    created_categories = 0

    for category_data in backup.get(
        "categories",
        []
    ):

        if category_data["name"] in existing_categories:

            continue

        try:

            category = await ctx.guild.create_category(
                category_data["name"],
                reason="Server backup restore"
            )

            existing_categories[
                category.name
            ] = category

            created_categories += 1

        except discord.Forbidden:

            pass

    existing_channels = {
        channel.name
        for channel in ctx.guild.channels
    }

    created_channels = 0

    for channel_data in backup.get(
        "channels",
        []
    ):

        name = channel_data["name"]

        if name in existing_channels:

            continue

        category = None

        category_name = channel_data.get(
            "category"
        )

        if category_name:

            category = existing_categories.get(
                category_name
            )

        try:

            if channel_data["type"] == "text":

                await ctx.guild.create_text_channel(
                    name,
                    category=category,
                    topic=channel_data.get(
                        "topic"
                    ),
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

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            pass

    await ctx.send(
        "Ã¢ÂÂ **Server restore finished.**\n\n"
        f"Ã°ÂÂÂ­ Roles created: **{created_roles}**\n"
        f"Ã°ÂÂÂ Categories created: **{created_categories}**\n"
        f"Ã°ÂÂÂ¬ Channels created: **{created_channels}**"
    )


# ============================================================
# $DM @USER MESSAGE
# ============================================================

@bot.command(name="dm")
@commands.has_permissions(manage_messages=True)
async def dm_command(
    ctx,
    member: discord.Member,
    *,
    message: str
):

    if member.bot:

        return await ctx.send(
            "Ã¢ÂÂ You cannot DM a bot."
        )

    if not message.strip():

        return await ctx.send(
            "Ã¢ÂÂ Usage: `$dm @user message`"
        )

    embed = discord.Embed(
        title="Ã°ÂÂÂ© Message from the Server",
        description=message,
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.set_footer(
        text=f"Sent from {ctx.guild.name}"
    )

    try:

        await member.send(
            embed=embed
        )

    except discord.Forbidden:

        return await ctx.send(
            f"Ã¢ÂÂ I couldn't DM {member.mention}. "
            "Their DMs may be closed."
        )

    except discord.HTTPException:

        return await ctx.send(
            "Ã¢ÂÂ Discord returned an error while sending "
            "the DM."
        )

    await ctx.send(
        f"Ã¢ÂÂ DM sent to {member.mention}."
    )


@dm_command.error
async def dm_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need the **Manage Messages** permission."
        )

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Usage: `$dm @user message`"
        )

    if isinstance(
        error,
        commands.BadArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Please mention a valid member."
        )


# ============================================================
# $MASSDM @ROLE MESSAGE
# ============================================================

@bot.command(name="massdm")
@commands.has_permissions(administrator=True)
async def massdm_command(
    ctx,
    role: discord.Role,
    *,
    message: str
):

    if role == ctx.guild.default_role:

        return await ctx.send(
            "Ã¢ÂÂ You cannot mass DM the @everyone role."
        )

    if role.managed:

        return await ctx.send(
            "Ã¢ÂÂ You cannot use a managed/integration role."
        )

    if not message.strip():

        return await ctx.send(
            "Ã¢ÂÂ Usage: `$massdm @role message`"
        )

    members = [
        member
        for member in ctx.guild.members
        if role in member.roles
        and not member.bot
    ]

    if not members:

        return await ctx.send(
            f"Ã¢ÂÂ No members with {role.mention} were found."
        )

    await ctx.send(
        f"Ã°ÂÂÂ¨ **Mass DM started.**\n"
        f"Ã°ÂÂÂ­ Role: {role.mention}\n"
        f"Ã°ÂÂÂ¥ Members with role: **{len(members)}**"
    )

    success = 0
    failed = 0

    for member in members:

        embed = discord.Embed(
            title="Ã°ÂÂÂ© Message from the Server",
            description=message,
            color=discord.Color.from_rgb(
                255,
                20,
                180
            )
        )

        embed.set_footer(
            text=f"Sent from {ctx.guild.name}"
        )

        try:

            await member.send(
                embed=embed
            )

            success += 1

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            failed += 1

        await asyncio.sleep(1)

    embed = discord.Embed(
        title="Ã°ÂÂÂ¨ Mass DM Finished",
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ­ Role",
        value=role.mention,
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ¥ Members Found",
        value=f"**{len(members)}**",
        inline=True
    )

    embed.add_field(
        name="Ã¢ÂÂ DMs Sent",
        value=f"**{success}**",
        inline=True
    )

    embed.add_field(
        name="Ã¢ÂÂ DMs Failed",
        value=f"**{failed}**",
        inline=True
    )

    embed.set_footer(
        text=f"Mass DM by {ctx.author.display_name}"
    )

    await ctx.send(
        embed=embed
    )


@massdm_command.error
async def massdm_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You need the **Administrator** permission."
        )

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Usage: `$massdm @role message`"
        )

    if isinstance(
        error,
        commands.BadArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Please mention a valid role."
        )


# ============================================================
# $HELP
# ============================================================

bot.remove_command("help")


@bot.command(name="help")
async def help_command(ctx):

    embed = discord.Embed(
        title="Ã°ÂÂÂ Bot Commands",
        description=(
            "Here are all available commands.\n"
            "Commands requiring permissions can only be used "
            "by members with the required permissions."
        ),
        color=discord.Color.from_rgb(
            255,
            20,
            180
        )
    )

    embed.add_field(
        name="Ã°ÂÂÂ Application Commands",
        value=(
            "`$trigger @user` Ã¢ÂÂ Send a flopping application"
        ),
        inline=False
    )

    embed.add_field(
        name="Ã¢Â­Â Vouch Commands",
        value=(
            "`$addvouch @user (number)` Ã¢ÂÂ Add vouches\n"
            "`$removevouch @user (number)` Ã¢ÂÂ Remove vouches\n"
            "`$vouches @user` Ã¢ÂÂ Check vouches"
        ),
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ­ Role Commands",
        value=(
            "`$role @user @role` Ã¢ÂÂ Give a role\n"
            "`$promo @user` Ã¢ÂÂ Promote a user\n"
            "`$demo @user` Ã¢ÂÂ Demote a user\n"
            "`$fill` Ã¢ÂÂ Fill missing roles\n"
            "`$roles` Ã¢ÂÂ Show server roles"
        ),
        inline=False
    )

    embed.add_field(
        name="Ã¢ÂÂ¸Ã¯Â¸Â Temporary Role Commands",
        value=(
            "`$temp` Ã¢ÂÂ Temporarily remove roles\n"
            "`$canceltemp` Ã¢ÂÂ Restore saved roles"
        ),
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ¤ User / Server Commands",
        value=(
            "`$w @user` Ã¢ÂÂ View user profile\n"
            "`$serverinfo` Ã¢ÂÂ View server information"
        ),
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ¡Ã¯Â¸Â Moderation Commands",
        value=(
            "`$to @user (time)` Ã¢ÂÂ Timeout a member\n"
            "`$unto @user` Ã¢ÂÂ Remove timeout\n"
            "`$ban @user / ID` Ã¢ÂÂ Ban a member\n"
            "`$unban (user ID)` Ã¢ÂÂ Unban a member\n"
            "`$kick @user / ID` Ã¢ÂÂ Kick a member\n"
            "`$purge (number)` Ã¢ÂÂ Delete messages"
        ),
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ« Ticket Commands",
        value=(
            "`$claim` Ã¢ÂÂ Claim current ticket\n"
            "`$unclaim` Ã¢ÂÂ Unclaim current ticket\n"
            "`$transferticket @user / ID` Ã¢ÂÂ Transfer ticket\n"
            "`$add @user / ID` Ã¢ÂÂ Add member to ticket\n"
            "`$close` Ã¢ÂÂ Close and delete current ticket\n"
            "`$transferroles @user` Ã¢ÂÂ Transfer roles"
        ),
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ© DM Commands",
        value=(
            "`$dm @user message` Ã¢ÂÂ DM one member\n"
            "`$massdm @role message` Ã¢ÂÂ DM everyone with a role"
        ),
        inline=False
    )

    embed.add_field(
        name="Ã°ÂÂÂ¾ Server Backup",
        value=(
            "`$backup` Ã¢ÂÂ Create server backup\n"
            "`$restore` Ã¢ÂÂ Restore server backup"
        ),
        inline=False
    )

    if ctx.guild.icon:

        embed.set_thumbnail(
            url=ctx.guild.icon.url
        )

    embed.set_footer(
        text=f"Requested by {ctx.author.display_name}"
    )

    await ctx.send(
        embed=embed
    )


# ============================================================
# GLOBAL COMMAND ERROR HANDLER
# ============================================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.CommandNotFound
    ):

        return

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        return await ctx.send(
            "Ã¢ÂÂ You don't have permission to use this command."
        )

    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Missing required argument. "
            "Use `$help` to see usage."
        )

    if isinstance(
        error,
        commands.BadArgument
    ):

        return await ctx.send(
            "Ã¢ÂÂ Invalid argument. "
            "Use `$help` to see the correct format."
        )

    if isinstance(
        error,
        commands.CommandInvokeError
    ):

        original = error.original

        print(
            "\n============================================================"
        )

        print(
            f"Ã¢ÂÂ Error in command `{ctx.command}`"
        )

        print(
            f"Type: {type(original).__name__}"
        )

        print(
            f"Details: {original}"
        )

        print(
            "============================================================\n"
        )

        return await ctx.send(
            f"Ã¢ÂÂ An error occurred while running "
            f"`{ctx.command}`:\n"
            f"`{type(original).__name__}: {original}`"
        )

    print(
        f"Ã¢ÂÂ Unhandled command error: "
        f"{type(error).__name__}: {error}"
    )


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    print(
        f"Ã¢ÂÂ Logged in as {bot.user}"
    )

    print(
        f"Ã¢ÂÂ Bot is running in "
        f"{len(bot.guilds)} server(s)"
    )

    print(
        "Ã¢ÂÂ $trigger application system loaded"
    )

    print(
        "Ã¢ÂÂ Accept / Decline buttons loaded"
    )

    print(
        "Ã¢ÂÂ Application role system loaded"
    )

    print(
        "Ã¢ÂÂ New Flopper system loaded"
    )

    print(
        "Ã¢ÂÂ Ticket commands loaded"
    )

    print(
        "Ã¢ÂÂ $claim loaded"
    )

    print(
        "Ã¢ÂÂ $unclaim loaded"
    )

    print(
        "Ã¢ÂÂ $transferticket loaded"
    )

    print(
        "Ã¢ÂÂ $add loaded"
    )

    print(
        "Ã¢ÂÂ $close loaded"
    )


# ============================================================
# RUN BOT
# ============================================================

bot.run(TOKEN)
