import random
from typing import Dict, List, Collection
from abc import ABC, abstractmethod

class Action(ABC):
    name: str
    base_power: float
    power_variance: float
    is_multi_target: bool = False
    user: "Creature"
    @property
    def power(self):
        return self.base_power - (self.power_variance / 2) + (self.power_variance * random.random())

    def __init__(self, user: "Creature"):
        self.user = user

    @abstractmethod
    def describe(self) -> str:
        pass

class Attack(Action):
    @property
    def power_variance(self):
        return self.user.damage_range_base

    @abstractmethod
    def describe(self):
        pass

class Healing(Action):
    @abstractmethod
    def describe(self):
        pass

class Spell(Action):
    mp_cost: int
    user: "SpellcasterMixin"
    @abstractmethod
    def describe(self):
        pass

class Buff(Action):
    buff_effects: Dict[str, int]
    @abstractmethod
    def describe(self):
        pass

class Debuff(Action):
    debuff_effects: Dict[str, int]
    @abstractmethod
    def describe(self):
        pass

class Creature(ABC):
    name: str
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    hp_current: int
    xp: int
    tracker: "Tracker"
    actions: Collection[Action]
    modifiers: Dict[str, int] = {"attack": 0, "defence": 0, "damage_base": 0, "damage_range": 0, "crit_chance": 0, "crit_mult": 0}
    @property
    def hp_max(self) -> int:
        return self.constitution * 10
    @property
    def attack(self):
        return ((self.strength + self.dexterity) / 2.0) + self.modifiers["attack"]
    @property
    def defence(self):
        return ((self.dexterity + self.constitution) / 2.0) + self.modifiers["defence"]
    @property
    def damage_base(self):
        return self.strength + (self.dexterity / 2.0) + self.modifiers["damage_base"]
    @property
    def damage_range_base(self):
        return (self.damage_base * 0.15) + self.modifiers["damage_range"]
    @property
    def crit_chance(self):
        return ((self.dexterity / 10.0) + self.modifiers["crit_chance"]) / 100
    @property
    def crit_mult(self):
        return 1 + (self.dexterity / 10.0) + self.modifiers["crit_mult"]

    def __init__(self, name: str, strength: int, dexterity: int, constitution: int, intelligence: int, tracker: "Tracker") -> None:
        self.name = name
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.hp_current = self.hp_max
        self.tracker = tracker

    def make_attack(self, action: Attack, target: "Creature") -> None:
        # max means hit chance won't drop below 0.05
        hit_chance = max(0.5 + ((self.attack - target.defence) / (2.0 * self.attack)), 0.05)
        if random.random() <= hit_chance:
            dmg = action.power
            if random.random() <= self.crit_chance:
                dmg *= self.crit_mult
            dmg = int(dmg)
            target.take_damage(dmg)
            print(f"{self.name} attacks {target.name} with {action.name} for {dmg} damage")
        else:
            print(f"{self.name} attacks {target.name} but misses")

    def heal_target(self, action: Healing, target: "Creature") -> None:
        heal_amt = action.power
        target.hp_current += heal_amt
        if target.hp_max < target.hp_current:
            target.hp_current = target.hp_max
        print(f"{self.name} heals {target.name} for {heal_amt} hp")

    def take_damage(self, damage) -> None:
        self.hp_current -= damage
        if self.hp_current <= 0:
            self.die()

    def buff_target(self, action: Buff, target: "Creature") -> None:
        for effect in action.buff_effects:
            target.modifiers[effect] += action.buff_effects[effect]
            print(f"{self.name} buffs {effect} by {action.buff_effects[effect]}")

    def debuff_target(self, action: Debuff, target: "Creature") -> None:
        for effect in action.debuff_effects:
            target.modifiers[effect] += action.debuff_effects[effect]
            print(f"{self.name} debuffs {target.name}'s {effect} by {action.debuff_effects[effect]}")

    @abstractmethod
    def die(self) -> None:
        pass

    def describe(self) -> str:
        return f'{self.name} has {self.hp_current} hp.'

    @abstractmethod
    def choose_action(self) -> None:
        pass

    def do_action(self, action: Action, targets: List["Creature"], positive_effect: bool) -> None:
        print(f"{self.name} uses {action.name}")
        for target in targets:
            # if multiple categories, apply buffs/debuffs first, then attack/heal
            if isinstance(action, Buff) and positive_effect:
                self.buff_target(action, target)
            if isinstance(action, Debuff) and not positive_effect:
                self.debuff_target(action, target)
            if isinstance(action, Attack) and not positive_effect:
                self.make_attack(action, target)
            if isinstance(action, Healing) and positive_effect:
                self.heal_target(action, target)

    @abstractmethod
    def choose_target(self, action: Action) -> List["Creature"]:
        pass

    def reset_modifiers(self) -> None:
        for modifier in self.modifiers:
            self.modifiers[modifier] = 0

class NPC(Creature):
    actions: Dict[Action, int]

    def __init__(self, name: str, strength: int, dexterity: int, constitution: int, intelligence: int, tracker: "Tracker") -> None:
        super().__init__(name, strength, dexterity, constitution, intelligence, tracker)

    def choose_action(self) -> None:
        action = random.choices(list(self.actions.keys()), list(self.actions.values()))[0]
        if isinstance(action, Spell) and isinstance(self, SpellcasterMixin):
            can_cast = self.try_cast_spell(action)
            if not can_cast:
                self.actions[action] = 0
                self.choose_action()
                return
        else:
            self.choose_target(action)

    def choose_target(self, action: Action) -> None:
        if isinstance(action, Attack) or isinstance(action, Debuff):
            self.do_action(action,[self.tracker.player], False)
        if isinstance(action, Healing) or isinstance(action, Buff):
            self.do_action(action, self.tracker.active_creatures if action.is_multi_target else [self], True)

    def die(self) -> None:
        self.tracker.active_creatures.remove(self)
        print(f"{self.name} is dead")
        self.tracker.player.gain_xp(self.xp)
        print(f"{self.tracker.player.name} gained {self.xp} xp")

class Player(Creature):
    actions: List[Action]

    def __init__(self, name: str, strength: int, dexterity: int, constitution: int, intelligence: int, tracker: "Tracker") -> None:
        tracker.player = self
        super().__init__(name, strength, dexterity, constitution, intelligence, tracker)
        self.xp = 0

    def choose_action(self) -> None:
        print("Choose an action by entering the number:")
        for i in range(len(self.actions)):
            print(f"{i + 1}: {self.actions[i].describe()}")
        choice = -1
        while choice not in range(len(self.actions)):
            try:
                choice = int(input("> ")) - 1
            except ValueError:
                print("Please enter a number:")
        action = self.actions[choice]
        if isinstance(action, Spell) and isinstance(self, SpellcasterMixin):
            can_cast = self.try_cast_spell(action)
            if not can_cast:
                self.choose_action()
            return
        else:
            self.choose_target(action)

    def choose_target(self, action: Action) -> None:
        if isinstance(action, Healing) or isinstance(action, Buff):
            self.do_action(action, [self], True)
        if isinstance(action, Attack) or isinstance(action, Debuff):
            if action.is_multi_target:
                self.do_action(action, self.tracker.active_creatures, False)
            else:
                print("Choose a target by entering the number:")
                for i in range(len(self.tracker.active_creatures)):
                    print(f"{i + 1}: {self.tracker.active_creatures[i].name}")
                choice = -1
                while choice not in range(len(self.tracker.active_creatures)):
                    try:
                        choice = int(input("> ")) - 1
                    except ValueError:
                        print("Please enter a number:")
                        choice = input("> ")
                target = self.tracker.active_creatures[choice]
                self.do_action(action, [target], False)

    def gain_xp(self, xp: int) -> None:
        self.xp += xp
        if self.xp > 100:
            self.xp -= 100
            self.level_up()

    def level_up(self) -> None:
        print(f"""You level up! Choose an attribute to increase by entering the number:
1: Strength     (currently {self.strength})
2: Dexterity    (currently {self.dexterity})
3: constitution (currently {self.constitution})
4: Intelligence (currently {self.intelligence})""")
        choice = 0
        while choice not in range(1, 5):
            try:
                choice = int(input("> "))
            except ValueError:
                print("Please enter a number:")
        match choice:
            case 1:
                self.strength += 1
            case 2:
                self.dexterity += 1
            case 3:
                self.constitution += 1
            case 4:
                self.intelligence += 1
        self.hp_current = self.hp_max

    def die(self) -> None:
        print("You are dead! Game over")
        exit(0)

    def regen(self):
        hp_regen = max(int(self.constitution / 10), 1)
        self.hp_current += hp_regen
        print(f"{self.name} recovers {hp_regen} hp")
        if isinstance(self, SpellcasterMixin):
            mp_regen = max(int(self.intelligence / 10), 1)
            self.mp_current += mp_regen
            print(f"{self.name} recovers {mp_regen} mp")

class SpellcasterMixin(Creature):
    mp_current: int
    @property
    def spell_power(self):
        return self.intelligence
    @property
    def mp_max(self):
        return self.intelligence * 10

    def try_cast_spell(self, spell: Spell) -> bool:
        if spell.mp_cost > self.mp_current:
            if isinstance(self, Player):
                print(f"Not enough mana! {spell.name} costs {spell.mp_cost} and you have {self.mp_current}")
            return False
        self.mp_current -= spell.mp_cost
        self.choose_target(spell)
        return True

    def describe(self) -> str:
        return f"{self.name} has {self.hp_current} hp and {self.mp_current} mp"

    @abstractmethod
    def choose_action(self) -> None:
        pass

class Tracker: # this helps track the active creatures
    active_creatures: List[Creature]
    player: Player

    def __init__(self):
        self.active_creatures = []

    def add_active_creature(self, creature: Creature):
        self.active_creatures.append(creature)

    def remove_active_creature(self, creature: Creature):
        self.active_creatures.remove(creature)
