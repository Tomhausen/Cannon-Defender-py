namespace SpriteKind {
    export const cannon = SpriteKind.create()
    export const trap = SpriteKind.create()
}

// 
//  variables
let health = 0
let spawn_frequency = 7200
info.setScore(500)
let item_selected = "cannon"
// 
//  setup
scene.setTileMapLevel(assets.tilemap`level`)
scene.centerCameraAt(96, 64)
//  sprites
let selector = sprites.create(assets.image`selector`, SpriteKind.Player)
selector.setStayInScreen(true)
selector.z = 5
grid.snap(selector)
grid.moveWithButtons(selector)
function make_level_text(level: number, cannon: Sprite) {
    let level_text = textsprite.create("" + level, 15, 1)
    level_text.setPosition(cannon.x - 5, cannon.y + 4)
    level_text.z = 4
    sprites.setDataSprite(cannon, "level_text", level_text)
}

function upgrade_cannon(cannon: Sprite) {
    let limit = sprites.readDataNumber(cannon, "time_between_fire")
    limit = Math.constrain(limit - 20, 50, 500)
    sprites.setDataNumber(cannon, "time_between_fire", limit)
    sprites.changeDataNumberBy(cannon, "level", 1)
    sprites.readDataSprite(cannon, "level_text").destroy()
    make_level_text(sprites.readDataNumber(cannon, "level"), cannon)
}

function buy_cannon(tile: any) {
    let cannon: Sprite;
    if (tiles.tileAtLocationEquals(tile, assets.tile`empty`)) {
        cannon = sprites.create(assets.image`cannon`, SpriteKind.cannon)
        tiles.placeOnTile(cannon, tile)
        tiles.setTileAt(tile, assets.tile`placed`)
        cannon.z = 3
        sprites.setDataNumber(cannon, "frames_since_fired", 390)
        sprites.setDataNumber(cannon, "time_between_fire", 400)
        sprites.setDataNumber(cannon, "level", 1)
        make_level_text(1, cannon)
        info.changeScoreBy(-100)
    }
    
}

function buy_trap(tile: any) {
    let trap: Sprite;
    // 
    if (tiles.tileAtLocationEquals(tile, assets.tile`empty`)) {
        trap = sprites.create(assets.image`lava`, SpriteKind.trap)
        tiles.placeOnTile(trap, tile)
        trap.z = -1
        tiles.setTileAt(tile, assets.tile`placed`)
        info.changeScoreBy(-50)
    }
    
}

// 
controller.A.onEvent(ControllerButtonEvent.Pressed, function interact() {
    if (info.score() < 100) {
        return
    }
    
    let tile = selector.tilemapLocation()
    let cannons = spriteutils.getSpritesWithin(SpriteKind.cannon, 1, selector)
    if (tiles.tileAtLocationEquals(tile, assets.tile`placed`)) {
        info.changeScoreBy(-100)
        upgrade_cannon(cannons[0])
    } else if (item_selected == "cannon") {
        // 
        buy_cannon(tile)
    } else if (item_selected == "trap") {
        // 
        // 
        buy_trap(tile)
    }
    
})
controller.B.onEvent(ControllerButtonEvent.Pressed, function swap_item() {
    // 
    
    if (item_selected == "cannon") {
        item_selected = "trap"
    } else if (item_selected == "trap") {
        item_selected = "cannon"
    }
    
})
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.Enemy, function hit(cannon_ball: Sprite, enemy: Sprite) {
    sprites.changeDataNumberBy(enemy, "hp", -1)
    if (sprites.readDataNumber(enemy, "hp") < 1) {
        enemy.destroy()
        info.changeScoreBy(100)
    }
    
    cannon_ball.destroy()
})
sprites.onOverlap(SpriteKind.cannon, SpriteKind.Enemy, function destroy_cannon(cannon: Sprite, enemy: Sprite) {
    tiles.setTileAt(cannon.tilemapLocation(), assets.tile`empty`)
    sprites.readDataSprite(cannon, "level_text").destroy()
    cannon.destroy()
    enemy.destroy()
})
sprites.onOverlap(SpriteKind.Enemy, SpriteKind.trap, function use_trap(enemy: Sprite, trap: Sprite) {
    // 
    tiles.setTileAt(trap.tilemapLocation(), assets.tile`empty`)
    trap.destroy()
    sprites.changeDataNumberBy(enemy, "hp", -1)
    if (sprites.readDataNumber(enemy, "hp") < 1) {
        enemy.destroy()
    }
    
})
scene.onOverlapTile(SpriteKind.Enemy, assets.tile`game over`, function game_over() {
    game.over(false)
})
game.onUpdateInterval(20000, function difficulty_increase() {
    
    health = Math.constrain(health + 1, 0, 20)
    spawn_frequency = Math.constrain(spawn_frequency - 100, -200, 10000)
})
function spawn_enemy() {
    let enemy = sprites.create(assets.image`ghost`, SpriteKind.Enemy)
    tiles.placeOnRandomTile(enemy, assets.tile`spawn`)
    enemy.vx = -7
    sprites.setDataNumber(enemy, "hp", health)
    timer.after(spawn_frequency, spawn_enemy)
}

spawn_enemy()
function fire(cannon: Sprite) {
    let ball = sprites.create(assets.image`cannon ball`, SpriteKind.Projectile)
    ball.setPosition(cannon.x + 4, cannon.y)
    ball.z = 0
    ball.setVelocity(50, 0)
    ball.setFlag(SpriteFlag.AutoDestroy, true)
    ball.setFlag(SpriteFlag.StayInScreen, false)
    sprites.setDataNumber(cannon, "frames_since_fired", 0)
}

function fire_control() {
    let count: number;
    for (let cannon of sprites.allOfKind(SpriteKind.cannon)) {
        sprites.changeDataNumberBy(cannon, "frames_since_fired", 1)
        count = sprites.readDataNumber(cannon, "frames_since_fired")
        if (count > sprites.readDataNumber(cannon, "time_between_fire")) {
            fire(cannon)
        }
        
    }
}

game.onUpdate(function tick() {
    fire_control()
})
