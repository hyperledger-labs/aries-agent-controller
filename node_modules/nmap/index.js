"use strict";

function nmap(n, map) {
  var result = new Array(n);

  for (var i = 0; i < n; i++) {
    result[i] = map(i, i, result);
  }

  return result;
}

module.exports = nmap;
