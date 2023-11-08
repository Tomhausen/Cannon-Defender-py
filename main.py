@namespace
class SpriteKind:
    cannon = SpriteKind.create()
    trap = SpriteKind.create()

# variables
health = 0
spawn_frequency = 7200
info.set_score(500)
item_selected = "cannon"

# setup
scene.set_tile_map_level(assets.tilemap("level"))
scene.center_camera_at(96, 64)

# sprites
selector = sprites.create(assets.image("selector"), SpriteKind.player)
selector.set_stay_in_screen(True)
selector.z = 5
grid.snap(selector)
grid.move_with_buttons(selector)

def make_level_text(level, cannon: Sprite):
    level_text = textsprite.create(str(level), 15, 1)
    level_text.set_position(cannon.x - 5, cannon.y + 4)
    level_text.z = 4
    sprites.set_data_sprite(cannon, "level_text", level_text)

def upgrade_cannon(cannon: Sprite):
    limit = sprites.read_data_number(cannon, "time_between_fire")
    limit = Math.constrain(limit - 20, 50, 500)
    sprites.set_data_number(cannon, "time_between_fire", limit)
    sprites.change_data_number_by(cannon, "level", 1)
    sprites.read_data_sprite(cannon, "level_text").destroy()
    make_level_text(sprites.read_data_number(cannon, "level"), cannon)

def buy_cannon(tile: tile.Location):
    if tiles.tile_at_location_equals(tile, assets.tile("empty")):
        cannon = sprites.create(assets.image("cannon"), SpriteKind.cannon)
        tiles.place_on_tile(cannon, tile)
        tiles.set_tile_at(tile, assets.tile("placed"))
        cannon.z = 3
        sprites.set_data_number(cannon, "frames_since_fired", 390)
        sprites.set_data_number(cannon, "time_between_fire", 400)
        sprites.set_data_number(cannon, "level", 1)
        make_level_text(1, cannon)
        info.change_score_by(-100)

def buy_trap(tile: tile.Location):
    if tiles.tile_at_location_equals(tile, assets.tile("empty")):
        trap = sprites.create(assets.image("lava"), SpriteKind.trap)
        tiles.place_on_tile(trap, tile)
        trap.z = -1
        tiles.set_tile_at(tile, assets.tile("placed"))
        info.change_score_by(-50)

def interact():
    if info.score() < 100:
        return
    tile = selector.tilemap_location()
    cannons = spriteutils.get_sprites_within(SpriteKind.cannon, 1, selector)
    if tiles.tile_at_location_equals(tile, assets.tile("placed")):
        info.change_score_by(-100)
        upgrade_cannon(cannons[0])
    else:
        if item_selected == "cannon": 
            buy_cannon(tile) 
        elif item_selected == "trap": 
            buy_trap(tile)
controller.A.on_event(ControllerButtonEvent.PRESSED, interact)

def swap_item(): 
    global item_selected
    if item_selected == "cannon":
        item_selected = "trap"
    elif item_selected == "trap":
        item_selected = "cannon"
controller.B.on_event(ControllerButtonEvent.PRESSED, swap_item)

def hit(cannon_ball, enemy):
    bar = statusbars.get_status_bar_attached_to(StatusBarKind.enemy_health, enemy) # 
    bar.value -= 1 #
    # sprites.change_data_number_by(enemy, "hp", -1)
    # if sprites.read_data_number(enemy, "hp") < 1:
    #     enemy.destroy()
    #     info.change_score_by(100)
    cannon_ball.destroy()
sprites.on_overlap(SpriteKind.projectile, SpriteKind.enemy, hit)

def destroy_cannon(cannon, enemy):
    tiles.set_tile_at(cannon.tilemap_location(), assets.tile("empty"))
    sprites.read_data_sprite(cannon, "level_text").destroy()
    cannon.destroy()
    enemy.destroy()
sprites.on_overlap(SpriteKind.cannon, SpriteKind.enemy, destroy_cannon)

def use_trap(enemy, trap):
    tiles.set_tile_at(trap.tilemap_location(), assets.tile("empty"))
    trap.destroy()
    bar = statusbars.get_status_bar_attached_to(StatusBarKind.enemy_health, enemy) #
    bar.value -= 1 #
    # sprites.change_data_number_by(enemy, "hp", -1)
    # if sprites.read_data_number(enemy, "hp") < 1:
    #     enemy.destroy()
sprites.on_overlap(SpriteKind.enemy, SpriteKind.trap, use_trap)

def on_zero(bar): # 
    info.change_score_by(100)
    enemy = bar.sprite_attached_to()
    enemy.destroy()
    bar.destroy()
statusbars.on_zero(StatusBarKind.enemy_health, on_zero)

def game_over():
    game.over(False)
scene.on_overlap_tile(SpriteKind.enemy, assets.tile("game over"), game_over)

def difficulty_increase():
    global health, spawn_frequency
    health = Math.constrain(health + 1, 0, 20)
    spawn_frequency = Math.constrain(spawn_frequency - 100, -200, 10000)
game.on_update_interval(20000, difficulty_increase)

def spawn_enemy():
    enemy = sprites.create(assets.image("ghost"), SpriteKind.enemy)
    tiles.place_on_random_tile(enemy, assets.tile("spawn"))
    enemy.vx = -7
    # sprites.set_data_number(enemy, "hp", health)
    bar = statusbars.create(16, 4, StatusBarKind.enemy_health) #
    bar.max = health #
    bar.value = health #
    bar.set_color(4, 2)
    bar.attach_to_sprite(enemy) #
    timer.after(spawn_frequency, spawn_enemy)
# spawn_enemy()
timer.after(100, spawn_enemy) # 

def fire(cannon: Sprite):
    ball = sprites.create(assets.image("cannon ball"), SpriteKind.projectile)
    ball.set_position(cannon.x + 4, cannon.y)
    ball.z = 0
    ball.set_velocity(50, 0)
    ball.set_flag(SpriteFlag.AUTO_DESTROY, True)
    ball.set_flag(SpriteFlag.STAY_IN_SCREEN, False)
    sprites.set_data_number(cannon, "frames_since_fired", 0)

def fire_control():
    for cannon in sprites.all_of_kind(SpriteKind.cannon):
        sprites.change_data_number_by(cannon, "frames_since_fired", 1)
        count = sprites.read_data_number(cannon, "frames_since_fired")
        if count > sprites.read_data_number(cannon, "time_between_fire"):
            fire(cannon)

def tick():
    fire_control()
game.on_update(tick)
