import random

# Each entry in this table corresponds to a damage base, between 1 and 28.
# A damage base is XdY+Z. Dice is X, sides is Y, and bonus is Z.
# They also have a flat average that can be used.
db_table = {
    1: {'dice': 1, 'sides': 6, 'bonus': 1, 'set': 5},
    2: {'dice': 1, 'sides': 6, 'bonus': 3, 'set': 7},
    3: {'dice': 1, 'sides': 6, 'bonus': 5, 'set': 9},
    4: {'dice': 1, 'sides': 8, 'bonus': 6, 'set': 11},
    5: {'dice': 1, 'sides': 8, 'bonus': 8, 'set': 13},
    6: {'dice': 2, 'sides': 6, 'bonus': 8, 'set': 15},
    7: {'dice': 2, 'sides': 6, 'bonus': 10, 'set': 17},
    8: {'dice': 2, 'sides': 8, 'bonus': 10, 'set': 19},
    9: {'dice': 2, 'sides': 10, 'bonus': 10, 'set': 21},
    10: {'dice': 3, 'sides': 8, 'bonus': 10, 'set': 24},
    11: {'dice': 3, 'sides': 10, 'bonus': 10, 'set': 27},
    12: {'dice': 3, 'sides': 12, 'bonus': 10, 'set': 30},
    13: {'dice': 4, 'sides': 10, 'bonus': 10, 'set': 35},
    14: {'dice': 4, 'sides': 10, 'bonus': 15, 'set': 40},
    15: {'dice': 4, 'sides': 10, 'bonus': 20, 'set': 45},
    16: {'dice': 5, 'sides': 10, 'bonus': 20, 'set': 50},
    17: {'dice': 5, 'sides': 12, 'bonus': 25, 'set': 60},
    18: {'dice': 6, 'sides': 12, 'bonus': 25, 'set': 65},
    19: {'dice': 6, 'sides': 12, 'bonus': 30, 'set': 70},
    20: {'dice': 6, 'sides': 12, 'bonus': 35, 'set': 75},
    21: {'dice': 6, 'sides': 12, 'bonus': 40, 'set': 80},
    22: {'dice': 6, 'sides': 12, 'bonus': 45, 'set': 85},
    23: {'dice': 6, 'sides': 12, 'bonus': 50, 'set': 90},
    24: {'dice': 6, 'sides': 12, 'bonus': 55, 'set': 95},
    25: {'dice': 6, 'sides': 12, 'bonus': 60, 'set': 100},
    26: {'dice': 7, 'sides': 12, 'bonus': 65, 'set': 110},
    27: {'dice': 8, 'sides': 12, 'bonus': 70, 'set': 120},
    28: {'dice': 8, 'sides': 12, 'bonus': 80, 'set': 130}
}

#Each entry in the list is the experience it takes to reach a certain level. The training function will step through this list to find the current level of the pokemon.
xp_table = {
    0: 1,
    10: 2,
    20: 3,
    30: 4,
    40: 5,
    50: 6,
    60: 7,
    70: 8,
    80: 9,
    90: 10,
    110: 11,
    135: 12,
    160: 13,
    190: 14,
    220: 15,
    250: 16,
    285: 17,
    320: 18,
    360: 19,
    400: 20,
    460: 21,
    530: 22,
    600: 23,
    670: 24,
    745: 25,
    820: 26,
    900: 27,
    990: 28,
    1075: 29,
    1165: 30,
    1260: 31,
    1355: 32,
    1455: 33,
    1555: 34,
    1660: 35,
    1770: 36,
    1880: 37,
    1995: 38,
    2110: 39,
    2230: 40,
    2355: 41,
    2480: 42,
    2610: 43,
    2740: 44,
    2875: 45,
    3015: 46,
    3155: 47,
    3300: 48,
    3445: 49,
    3645: 50,
    3850: 51,
    4060: 52,
    4270: 53,
    4485: 54,
    4705: 55,
    4930: 56,
    5160: 57,
    5390: 58,
    5625: 59,
    5865: 60,
    6110: 61,
    6360: 62,
    6610: 63,
    6865: 64,
    7125: 65,
    7390: 66,
    7660: 67,
    7925: 68,
    8205: 69,
    8485: 70,
    8770: 71,
    9060: 72,
    9350: 73,
    9645: 74,
    9945: 75,
    10250: 76,
    10560: 77,
    10870: 78,
    11185: 79,
    11505: 80,
    11910: 81,
    12320: 82,
    12735: 83,
    13155: 84,
    13580: 85,
    14010: 86,
    14445: 87,
    14885: 88,
    15330: 89,
    15780: 90,
    16235: 91,
    16695: 92,
    17160: 93,
    17630: 94,
    18105: 95,
    18585: 96,
    19070: 97,
    19560: 98,
    20055: 99,
    20555: 100
}

# Every level is a multiple of five.
# To find the current level, subtract 1 until you get to a multiple of 5, then check against the table and subtract 5 until you find a level marker.
def get_level(xp):
    while xp % 5 > 0:
        xp -= 1
    while not xp in xp_table:
        xp -= 5
    return xp_table[xp]

# Similarly, to find the next level, add 1 until you get to a multiple of 5, then check against the table and add 5 until you find a level marker. Start by adding 1 exp in case you're exactly at a level mark.
def next_level(xp):
    ret = 1
    xp += 1
    while xp % 5 > 0:
        xp += 1
        ret += 1
    while not xp in xp_table:
        xp += 5
        ret += 5
    return ret

# A 2d array for natures, sorted by which stats are raised and lowered.
nature_table = [
    ["Composed", "Cuddly", "Distracted", "Proud", "Decisive", "Patient"], # HP+
    ["Desperate", "Hardy", "Lonely", "Adamant", "Naughty", "Brave"], # Attack+
    ["Stark", "Bold", "Docile", "Impish", "Lax", "Relaxed"], # Defense+
    ["Curious", "Modest", "Mild", "Bashful", "Rash", "Quiet"], # Sp. Attack+
    ["Dreamy", "Calm", "Gentle", "Careful", "Quirky", "Sassy"], # Sp. Defense+
    ["Skittish", "Timid", "Hasty", "Jolly", "Naive", "Serious"] # Speed+
] # HP-, Attack-, Defense-, Sp. Attack-, Sp. Defense-, Speed -

# this functions will randomly return a nature from the above table by rolling 2d6.
def random_nature():
    raised = random.randint(0,5)
    lowered = random.randint(0,5)
    return nature_table[raised][lowered]

type_table = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fight", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Steel", "Dark", "Fairy"]

def random_type():
    return random.choice(type_table)