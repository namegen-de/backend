# _utils.py
#  helper functions and classes
# by: mika senghaas

import os
import json
import torch
import pickle
import numpy as np
from torch.nn import Softmax

# custom imports
from .model import Model

softmax = Softmax(dim=1)
CURR = os.path.dirname(os.path.abspath(__file__))

def load_model():
  # load meta
  with open(f"{CURR}/meta.pkl", "rb") as f:
    meta = pickle.loads(f.read())

  # extract model init params
  params = meta['params']

  # init model
  model = Model(
      params['num_countries'],
      params['num_chars'],
      params['conversions'],
      params['embedding_size'],
      params['hidden_size'])

  # load weights
  model.load_state_dict(torch.load(f"{CURR}/model.pt"))

  return model, meta

def sample(model, countries, gender, start_with, max_len):
  # output string
  res = start_with

  # model in evaluation mode, not saving gradients
  with torch.no_grad():
    # initialise input and hidden tensors
    input_tensor = _get_input_tensor(start_with, model.conversions['ch2i'])
    country_tensor = _get_country_tensor(countries, model.conversions['a2i'])
    gender_tensor = _get_gender_tensor(gender)

    # initialise hidden tensor from gender
    hidden = model.init_hidden(gender_tensor)

    if input_tensor.size(0)>1:
      for i in range(input_tensor.size(0)-1):
        _, hidden = model(country_tensor, input_tensor[i], hidden)
      input_tensor = input_tensor[-1]

    for _ in range(max_len-len(start_with)):
      output, hidden = model(country_tensor, input_tensor, hidden)

      # get top 5 most likely next letters
      topv, topi = output.topk(5)
      topv = torch.exp(topv)
      topv = np.array(topv.flatten()).astype('float64')
      topv = topv / topv.sum()
      topi = np.random.choice(topi.flatten(), p=topv)
      letter = model.conversions['i2ch'][topi.item()]

      if letter == "</S>":
        break
      else:
        res += letter
        input_tensor = _get_input_tensor(letter, model.conversions['ch2i'], start_token=False)

    return res

def _get_country_tensor(countries, country2idx):
  return torch.tensor([country2idx[c] for c in countries], dtype=torch.long)

def _get_gender_tensor(gender):
  return torch.tensor([0 if gender=="M" else 1], dtype=torch.long)

def _get_input_tensor(line, char2idx, start_token=True):
  # integer encode char seq
  indices = [char2idx[char] for char in line]
  if start_token: indices.insert(0, 0)

  return torch.tensor(indices, dtype=torch.long)

def _get_target_tensor(line, char2idx, end_token=True):
  # integer encode target tensor
  indices = [char2idx[char] for char in line]
  if end_token: indices.append(1)

  return torch.tensor(indices, dtype=torch.long)


if __name__ == "__main__":
  main()
