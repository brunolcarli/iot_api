

def translate_ldr_value(value):
    if value < 40:
        return 'Dark'
    elif 40 <= value < 800:
        return 'Dim'
    elif 800 <= value < 2000:
        return 'Light'
    elif 2000 <= value < 3200:
        return 'Bright'
    else:
        return 'Very bright'
