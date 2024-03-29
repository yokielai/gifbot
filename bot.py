import discord
import os
import requests
import db
import io

token = os.getenv("DISCORD_TOKEN")
client = discord.Client()


@client.event
async def on_ready():
    db.setup_database()
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith("-gif"):
        return

    parts = message.content.split(" ")
    command = parts[1]

    try:
        if command == "s" or command == "save":
            await save_command(message, parts)
        elif command == "l" or command == "list":
            await list_command(message, parts)
        elif command == "d" or command == "del" or command == "delete":
            await delete_command(message, parts)
        elif command == "u" or command == "update":
            await update_command(message, parts)
        else:
            image = db.read_image(parts[1], message.channel.guild.id)
            await message.channel.send(file=discord.File(
                io.BytesIO(image.tobytes()),
                filename=f"{parts[1]}.gif",
            ))
    except Exception as err:
        print(f"oops an error occurred: {err}")


async def save_command(message, parts):
    if not is_uploader(message):
        await message.channel.send("Sorry you can't do that because you aren't an uploader ╘[◉﹃◉]╕")
        return

    if len(message.attachments) > 0 and len(parts) == 3:
        if db.image_exists(parts[2], message.channel.guild.id):
            await message.channel.send("That gif already exists! Try using a different name ┐(‘～`；)┌")
            return

        print(f"saving image as key {parts[2]} ")
        url = message.attachments[0].url
        r = requests.get(url)
        db.insert_image(parts[2], r.content, message.channel.guild.id)
        await message.channel.send(f"Saved gif as {parts[2]} ✌.ʕʘ‿ʘʔ.✌")
        return
    else:
        print("invalid save command sent")
        await message.channel.send("That save command doesn't look quite right, try again ┐(‘～`；)┌")


async def list_command(message, parts):
    try:
        if len(parts) == 2:
            keys = db.list_keys(message.channel.guild.id)

            if keys is None or keys == []:
                await message.channel.send("No one has saved any GIFs yet! (◡﹏◡✿)")
                return

            batch = []
            batch_char_count = 0
            for key in keys:
                batch.append(key)
                batch_char_count += len(key)
                if batch_char_count > 1600:
                    await message.channel.send(", ".join(batch))
                    batch = []
                    batch_char_count = 0

            await message.channel.send(", ".join(batch))
        else:
            print("Cannot list all keys available")
            await message.channel.send("Failed to find gifs ┐(‘～`；)┌")

    except:
        print("Cannot list all keys available")
        await message.channel.send("Failed to find gifs ┐(‘～`；)┌")

async def delete_command(message, parts):
    if not is_uploader(message):
        await message.channel.send("Sorry you can't do that because you aren't an uploader ╘[◉﹃◉]╕")
        return

    if len(parts) == 3:
        if not db.image_exists(parts[2], message.channel.guild.id):
            await message.channel.send("Can't delete that gif, it doesn't exists ಥ_ಥ")
            return

        print(f"deleting image with key {parts[2]}")
        db.delete_image(parts[2], message.channel.guild.id)
        await message.channel.send(f"Deleted the gif {parts[2]} ＼(￣▽￣;)／")
    else:
        print(f"failed to delete {parts[2]}")
        await message.channel.send("Failed to delete the gif ┐(‘～`；)┌")


async def update_command(message, parts):
    if not is_uploader(message):
        await message.channel.send("Sorry you can't do that because you aren't an uploader ╘[◉﹃◉]╕")
        return

    if len(message.attachments) > 0 and len(parts) == 3:
        print(f"updating image for key {parts[2]}")
        url = message.attachments[0].url
        r = requests.get(url)
        db.update_image(parts[2], r.content, message.channel.guild.id)
        await message.channel.send(f"Updated the gif {parts[2]} (●´ω｀●)")
    else:
        print("invalid update command sent")
        await message.channel.send("Failed to update the gif ┐(‘～`；)┌")


def is_uploader(message):
    return "uploader" in [y.name.lower() for y in message.author.roles]


client.run(token)
