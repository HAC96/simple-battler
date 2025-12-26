from abstract_classes import Action, Attack, Healing, Buff, Debuff, Spell, Creature


class BasicAttack(Attack):
    @property
    def base_power(self):
        return self.user.damage_base

    def __init__(self, user: Creature, name: str="Basic Attack"):
        self.name = name
        super().__init__(user)

    def describe(self):
        return f"{self.name}: A basic attack."

class PowerAttack(Attack, Debuff):
    name = "Power Attack"
    @property
    def base_power(self):
        return self.user.damage_base * 2
    debuff_effects = {"defence": -2}

    def describe(self):
        return f"{self.name}: Attack with double damage at the cost of reduced defence until start of next turn."

class MinorHeal(Healing, Spell):
    name = "Basic Heal"
    @property
    def base_power(self):
        return self.user.spell_power / 3
    power_variance = 1
    mp_cost = 5

    def describe(self):
        return f"{self.name}: A weak healing spell. Costs {self.mp_cost} MP"

class SneakAttack(Attack, Buff):
    name = "Sneak Attack"
    @property
    def base_power(self):
        return self.user.damage_base * 0.8
    buff_effects = {"attack": +1, "crit_mult": +10}

    def describe(self):
        return f"{self.name}: Attack with a bonus to hit and crit chance at the cost of reduced base damage"

class LightningBolt(Attack, Spell):
    name = "Lightning Bolt"
    @property
    def base_power(self):
        return self.user.spell_power * 3
    mp_cost = 10

    def describe(self):
        return f"{self.name}: A powerful single-target attack spell. Costs {self.mp_cost} MP"

class FireBall(Attack, Spell):
    name = "Fireball"
    @property
    def base_power(self):
        return self.user.spell_power * 1.2
    mp_cost = 10

    def describe(self):
        return f"{self.name}: An attack spell that targets multiple enemies. Costs {self.mp_cost} MP"

class DefensiveStrike(Attack, Buff):
    name = "Defensive Strike"
    @property
    def base_power(self):
        return self.user.damage_base * 0.3
    buff_effects = {"defence": +3}

    def describe(self):
        return f"{self.name}: Strike with significantly reduced damage but increase your defence until the start of next turn."

class SapMorale(Debuff, Spell):
    name = "Sap Morale"
    mp_cost = 5
    debuff_effects = {"attack": -5, "damage_base": -5}
    is_multi_target = True

    def describe(self):
        return f"{self.name}: Reduce the attack and damage of all enemies until the start of next turn. Costs {self.mp_cost} MP"

class MagicBarrier(Buff, Spell):
    name = "Magic Barrier"
    mp_cost = 5
    buff_effects = {"defence": +10}

    def describe(self):
        return f"{self.name}: Significantly increase defence until the start of next turn. Costs {self.mp_cost} MP"

class MajorHeal(Healing, Spell):
    name = "Major Heal"
    mp_cost = 20
    @property
    def base_power(self):
        return self.user.spell_power * 2

    def describe(self):
        return f"{self.name}: A strong healing spell. Costs {self.mp_cost} MP"

class Dodge(Buff):
    name = "Dodge"
    buff_effects = {"defence": +5}

    def describe(self):
        return f"{self.name}: Increase defence until the start of next turn."
