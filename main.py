
try:
    import discord
    from discord import member
    from discord.ext import commands
except:
    print("error")
import requests
import json
import platform
import random
import time
import os
# Image Generation Imports
try:
    import sdkit
    from sdkit.models import load_model
    from sdkit.generate import generate_images
except:
    print("error")
try: 
    import torch
except:
    print("error")     
from PIL import Image
import numpy as np
import torch



#Function to get path
def get_path():
    path = os.getcwd()
    return path

# Setup SDKIT
context = sdkit.Context()
context.device ='cpu'    # set the device to use (cpu or cuda) dont use cuda if you dont have an nvida gpu or dont have drivers installed

# set the path to the model file on the disk (.ckpt or .safetensors file)
context.model_paths['stable-diffusion'] = f'{get_path()}/model_storage/ema-512.ckpt'
load_model(context, 'stable-diffusion')



# Generate Image from prompt function
def generate_image(prompt):
    image_name = remove_spaces(prompt)
    image11 = generate_images(context, prompt=prompt, seed=random.randint(1,999999), width=512, height=512)
    
    os.system(f"touch /home/kalisu/discord_interface/images{image_name}.png")
    image11[0].save(f"/home/kalisu/discord_interface/images/{image_name}.png")


# Get system information
system_info = platform.system()
version_info = platform.version()
architecture_info = platform.architecture()
operating_node = platform.node()
operating_release = platform.release()
hostname = platform.uname()
processor = platform.processor()
machine = platform.machine()
pyversion = platform.python_version()

# Give the current node an ID:
node_id = 1

# Set nice threads
torch.set_num_threads(69)

# Info as f string literal
info = f"System: {system_info}\nVersion: {version_info}\nArchitecture: {architecture_info}\nOperating Node: {operating_node}\nOperating Release: {operating_release}\nHostname: {hostname}\nProcessor: {processor}\nMachine: {machine}\nPython Version: {pyversion}"

def ask_chat(prompt, extrainfo=""):
        extra_info = extrainfo
        # Define the Mixtral API endpoint on your localhost, if it is not running on localhost, change the URL, if it is running on a different port, change the port
        mixtral_api_url = 'http://localhost:11434/api/generate'

        # Define your headers and payload for the prompt
        headers = {'Content-Type': 'application/json'}
        payload = {'model': 'dolphin-mistral', 'prompt': prompt}

        # Make a request to the Mixtral API and save it as response
        response = requests.post(mixtral_api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses

        # Extract individual JSON objects from the response for each generated word chunk
        try:
            json_objects = [json.loads(obj) for obj in response.text.strip().split('\n')]
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON response: {e}. Response content: {response.text}")

        # Extract the 'response' field from each JSON object
        generated_words = ' '.join(obj.get('response', '') for obj in json_objects)

        # Concatenate the generated words into a single message
        result_message = f"{' '.join(generated_words.split())}"

        # Truncate at 1999 characters if necessary to ensure that the message is not blocked
        result_message = result_message[:1999]

        return result_message


#Random time for messages to be readable
def rantime():
    time_2_sleep = random.randint(200, 450)/100
    time.sleep(time_2_sleep)

# Remove spaces for filename
def remove_spaces(prompt):
    prompt = prompt.replace(" ", "_")
    return prompt

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)  # Set your desired command prefix

@bot.command(name='ask')
async def ask(ctx, *, prompt):
    # Extra information for the user
    extra_info = f"Node ID: {node_id}\nUser: {ctx.author.mention}\nServer: {ctx.guild.name}\nChannel: {ctx.channel.name}\n\nWhy have this? Well, if you go too crazy we might need evidence. :/"
    # Retrieve name of the user for logging purposes and evidence (if needed :eyes:)
    membername = ctx.author.name
    # Give Information about the node
    await ctx.send(f'Searching for machine to complete task: {prompt} from user: {ctx.author.mention}')  # Mention the user who sent the command
    rantime()
    await ctx.send(f'Connecting to node with ID: {node_id}')
    rantime()
    await ctx.send(f"Connecting to server . . .\nFound Server with Information:\n{info}")
    rantime()
    await ctx.send("Generating...")
    rantime()
    try:
        # Generate the text
        res_message = ask_chat(prompt)
        result_message = f"Response from Bot:\n\n{res_message}"

        # Send the result as a reply to the user
        await ctx.send(f"{result_message}")

    except requests.RequestException as e:
        error_message = f"Error making request to local API with error message: {e}"
        print(error_message)
        await ctx.send(error_message)

@bot.command(name='imagine')
async def imagine(ctx, *, prompt):
        # Give Information about the node
        await ctx.send(f'Searching for machine to complete task: {prompt} from user: {ctx.author.mention}')  # Mention the user who sent the command
        rantime()
        await ctx.send(f'Connecting to node with ID: {node_id}')
        rantime()
        await ctx.send(f"Connecting to server . . .\nFound Server with Information:\n{info}")
        rantime()
        await ctx.send("Generating...")
        rantime()

        # Make name
        image_name = remove_spaces(prompt)

        # improve the prompt
        improved = ask_chat(prompt, extrainfo="Please make the prompt better, adding more adjectives and trying to make the stable diffusion model make a better image that will more fit what the user is really wanting, please take the request and make it a little bit better and do not say anything eles, only responding with the imroved prompt, thank you. Remember, make sure that you are as if you are talking to the image bot, not extra talk, your output is going directly to the bot, make sure that you are only giving the new prompt. make it very descriptive, right a very discriptive paragraph from the inputted prompt.")
        
        await ctx.send(f"Improved Prompt:\n\n{improved}")
        
        generate_image(improved)

        time.sleep(2)

        await ctx.send(file=discord.File(f"/home/kalisu/discord_interface/images/{image_name}.png"))


        

@bot.command(name="image")
async def image(ctx, *, prompt): 
    # Give Information about the node
    await ctx.send(f'Searching for machine to complete task: {prompt} from user: {ctx.author.mention}')  # Mention the user who sent the command
    rantime()
    await ctx.send(f'Connecting to node with ID: {node_id}')
    rantime()
    await ctx.send(f"Connecting to server . . .\nFound Server with Information:\n{info}")
    rantime()
    await ctx.send("Generating...")
    rantime()
    # Generate the image
    generate_image(prompt)

    # Remove spaces from prompt for filename
    image_name = remove_spaces(prompt)

    # Send the image to the user on discord with the filename being the prompt
    await ctx.send(file=discord.File(f"/home/kalisu/discord_interface/images/{image_name}.png"))

# Connect to the shard api and start the bot
bot.run("MTE4NjcwOTE4NDUzNjkxNTk2OA.GAshzT.2XVxMM-gglwUYz-T1GqaTf4Ad4SDBvWwZHAlWY")
