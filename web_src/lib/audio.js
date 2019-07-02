export function init() {
  window.sounds = {}
  window.sounds.attack = new Audio('assets/sounds/attack.wav')
  window.sounds.attack.volume = 0.5
  window.sounds.level_up = new Audio('assets/sounds/level up.wav')
  window.sounds.level_up.volume = 0.5
  window.sounds.chain_complete = new Audio('assets/sounds/chain complete.wav')
  window.sounds.chain_complete.volume = 0.5
  window.sounds.chain_increment = new Audio('assets/sounds/chain increment.wav')
  window.sounds.chain_increment.volume = 0.5
  window.sounds.door = new Audio('assets/sounds/door.wav')
  window.sounds.door.volume = 0.5
  window.sounds.unlock_point = new Audio('assets/sounds/unlock point.wav')
  window.sounds.unlock_point.volume = 0.5
  window.sounds.purchase = new Audio('assets/sounds/purchase.wav')
  window.sounds.purchase.volume = 0.5
  window.sounds.unlock_card = new Audio('assets/sounds/unlock card.wav')
  window.sounds.unlock_card.volume = 0.5
  window.sounds.stairs = new Audio('assets/sounds/stairs.wav')
  window.sounds.stairs.volume = 0.5
}

export function makeSounds(sounds) {
  for (let sound of sounds) {
    if (window.sounds[sound.replace(/\0/g, '')]) {
      window.sounds[sound.replace(/\0/g, '')].play()
    }
  }
}
