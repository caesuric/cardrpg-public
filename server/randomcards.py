import random

class RandomCard(object):
    def __init__(self, cost, attributes):
        self.cost = max(cost,1)
        self.attributes = attributes
    def __str__(self):
        return "Cost: {0}, \nAttributes:\n{1}".format(self.cost, stringify_list(self.attributes))

class RandomAttackCard(RandomCard):
    def __init__(self, cost=0, damage=0, dot_based_damage=0, dot_based_damage_seconds=0, attributes=[], mp_usage=0, element='', basis='', radius=0, is_ranged = False):
        super(RandomAttackCard, self).__init__(cost, attributes)
        self.damage = damage
        self.dot_based_damage = dot_based_damage
        self.dot_based_damage_seconds = dot_based_damage_seconds
        self.mp_usage = mp_usage
        self.element = element
        self.basis = basis
        self.radius = radius
        self.is_ranged = is_ranged
    def __str__(self):
        return "Cost: {0}, Starting damage: {1}, DoT Damage: {2}, MP: {3}, Element: {4}, Basis: {5}, Radius: {6}, Is Ranged: {7}, \nAttributes:\n{8}".format(self.cost, int(self.damage*16), int(self.dot_based_damage*16), self.mp_usage, self.element, self.basis, self.radius, self.is_ranged, stringify_list(self.attributes))

def stringify_list(some_list):
    value = ''
    for item in some_list:
        value+= str(item)+'\n'
    return value

class RandomUntargetedUtilityCard(RandomCard):
    def __init__(self, cost=0, attributes=[]):
        super(RandomUntargetedUtilityCard, self).__init__(cost, attributes)

class RandomAllyTargetedUtilityCard(RandomCard):
    def __init__(self, cost=0, attributes=[]):
        super(RandomAllyTargetedUtilityCard, self).__init__(cost, attributes)

class RandomAllAllyUtilityCard(RandomCard):
    def __init__(self, cost=0, attributes=[]):
        super(RandomAllAllyUtilityCard, self).__init__(cost, attributes)

class RandomPermanentCard(RandomCard):
    def __init__(self, cost=0, attributes=[]):
        super(RandomPermanentCard, self).__init__()

class RandomCardAttribute(object):
    def __init__(self, attr, param):
        self.attr = attr
        self.param = param
    def __str__(self):
        return '{0} {1}'.format(self.attr,self.param)

def random_card(level, multiplayer = False):
    points = 70.0
    if level>1:
        for i in range(level-1):
            points *=1.1
    points = int(points)
    roll = random.uniform(1,100)
    if roll<=80.0:
        return random_attack(points, multiplayer)
    elif roll<=82.5:
        return random_all_ally_utility(points, multiplayer)
    elif roll<=88.57:
        return random_untargeted_utility(points, multiplayer)
    elif roll<=94.28:
        return random_ally_targeted_utility(points, multiplayer)
    elif roll<=95.71:
        return random_summon(points, multiplayer)
    else:
        return random_permanent(points, multiplayer)

def random_all_ally_utility(points, multiplayer):
    if not multiplayer:
        return random_ally_targeted_utility(points, multiplayer)
    original_points = points
    points = int(points/2)
    points, attributes = get_ally_utility_attributes(points, multiplayer)
    cost = int((original_points-points)/14)
    return RandomAllAllyUtilityCard(cost=cost, attributes=attributes)

def random_ally_targeted_utility(points, multiplayer):
    original_points = points
    points, attributes = get_ally_utility_attributes(points, multiplayer)
    cost = int((original_points-points)/14)
    return RandomAllyTargetedUtilityCard(cost=cost, attributes=attributes)

def random_untargeted_utility(points, multiplayer):
    original_points = points
    points, attributes = get_untargeted_utility_attributes(points, multiplayer)
    cost = int((original_points-points)/14)
    return RandomUntargetedUtilityCard(cost=cost, attributes=attributes)

def random_permanent(points, multiplayer):
    permanent_type = random.choice['mental', 'magical', 'tactical']
    points, attributes = get_permanent_attributes(points, multiplayer, permanent_type)
    cost = int(points/14)
    return RandomUntargetedUtilityCard(cost=cost, attributes=attributes)

def random_attack(points, multiplayer):
    roll = random.randint(1,100)
    if roll<=45:
        return random_melee_attack(int(points*1.5), points, multiplayer)
    elif roll<=90:
        return random_ranged_attack(points, points, multiplayer)
    else:
        return random_untargeted_aoe_attack(int(points/2), points, multiplayer)

def random_ranged_attack(points, original_points, multiplayer):
    roll = random.randint(1,100)
    uses_mp = (roll <= 50)
    if uses_mp:
        points, mp_usage = determine_mp_usage(points)
        basis = 'intelligence'
    else:
        mp_usage = 0
        basis = 'dexterity'
    elemental_affinity = determine_elemental_affinity(uses_mp)
    points, radius = generate_radius(points)
    points, dot_based_damage, dot_based_damage_seconds = is_a_dot(points)
    points, attributes = get_attack_attributes(points, multiplayer, uses_mp, dot_based_damage, radius, is_ranged=True)
    if dot_based_damage==0:
        damage = calc_damage(points)
    else:
        damage = 0
    return RandomAttackCard(cost=int(original_points/14), damage=damage, dot_based_damage=dot_based_damage, dot_based_damage_seconds=dot_based_damage_seconds, attributes=attributes, mp_usage=mp_usage, element=elemental_affinity, basis=basis, radius = radius, is_ranged = True)

def random_melee_attack(points, original_points, multiplayer):
    roll = random.randint(1,100)
    uses_mp = (roll <= 10)
    if uses_mp:
        points, mp_usage = determine_mp_usage(points)
    else:
        mp_usage = 0
    elemental_affinity = determine_elemental_affinity(uses_mp)
    basis = 'strength'
    points, radius = generate_radius(points)
    points, dot_based_damage, dot_based_damage_seconds = is_a_dot(points)
    points, attributes = get_attack_attributes(points, multiplayer, uses_mp, dot_based_damage, radius)
    if dot_based_damage==0:
        damage = calc_damage(points)
    else:
        damage = 0
    return RandomAttackCard(cost=int(original_points/14), damage=damage, dot_based_damage=dot_based_damage, dot_based_damage_seconds=dot_based_damage_seconds, attributes=attributes, mp_usage=mp_usage, element=elemental_affinity, basis=basis, radius = radius, is_ranged = False)

def get_attack_attributes(points, multiplayer, uses_mp, is_dot, radius, is_ranged = False):
    roll = random.randint(1,100)
    attributes = []
    if roll<=10:
        num_attributes = 0
    elif roll<=60:
        num_attributes = 1
    elif roll<=85:
        num_attributes = 2
    elif roll<=95:
        num_attributes = 3
    else:
        num_attributes = 4
    while num_attributes>0:
        success, points, attribute = get_attack_attribute(points, multiplayer, uses_mp, is_dot, radius, is_ranged)
        if success:
            attributes.append(attribute)
            num_attributes -= 1
    return points, attributes

def get_ally_utility_attributes(points, multiplayer):
    roll = random.randint(1,100)
    attributes = []
    if roll<=60:
        num_attributes = 1
    elif roll<=85:
        num_attributes = 2
    elif roll<=97:
        num_attributes = 3
    else:
        num_attributes = 4
    while num_attributes>0:
        success, points, attribute = get_ally_utility_attribute(points, multiplayer, num_attributes)
        if success:
            attributes.append(attribute)
            num_attributes -= 1
    return points, attributes

def get_untargeted_utility_attributes(points, multiplayer):
    roll = random.randint(1,100)
    attributes = []
    if roll<=50:
        num_attributes=1
    elif roll<=80:
        num_attributes=2
    elif roll<=95:
        num_attributes=3
    else:
        num_attributes=4
    while num_attributes>0:
        success, points, attribute = get_untargeted_utility_attribute(points, multiplayer, num_attributes)
        if success:
            attributes.append(attribute)
            num_attributes -= 1
    return points, attributes

def get_permanent_attributes(points, multiplayer, permanent_type):
    roll = random.randint(1,100)
    attributes = []
    if roll<=80:
        num_attributes=1
    elif roll<=95:
        num_attributes=2
    elif roll<=98:
        num_attributes=3
    else:
        num_attributes=4
    while num_attributes>0:
        success, points, attribute = get_permanent_attribute(points, multiplayer, num_attributes, permanent_type)
        if success:
            attributes.append(attribute)
            num_attributes -= 1
    return points, attributes

def get_attack_attribute(points, multiplayer, uses_mp, is_dot, radius, is_ranged):
    roll = random.uniform(1,100)
    if roll<=6.34:
        return True, int(points/2), RandomCardAttribute('ap+', 1.0)
    elif roll<=12.69:
        return True, int(points*0.8), RandomCardAttribute('chain_timer+', 2.5)
    elif roll<=19.04:
        return True, int(points/2), random_dot(int(points/2))
    elif roll<=20.63:
        return True, int(points*0.85), RandomCardAttribute('remove_debuff', None)
    elif roll<=23.80:
        return True, int(points*0.8), RandomCardAttribute('restore_mp', 20)
    elif roll<=26.98:
        if multiplayer:
            return True, int(points/2), RandomCardAttribute('aggro_multiplier', 4)
        else:
            return False, points, None
    elif roll<=28.57:
        return True, int(points/2), RandomCardAttribute('shield', 16*calc_damage(int(points/2)))
    elif roll<=30.15:
        return True, int(points/2), RandomCardAttribute('invisibility', 8)
    elif roll<=30.95:
        return True, int(points/4), RandomCardAttribute('invisibility+', 8)
    elif roll<=34.12:
        return True, int(points*0.7), RandomCardAttribute('stealthy', None)
    elif roll<=37.30:
        return True, int(points*0.5), RandomCardAttribute('backstabs', 4)
    elif roll<=40.47:
        return True, int(points*1.5), RandomCardAttribute('delay', 4)
    elif roll<=42.06:
        if multiplayer:
            return True, int(points*0.75), RandomCardAttribute('aggro_divisor', 2)
        else:
            return False, points, None
    elif roll<=42.85:
        if multiplayer:
            return True, int(points/4), RandomCardAttribute('aggro_all', 8)
        else:
            return False, points, None
    elif roll<=46.03:
        roll2 = random.randint(1,3)
        if roll2==1:
            return True, int(points/4), RandomCardAttribute('vulnerability', {'degree': 100, 'duration': 12})
        elif roll2==2:
            return True, int(points/2), RandomCardAttribute('vulnerability', {'degree': 50, 'duration': 12})
        elif roll2==3:
            return True, int(points*0.75), RandomCardAttribute('vulnerability', {'degree': 25, 'duration': 12})
    elif roll<=47.62:
        return True, int(points/2), RandomCardAttribute('blunting', 16*calc_damage(int(points/2)))
    elif roll<=50.79:
        roll2 = random.randint(1,4)
        if roll2==1:
            return True, int(points*0.9), RandomCardAttribute('trash', 1)
        elif roll2==2:
            return True, int(points*0.75), RandomCardAttribute('trash', 2)
        elif roll2==3:
            return True, int(points*0.5), RandomCardAttribute('trash', 3)
        elif roll2==4:
            return True, int(points*0.25), RandomCardAttribute('trash', 6)
    elif roll<=52.38:
        roll2 = random.randint(0,2)
        bonus_table = [100, 50, 25]
        points_mod_table = [0.5, 0.75, 0.9]
        bonus = bonus_table[roll2]
        points = int(points * points_mod_table[roll2])
        return True, points, RandomCardAttribute('damage+', {'bonus': bonus, 'duration': 12})
    elif roll<=53.96:
        roll2 = random.randint(0,2)
        bonus_table = [100, 50, 25]
        points_mod_table = [0.94, 0.97, 0.99]
        bonus = bonus_table[roll2]
        points = int(points * points_mod_table[roll2])
        element = determine_elemental_affinity(uses_mp)
        return True, points, RandomCardAttribute('elemental_damage+', {'bonus': bonus, 'duration': 12, 'element': element})
    elif roll<=54.76:
        if multiplayer:
            roll2 = random.randint(0,2)
            bonus_table = [100, 50, 25]
            points_mod_table = [0.5, 0.75, 0.9]
            bonus = bonus_table[roll2]
            points = int(points * points_mod_table[roll2])
            return True, points, RandomCardAttribute('all_allies_damage+', {'bonus': bonus, 'duration': 12})
        else:
            return False, points, None
    elif roll<=55.55:
        if multiplayer:
            roll2 = random.randint(0,2)
            bonus_table = [100, 50, 25]
            points_mod_table = [0.94, 0.97, 0.99]
            bonus = bonus_table[roll2]
            points = int(points * points_mod_table[roll2])
            element = determine_elemental_affinity(uses_mp)
            return True, points, RandomCardAttribute('elemental_damage+', {'bonus': bonus, 'duration': 12, 'element': element})
        else:
            return False, points, None
    elif roll<=57.14:
        return True, int(points*0.8), RandomCardAttribute('mp_over_time', {'mp': 40, 'time': 8})
    elif roll<=63.49:
        return True, int(points/2), RandomCardAttribute('heal', 16*calc_damage(int(points/2)))
    elif roll<=65.07:
        return True, int(points*0.85), RandomCardAttribute('usable_while_paralyzed', None)
    elif roll<=66.66:
        return True, int(points*0.5), RandomCardAttribute('paralyzes', 8)
    elif roll<=68.25:
        return True, int(points*0.25), RandomCardAttribute('off_gcd', None)
    elif roll<=74.60:
        return True, int(points*0.75), RandomCardAttribute('knockback', None)
    elif roll<=80.95:
        if is_ranged:
            return True, int(points*0.75), RandomCardAttribute('pull_towards', None)
        else:
            return False, points, None
    elif roll<=87.30:
        if not is_ranged:
            return True, int(points*0.75), RandomCardAttribute('charge_towards', None)
        else:
            return False, points, None
    elif roll<=93.65:
        return True, int(points*0.75), RandomCardAttribute('jump_back', None)
    elif roll<=96.82:
        if is_ranged:
            return True, int(points*0.65), RandomCardAttribute('projectile_spread', None)
        else:
            return False, points, None
    else:
        if is_dot and radius>0:
            return True, points, RandomCardAttribute('create_damage_zone', None)
        else:
            return False, points, None

def get_untargeted_utility_attribute(points, multiplayer, num_attributes):
    roll = random.uniform(1,100)
    if roll<=6.06:
        if num_attributes>1:
            return True, int(points*1.5), RandomCardAttribute('mp-', 44)
        else:
            return False, points, None
    elif roll<=12.12:
        return True, int(points*0.8), RandomCardAttribute('mp+', 20)
    elif roll<=13.63:
        if multiplayer:
            return True, int(points*(num_attributes-1)/num_attributes), RandomCardAttribute('aggro_all', calc_damage(int(points/num_attributes))*4*16)
        else:
            return False, points, None
    elif roll<=15.15:
        return True, int(points*(num_attributes-1)/num_attributes), RandomCardAttribute('shield', calc_damage(int(points/num_attributes)))
    elif roll<=18.18:
        if points>=70:
            return True, points-35, RandomCardAttribute('invisibility', 8)
        else:
            return False, points, None
    elif roll<=19.69:
        if points>=200:
            return True, points-100, RandomCardAttribute('invisibility+', 8)
        else:
            return False, points, None
    elif roll<=25.75:
        return True, int(points*(num_attributes-1)/num_attributes), RandomCardAttribute('heal', calc_damage(int(points/num_attributes)))
    elif roll<=31.81:
        return True, int(points*(num_attributes-1)/num_attributes), RandomCardAttribute('hot', {'healing': calc_damage(int(points/num_attributes))*2, 'time': 8})
    elif roll<=37.87:
        if num_attributes>1:
            return True, int(points*0.75), RandomCardAttribute('stealthy', None)
        else:
            return False, points, None
    elif roll<=43.93:
        return True, int(points*0.75), RandomCardAttribute('disable_mechanisms', None)
    elif roll<=50.00:
        if multiplayer:
            return True, int(points*0.75), RandomCardAttribute('aggro_divisor', 2)
        else:
            return False, points, None
    elif roll<=56.06:
        return True, int(points*0.75), RandomCardAttribute('detect_mechanisms', None)
    elif roll<=59.09:
        if num_attributes>1:
            roll2 = random.randint(1,4)
            if roll2==1:
                return True, int(points*0.9), RandomCardAttribute('trash', 1)
            elif roll2==2:
                return True, int(points*0.75), RandomCardAttribute('trash', 2)
            elif roll2==3:
                return True, int(points*0.5), RandomCardAttribute('trash', 3)
            elif roll2==4:
                return True, int(points*0.25), RandomCardAttribute('trash', 6)
        else:
            return False, points, None
    elif roll<=62.12:
        roll2 = random.randint(0,2)
        bonus_table = [100, 50, 25]
        points_mod_table = [0.5, 0.75, 0.9]
        bonus = bonus_table[roll2]
        points = int(points * points_mod_table[roll2])
        return True, points, RandomCardAttribute('damage+', {'bonus': bonus, 'duration': 12})
    elif roll<=65.15:
        roll2 = random.randint(0,2)
        bonus_table = [100, 50, 25]
        points_mod_table = [0.94, 0.97, 0.99]
        bonus = bonus_table[roll2]
        points = int(points * points_mod_table[roll2])
        element = random.choice(['piercing', 'slashing', 'bashing', 'fire', 'ice', 'acid', 'light', 'dark'])
        return True, points, RandomCardAttribute('elemental_damage+', {'bonus': bonus, 'duration': 12, 'element': element})
    elif roll<=66.66:
        if multiplayer:
            roll2 = random.randint(0,2)
            bonus_table = [100, 50, 25]
            points_mod_table = [0.5, 0.75, 0.9]
            bonus = bonus_table[roll2]
            points = int(points * points_mod_table[roll2])
            return True, points, RandomCardAttribute('all_allies_damage+', {'bonus': bonus, 'duration': 12})
        else:
            return False, points, None
    elif roll<=68.18:
        if multiplayer:
            roll2 = random.randint(0,2)
            bonus_table = [100, 50, 25]
            points_mod_table = [0.94, 0.97, 0.99]
            bonus = bonus_table[roll2]
            points = int(points * points_mod_table[roll2])
            element = random.choice(['piercing', 'slashing', 'bashing', 'fire', 'ice', 'acid', 'light', 'dark'])
            return True, points, RandomCardAttribute('all_allies_elemental_damage+', {'bonus': bonus, 'duration': 12, 'element': element})
        else:
            return False, points, None
    elif roll<=71.21:
        return True, int(points*0.8), RandomCardAttribute('mp_over_time', {'mp': 40, 'time': 8})
    elif roll<=72.72:
        if num_attributes>1:
            return True, int(points*0.85), RandomCardAttribute('usable_while_paralyzed', None)
        else:
            return False, points, None
    elif roll<=75.75:
        if num_attributes>1:
            return True, int(points*0.5), RandomCardAttribute('off_gcd', None)
        else:
            return False, points, None
    elif roll<=81.81:
        return True, int(points*0.5), RandomCardAttribute('dismiss_summon', None)
    elif roll<=87.87:
        return True, int(points*0.5), RandomCardAttribute('dismiss_tactical', None)
    elif roll<=93.93:
        return True, int(points*0.5), RandomCardAttribute('dismiss_mental', None)
    else:
        return True, int(points*0.5), RandomCardAttribute('dismiss_magical', None)

def get_ally_utility_attribute(points, multiplayer, num_attributes):
    roll = random.uniform(1,100)
    if roll<=9.87:
        if num_attributes>1:
            return True, int(points*1.5), RandomCardAttribute('mp-', 44)
        else:
            return False, points, None
    elif roll<=19.75:
        return True, int(points*0.8), RandomCardAttribute('mp+', 20)
    elif roll<=29.62:
        return True, int(points*(num_attributes-1)/num_attributes), RandomCardAttribute('heal', calc_damage(int(points/num_attributes)))
    elif roll<=39.50:
        return True, int(points*(num_attributes-1)/num_attributes), RandomCardAttribute('hot', {'healing': calc_damage(int(points/num_attributes))*2, 'time': 8})
    elif roll<=49.38:
        return True, int(points*0.75), RandomCardAttribute('remove_debuff', None)
    elif roll<=59.25:
        return True, int(points*(num_attributes-1)/num_attributes), RandomCardAttribute('shield', calc_damage(int(points/num_attributes)))
    elif roll<=61.72:
        if points>=70:
            return True, int(points*0.75), RandomCardAttribute('invisibility', 8)
        else:
            return False, points, None
    elif roll<=62.96:
        if points>=200:
            return True, int(points*0.5), RandomCardAttribute('invisibility+', 8)
        else:
            return False, points, None
    elif roll<=67.90:
        if num_attributes>1:
            return True, int(points*0.85), RandomCardAttribute('stealthy', None)
        else:
            return False, points, None
    elif roll<=72.83:
        if num_attributes>1:
            roll2 = random.randint(1,4)
            if roll2==1:
                return True, int(points*0.9), RandomCardAttribute('trash', 1)
            elif roll2==2:
                return True, int(points*0.75), RandomCardAttribute('trash', 2)
            elif roll2==3:
                return True, int(points*0.5), RandomCardAttribute('trash', 3)
            elif roll2==4:
                return True, int(points*0.25), RandomCardAttribute('trash', 6)
        else:
            return False, points, None
    elif roll<=77.77:
        roll2 = random.randint(0,2)
        bonus_table = [100, 50, 25]
        points_mod_table = [0.5, 0.75, 0.9]
        bonus = bonus_table[roll2]
        points = int(points * points_mod_table[roll2])
        return True, points, RandomCardAttribute('damage+', {'bonus': bonus, 'duration': 12})
    elif roll<=82.71:
        roll2 = random.randint(0,2)
        bonus_table = [100, 50, 25]
        points_mod_table = [0.94, 0.97, 0.99]
        bonus = bonus_table[roll2]
        points = int(points * points_mod_table[roll2])
        element = random.choice(['piercing', 'slashing', 'bashing', 'fire', 'ice', 'acid', 'light', 'dark'])
        return True, points, RandomCardAttribute('elemental_damage+', {'bonus': bonus, 'duration': 12, 'element': element})
    elif roll<=87.65:
        return True, int(points*0.8), RandomCardAttribute('mp_over_time', {'mp': 40, 'time': 8})
    elif roll<=90.12:
        if num_attributes>1:
            return True, int(points*0.85), RandomCardAttribute('usable_while_paralyzed', None)
        else:
            return False, points, None
    elif roll<=95.06:
        if num_attributes>1:
            return True, int(points*0.5), RandomCardAttribute('off_gcd', None)
        else:
            return False, points, None
    else:
        if multiplayer:
            points = int(points*0.5)
            return True, int(points*(num_attributes-1)/num_attributes), RandomCardAttribute('resurrect', calc_damage(int(points/num_attributes)))
        else:
            return False, points, None

def get_permanent_attribute(points, multiplayer, num_attributes, permanent_type):
    roll = random.uniform(1,100)
    if roll<=14.95:
        pass

def random_dot(points):
    roll = random.randint(1,100)
    if roll<=25:
        duration = 4
        points = int(points*1.5)
    elif roll<=75:
        duration = 8
        points = int(points*2)
    else:
        duration = 12
        points = int(points*2.5)
    return RandomCardAttribute('dot', {'duration': duration, 'damage': calc_damage(points)})

def calc_damage(points):
    return 0.01071428571*float(points)

def is_a_dot(points):
    roll = random.randint(1,100)
    if roll<=85:
        return points, False, 0
    else:
        roll2 = random.randint(1,100)
        if roll2<=25:
            return int(points*1.5), True, 4
        elif roll2<=75:
            return int(points*2), True, 8
        else:
            return int(points*2.5), True, 12

def generate_radius(points):
    roll = random.uniform(1,100)
    if roll<=90.0:
        return points, 0
    elif roll<=97.0:
        return int(points/1.5), 1
    elif roll<=99.0:
        return int(points/2.0), 2
    elif roll<=99.66:
        return int(points/2.5), 3
    else:
        return int(points/3.0), 4

def determine_mp_usage(points):
    roll = random.randint(1,100)
    if roll<=80:
        return int(points*1.5), 44
    elif roll<=90:
        return int(points*1.25), 22
    else:
        return int(points*2), 88

def determine_elemental_affinity(uses_mp):
    roll = random.randint(1,100)
    if not uses_mp:
        if roll<=25:
            return 'piercing'
        elif roll<=50:
            return 'slashing'
        elif roll<=75:
            return 'bashing'
        elif roll<=79:
            return 'fire'
        elif roll<=83:
            return 'ice'
        elif roll<=87:
            return 'acid'
        elif roll<=91:
            return 'light'
        elif roll<=95:
            return 'dark'
        else:
            return 'none'
    else:
        if roll<=16:
            return 'fire'
        elif roll<=32:
            return 'ice'
        elif roll<=48:
            return 'acid'
        elif roll<=64:
            return 'light'
        elif roll<=80:
            return 'dark'
        elif roll<=85:
            return 'piercing'
        elif roll<=90:
            return 'slashing'
        elif roll<=95:
            return 'bashing'
        else:
            return 'none'

if __name__=='__main__':
    level = 1
    print level, random_card(level)
