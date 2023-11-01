# hot takes, deep questions, babylon quotes, todo list
# metaprogramming yay!
import openai
import discord
import sys
from discord.ext import commands
import json

openai.api_key = ""
token = ""
client = commands.Bot(command_prefix="$", intents=discord.Intents.all())
server = "jerryjr"
last = ['', '', -1]

def babylon_headline_generator(keyword):
    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0613:personal::8F2gvlKW",
        messages=[{'role': "user", "content": keyword}],
        temperature=1,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

def babylon_generator(keyword):
    headline = babylon_headline_generator(keyword)
    try:
        response = openai.Image.create(
            prompt=headline,
            n=1,
            size="1024x1024"
        )
        return headline, response.data[0].url
    except:
        return headline

def search(_search):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{'role': "user", "content": _search}]
    )
    return response.choices[0].message.content

def hot_takes(keyword):
    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0613:personal::8EfZAgvd",
        messages=[{'role': "user", "content": keyword}],
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

def deep_questions(keyword):
    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0613:personal::8Eh8qcO4",
        messages=[{'role': "user", "content": keyword}],
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

def addto(item, rec=True, _end='\n'):
    sys.stdout = open('todo', 'a')
    print(item, end=_end)
    if rec:
        addto('', rec=False, _end='')
    sys.stdout = sys.__stdout__

@client.event
async def on_ready():
    for i in client.guilds:
        if i.name == server:
            break
    print(f'{client.user} is connected to the following server:\n'f'{i.name}(id: {i.id})')

@client.event
async def on_message(message):
    global last
    if message.content.startswith('$headline'):
        lines = babylon_generator(message.content[10:])
        if len(lines) == 2:
            await message.channel.send(lines[0])
            await message.channel.send(lines[1])
            last = [message.content[10:], lines[0], 0]
        else:
            await message.channel.send(lines)
            last = [message.content[10:], lines, 0]
    if message.content.startswith('$search'):
        lines = search(message.content[8:])
        await message.channel.send(lines)
    if message.content.startswith('$take'):
        lines = hot_takes(message.content[6:])
        await message.channel.send(lines)
        last = [message.content[6:], lines, 1]
    if message.content.startswith('$question'):
        lines = deep_questions(message.content[10:])
        await message.channel.send(lines)
        last = [message.content[10:], lines, 2]
    if message.content.startswith('$addto'):
        addto(message.content[7:])
        await message.channel.send("Added!")
    if message.content.startswith('$todo'):
        for i in open('todo', 'r'):
            await message.channel.send(i)
    if message.content.startswith('$last'):
        if last[2] == -1:
            await message.channel.send('No last accessible')
        elif last[2] == 0:
            sys.stdout = open('babylon.jsonl', 'a')
            print(json.dumps({"messages": [{"role": "user", "content": last[0]}, {"role": "assistant", "content": last[1]}]}))
            print('', end='')
            sys.stdout = sys.__stdout__
            await message.channel.send('Last Added')
        elif last[2] == 1:
            sys.stdout = open('hot_takes.jsonl', 'a')
            print(json.dumps({"messages": [{"role": "user", "content": last[0]}, {"role": "assistant", "content": last[1]}]}))
            print('', end='')
            sys.stdout = sys.__stdout__
            await message.channel.send('Last Added')
        elif last[2] == 2:
            sys.stdout = open('deep_questions.jsonl', 'a')
            print(json.dumps({"messages": [{"role": "user", "content": last[0]}, {"role": "assistant", "content": last[1]}]}))
            print('', end='')
            sys.stdout = sys.__stdout__
            await message.channel.send('Last Added')
        else:
            await message.channel.send('Last failed')
    if message.content.startswith('$retrain'):
        if message.content[9:] == 'headline':
            file = openai.File.create(
                file=open("babylon.jsonl", "rb"),
                purpose='fine-tune'
            )
            new_model = openai.FineTuningJob.create(training_file=file.id, model="ft:gpt-3.5-turbo-0613:personal::8EOTiP75")
            await message.channel.send(new_model.id)
        if message.content[9:] == 'take':
            file = openai.File.create(
                file=open("hot_takes.jsonl", "rb"),
                purpose='fine-tune'
            )
            new_model = openai.FineTuningJob.create(training_file=file.id, model='ft:gpt-3.5-turbo-0613:personal::8EfZAgvd')
            await message.channel.send(new_model.id)
        if message.content[9:] == 'question':
            file = openai.File.create(
                file=open("deep_questions.jsonl", "rb"),
                purpose='fine-tune'
            )
            new_model = openai.FineTuningJob.create(training_file=file.id, model='ft:gpt-3.5-turbo-0613:personal::8Eh8qcO4')
            await message.channel.send(new_model.id)
    if message.content.startswith('$help'):
        await message.channel.send('$headline \*keyword, $search query, $take \*keyword, $question *keyword, $addto item, $todo, $last, $retrain headline or take or question')

client.run(token)
