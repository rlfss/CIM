odoo.define('internal_memo.onchange_select', function (require) {
'use strict';

var core = require('web.core');
var qweb = core.qweb;
var rpc = require('web.rpc')

    function test() {
      var x = document.getElementById("mySelect").value;
      document.getElementById("memo").innerHTML = "You selected: " + x;
    }


});

