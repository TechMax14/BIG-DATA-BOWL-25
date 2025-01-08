# Constants for fluent model training

RUN_PASS_DICT = {
    'run': 0,
    'pass': 1,
}



MOTION_CAT_DICT = {
    'no motion': 0,
    'single shift': 1,
    'single motion': 2,
    'single combined': 3,
    'multi shift': 4,
    'multi motion': 5,  
    'multi combined': 6,  
}

OFFENSIVE_FORMATION_DICT = {
    'EMPTY': 0,           # Typically no running back, wide receivers spread out.
    'I_FORM': 1,          # A formation where the QB is under center with the FB and RB behind him.
    'JUMBO': 2,           # Heavy personnel with more tight ends or linemen on the field.
    'PISTOL': 3,          # QB is in a position between the Shotgun and Under Center, with RB behind him.
    'SHOTGUN': 4,         # QB stands a few yards behind the center, typically used in passing.
    'SINGLEBACK': 5,      # One running back behind the QB, no fullback.
    'WILDCAT': 6,         # A formation where the running back lines up to take the snap directly.
    'KNEEL': 7              # For plays where the QB kneels the ball  
}


REC_ALIGNMENT_DICT = {
    '0x0': 0,
    '1x0': 1,
    '1x1': 2,
    '2x0': 3,
    '2x1': 4,
    '2x2': 5,
    '3x0': 6,
    '3x1': 7,
    '3x2': 8,
    '3x3': 9,
    '4x1': 10,
    '4x2': 11,
    'NaN': 12
}
