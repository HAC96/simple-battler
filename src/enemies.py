from .abstract_classes import NPC, SpellcasterMixin, Tracker
from .actions import *

class Goblin(NPC):
    xp = 5

    def __init__(self, tracker: Tracker):
        super().__init__(
            name="Goblin",
            strength=7,
            dexterity=12,
            constitution=7,
            intelligence=5,
            tracker=tracker
        )
        self.actions = {
            BasicAttack(self, "Stab"): 10,
            SneakAttack(self): 3,
            Dodge(self): 3,
        }

class DarkMage(NPC, SpellcasterMixin):
    xp = 10

    def __init__(self, tracker: Tracker):
        super().__init__(
            name="Dark Mage",
            strength=7,
            dexterity=12,
            constitution=6,
            intelligence=12,
            tracker=tracker
        )
        self.mp_current = self.mp_max
        self.actions = {
            BasicAttack(self, "Stab"): 3,
            LightningBolt(self): 5,
            MagicBarrier(self): 5,
        }

class Shaman(NPC, SpellcasterMixin):
    xp = 8

    def __init__(self, tracker: Tracker):
        super().__init__(
            name="Shaman",
            strength=9,
            dexterity=9,
            constitution=8,
            intelligence=12,
            tracker=tracker
        )
        self.mp_current = self.mp_max
        self.actions = {
            BasicAttack(self, "Strike"): 5,
            MinorHeal(self): 3,
            SapMorale(self): 5,
            GroupHeal(self): 3,
        }
