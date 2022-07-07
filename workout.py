import requests
import os
import pandas as pd
import sqlalchemy as db
from datetime import date

# This section contains relevant authentication information 
# And base url information for the WGER api
WGER_API_key = os.environ.get('WORKOUT_API_KEY')
BASE_URL = 'https://wger.de/api/v2/'
headers = {'Authorization': f'Token {WGER_API_key}', 'Content-Type': 'application/json'}

# The follow section contains various static elements
# This is a section comment 
# This is a section comment
engine = db.create_engine('sqlite:///workouts.db')
user_table = {"username": [], "first_name": []}
workout_plan_table = {"username": [], "workout_id": [], "workout_name": [], "date_created": []}
session_table = {"username": [], "workout_id": [], "session_id": [], "session_dow": []}
exercises_table = {"username": [], "workout_id": [], "session_id": [], "exercise_id": [],
                    "exercise_name":[]}
panda_data_frame = pd.DataFrame.from_dict(user_table)
panda_data_frame.to_sql('workout_users', con=engine, if_exists='append', index=False)
panda_data_frame = pd.DataFrame.from_dict(workout_plan_table)
panda_data_frame.to_sql('workout_plan', con=engine, if_exists='append', index=False)
panda_data_frame = pd.DataFrame.from_dict(session_table)
panda_data_frame.to_sql('sessions', con=engine, if_exists='append', index=False)
panda_data_frame = pd.DataFrame.from_dict(exercises_table)
panda_data_frame.to_sql('exercises', con=engine, if_exists='append', index=False)

# dictionaries for session day of week
three_day = {1: 'Mon', 2: 'Wed', 3: 'Fri'}
four_day = {1: 'Mon', 2: 'Tues', 3: 'Thurs', 4: 'Fri'}

def getUsername():
    # Flag for input 
    input_flag = False
    # Get input from the user
    while input_flag is False:
        user_flag = False
        username = input("Enter your username to begin: ")
        query_user = "SELECT username FROM workout_users WHERE username='" + username + "';"
        query_result = engine.execute(query_user).fetchall()
        if len(query_result) == 0:
            found_name = ''
        else:
            found_name = query_result[0][0]

        if found_name == username:
            input_flag = True
        else:
            while user_flag is False:
                print("Username not found. Would you like to create a new user?")
                create_new = input("Enter 'Y' for Yes or 'N' to try again: ")
                if create_new.upper() == 'Y':
                    user_flag = True
                    input_flag = True
                    #create new user
                    first_name = input("Enter your first name: ")
                    user_dict = {"username": [username], "first_name": [first_name]}
                    panda_data_frame = pd.DataFrame.from_dict(user_dict)
                    panda_data_frame.to_sql('workout_users', con=engine, if_exists='append', index=False)
                elif create_new.upper() == 'N':
                    user_flag = True
                else:
                    print("Invalid input. Please try again.")

    return username

def displayMenu(username):
    query_user = "SELECT first_name FROM workout_users WHERE username = '" + username + "';"
    query_result = engine.execute(query_user).fetchall()[0][0]
    print(f"""Welcome, {query_result} please chooose from the following options:\n
    1 - Add new workout\n
    2 - Update workout\n""")
    choice_flag = False
    while choice_flag is False:
        choice = int(input("Enter your choice: "))
        if choice == 1:
            choice_flag = True
        elif choice == 2:
            choice_flag = True
        else:
            print("Please try again.")
    return choice

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
            print("Invalid input: please enter either 'a' or 'b'.")
    input_flag = False

    print('How long would you like to workout?')
    while input_flag is False:
        workout_length = input("Enter 'a' for thirty minutes or 'b' for one hour: ")
        if workout_length == 'a' or workout_length == 'b':
            input_flag = True
        else:
            print("Invalid input: please enter either 'a' or 'b'.")
    return (days_per_week, workout_length)

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
        try:
            response = int(input().strip())
        
            # validate user input
            if response in ids:
                input_flag = True
            else:
                print("Invalid input: this id is not an option. Please input one from the list.")
        except:
            print("Invalid input: please input the id to the left of the category")
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
        try:
            response = int(input().strip())
            # validate user input
            if response in ids:
                input_flag = True
            else:
                print("Invalid input: this id is not an option. Please input one from the list.")
        except:
            print("Invalid input: please input the id to the left of the exercise.")
    print("")
    return response

# receives: a list of workout groups, valid values are U (upper
#           body), L (lower body), B (back and biceps), C (chest and triceps),
#           or A (accessory).
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
        # get back and biceps exercises
        elif key == 'B':
            bnb_cat = get_category(back_and_bis)
            bnb_exercises = get_exercises(bnb_cat)
            bnb_choice = choose_exercise(bnb_exercises)
            choices.append(bnb_choice)
        # get chest and triceps exercises
        elif key == 'C':
            cnt_cat = get_category(chest_and_tris)
            cnt_exercises = get_exercises(cnt_cat)
            cnt_choice = choose_exercise(cnt_exercises)
            choices.append(cnt_choice)
        else:
            print("Invalid workout: workout type not an option.")
    return choices
    
# method to ask the user what they would like to name their workout
def getWorkoutName():
    workout_name = input("What would you like to name this workout? ")
    return workout_name
    
# method to get the name of an exercise when passed the exercise id
def getExercise(exercise_id):
    r = requests.get(BASE_URL + 'exerciseinfo/' + str(exercise_id), headers=headers)
    exercise = r.json()
    name = exercise["name"]
    return name 

def addNewWorkout(username):
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
    workout_name = getWorkoutName()
    current_date = date.today()
    # add workout plan to workout_plan table
    workout_obj = {}

    # get unique workout plan id
    query_workout_id = "SELECT MAX(workout_id) + 1 FROM workout_plan WHERE username = '" + username + "';"
    query_result = engine.execute(query_workout_id).fetchall()
    workout_id = query_result[0][0]
    if workout_id is None:
        workout_id = 1

    # Build workout object
    workout_obj["username"] = [username]
    workout_obj["workout_id"] = [workout_id]
    workout_obj["workout_name"] = [workout_name]
    workout_obj["date_created"] = [current_date]

    # Add workout object to data frame
    panda_data_frame = pd.DataFrame.from_dict(workout_obj)
    panda_data_frame.to_sql('workout_plan', con=engine, if_exists='append', index=False)

    # build session object
    if len(workout_days) == 3:
        dow_dict = three_day
    else:
        dow_dict = four_day
    for val in workout_days:
        session_obj = {}
        session_obj["username"] = [username]
        session_obj["workout_id"] = [workout_id] 
        session_obj["session_id"] = [val]
        session_obj["session_dow"] = [dow_dict[val]]
        # add session object to data frame
        panda_data_frame = pd.DataFrame.from_dict(session_obj)
        panda_data_frame.to_sql('sessions', con=engine, if_exists='append', index=False)
        # build exercise object
        for exercise_id in workout_days[val]:
            exercise_obj = {}
            exercise_name = getExercise(exercise_id)
            exercise_obj["username"] = [username]
            exercise_obj["workout_id"] = [workout_id] 
            exercise_obj["session_id"] = [val]
            exercise_obj["exercise_id"] = [exercise_id]
            exercise_obj["exercise_name"] = [exercise_name]
            #add exercise object to data frame
            panda_data_frame = pd.DataFrame.from_dict(exercise_obj)
            panda_data_frame.to_sql('exercises', con=engine, if_exists='append', index=False)

def displayUpdateWorkout(username):
    print("Here is a list of available workouts to update:")
    # get all workout plans for this user
    query_workouts = "SELECT * FROM workout_plan WHERE username = '" + username + "';"
    query_result = engine.execute(query_workouts).fetchall()

    for workout in query_result:
        # print the workout id and name for each plan
        print(str(int(workout[1])) + ': ' + str(workout[2]))

    choice = int(input("Enter the ID for the workout you would like to update: "))
    return choice

def updateWorkout(workout_id, username):
    new_name = input("Enter the new workout name: ")
    update_workouts = "UPDATE workout_plan SET workout_name ='" + str(new_name) + "' WHERE username='"+ str(username) +"' AND workout_id=" + str(workout_id) +";"
    query_result = engine.execute(update_workouts)

def main():
    
    #get user input
    username = getUsername()
    display_choice = displayMenu(username)

    if display_choice == 1:
        addNewWorkout(username)
    elif display_choice == 2:
        update_choice = displayUpdateWorkout(username)
        updateWorkout(update_choice, username)
    else:
        print("Invalid menu selection.")

    #query_plan = "SELECT * FROM workout_plan;"
    #query_result = engine.execute(query_plan).fetchall()  
    #print(query_result)

main()
