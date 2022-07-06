import requests
import os
import pandas as pd
import sqlalchemy as db
from sqlalchemy import create_engine 

# This section contains relevant authentication information 
# And base url information for the WGER api
WGER_API_key = os.environ.get('WORKOUT_API_KEY')
BASE_URL = 'https://wger.de/api/v2/'
headers = {'Authorization': f'Token {WGER_API_key}', 'Content-Type': 'application/json'}

def getInput():
    # Flag for input 
    input_flag = False
    # Get input from the user
    print('How many days per week would you like to workout?')
    while input_flag is False:
        days_per_week = input("Enter 'a' for 3 days or 'b' for 4 days: ")
        if days_per_week == 'a' or days_per_week == 'b':
            input_flag = True
        else:
            print("Invalid input. Please try again.")
    input_flag = False

    print('How long would you like to workout?')
    while input_flag is False:
        workout_length = input("Enter 'a' for thirty minutes or 'b' for one hour: ")
        if workout_length == 'a' or workout_length == 'b':
            input_flag = True
        else:
            print("Invalid input. Please try again.")
    return (days_per_week, workout_length)

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

# receives: a muscle type (UPPER/LOWER/ALL)
# returns: a dictionary of categories in the workout type (name:id)
def get_categories(muscle_type):

    names = []
    categories = {}
    if muscle_type == 'UPPER':
        names = ["Arms","Back","Chest","Shoulders"]
    elif muscle_type == 'LOWER':
        names = ["Calves","Legs"]
    elif muscle_type == 'BNB':
        names = ["Arms", "Back"]
    elif muscle_type == 'CNT':
        names = ["Arms", "Chest"]

    if muscle_type == 'ALL':
        r = requests.get(BASE_URL + 'exercisecategory?language=2', headers=headers).json()['results']
        for item in r:
            categories[item['id']] = item['name'].lower()
    else:
        for group in names:
            r = requests.get(BASE_URL + 'exercisecategory?name=' + group, headers=headers).json()['results']
            for item in r:
                categories[item['id']] = item['name'].lower()
    return categories

# receives: a muscle group id
# returns: a dictionary of exercises in the muscle group (name:id)
def get_exercises(id):

    r = requests.get(BASE_URL +'exercise/?category=' + str(id) + '&language=2', headers=headers).json()['results']
    exercises = {}

    for item in r:
        exercises[item['id']] = item['name'].lower()
    return exercises

#recieves and validates user input: prints options to console, handles response
#by making sure it is lowercase and there is no whitespace. then it makes sure 
#the response can be found in the options. if not, loops through until a correct
#response is given
def get_category(ids):

    input_flag = False;
    
    print("What do you want to target? Below is a list of options")     
    for key in ids:
        print(str(key) + ': ' + ids[key])

    while input_flag == False: 
        print("Enter the id for the muscle group you would like to target: ", end="")
        response = int(input().strip())
        
        # validate user input
        if response in ids:
            input_flag = True
        else:
            print("Invalid input. Please try again.")

    print("")
    return response

# receives: a list of exercise options
# returns: the id chosen by the user for their exercise
# asks the user to choose an exercise id from a list
def choose_exercise(ids):
    input_flag = False;

    print("Which exercise would you like to add? Below is a list of options")
    
    for key in ids:
        print(str(key) + ': ' + ids[key])
    
    while input_flag == False:
        print("Enter the id for the exercise you would like to add: ", end="")
        response = int(input().strip())

        # validate user input
        if response in ids:
            input_flag = True
        else:
            print("Invalid input. Please try again.")
    print("")
    return response

# receives: a list of workout groups, valid values are U (upper
#           body), L (lower body), or A (accessory)
# returns: a list of ids for the chosen exercises
# for each workout type in the input list, asks the user to pick
# a muscle group from the UPPER/LOWER/ALL options, then asks the
# user to pick an exercise coorsponding to the category. Adds each
# exercise id to the list of choises, which it then returns
def get_choices(workouts):
    choices = []

    # get categories for different splits
    upper_categories = get_categories('UPPER')
    lower_categories = get_categories('LOWER')
    all_categories = get_categories('ALL')
    back_and_bis = get_categories('BNB')
    chest_and_tris = get_categories('CNT')

    for key in workouts:
        # get upper body exercise
        if key == 'U':
            # ask the user which category they want to target
            upper_cat = get_category(upper_categories)
            # get all excercises in the chosen category
            upper_exercises = get_exercises(upper_cat)
            # ask the user what exercise they want to add to workout
            upper_choice = choose_exercise(upper_exercises)
            # add the exercise to list of choices
            choices.append(upper_choice)
        # get lower body exercise
        elif key == 'L':
            lower_cat = get_category(lower_categories)
            lower_exercises = get_exercises(lower_cat)
            lower_choice = choose_exercise(lower_exercises)
            choices.append(lower_choice)
        # get accessory exercise
        elif key == 'A':
            accessory_cat = get_category(all_categories)
            accessory_exercises = get_exercises(accessory_cat)
            accessory_choice = choose_exercise(accessory_exercises)
            choices.append(accessory_choice)
        # get back and bicep exercises
        elif key == 'B':
            bnb_cat = get_category(back_and_bis)
            bnb_exercises = get_exercises(bnb_cat)
            bnb_choice = choose_exercise(bnb_exercises)
            choices.append(bnb_choice)
        elif key == 'C':
            cnt_cat = get_category(chest_and_tris)
            cnt_exercises = get_exercises(cnt_cat)
            cnt_choice = choose_exercise(cnt_exercises)
            choices.append(cnt_choice)
        else:
            print("Invalid workout: workout type not an option.")
    return choices

def main():
    #get user input
    input = getInput()
    days_per_week = input[0]
    workout_length = input[1]
    workout_days = {}
    # 3 day workout split
    if days_per_week == 'a':
        # 30 minute workouts
        if workout_length == 'a':
            # 1 upper, 1 lower, 1 accessory
            workouts = ['U', 'L','A']
            choices = get_choices(workouts)

            # add 3 identical workouts with exercise choices
            for index in range(1, 4):
                workout_days[index] = choices
            print(workout_days)

        # 1 hour workouts
        else:
            workouts = ['U','U','L','L','A']
            choices = get_choices(workouts)
            for index in range(1, 4):
                workout_days[index] = choices
            print(workout_days)

    option1 = [
        ['L', 'L', 'L'],
        ['B', 'B', 'B'],
        ['L', 'L', 'L'],
        ['C', 'C', 'C']
    ]
    option2 = [
        ['L', 'L', 'L', 'L', 'L', 'L'],
        ['B', 'B', 'B', 'B', 'B', 'B'],
        ['L', 'L', 'L', 'L', 'L', 'L'],
        ['C', 'C', 'C', 'C', 'C', 'C']
    ]

    # 4 day workout split
    if days_per_week == 'b':
        # 30 minute workouts
        if workout_length == 'a':
            # lower, back & bicep, lower, chest & tricep
            for index in range(0, len(option1)):
                    choices = get_choices(option1[index])
                    workout_days[index+1] = choices
            print(workout_days)
        
        # 1 hour workout
        else:
            for index in range(0, len(option2)):
                    choices = get_choices(option2[index])
                    workout_days[index+1] = choices
            print(workout_days)
            

main()
