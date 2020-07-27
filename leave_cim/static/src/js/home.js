odoo.define('systray.systray_leave_cim', function (require) {
    "use strict";
    var localStorage = require('web.local_storage');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');

    var ActionMenu = Widget.extend({
        template: 'leave_cim.home_icon',
        events: {
            'click .home_icon': 'onclick_home_icon',
        },

        onclick_home_icon: function () {
            window.open('/my/home');
        },
    });
    SystrayMenu.Items.push(ActionMenu);
    return ActionMenu;

});
