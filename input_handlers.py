import tcod as libtcod

def handle_keys(key):
    # Movement keys
    key_char = chr(key.c)

    if key.vk == libtcod.KEY_UP or key_char == 'u':
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'm':
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'k':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'i':
        return {'move': (1, -1)}
    elif key_char == 'n':
        return {'move': (-1, 1)}
    elif key_char == ',':
        return {'move': (1, 1)}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    if key.vk == libtcod.KEY_SPACE:
        return {'regenerate': True}

    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}
