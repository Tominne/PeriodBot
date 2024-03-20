import discord
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from cycles import sql_query, get_startDate
from discord.ext import commands
from predict import predict_next_start_date

load_dotenv()
tokens = os.getenv('token')

intents = discord.Intents.default()
intents.message_content = True
token = tokens
client = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

PREFIX = "!"

def handle_user_messages(msg: discord.Message) ->str:
    message = msg.lower() #Converts all inputs to lower case
    if(message == 'hi'):
        return 'Hi there'
    if(message =='hello'):
        return ('Hello there')
    
async def processMessage(message: discord.Message):
    try:
        botfeedback = handle_user_messages(message)
        await message.channel.send(botfeedback)
    except Exception as error:
        print(error)

@client.event
async def on_ready():
    print("Bot is ready")
    print(client.guilds)

@client.event
async def on_message(message: discord.Message):
    user_id = message.author.id
    if message.author == client.user:
        return

    botfeedback = handle_user_messages(message.content)
    if botfeedback:
        await message.channel.send(botfeedback)

    if message.content.startswith('startP'):
        start_date = datetime.now()
        last_start_date = get_startDate(start_date, user_id)
        sql_query('INSERT INTO periods (user_id, start_date) VALUES (?, ?)', (user_id, start_date))
        await message.channel.send(f'{message.author}s period started.')
       
    if message.content.startswith('setP '):
        start_date = datetime.strptime(message.content[5:], '%d-%m-%y')
        sql_query('UPDATE periods SET start_date = ? WHERE user_id = ? ORDER BY start_date DESC LIMIT 1', (start_date, user_id))
        await message.channel.send(f'{message.author}s period start date set to {start_date}.')
    
    if message.content.startswith('checkP'):
      next_start_date, avg_duration = predict_next_start_date(user_id)
      last_start_date_str = get_startDate('SELECT MAX(start_date) FROM periods WHERE user_id = ?', user_id)
      if last_start_date_str is not None:
        last_start_date = datetime.strptime(last_start_date_str, '%Y-%m-%d %H:%M:%S.%f')
        days_since_last_period = (datetime.now() - last_start_date).days
        if avg_duration is None:  # If there's only one start date
            avg_duration = 5  # Assume a default period duration of 5 days
        if next_start_date is None:  # If there's no prediction for the next start date
            next_start_date = last_start_date + timedelta(days=28)  # Assume a default cycle length of 28 days
        if days_since_last_period <= avg_duration:
            await message.channel.send('{message.author}s Period is due.')
            days_until_end = avg_duration - days_since_last_period
            if days_until_end > 0:
                await message.channel.send(f'{message.author}s period should end in {days_until_end} days.')
            else:
                await message.channel.send('{message.author}s period should be over tomorrow')
        else:
            days_until_next_period = (next_start_date - datetime.now()).days
            await message.channel.send(f'{message.author}s next period is due in {days_until_next_period} days :)')
            if days_until_next_period <= 14:
                await message.channel.send('{message.author} is now ovulating.')
      else:
        await message.channel.send('No period start date found for this user.')

    

client.run(token)

