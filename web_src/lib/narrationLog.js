export function init() {
  if (!window.console) {
    window.console = {}
  }
  if (!window.console.log) {
    window.console.log = function() {}
  }
  window.narration = []
}
