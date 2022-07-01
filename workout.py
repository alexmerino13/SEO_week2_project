import requests
import os
import pandas as pd
import sqlalchemy as db
from sqlalchemy import create_engine 

WGER_API_key = os.environ.get('WORKOUT_API_KEY')

BASE_URL = 'https://wger.de/api/v2/'

headers = {'Authorization': f'Token {WGER_API_key}', 'Content-Type': 'application/json'}

#language 2 restricts it to english
#mass req for random exercises, returns descriptions
#returns an array of descriptions
def mass_req():
    r = requests.get(BASE_URL + 'exercise/?language=2', headers=headers).json()
    results = r['results']

    descriptions = []

    for workout in results:
        descriptions.append(workout['description'])

    return descriptions

#creates a dictionary with the target area as the key, and id as the value
#because I think we might be able to use the IDs? but not sure yet
#returns a dictionary of the name:id pairs
def get_categories():
    r = requests.get(BASE_URL + 'exercisecategory?language=2', headers=headers).json()['results']

    categories = {}

    for item in r:
        categories[item['name'].lower()] = item['id']
    return categories


print(get_categories())