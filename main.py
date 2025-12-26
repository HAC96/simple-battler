from src.abstract_classes import Tracker
from src.player_classes import *

def main():
    print("""Welcome to the dungeon!

Please select a character class.
The Warrior starts with 15 Strength, 12 Dexterity, 15 Constitution, 5 Intelligence.
They can trade-off stronger attacks at the cost of defence or vice versa. They are the toughest class.
The Rogue starts with 10 Strength, 20 Dexterity, 10 Constitution, 8 Intelligence.
They deal more damage with critical hits, and can strike with increased accuracy.
The Mage starts with 5 Strength, 12 Dexterity, 8 Constitution, 20 Intelligence.
They can cast powerful spells, and are the only class to use Intelligence instead of Strength for their basic attack.
The Priest starts with 10 Strength, 10 Dexterity, 10 Constitution, 15 Intelligence.
They can cast healing spells and debuff their enemies.

Overview of the key attributes:
Strength affects attack hit chance and attack damage.
Dexterity affects attack hit chance, attack damage, critical hit chance, and critical damage.
Constitution affects maximum health points, defence, and health regen between turns.
Intelligence affects spell power, maximum mana points, and mana regen between turns.

Please enter a number to select your class:
1. Warrior
2. Rogue
3. Mage
4. Priest
""")
    choice = input("> ")
    while choice not in ["1", "2", "3", "4"]:
        print("Please enter a number corresponding to your class:")
        choice = input("> ")
    print("Please name your character:")
    name = input("> ")
    while name.strip() == "":
        print("Please name your character:")
        name = input("> ")
    player = None
    tracker = Tracker()
    match choice:
        case 1:
            player = Warrior(name, tracker)
        case 2:
            player = Rogue(name, tracker)
        case 3:
            player = Mage(name, tracker)
        case 4:
            player = Priest(name, tracker)
    player.describe()
    new_encounter(tracker)
    while True: # continue until player dies
        player.choose_action()
        for creature in tracker.active_creatures:
            creature.choose_action()
        next_turn(tracker)

def next_turn(tracker: Tracker):
    tracker.player.reset_modifiers()
    tracker.player.regen()
    print(tracker.player.describe())
    for creature in tracker.active_creatures:
        creature.reset_modifiers()
        print(creature.describe())
    if tracker.active_creatures == []:
        new_encounter(tracker)

def new_encounter(tracker: Tracker):
    print("As you advance deeper into the dungeon, new enemies emerge to fight...")
    # TODO: introduce logic to spawn new enemies and add to tracker
    for creature in tracker.active_creatures:
        creature.describe()

if __name__ == "__main__":
    main()