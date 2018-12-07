import discord
from discord.ext import commands
from PIL import Image
import requests
from io import BytesIO

bot_prefix = "q!"
Client = discord.Client()
client = commands.Bot(command_prefix=bot_prefix)


@client.async_event
async def on_ready():
    print("Logged on as {}".format(client.user))


@client.command(pass_context=True)
async def for_shed(ctx):
    await client.send_file(ctx.message.channel, "users/shed/lugia.png")


def check_hat(args):
    """
    Helper function that checks puthat arguments for specific flags
    Checks flipping the image horizontally and scaling by a factor
    Opens the hat file, manipulates it, and returns it
    :param args: Arguments to parse
    :return: Manipulated hat file
    """
    hat = Image.open("crimmis_hats/cryms.png")
    for arg in args:
        if arg == '-flip':
            hat = hat.transpose(Image.FLIP_LEFT_RIGHT)
        if arg.startswith('-scaled='):
            value = float(arg.split('=')[1])
            w, h = hat.size
            w_scaled, h_scaled = (int(w * value), int(h * value))
            hat = hat.resize((w_scaled, h_scaled))
    return hat


def check_dim(args, image_h, image_w, hat_w):
    """
    Helper function to shift the x/y coords of the hat, as well as setting default values
    :param args: Arguments to parse
    :param image_h: Height of the image
    :param image_w: Width of the image
    :param hat_w: Width of the hat
    :return: Tuple with manipulated coordinates
    """
    width = (image_w - hat_w) // 2
    height = int(image_h - (.9 * image_h))
    for arg in args:
        if arg.startswith('-w='):
            value = int(arg.split('=')[1])
            width = ((image_w - hat_w) // 2) + value
        if arg.startswith('-h='):
            height = int(arg.split('=')[1])

    return width, height


@client.command(pass_context=True)
async def puthat(ctx, *args):
    """
    Main command of the bot, creates a new avatar for a user with a Christmas hat on it.
    Grabs the user avatar and puts the hat in the top middle location with optional flags
    on x/y coords and image scaling
    :param ctx: Context of the message, i.e. sender/channel/attachments
    :param args: Optional flags to manipulate image
    """
    if '-i' or '-help' in args:
        string = "Usage q!puthat:\n" \
                 " -\t flip [flips hat horizontally]\n" \
                 " -\t scaled=NUMBER [resizes hat by a factor of NUMBER]\n" \
                 " -\t w=NUMBER [shifts hat horizontally by NUMBER px\n" \
                 " -\t h=NUMBER [shifts hat vertically by NUMBER px"
        await client.send_message(ctx.message.channel, content=string)
        return

    message = ctx.message
    url = message.author.avatar_url
    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})

    image = Image.open(BytesIO(response.content))
    hat = check_hat(args)
    image_w, image_h = image.size
    hat_w, hat_h = hat.size

    w_offset, h_offset = check_dim(args, image_h, image_w, hat_w)
    image.paste(hat, (w_offset, h_offset), mask=hat)
    image.save("crimmis_hats/remade.png")

    await client.send_file(message.channel, "crimmis_hats/remade.png", filename="newhat.png", content="Hat: ")


client.run('BOT_TOKEN')
