import tcod as tcod

from input_handlers import handle_keys
from entity import Entity, get_blocking_entities_at_location
from render_functions import render_all, clear_all, RenderOrder
from map_objects.game_map import GameMap
from game_states import GameStates
from fov_functions import initialize_fov, recompute_fov
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from game_messages import MessageLog,Message
import constants

screen_width = 80
screen_height = 50

bar_width = 20
panel_height = 7
panel_y = screen_height - panel_height

message_x = bar_width + 2
message_width = screen_width - bar_width - 2
message_height = panel_height - 1

map_width = 80
map_height = 43

fov_algorithm = 0
fov_light_walls = True
fov_radius = 100

message_log = MessageLog(message_x, message_width, message_height)

key = tcod.Key()
mouse = tcod.Mouse()

room_max_size = 10
room_min_size = 6
max_rooms = 30
max_monsters_per_room = 3




class Engine():
    game_map = None
    game_state = GameStates.PLAYERS_TURN

    def main(self):
        fighter_component = Fighter(hp=30, defense=2, power=5)
        player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component)
        entities = [player]

        tcod.console_set_custom_font('terminal12x12_gs_ro.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW)

        tcod.console_init_root(screen_width, screen_height, 'tcod tutorial revised', False)

        con = tcod.console_new(screen_width, screen_height)
        panel = tcod.console_new(screen_width, panel_height)

        self.generate_map(player,  entities, max_monsters_per_room)
        fov_recompute = True
        fov_map = initialize_fov(self.game_map)

        while not tcod.console_is_window_closed():
            clear_all(con, entities)

            # get input
            tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)
            action = handle_keys(key)

            move = action.get('move')
            exit = action.get('exit')
            fullscreen = action.get('fullscreen')

            player_turn_results = []

            if move and self.game_state == GameStates.PLAYERS_TURN:
                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                if not self.game_map.is_blocked(player.x + dx, player.y + dy):
                    if not self.game_map.is_blocked(destination_x, destination_y):
                        target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                        if target:
                            attack_results = player.fighter.attack(target)
                            player_turn_results.extend(attack_results)
                        else:
                            player.move(dx, dy)

                            fov_recompute = True
                        self.game_state = GameStates.ENEMY_TURN

            if exit:
                return True

            if action.get('regenerate'):
                self.generate_map(player)

            if fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            for player_turn_result in player_turn_results:
                message = player_turn_result.get('message')
                dead_entity = player_turn_result.get('dead')

                if message:
                    message_log.add_message(message)

                if dead_entity:
                    if dead_entity == player:
                        message, self.game_state = kill_player(dead_entity)
                    else:
                        message = kill_monster(dead_entity)

                    message_log.add_message(message)

            if self.game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity.ai:
                        enemy_turn_results = entity.ai.take_turn(player, fov_map, self.game_map, entities)

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get('message')
                            dead_entity = enemy_turn_result.get('dead')

                            if message:
                                message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == player:
                                    message, self.game_state = kill_player(dead_entity)
                                else:
                                    message = kill_monster(dead_entity)

                                message_log.add_message(message)

                                if self.game_state == GameStates.PLAYER_DEAD:
                                    break

                            if self.game_state == GameStates.PLAYER_DEAD:
                                break

                    else:
                        self.game_state = GameStates.PLAYERS_TURN

            if fov_recompute:
                recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

            render_all(con, panel, entities, player, self.game_map, fov_map, fov_recompute, message_log, screen_width,
                       screen_height, bar_width, panel_height, panel_y, constants.COLORS)

            tcod.console_flush()

    def generate_map(self, player,  entities, max_monsters_per_room):
        self.game_map = GameMap(map_width, map_height)
        self.game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)


if __name__ == '__main__':
     engine = Engine()
     engine.main()
