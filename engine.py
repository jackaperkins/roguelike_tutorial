import tcod as libtcod

from input_handlers import handle_keys
from entity import Entity, get_blocking_entities_at_location
from render_functions import render_all, clear_all
from map_objects.game_map import GameMap
from game_states import GameStates
from fov_functions import initialize_fov, recompute_fov

screen_width = 80
screen_height = 45
map_width = 80
map_height = 45

fov_algorithm = 0
fov_light_walls = True
fov_radius = 100

key = libtcod.Key()
mouse = libtcod.Mouse()

room_max_size = 10
room_min_size = 6
max_rooms = 30
max_monsters_per_room = 3




class Engine():
    game_map = None
    game_state = GameStates.PLAYERS_TURN

    def main(self):
        player = Entity(0, 0, '@', libtcod.white, 'Player', blocks=True)
        entities = [player]

        libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

        libtcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

        con = libtcod.console_new(screen_width, screen_height)

        self.generate_map(player,  entities, max_monsters_per_room)
        fov_recompute = True
        fov_map = initialize_fov(self.game_map)

        while not libtcod.console_is_window_closed():
            clear_all(con, entities)

            # get input
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
            action = handle_keys(key)

            move = action.get('move')
            exit = action.get('exit')
            fullscreen = action.get('fullscreen')

            if move and self.game_state == GameStates.PLAYERS_TURN:
                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                if not self.game_map.is_blocked(player.x + dx, player.y + dy):
                    if not self.game_map.is_blocked(destination_x, destination_y):
                        target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                        if target:
                            print('You kick the ' + target.name + ' in the shins, much to its annoyance!')
                        else:
                            player.move(dx, dy)

                            fov_recompute = True
                        self.game_state = GameStates.ENEMY_TURN

            if exit:
                return True

            if action.get('regenerate'):
                self.generate_map(player)

            if fullscreen:
                libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

            if self.game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity != player:
                        print('The ' + entity.name + ' ponders the meaning of its existence.')

                self.game_state = GameStates.PLAYERS_TURN

            if fov_recompute:
                recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

            render_all(con, entities, self.game_map, fov_map, fov_recompute, screen_width, screen_height)

            libtcod.console_flush()

    def generate_map(self, player,  entities, max_monsters_per_room):
        self.game_map = GameMap(map_width, map_height)
        self.game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)


if __name__ == '__main__':
     engine = Engine()
     engine.main()
