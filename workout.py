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
        categories[item['name'].lower()] = str(item['id'])
    return categories

#gets a list of exercises by muscle group id and prints it to console
def get_exercises(id):
    r = requests.get(BASE_URL +'exercise/?muscles=' + id + '&language=2').json()
    print(r)

#recieves and validates user input: prints options to console, handles response
#by making sure it is lowercase and there is no whitespace. then it makes sure 
#the response can be found in the options. if not, loops through until a correct
#response is given
def get_input(ids):
    keys = list(ids.keys())
    print("What do you want to target? Below is a list of options")
    
    for key in keys:
        print(key, end=" ")
    print("")
    
    response = input().strip().lower()

    try:
        return response
    except:
        print("Invalid input: input not an option.")
        return get_input(ids)

def driver():
    ids = get_categories()
    input = get_input(ids)
    get_exercises(input)
driver()