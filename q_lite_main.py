import db_functions as db
import itertools
import os
import platform

def chunker_longest(iterable, chunksize):
    return itertools.zip_longest(*[iter(iterable)] * chunksize)

def input_validate(input_prompt, menu_items):
    if len(menu_items) > 10:
        column_menu = []
        for i in range(1, len(menu_items)):
            column_menu.append("{}: {}".format(i, menu_items[i]))
        for chunk in chunker_longest(column_menu, 3):
            print("{:<25} | {:<25} | {:<25}".format(str(chunk[0]), str(chunk[1]), str(chunk[2])))
    else:
        for i in range(1, len(menu_items)):
            print("{}: {}".format(i, menu_items[i]))
    
    user_input = input(input_prompt)
    if user_input == "":
        user_input = 0
    
    try:
        user_input = int(user_input)
    except ValueError:
        user_input = 0
    
    if user_input < 1 or user_input >= len(menu_items):
        print("Not a valid choice. Must be between 1 and {}".format(len(menu_items) - 1))
        return None
    else:
        return user_input
    
def main_menu():
    print("Current system is [{}]".format(current_system))
    my_input = input_validate("Enter choice: ", main_menu_choices)
    if my_input is not None:
        return my_input
    else:
        return 0
    
def set_system():
    global current_system
    systems = db.get_systems()
    my_input = input_validate("Select System: ", systems)
    if my_input is not None:
        current_system = systems[my_input]
        config_properties["current_system"] = current_system
        save_config()
        
def add_game():
    game_name = input("Game Name: ")
    game_notes = input("Game Notes: ")
    if game_name != '' and current_system != '':
        db.insert_game(game_name, current_system, game_notes)
        global num_updates
        num_updates += 1
    else:
        print("Could not add game. Either game name or current system is blank.")
    
def update_game():
    global num_updates
    game_id = input("Game ID: ")
    db.get_game_by_id(game_id)
    
    game_name = input("Updated Game Name: ")
    if game_name != "":
        db.update_game_name(game_name, game_id)
        num_updates += 1
        
    game_notes = input("Updated Game Notes: ")
    if game_notes != "":
        db.update_game_notes(game_notes, game_id)
        num_updates += 1

def get_games_letter():
    game_letter = input("Enter starting letter: ")
    db.get_games_for_system_letter(current_system, game_letter)
    
def get_games_search():
    game_search = input("Enter search string: ")
    db.get_games_for_system_search(game_search)

def load_config():
    global config_properties
    if os.path.exists("config.txt"):
        with open("config.txt") as f:
            for line in f.readlines():
                (key, value) = line.strip().split("=")
                config_properties[key] = value   
        
def save_config():
    global config_properties
    with open("config.txt", 'w') as f:
        for key in config_properties:
            f.write("{}={}".format(key, config_properties[key]))

def q_exit():
    global num_updates
    if num_updates > 0:
        db.backup_database()
    
    
########
# Main #
########

print("Q Lite")

# Load config file
config_properties = {
        "current_system" : ""
}
load_config()  
current_system = config_properties["current_system"]

# Global variables
choice = 0
num_updates = 0

functions = {
        "Choose System" : set_system,
        "Add Game" : add_game,
        "List All" : db.get_games_for_system,
        "List <letter>" : get_games_letter,
        "Search" : get_games_search,
        "Update" : update_game,
        "Exit" : q_exit
}
main_menu_choices = [""] + list(functions.keys())
exit_choice = main_menu_choices.index("Exit")

if platform.system() == 'Linux':
    Clear = lambda: os.system('clear')
else:
    clear = lambda: os.system('cls')

while(choice != exit_choice):
    choice = main_menu()
    if choice != 0:
        print("Your choice was {}.".format(main_menu_choices[choice]))

        if main_menu_choices[choice] == "List All":
            functions[main_menu_choices[choice]](current_system)
        else:
            functions[main_menu_choices[choice]]()
        
        if main_menu_choices[choice] != "Exit":
            input("Press enter to continue")
            clear()
