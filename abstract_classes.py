import random
from enum import Enum
from typing import Callable, Dict, List, Tuple, Collection
from abc import ABC, abstractmethod

from orca.sound import Player


class ActionType(Enum):
    ATTACK = 1
    HEAL = 2
    BUFF = 3
    DEBUFF = 4

class Action:
    name: str
    base_power: int
    power_variance: float
    type: ActionType
    is_multi_target: bool
    attribute: str
    @property
    def power(self):
        return self.base_power - (self.power_variance / 2) + (self.power_variance * random.random())

class Creature(ABC):
    name: str
    base_strength: int
    base_dexterity: int
    base_constitution: int
    base_intelligence: int
    hp_current: int
    xp: int
    tracker: "Tracker"
    actions: Collection[Action]
    modifiers: Dict[str, int] = {"strength": 0, "dexterity": 0, "constitution": 0, "intelligence": 0}
    @property
    def strength(self):
        return self.base_strength + self.modifiers["strength"]
    @property
    def dexterity(self):
        return self.base_dexterity + self.modifiers["dexterity"]
    @property
    def constitution(self):
        return self.base_constitution + self.modifiers["constitution"]
    @property
    def intelligence(self):
        return self.base_intelligence + self.modifiers["intelligence"]
    @property
    def hp_max(self) -> int:
        return self.base_constitution * 10
    @property
    def attack(self):
        return (self.strength + self.dexterity) / 2.0
    @property
    def defence(self):
        return (self.dexterity + self.constitution) / 2.0
    @property
    def base_damage(self):
        return self.strength
    @property
    def base_damage_range(self):
        return self.base_damage * 0.15

    def __init__(self, name: str, strength: int, dexterity: int, constitution: int, intelligence: int, tracker: "Tracker") -> None:
        self.name = name
        self.base_strength = strength
        self.base_dexterity = dexterity
        self.base_constitution = constitution
        self.base_intelligence = intelligence
        self.hp_current = self.hp_max
        self.tracker = tracker
        tracker.add_active_creature(self)

    def make_attack(self, action: Action, target: "Creature") -> None:
        # max means hit chance won't drop below 0.05
        hit_chance = max(0.5 + ((self.attack - target.defence) / (2.0 * self.attack)), 0.05)
        if random.random() <= hit_chance:
            dmg = action.power
            target.take_damage_or_heal(dmg)
            print(f"{self.name} attacks {target.name} with {action.name} for {dmg} damage")
        else:
            print(f"{self.name} attacks {target.name} but misses")

    def heal_self(self, action: Action) -> None:
        heal_amt = action.power
        self.take_damage_or_heal(heal_amt)
        print(f"{self.name} heals for {heal_amt} hp")

    def take_damage_or_heal(self, damage) -> None:
        self.hp_current -= damage
        if self.hp_current <= 0:
            self.die()
        if self.hp_max < self.hp_current:
            self.hp_current = self.hp_max

    @abstractmethod
    def die(self) -> None:
        pass

    def buff_self(self, action: Action) -> None:
        buff_amt = action.power
        self.modifiers[action.attribute] += buff_amt
        print(f"{self.name} buffs {action.attribute} by {buff_amt}")

    def debuff_target(self, action: Action, target: "Creature") -> None:
        debuff_amt = action.power
        target.modifiers[action.attribute] -= debuff_amt
        print(f"{self.name} debuffs {target.name}'s {action.attribute} by {debuff_amt}")

    def describe(self) -> str:
        return f'{self.name} has {self.hp_current} hp left.'

    @abstractmethod
    def choose_action(self) -> None:
        pass

    def do_action(self, action: Action, target) -> None:
        match action.type:
            case ActionType.ATTACK:
                self.make_attack(action, target)
            case ActionType.HEAL:
                self.heal_self(action)
            case ActionType.BUFF:
                self.buff_self(action)
            case ActionType.DEBUFF:
                self.debuff_target(action, target)

class BasicAttack(Action):
    type = ActionType.ATTACK
    is_multi_target = False

    def __init__(self, creature: Creature, name: str="Basic Attack"):
        self.name = name
        self.base_power = creature.base_damage
        self.power_variance = creature.base_damage_range

class Spell(Action):
    mp_cost: int

class NPC(Creature):
    actions: Dict[Action, int]

    def __init__(self, name: str, strength: int, dexterity: int, constitution: int, intelligence: int, tracker: "Tracker") -> None:
        super().__init__(name, strength, dexterity, constitution, intelligence, tracker)
        self.actions[BasicAttack(self)] = 10

    def choose_action(self) -> None:
        action = random.choices(list(self.actions.keys()), list(self.actions.values()))
        self.do_action(action, self.tracker.player)

    def die(self) -> None:
        self.tracker.active_creatures.remove(self)
        print(f"{self.name} is dead")


class Player(Creature):
    actions: List[Action]

    def __init__(self, name: str, strength: int, dexterity: int, constitution: int, intelligence: int, tracker: "Tracker") -> None:
        super().__init__(name, strength, dexterity, constitution, intelligence, tracker)
        self.actions = [BasicAttack(self)] + self.actions

    def choose_action(self):
        print("Choose an action by entering the number:")
        for i in range(len(self.actions)):
            print(f"{i + 1}: {self.actions[i]}")
        choice = -1
        while choice not in range(len(self.actions)):
            try:
                choice = int(input("> ")) - 1
            except ValueError:
                print("Please enter a number:")
                choice = input("> ")
        action = self.actions[choice - 1]
        target = self if action.type in [ActionType.HEAL, ActionType.BUFF] else None
        if isinstance(action, Spell) and isinstance(self, SpellcasterMixin):
            can_cast = self.try_cast_spell(action, target)
            if not can_cast:
                self.choose_action()
        else:
            self.do_action(action, target)

    def gain_xp(self, xp: int) -> None:
        print(f"You gain {xp} xp")
        self.xp += xp
        if self.xp > 100:
            self.xp -= 100
            self.level_up()

    def level_up(self) -> None:
        print(f"""You level up! Choose an attribute to increase by entering the number:
1: Strength     (currently {self.base_strength})
2: Dexterity    (currently {self.base_dexterity})
3: constitution    (currently {self.base_constitution})
4: Intelligence (currently {self.base_intelligence})""")
        choice = 0
        while choice not in range(1, 5):
            try:
                choice = int(input("> "))
            except ValueError:
                print("Please enter a number:")
        match choice:
            case 1:
                self.base_strength += 1
            case 2:
                self.base_dexterity += 1
            case 3:
                self.base_constitution += 1
            case 4:
                self.base_intelligence += 1
        self.hp_current = self.hp_max

    def die(self) -> None:
        print("You are dead! Game over")
        exit(0)

class SpellcasterMixin(Creature):
    mp_current: int
    @property
    def spell_power(self):
        return self.intelligence
    @property
    def mp_max(self):
        return self.base_intelligence * 10

    def try_cast_spell(self, spell: Spell, target: Creature) -> bool:
        if spell.mp_cost > self.mp_current:
            if isinstance(self, Player):
                print(f"Not enough mana! {spell.name} costs {spell.mp_cost} and you have {self.mp_current}")
            return False
        self.mp_current -= spell.mp_cost
        self.do_action(spell, target)
        return True

    def describe(self) -> str:
        return f"{self.name} has {self.hp_current} hp and {self.mp_current} mp"

    @abstractmethod
    def choose_action(self) -> None:
        pass

class Tracker: # this helps track the active creatures
    active_creatures: List[Creature]
    player: Player

    def __init__(self, player: Player):
        self.active_creatures = []
        self.player = player

    def add_active_creature(self, creature: Creature):
        self.active_creatures.append(creature)

    def remove_active_creature(self, creature: Creature):
        self.active_creatures.remove(creature)
