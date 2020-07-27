odoo.define('systray.systray_odoo_referral', function (require) {
    "use strict";
    var localStorage = require('web.local_storage');
    var Widget = require('web.Widget');

    var ActionMenu = Widget.extend({
        template: 'leave_cim.home_icon',
        events: {
            'click .home_icon': 'onclick_home_icon',
        },

        onclick_home_icon: function () {
            var self = this;
            this._rpc({
                route: '/my/home'
            }).then(function (result) {
                window.open(result.link, '_blank', 'noopener noreferrer');
            });
        },
    });
});
