from flask import Blueprint, render_template, request
import torch
import random
import json

chatbot_bp = Blueprint('chatbot', __name__, template_folder='templates')

from blueprints.chatbot.model import NeuralNet
from blueprints.chatbot.nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('blueprints/chatbot/intents.json', 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

FILE = "blueprints/chatbot/data.pth"
data = torch.load(FILE) 

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(model_state)
model.eval()

def get_response(sentence):
  sentence = tokenize(sentence)
  X = bag_of_words(sentence, all_words)
  X = X.reshape(1, X.shape[0])
  X = torch.from_numpy(X)

  output = model(X)
  _, predicted = torch.max(output, dim=1)

  tag = tags[predicted.item()]

  for intent in intents['intents']:
    if tag == intent['tag']:
      return random.choice(intent['responses'])

@chatbot_bp.route('/')
def chatbot():
  return render_template("chatbot.html")

@chatbot_bp.route('/get')
def get_bot_response():
  user_input = request.args.get('msg')
  response = get_response(user_input)
  return str(response)