odoo.define('employee_portal_timeoff.portal_timeoff', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

publicWidget.registry.EmpPortalTimeOff = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.new_timeoff_form, .edit_timeoff_form,.new_permission_form,.edit_permission_form,.new_return_form,.edit_return_form)',
    events: {
        'click .action_validate': '_onNewTeamVal',
        'click .action_validate2': '_onNewTeamVal2',
        'click .action_confirm': '_onNewTeamConfirm',
        'click .action_confirm2': '_onNewTeamConfirm2',
        'click .action_approve': '_onNewTeamApprove',
        'click .action_approve2': '_onNewTeamApprove2',
        'click .action_refuse': '_onNewTeamRefuse',
        'click .action_refuse2': '_onNewTeamRefuse2',
        'click .new_timeoff_confirm': '_onNewTimeOffConfirm',
        'click .new_permission_confirm': '_onNewpermissionConfirm',
        'click .new_return_confirm': '_onNewreturnConfirm',
        'click .edit_timeoff_confirm': '_onEditTimeOffConfirm',
        'click .edit_permission_confirm': '_onEditPermissionConfirm',
        'click .edit_return_confirm': '_onEditReturnConfirm',
        'change .request_date_to': '_onchange',
    },


    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {jQuery} $btn
     * @param {function} callback
     * @returns {Promise} 
     */
    _buttonExec: function ($btn, callback) {
        // TODO remove once the automatic system which does this lands in master
        $btn.prop('disabled', true);
        return callback.call(this).guardedCatch(function () {
            $btn.prop('disabled', false);
        });
    },
    /**
     * @private
     * @returns {Promise} 
     */




    _create_NewTeamVal: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_validate',
            args: [[parseInt($('.actions_form .timeoff_id').val())], {
                timeoffID: parseInt($('.actions_form .timeoff_id').val()),
                conf_code: $('.actions_form .conf_code').val(),
            }],
        }).then(function () {
                  self.$('a.action_validate_conf').click();
                    let remSec = $("#count3"),
                      countSec = 100,
                      timer = setInterval(() => {
                      countSec >= 0 ? remSec.text(countSec--) : clearInterval(timer);
                      }, 1000); 
                  });;
        },


    _create_NewTeamVal2: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_validate2',
            args: [[parseInt($('.code_validate_form .timeoff_id').val())], {
                timeoffID: parseInt($('.code_validate_form .timeoff_id').val()),
                conf_code: $('.code_validate_form .conf_code').val(),
            }],
        }).then(function (response) {
            if (response.errors) {
                $('.new-opp-dialog-val .alert').remove();
                $('.new-opp-dialog-val div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/my/team/' + response.id;
            }
        });
    },



    _create_NewTeamConfirm: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_confirm',
            args: [[parseInt($('.actions_form .timeoff_id').val())], {
                timeoffID: parseInt($('.actions_form .timeoff_id').val()),
                conf_code: $('.actions_form .conf_code').val(),
            }],
        }).then(function () {
                  self.$('a.action_confirm_conf').click();
                    let remSec = $("#count"),
                      countSec = 100,
                      timer = setInterval(() => {
                      countSec >= 0 ? remSec.text(countSec--) : clearInterval(timer);
                      }, 1000); 
                  });;
        },


    _create_NewTeamConfirm2: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_confirm2',
            args: [[parseInt($('.code_confirm_form .timeoff_id').val())], {
                timeoffID: parseInt($('.code_confirm_form .timeoff_id').val()),
                conf_code: $('.code_confirm_form .conf_code').val(),
            }],
        }).then(function (response) {
            if (response.errors) {
                $('.new-opp-dialog-conf .alert').remove();
                $('.new-opp-dialog-conf div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/my/team/' + response.id;
            }
        });
    },






    _create_NewTeamApprove: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_approve',
            args: [[parseInt($('.actions_form .timeoff_id').val())], {
                timeoffID: parseInt($('.actions_form .timeoff_id').val()),
                conf_code: $('.actions_form .conf_code').val(),
            }],
        }).then(function () {
                  self.$('a.action_approve_conf').click();
                    let remSec = $("#count2"),
                      countSec = 100,
                      timer = setInterval(() => {
                      countSec >= 0 ? remSec.text(countSec--) : clearInterval(timer);
                      }, 1000); 
                  });;
    },


    _create_NewTeamApprove2: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_approve2',
            args: [[parseInt($('.code_approve_form .timeoff_id').val())], {
                timeoffID: parseInt($('.code_approve_form .timeoff_id').val()),
                conf_code: $('.code_approve_form .conf_code').val(),
            }],
        }).then(function (response) {
            if (response.errors) {
                $('.new-opp-dialog-aprv .alert').remove();
                $('.new-opp-dialog-aprv div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                self.$('a.modalaccept').click();
            }
        });
    },



    _create_NewTeamRef: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_ref',
            args: [[parseInt($('.edit_timeoff_form .timeoff_id').val())], {
                timeoffID: parseInt($('.edit_timeoff_form .timeoff_id').val()),
                description: $('.edit_timeoff_form .name').val(),
                timeoff_address: $('.edit_timeoff_form .timeoff_address').val(),
                timeoff_type: $('.edit_timeoff_form .holiday_status_id').val(),
                from: this._parse_date($('.edit_timeoff_form .request_date_from').val()),
                to: this._parse_date($('.edit_timeoff_form .request_date_to').val()),
                number_of_days: this._parse_date($('.edit_timeoff_form .number_of_days').val()),
                half_day: $('.edit_timeoff_form .request_unit_half').prop("checked"),
                custom_hours: $('.edit_timeoff_form .request_unit_hours').prop("checked"),
                request_hour_from: $('.edit_timeoff_form .request_hour_from').val(),
                request_hour_to: $('.edit_timeoff_form .request_hour_to').val(),
                request_date_from_period: $('.edit_timeoff_form .request_date_from_period').val(),
            }],
        }).then(function () {
            window.location.reload();
        });
    },





    _create_NewTeamRef: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_ref',
            args: [[parseInt($('.actions_form .timeoff_id').val())], {
                timeoffID: parseInt($('.actions_form .timeoff_id').val()),
                conf_code: $('.actions_form .conf_code').val(),
            }],
        }).then(function () {
                  self.$('a.action_refuse_conf').click();
                    let remSec = $("#count4"),
                      countSec = 100,
                      timer = setInterval(() => {
                      countSec >= 0 ? remSec.text(countSec--) : clearInterval(timer);
                      }, 1000); 
                  });;
    },


    _create_NewTeamRef2: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'team_action_ref2',
            args: [[parseInt($('.code_refuse_form .timeoff_id').val())], {
                timeoffID: parseInt($('.code_refuse_form .timeoff_id').val()),
                conf_code: $('.code_refuse_form .conf_code').val(),
            }],
        }).then(function (response) {
            if (response.errors) {
                $('.new-opp-dialog-ref .alert').remove();
                $('.new-opp-dialog-ref div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                self.$('a.modalsignrefuse').click();
            }
        });
    },

    _createChanges: function () {
        return this._rpc({
            model : 'hr.leave',
            method: 'number_of_days_portal',
            args: [{
            start: $('.new_timeoff_form .request_date_from').val(),
            end: $('.new_timeoff_form .request_date_to').val(),
            timeoff_type: $('.new_timeoff_form .holiday_status_id').val(),
        }],
        }).then(function(response){
            if (response.errors) {
                $('#new-opp-dialog-1 .alert').remove();
                $('#new-opp-dialog-1 div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                self.$("input.number_of_days").val('');
                return Promise.reject(response);
            } else {
                self.$("input.request_date_to").prop("disabled", false);                
                self.$("input.number_of_days").val(response.date_to);
                self.$("input.current").val(response.current);                
                self.$("input.requested").val(response.requested);                
                self.$("input.remaining").val(response.remaining);                
            }
        })
        
    },

    _createTimeOff: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'create_timeoff_portal',
            args: [{
                description: $('.new_timeoff_form .name').val(),
                timeoff_address: $('.new_timeoff_form .timeoff_address').val(),
                timeoff_type: $('.new_timeoff_form .holiday_status_id').val(),
                from: $('.new_timeoff_form .request_date_from').val(),
                to: $('.new_timeoff_form .request_date_to').val(),
                number_of_days: $('.new_timeoff_form .number_of_days').val(),
                half_day: $('.new_timeoff_form .request_unit_half').prop("checked"),
                custom_hours: $('.new_timeoff_form .request_unit_hours').prop("checked"),
                request_hour_from: $('.new_timeoff_form .request_hour_from').val(),
                request_hour_to: $('.new_timeoff_form .request_hour_to').val(),
                request_date_from_period: $('.new_timeoff_form .request_date_from_period').val(),
                notes: $('.new_timeoff_form .notes').val(),
                attachment: $('.new_timeoff_form .attachment').val(),
            }],
        }).then(function (response) {
            if (response.errors) {
                $('#new-opp-dialog-1 .alert').remove();
                $('#new-opp-dialog-1 div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/my/timeoff/' + response.id;
            }
        });
    },







    _createPermission: function () {
        return this._rpc({
            model: 'hr.permission',
            method: 'create_permission_portal',
            args: [{
                req_type: $('.new_permission_form .req_type').val(),
                date_time: $('.new_permission_form .date_time').val(),
                reason: $('.new_permission_form .reason').val(),
            }],
        }).then(function (response) {
            if (response.errors) {
                $('#new-opp-dialog-2 .alert').remove();
                $('#new-opp-dialog-2 div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/my/permission_req/' + response.id;
            }
        });
    }, 

    _createReturn: function () {
        return this._rpc({
            model: 'hr.leavereturn',
            method: 'create_return_portal',
            args: [{
                reference_ret: $('.new_return_form .reference_ret').val(),
                holiday_status_id: $('.new_return_form .holiday_status_id').val(),
                request_date: $('.new_return_form .request_date').val(),
            }],
        }).then(function (response) {
            if (response.errors) {
                $('#new-opp-dialog-3 .alert').remove();
                $('#new-opp-dialog-3 div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/my/return_req/' + response.id;
            }
        });
    },





       /**
     * @private
     * @returns {Promise}
     */
    _editTimeOffRequest: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'update_timeoff_portal',
            args: [[parseInt($('.edit_timeoff_form .timeoff_id').val())], {
                timeoffID: parseInt($('.edit_timeoff_form .timeoff_id').val()),
                description: $('.edit_timeoff_form .name').val(),
                timeoff_address: $('.edit_timeoff_form .timeoff_address').val(),
                timeoff_type: $('.edit_timeoff_form .holiday_status_id').val(),
                from: $('.edit_timeoff_form .request_date_from').val(),
                to: $('.edit_timeoff_form .request_date_to').val(),
                number_of_days: this._parse_date($('.edit_timeoff_form .number_of_days').val()),
                half_day: $('.edit_timeoff_form .request_unit_half').prop("checked"),
                custom_hours: $('.edit_timeoff_form .request_unit_hours').prop("checked"),
                request_hour_from: $('.edit_timeoff_form .request_hour_from').val(),
                request_hour_to: $('.edit_timeoff_form .request_hour_to').val(),
                request_date_from_period: $('.edit_timeoff_form .request_date_from_period').val(),
            }],
        }).then(function () {
            window.location.reload();
        });
    },

    _editPermission: function () {
        return this._rpc({
            model: 'hr.permission',
            method: 'update_permission_portal',
            args: [[parseInt($('.edit_permission_form .permission_id').val())],{
                permissionID: parseInt($('.edit_permission_form .permission_id').val()),
                req_type: $('.edit_permission_form .req_type').val(),
                date_time: $('.edit_permission_form .date_time').val(),
                reason: $('.edit_permission_form .reason').val(),
            }],
        }).then(function () {
            window.location.reload();
        });
    },

    _editReturn: function () {
        return this._rpc({
            model: 'hr.leavereturn',
            method: 'update_return_portal',
            args: [[parseInt($('.edit_return_form .return_id').val())],{
                returnID: parseInt($('.edit_return_form .return_id').val()),
                reference_ret: $('.edit_return_form .reference_ret').val(),
                holiday_status_id: $('.edit_return_form .holiday_status_id').val(),
                request_date: $('.edit_return_form .request_date').val(),
            }],
        }).then(function () {
            window.location.reload();
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onNewTeamVal: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_NewTeamVal);
    },
    _onNewTeamVal2: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_NewTeamVal2);
    },

    _onNewTeamConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_NewTeamConfirm);
    },


    _onNewTeamConfirm2: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_NewTeamConfirm2);
    },


    _onNewTeamApprove: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_NewTeamApprove);
    },

    _onNewTeamApprove2: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_NewTeamApprove2);
    },

    _onNewTeamRefuse: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_NewTeamRef);
    },
    _onNewTeamRefuse2: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._create_NewTeamRef2);
    },

    _onNewTimeOffConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._createTimeOff);
    },

    _onNewpermissionConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._createPermission);
    },

    _onNewreturnConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._createReturn);
    },

    _onchange: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._createChanges);
    },


    /**
     * @private
     * @param {Event} ev
     */
    _onEditTimeOffConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._editTimeOffRequest);
    },
    _onEditPermissionConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._editPermission);
    },

    _onEditReturnConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._editReturn);
    },
    _parse_date: function (value) {
        console.log(value);
        var date = moment(value, "YYYY-MM-DD", true);
        if (date.isValid()) {
            return time.date_to_str(date.toDate());
        }
        else {
            return false;
        }
    },
});
});
