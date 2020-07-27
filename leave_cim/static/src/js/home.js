odoo.define('leave_cim.home_icon', function (require) {
    "use strict";
    var localStorage = require('web.local_storage');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');

    var ActionMenu = Widget.extend({
        template: 'leave_cim.home_icon',
        events: {
            'click .home_icon': 'onclick_gifticon',
        },

        start: function (parent) {

        onclick_gifticon: function () {
            var self = this;
            this._rpc({
                route: '/my/home'
            }).then(function (result) {
                window.open(result.link, '_blank', 'noopener noreferrer');
            });
        },
    });

    SystrayMenu.Items.push(ActionMenu);
    return ActionMenu;
});
