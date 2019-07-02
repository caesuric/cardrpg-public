import * as constants from 'cardrpgConstants'

export var guid = function() {
  var s4
  s4 = function() {
    return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1)
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4()
}

export var stripOutZeros = function(string) {
  return string.replace(/\0/g, '')
}
