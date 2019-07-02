export function drawBottomRightPanel (message) {
  window.canvas.add(new fabric.Rect({
    left: ((window.view_x - 1020) / 2) + 1020,
    top: window.view_y - 84,
    height: 84,
    width: (window.view_x - 1020) / 6,
    stroke: 'black',
    fill: 'yellow',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text('Buy Cards', {
    left: ((window.view_x - 1020) / 2) + 1020 + ((window.view_x - 1020) / 12),
    top: window.view_y - 84 + 42,
    height: 84,
    width: (window.view_x - 1020) / 6,
    fill: 'black',
    strokeWidth: 1,
    selectable: false,
    originX: 'center',
    originY: 'center',
    fontSize: 15
  }))
  window.canvas.add(new fabric.Rect({
    left: ((window.view_x - 1020) / 2) + 1020 + ((window.view_x - 1020) / 6),
    top: window.view_y - 84,
    height: 84,
    width: (window.view_x - 1020) / 6,
    stroke: 'black',
    fill: 'green',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text('View Deck', {
    left: ((window.view_x - 1020) / 2) + 1020 + ((window.view_x - 1020) / 6) + ((window.view_x - 1020) / 12),
    top: window.view_y - 84 + 42,
    height: 84,
    width: (window.view_x - 1020) / 6,
    fill: 'white',
    strokeWidth: 1,
    selectable: false,
    originX: 'center',
    originY: 'center',
    fontSize: 15
  }))
  window.canvas.add(new fabric.Rect({
    left: ((window.view_x - 1020) / 2) + 1020 + ((window.view_x - 1020) / 3),
    top: window.view_y - 84,
    height: 84,
    width: (window.view_x - 1020) / 6,
    stroke: 'black',
    fill: 'blue',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text('View Log', {
    left: ((window.view_x - 1020) / 2) + 1020 + ((window.view_x - 1020) / 3) + ((window.view_x - 1020) / 12),
    top: window.view_y - 84 + 42,
    height: 84,
    width: (window.view_x - 1020) / 6,
    fill: 'white',
    strokeWidth: 1,
    selectable: false,
    originX: 'center',
    originY: 'center',
    fontSize: 15
  }))
  window.canvas.add(new fabric.Rect({
    left: ((window.view_x - 1020) / 2) + 1020,
    top: window.view_y - 84 - 86,
    height: 86,
    width: (window.view_x - 1020) / 2,
    stroke: 'white',
    fill: 'black',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text('Chains:', {
    left: ((window.view_x - 1020) / 2) + 1020,
    top: window.view_y - 84 - 86,
    height: 86,
    width: (window.view_x - 1020) / 2,
    fill: 'white',
    strokeWidth: 1,
    selectable: false,
    fontSize: 30
  }))
  window.canvas.add(new fabric.Text(String(message.chains), {
    left: ((window.view_x - 1020) / 2) + 1020,
    top: window.view_y - 84 - 86 + 45,
    height: 86,
    width: (window.view_x - 1020) / 2,
    fill: 'white',
    strokeWidth: 1,
    selectable: false,
    fontSize: 30
  }))
  window.chains = message.chains
  window.unlock_points = message.unlock_points
  window.canvas.add(new fabric.Rect({
    left: ((window.view_x - 1020) / 2) + 1020,
    top: window.view_y - 84 - 86 - 86,
    height: 86,
    width: (window.view_x - 1020) / 2,
    stroke: 'white',
    fill: 'black',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Rect({
    left: ((window.view_x - 1020) / 2) + 1020,
    top: window.view_y - 84 - 86 - 86,
    height: 86,
    width: (window.view_x - 1020) / 2 * message.unlock_progress / 16,
    stroke: 'red',
    fill: 'red',
    strokeWidth: 1,
    selectable: false
  }))
  window.canvas.add(new fabric.Text('Unlocked: ' + message.unlock_points, {
    left: ((window.view_x - 1020) / 2) + 1020,
    top: window.view_y - 84 - 86 - 86,
    height: 86,
    width: (window.view_x - 1020) / 2,
    fill: 'white',
    strkeWidth: 1,
    selectable: false,
    fontSize: 30
  }))
  if (message.drops_added) {
    window.drops = message.drops
    window.drop_depth = message.drop_depth
    window.drop_unlocked = message.drop_unlocked
  }
}
