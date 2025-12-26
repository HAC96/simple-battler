from abstract_classes import Player, SpellcasterMixin, Tracker
from actions import *

class Warrior(Player):
    def __init__(self, name: str, tracker: Tracker) -> None:
        super().__init__(
            name=name,
            strength=15,
            dexterity=12,
            constitution=15,
            intelligence=5,
            tracker=tracker
        )
        self.actions = [
            BasicAttack(self, "Strike"),
            PowerAttack(self),
            DefensiveStrike(self)
        ]

class Rogue(Player):
    @property
    def crit_mult(self):
        return 2 + (self.dexterity / 10.0) + self.modifiers["crit_mult"]

    def __init__(self, name: str, tracker: Tracker) -> None:
        super().__init__(
            name=name,
            strength=10,
            dexterity=20,
            constitution=10,
            intelligence=8,
            tracker=tracker
        )
        self.actions = [
            BasicAttack(self, "Stab"),
            SneakAttack(self),
            Dodge(self),
        ]

class Mage(Player, SpellcasterMixin):
    @property
    def attack(self):
        return ((self.intelligence + self.dexterity) / 2.0) + self.modifiers["attack"]
    @property
    def damage_base(self):
        return self.intelligence + (self.dexterity / 2.0) + self.modifiers["damage_base"]

    def __init__(self, name: str, tracker: Tracker) -> None:
        super().__init__(
            name=name,
            strength=5,
            dexterity=12,
            constitution=8,
            intelligence=20,
            tracker=tracker
        )
        self.actions = [
            BasicAttack(self, "Spark"),
            LightningBolt(self),
            FireBall(self),
            MagicBarrier(self),
        ]

class Priest(Player, SpellcasterMixin):
    def __init__(self, name: str, tracker: Tracker) -> None:
        super().__init__(
            name=name,
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=15,
            tracker=tracker
        )
        self.actions = [
            BasicAttack(self, "Strike"),
            MinorHeal(self),
            SapMorale(self),
            MajorHeal(self),
        ]