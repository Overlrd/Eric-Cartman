# the os module helps us access environment variables
# i.e., our API keys
import os

#import keep_alive to keep running the bot
from keep_alive import keep_alive

# these modules are for querying the Hugging Face model
import json
import requests

# the Discord Python API
import discord

# this is my Hugging Face profile link
API_URL = 'https://api-inference.huggingface.co/models/Overlrd/'


class MyClient(discord.Client):

  def __init__(self, model_name):
    super().__init__(intents=discord.Intents.default())
    self.api_endpoint = API_URL + model_name
    # retrieve the secret API token from the system environment
    huggingface_token = os.environ['HUGGING_FACE_TOKEN']
    # format the header in our request to Hugging Face
    self.request_headers = {
      'Authorization': 'Bearer {}'.format(huggingface_token)
    }

  def query(self, payload):
    """
        make request to the Hugging Face model API
        """
    data = json.dumps(payload)
    response = requests.request('POST',
                                self.api_endpoint,
                                headers=self.request_headers,
                                data=data)
    ret = json.loads(response.content.decode('utf-8'))
    return ret

  async def on_ready(self):
    # print out information when the bot wakes up
    print('Logged in as')
    print(self.user.name)
    print(self.user.id)
    print('------')
    # send a request to the model without caring about the response
    # just so that the model wakes up and starts loading
    self.query({'inputs': {'text': 'Hello!'}})

  async def on_message(self, message):
    """
        this function is called whenever the bot sees a message in a channel
        """
    # ignore the message if it comes from the bot itself
    if message.author.id == self.user.id:
      return
    # ignore the message when bot not ping
    mentions_list = []
    # add user pinged to a list
    for i in message.mentions:
      mentions_list.append(i.name)
    # search for the bot
    is_in = int(mentions_list.count(self.user.name))
    # if not in , don't answer

    if is_in == 0:
      return

    # form query payload with the content of the message
    payload = {'inputs': {'text': message.content}}

    # while the bot is waiting on a response from the model
    # set the its status as typing for user-friendliness
    async with message.channel.typing():
      response = self.query(payload)
    bot_response = response.get('generated_text', None)

    # we may get ill-formed response if the model hasn't fully loaded
    # or has timed out
    loading_msg = 'Model Overlrd/DialoGPT-small-cartman is currently loading'
    wait_msg = 'wait I shit , Bitch!'
    if not bot_response:
      if 'error' in response:
        if response['error'] == loading_msg:

          bot_response = '`Error: {}`'.format(wait_msg)
      else:
        bot_response = 'Hmm... something is not right.'

    # send the model's response to the Discord channel
    await message.channel.send(bot_response)


def main():
  # DialoGPT-medium-joshua is my model name
  client = MyClient('DialoGPT-small-cartman')
  keep_alive()
  client.run(os.environ['DISCORD_TOKEN'])


if __name__ == '__main__':
  main()
