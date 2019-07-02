export function drawAnimations (animations, char_pos_x, char_pos_y) {
  if (!window.animations) {
    window.animations = []
  }
  for (let animation of animations) {
    var text = animation.split(',')
    text[5] = 15
    window.animations.push(text)
  }
  for (let animation of window.animations) {
    if (animation[5] > 0) {
      window.canvas.add(new fabric.Rect({
        left: parseInt(animation[0]) - parseInt(char_pos_x) + (window.view_x / 2),
        top: parseInt(animation[2]) - parseInt(char_pos_y) + (window.view_y / 2),
        height: parseInt(animation[3]) - parseInt(animation[2]),
        width: parseInt(animation[1]) - parseInt(animation[0]),
        stroke: animation[4],
        fill: animation[4],
        strokeWidth: 2,
        selectable: false,
        opacity: 0.5 * (animation[5] / 15)
      }))
      animation[5] -= 1
    }
    if (animation[5] <= 0) {
      window.animations.splice(window.animations.indexOf(animation), 1)
      break
    }
  }
}
