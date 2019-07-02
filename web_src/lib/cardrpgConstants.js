// Config data
export var url = 'ws://' + location.host + '/mainsocket'

// Others
export var classDescriptions = {
  'Archer': 'Possesses ranged attacks and the ability to extend the chain timer.',
  'Inferno Mage': 'Wields a weak MP-using ranged attack with an area of effect and the ability to artificially boost chains.',
  'Balance Mage': 'Uses MP-consuming ranged Poison Bolts to kill the enemies with damage over time, and can consume negative status effects to restore MP.',
  'Paladin': 'Better in multiplayer. Has a super-high damage melee attack that consumes MP. Also has a weak melee attack that draws enemy attention.',
  'Fighter': 'Uses a generic average melee attack. Also has a weaker melee attack that provides a damage shield after it hits.',
  'Cleric': 'Better in multiplayer. Uses a generic average melee attack. Also has a healing spell that costs MP.'
}

export var mobColors = {
  'Goblin': 'green',
  'Goblin Archer': '#00FF88',
  'Kobold': 'orange',
  'Wolf': '#BBBBBB',
  'Blink Dog': '#888800',
  'Cave Cheetah': 'yellow',
  'Ghoul': '#008800',
  'Giant Spider': '#666666',
  'Land Squid': 'white',
  'Young Dragon': 'red',
  'Imp': '#880000',
  'Ghost': 'white',
  'Ogre': '#88FF00',
  'Cockatrice': '#CCCCCC',
  'Fire Elemental': '#880000',
  'Ankheg': '#884400',
  'Animated Statue': 'grey',
  'Phantom Fungus': 'black',
  'Ochre Jelly': '#CC7722',
  'Troll': '#21B6A8',
  'Warlock': 'purple',
  'Spore Lord': 'lightgrey',
  'Sporeling': 'lightgrey'
}

export var mobEyeColors = {
  'Cave Cheetah': 'black',
  'Ghoul': 'red',
  'Giant Spider': 'red',
  'Land Squid': 'black',
  'Young Dragon': 'black',
  'Ghost': 'red',
  'Ogre': 'red',
  'Cockatrice': 'red',
  'Fire Elemental': '#880000',
  'Ankheg': 'black',
  'Phantom Fungus': 'black',
  'Ochre Jelly': '#CC7722',
  'Spore Lord': 'red',
  'Sporeling': 'red'
}

export var mobDetails = {
  'Goblin': '',
  'Goblin Archer': 'Ranged attacker',
  'Kobold': '',
  'Wolf': 'Fast',
  'Blink Dog': 'Teleports',
  'Cave Cheetah': 'Very fast',
  'Ghoul': 'Paralyzes',
  'Giant Spider': 'Poisons',
  'Land Squid': 'Blinds',
  'Young Dragon': 'Breathes fire',
  'Imp': 'Ranged attacker, summons imps',
  'Ghost': 'Ignores walls',
  'Ogre': 'Large attack radius',
  'Cockatrice': 'Petrifies (death)',
  'Fire Elemental': 'Exudes fire',
  'Ankheg': 'Spits acid',
  'Animated Statue': '',
  'Phantom Fungus': 'Invisible',
  'Ochre Jelly': 'Splits when attacked',
  'Troll': 'Regenerates',
  'Warlock': 'Curses',
  'Spore Lord': 'Infects deck',
  'Sporeling': ''
}

export var mobClassDescriptions = {
  0: '',
  1: 'Strong',
  2: 'Elite',
  3: 'Miniboss',
  4: 'Boss'
}

export var mobClassDescriptions2 = {
  0: 'Normal',
  1: 'Strong',
  2: 'Elite',
  3: 'Miniboss',
  4: 'Boss'
}

export var cardRange = {
  0: 8,
  2: 8,
  4: 8,
  6: 1,
  7: 1,
  8: 1,
  9: 1,
  11: 8,
  13: 8,
  14: 2,
  15: 3,
  16: 1,
  18: 8,
  20: 8,
  22: 8,
  23: 8,
  24: 8,
  25: 8,
  26: 1,
  27: 1,
  28: 8,
  30: 8,
  33: 8,
  35: 1,
  38: 1,
  40: 8,
  41: 8,
  42: 1,
  46: 8,
  47: 8,
  50: 1,
  56: 8
}

export var cardRangeType = {
  2: 'aoe2',
  14: 'radius',
  15: 'radius',
  16: 'radius',
  20: 'radius',
  28: 'radius',
  30: 'radius',
  33: 'radius',
  41: 'aoe4',
  56: 'radius'
}

export var cardText = ['Shoot\nRange: 8\nDoes 12 damage', 'Keen Perception\nUsable while paralyzed.\nIn combat only.\nIncreases chain timer by\n2.5 seconds', 'Fireball\nMP: 44\nRange: 8\nAoE: 2\nDoes 9 damage', 'Lorechannel\nUsable while paralyzed.\nIncreases chain bonus by\n1 if chain bonus is 2-3', 'Poison Bolt\nMP: 44\nRange: 8\nDoes 36 damage over 8\nseconds', 'Aura Cleanse\nFriendly Target\nRemoves the debuff with\nthe longest timer. If a\ndebuff was removed,\nrestores 50% of your MP.', 'Smite\nMP: 44\nRange: 1\nDoes 24 damage', 'Shimmerstrike\nRange: 1\nDoes 8 damage, quadruple\naggro', 'Strike\nRange: 1\nDoes 16 damage', 'Sword and Board\nRange: 1\nDoes 8 damage, prevents\nthe next 14 damage you\nwould take. Does not\nstack.', 'Lesser Healing\nMP: 44\nFriendly Target\nRestores 28 HP', 'Firebolt\nMP: 44\nRange: 8\nDoes 10 damage,\n24 damage over 8\nseconds.', 'Invisibility\nMP: 88\nUsable only outside\ncombat. Caster is invisible\nfor 25 seconds or until\nthey attack.', 'Shadow Bomb\nMP: 44\nRange: 8\nStealthy, Backstabs\nFive seconds after it hits,\ndoes 18 damage.', 'Holy Aura\nMP: 44\nAoE: 2\nCauses 11 aggro and\ndmg +15% for 10 seconds\nto all nearby enemies.', 'Lightning Cowl\nMP: 88\nAoE: 3\nDoes 15 damage', 'Ledgerdemain\nDisables nearby\nmechanisms and reduces\naggro by 50%', 'Blessing\nMP: 44\nHeals target for 24 health,\nincreases chain bonus by\n1 if chain bonus is\ncurrently 2-3.', 'Cinder Toss\nMP: 22\nRange: 8\nDoes 26 damage', 'Shout\nIncreases aggro with all\nnearby monsters by 21', 'Caution\nUsable only outside\ncombat. Triggers stealth\nfor 10 seconds and\ndetects nearby\nmechanisms.', 'Augury\nMP: 44\nIncreases chain timer by\n~9.5 seconds', 'Find Weakness\nRange: 8\nIncreases damage to\ntarget by 75% for 10\nseconds', 'Immolate\nMP: 100 or 176\nRange: 8\nDoes 35 or 56 damage', 'Fusillade\nRange: 8\nDoes 30 damage', 'Vexing Shot\nRange: 8\nDoes 15 damage,\nquadruple aggro', 'Essence Theft\nRange: 1\nDoes 28 damage. If it hits,\nadd a 3 chain to\ncompleted chains.', 'Distract\nRange: 1\nIncreases damage to\ntarget by 70% for 10\nseconds, prevents\nthe next 65 damage\nthat target would deal.', 'Make Right\nMP: 44\nHeals all allies for 25\nhealth. Disables all\nmechanisms in sight\neven if undetected.', 'Focus\nTrash 2\nOn buy, trash this card.', 'Noisy Search\nDetects all mechanisms\nin sight and generate\nwindow.tileSize aggro.', 'War Blessing\nMP: 44\nDoubles all ally damage\nfor 10 seconds.', 'Shadowmeld\nMP: 44\nBecome invisible for 15\nseconds even if in combat.\nDrop all aggro. Invisibility\npersists while attacking.', 'Perfect Knowledge\nMP: 44\nDetects all nearby\nmechanisms and doubles\nyour damage for 10\nseconds.', 'Tranquil Meditation\nUsable while paralyzed.\nDrops all aggro and\nincreases chain bonus\nby 2 if chain bonus is\n1 or higher.', 'Kindling Strike\nMP: 22\nRange: 1\nIncrease damage target\ntakes by 250% for 10\nseconds.', 'Greater Invisibility\nMP: 88\nBecome invisible for 15\nseconds. Invisibility\npersists when attacking.\nMP regen x2.', 'Void Rage\nTrash 2\nDeal double damage for\n10 seconds', 'Uncanny Expertise\nRange: 1\nDeals window.tileSize damage.\nIf it hits, adds a chain\nof 2 to the completed\nchains. Also increases\nchain timer by 5 seconds.', 'Breaker of Chains\nMP: 44\nUsable while paralyzed.\nRemove all status effects\nfrom everyone. Drop all\naggro. MP regen +25% for\n3 minutes.', 'Shadow Volley\nRange: 8\nBackstabs\nDoes 34 damage. Three\nseconds after attacking, you will\nbecome hidden even if in\ncombat, lasting 18 sec.\nAttacking will break stealth.', 'Star Breach\nTrash 5\nMP: 88\nRange: 8\nAoE: 4\nDeals 24 damage and 24\ndamage over 8 seconds.', 'Backstab\nRange: 1\nBackstabs\nDeals 22 damage', 'Sanctuary\nReduces aggro by 35%\nand increases MP regen\nby 20% for 10 seconds.', 'Aether Channel\nMP regen +60% for 10\nseconds', 'Ancient Knowledge\nTrash 1\nMP regen +40% for 10\nseconds.', 'Roast\nMP: 44\nRange: 8\nDeals 63 damage.', 'Halt and Catch Fire\nMP: 44\nDeals 88 damage over 8\nseconds and paralyzes\ntarget.', 'Second Wind\nHeals self for 35 health.', 'Aether Charge\nMP: 44\nBoosts your damage\nby 75% for 10 seconds.', 'Honed Strike\nTrash 1\nRange: 1\nDeals 20 damage.', 'Resurrection\nMP: 100\nResurrects a dead ally with\n1 health.', 'Healing Potion\nOne Use\nHeal self for 28 HP.', 'Curse\nMust use first.\nDoes nothing.', 'Sporeling\nMust use first.\nSpawns a Sporeling.', 'Karmic Aura\nAbsorbs 25% of damage\nwhile in hand.\nUse to deal 10% of\ndamage absorbed.', 'Thief\'s Expertise\nDetects traps\nwhile in hand.\nUse to disarm traps\nand unlock chests\nand doors.']

export var cardNames = ['Shoot', 'Keen Perception', 'Fireball', 'Lorechannel', 'Poison Bolt', 'Aura Cleanse', 'Smite', 'Shimmerstrike', 'Strike', 'Sword and Board', 'Lesser Healing', 'Firebolt', 'Invisibility', 'Shadow Bomb', 'Holy Aura', 'Lightning Cowl', 'Ledgerdemain', 'Blessing', 'Cinder Toss', 'Shout', 'Caution', 'Augury', 'Find Weakness', 'Immolate', 'Fusillade', 'Vexing Shot', 'Essence Theft', 'Distract', 'Make Right', 'Focus', 'Noisy Search', 'War Blessing', 'Shadowmeld', 'Perfect Knowledge', 'Tranquil Meditation', 'Kindling Strike', 'Greater Invisibility', 'Void Rage', 'Uncanny Expertise', 'Breaker of Chains', 'Shadow Volley', 'Star Breach', 'Backstab', 'Sanctuary', 'Aether Channel', 'Ancient Knowledge', 'Roast', 'Halt and Catch Fire', 'Second Wind', 'Aether Charge', 'Honed Strike', 'Resurrection', 'Healing Potion', 'Curse', 'Sporeling', 'Karmic Aura', 'Thief\'s Expertise']

export var colors = {
  'damage': 'gray',
  'damageFG': 'white',
  'mpDamage': 'DarkBlue',
  'mpDamageFG': 'white',
  'healing': 'green',
  'healingFG': 'white',
  'mpRegen': 'LightBlue',
  'mpRegenFG': 'black',
  'buff': 'LightGreen',
  'buffFG': 'black',
  'curse': 'purple',
  'curseFG': 'white',
  'handEffect': 'cyan',
  'handEffectFG': 'black'
}

export var backgroundColors = [colors.damage, colors.buff, colors.mpDamage, colors.buff, colors.mpDamage, colors.buff, colors.mpDamage, colors.damage, colors.damage, colors.damage, colors.healing, colors.mpDamage, colors.buff, colors.mpDamage, colors.buff, colors.mpDamage, colors.buff, colors.healing, colors.mpDamage, colors.buff, colors.buff, colors.buff, colors.buff, colors.mpDamage, colors.damage, colors.damage, colors.damage, colors.buff, colors.healing, colors.buff, colors.buff, colors.buff, colors.buff, colors.buff, colors.buff, colors.buff, colors.buff, colors.buff, colors.damage, colors.buff, colors.damage, colors.mpDamage, colors.damage, colors.mpRegen, colors.mpRegen, colors.mpRegen, colors.mpDamage, colors.mpDamage, colors.healing, colors.buff, colors.damage, colors.healing, colors.healing, colors.curse, colors.curse, colors.handEffect, colors.handEffect]

export var textColors = [colors.damageFG, colors.buffFG, colors.mpDamageFG, colors.buffFG, colors.mpDamageFG, colors.buffFG, colors.mpDamageFG, colors.damageFG, colors.damageFG, colors.damageFG, colors.healingFG, colors.mpDamageFG, colors.buffFG, colors.mpDamageFG, colors.buffFG, colors.mpDamageFG, colors.buffFG, colors.healingFG, colors.mpDamageFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.mpDamageFG, colors.damageFG, colors.damageFG, colors.damageFG, colors.buffFG, colors.healingFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.buffFG, colors.damageFG, colors.buffFG, colors.damageFG, colors.mpDamageFG, colors.damageFG, colors.mpRegenFG, colors.mpRegenFG, colors.mpRegenFG, colors.mpDamageFG, colors.mpDamageFG, colors.healingFG, colors.buffFG, colors.damageFG, colors.healingFG, colors.healingFG, colors.curseFG, colors.curseFG, colors.handEffectFG, colors.handEffectFG]

export var fontSize = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 13, 15, 15, 15, 15, 15, 15, 15, 15, 14, 15, 13, 13, 12, 13, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]

export var debuffColors = ['yellow', 'purple', 'grey', 'red', 'blue', 'blue', 'green', 'blue', 'blue', 'blue', 'red']


export var cardXpTable = {
  0: 0,
  1: 0,
  2: 0,
  3: 0,
  4: 0,
  5: 0,
  6: 0,
  7: 0,
  8: 0,
  9: 0,
  10: 0,
  11: 1,
  12: 1,
  13: 1,
  14: 1,
  15: 1,
  16: 2,
  17: 2,
  18: 2,
  19: 2,
  20: 2,
  21: 3,
  22: 3,
  23: 3,
  24: 3,
  25: 3,
  26: 4,
  28: 4,
  27: 4,
  29: 4,
  30: 4,
  31: 5,
  32: 5,
  33: 5,
  34: 5,
  35: 5,
  36: 6,
  37: 6,
  38: 6,
  39: 7,
  40: 7,
  41: 8,
  42: 2,
  43: 1,
  44: 2,
  45: 3,
  46: 4,
  47: 5,
  48: 1,
  49: 2,
  50: 3,
  51: 4,
  52: 0,
  53: 0,
  54: 0,
  55: 3,
  56: 7
}

export var hoverDescriptions = {
  'W': 'A wall.',
  'X': 'A wall.',
  'D': 'A door.',
  'O': 'A locked door.',
  'R': 'A trapped door.',
  'C': 'A treasure chest.',
  'H': 'A locked treasure chest.',
  'E': 'A trapped treasure chest.',
  '>': 'Stairs leading downwards. (> to descend)',
  '<': 'Stairs leading upwards. (< to ascend)',
  'f': 'Fire.',
  'a': 'Acid.',
  '@': 'A statue.',
  'F': 'A fountain (q to drink from it).',
  'Q': 'A depleted fountain.',
  'T': 'A trap.',
  ' ': 'Floor.',
  'P': 'A shop. (b to buy)'
}
