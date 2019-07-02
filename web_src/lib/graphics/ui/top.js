export function drawLevelInfo (message) {
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: 0,
    height: window.tileSize,
    width: window.view_x,
    stroke: 'black',
    fill: 'black',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text("Level: " + message.level, {
    left: 0,
    top: 0,
    fontSize: 15,
    fill: 'white',
    selectable: false
  }))
  window.canvas.add(new fabric.Text("Floor: " + (message.floor + 1), {
    left: 0,
    top: 15,
    fontSize: 14,
    fill: 'white',
    selectable: false
  }))
  window.canvas.add(new fabric.Rect({
    left: 75,
    top: 0,
    height: window.tileSize,
    width: window.view_x - 75,
    stroke: 'green',
    fill: 'black',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Rect({
    left: 75,
    top: 0,
    height: window.tileSize,
    width: (window.view_x - 75) * message.total_xp / message.next_level_xp,
    stroke: 'green',
    fill: 'green',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text("XP: " + message.total_xp + "/" + message.next_level_xp, {
    left: 75,
    top: 0,
    fontSize: 15,
    fill: 'white',
    selectable: false
  }))
}
export function drawChainInfo (message) {
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.tileSize,
    height: window.tileSize,
    width: window.view_x,
    stroke: 'blue',
    fill: 'black',
    strokeWidth: 1,
    selectable: false
  }))
  if (!window.chain_max || message.chain_timer > window.chain_max) {
    window.chain_max = message.chain_timer
  }
  if (message.chain_timer === '' || message.chain_timer === 0) {
    window.chain_max = undefined
    return
  }
  window.canvas.add(new fabric.Rect({
    left: 0,
    top: window.tileSize,
    height: window.tileSize,
    width: window.view_x * message.chain_timer / window.chain_max,
    stroke: 'blue',
    fill: 'blue',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text("Chain Time: " + message.chain_timer + 's', {
    left: 0,
    top: window.tileSize,
    fontSize: 15,
    fill: 'white',
    selectable: false
  }))
  window.canvas.add(new fabric.Text("Chain " + String(message.current_chain) + 'x', {
    left: 0,
    top: 64,
    fontSize: 60,
    fill: 'white',
    selectable: false
  }))
}
