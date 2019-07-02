import {updater} from 'gameComm'
import {drawTiles, drawChestsAndDoors} from 'graphics/tiles'
import {drawMobs} from 'graphics/mobs'
import {drawCharacters} from 'graphics/chars'
import {drawProjectiles} from 'graphics/projectiles'
import {drawEffects} from 'graphics/effects'
import {drawFloatingText} from 'graphics/floatingText'
import {drawLargeTextMessages} from 'graphics/largeTextMessages'
import {drawAnimations} from 'graphics/animations'
import {init} from 'graphics/init'
import * as audio from 'audio'
import * as ui from 'graphics/ui'
import * as keys from 'graphics/visualKey'

export {init}

export function drawAll (message) {
  var char_hp, char_max_hp, char_name
  [char_hp, char_max_hp, char_name] = drawMainCanvas(message)
  ui.drawLevelInfo(message)
  ui.drawChainInfo(message)
  ui.drawCards(message)
  ui.drawHpAndMp(message)
  ui.drawBottomRightPanel(message)
  drawEffects(message)
  ui.drawPartyBar(message, char_hp, char_max_hp, char_name)
  if (updater.counter >= updater.update_count_divisor) {
    window.canvas.renderAll()
  }
}
function drawMainCanvas (message) {
  var char_color, char_eye_color, char_facing, char_gcd, char_hp, char_max_hp, char_max_mp, char_mp, char_name, char_pos_x, char_pos_y, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6
  if (updater.counter >= updater.update_count_divisor) {
    window.canvas.clear()
  }
  [message,char_pos_x,char_pos_y,char_facing,char_hp,char_max_hp,char_mp,char_max_mp,char_slot_1,char_slot_2,char_slot_3,char_slot_4,char_slot_5,char_slot_6,char_gcd,char_color,char_eye_color,char_name] = updater.extractCharacterData(message)
  if (!window.char_color) {
    window.char_color = char_color
    window.char_eye_color = char_eye_color
    window.char_name = char_name
  }
  message = updater.extractTileData(message)
  drawMainCanvasElements(message, char_pos_x, char_pos_y, char_facing, char_hp, char_max_hp, char_mp, char_max_mp, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6, char_gcd, window.char_color, window.char_eye_color)
  return [char_hp, char_max_hp, char_name]
}
function drawBackgroundCallback () {
  window.preRenderCanvas.clear()
  drawTiles(window.message)
  window.preRenderCanvas.renderAll()
  window.backgroundImage = new fabric.Image(window.rawPreRenderCanvas, {
    left: 0,
    top: 0,
    selectable: false
  })
  window.previous_char_x = window.char_pos_x
  window.previous_char_y = window.char_pos_y
}
function drawMainCanvasElements (message, char_pos_x, char_pos_y, char_facing, char_hp, char_max_hp, char_mp, char_max_mp, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6, char_gcd, char_color, char_eye_color) {
  var mob_class, mob_name, mob_pos_x, mob_pos_y
  if (updater.background_counter >= updater.background_count_divisor) {
    window.message = message
    window.char_pos_x = char_pos_x
    window.char_pos_y = char_pos_y
    setTimeout(drawBackgroundCallback, 0)
  }
  if (updater.counter >= updater.update_count_divisor) {
    if (window.backgroundImage) {
      window.backgroundImage.left = window.previous_char_x - char_pos_x
      window.backgroundImage.top = window.previous_char_y - char_pos_y
      window.canvas.add(window.backgroundImage)
      if (window.miniMapImage && window.miniMapOn) {
        window.canvas.add(window.miniMapImage)
      }
    }
    [mob_pos_x, mob_pos_y, mob_class, mob_name] = drawMobs(message)
    drawChestsAndDoors(message)
    drawProjectiles(message)
    drawCharacters(message, char_pos_x, char_pos_y, char_facing, char_hp, char_max_hp, char_slot_1, char_slot_2, char_slot_3, char_slot_4, char_slot_5, char_slot_6, char_gcd, char_color, char_eye_color)
    drawLargeTextMessages(message)
    window.canvas.add(new fabric.Rect({
      left: 0,
      top: 0,
      width: view_x - 1,
      height: view_y - 1,
      stroke: 'white',
      fill: 'transparent',
      strokeWidth: 2,
      selectable: false
    }))
    keys.drawVisualKey(char_pos_x, char_pos_y)
    keys.drawDetailedMobData()
    drawAnimations(message.animations, char_pos_x, char_pos_y)
    audio.makeSounds(message.sounds)
    drawFloatingText(message.floating_text, char_pos_x, char_pos_y)
    keys.drawMouseHoverGuide()
  }
  if (updater.background_counter >= updater.background_count_divisor && window.miniMapOn) {
    window.minimap_message = message
    setTimeout(ui.drawMiniMapCallback, 0)
  }
}
