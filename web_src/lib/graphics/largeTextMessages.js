export function drawLargeTextMessages (message) {
  if (message.paralyzed === true) {
    window.canvas.add(new fabric.Text('PARALYZED', {
      left: window.view_x / 2,
      top: window.view_y / 2,
      originX: 'center',
      originY: 'center',
      fontSize: 50,
      fill: 'white',
      selectable: false
    }))
  }
  if (message.won === true) {
    window.canvas.add(new fabric.Text('YOU WON!', {
      left: window.view_x / 2,
      top: window.view_y / 2,
      originX: 'center',
      originY: 'center',
      fontSize: 50,
      fill: 'white',
      selectable: false
    }))
  }
}
