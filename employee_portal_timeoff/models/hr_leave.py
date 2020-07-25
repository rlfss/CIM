# Part of Odoo. See LICENSE file for full copyright and licensing details.

import random
from odoo import api, fields, models, _
from datetime import datetime, time, timedelta
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError, ValidationError
from pytz import timezone, UTC
from datetime import datetime, timedelta

import uuid

class EmpPortalTimeOff(models.Model):
    _inherit = "hr.leave"
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'First Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, tracking=True, copy=False, default='draft',
        help="The status is set to 'To Submit', when a time off request is created." +
        "\nThe status is 'To Approve', when time off request is confirmed by user." +
        "\nThe status is 'Refused', when time off request is refused by manager." +
        "\nThe status is 'Approved', when time off request is approved by manager.")


    conf_code = fields.Char('2FA Code')
    expiry_conf_code = fields.Datetime(string="Code Expiry")
    conf_action_type = fields.Selection([
        ('Confirm', 'Confirm'),
        ('Refuse', 'Refuse'),
        ('Approve', 'Approve'),
        ('Validate', 'Validate')
    ], string='Type')

    leave_signature = fields.Binary('Approve Signature', help='Signature received through the portal.', copy=False, attachment=True, readonly=True)
    leave_signed_by = fields.Char('Approve Signed By', help='Name of the person that signed the task.', copy=False, readonly=True)
    leave_signed_date = fields.Date(string="Approve Signature Date", readonly=True)
    leave_signed_hash = fields.Char(string="Approve Signature Hash", readonly=True)

    s_leave_signature = fields.Binary('First Approve Signature', help='Signature received through the portal.', copy=False, attachment=True, readonly=True)
    s_leave_signed_by = fields.Char('First Approve Signed By', help='Name of the person that signed the task.', copy=False, readonly=True)
    s_leave_signed_date = fields.Date(string="First Approve Signature Date", readonly=True)
    s_leave_signed_hash = fields.Char(string="First Approve Signature Hash", readonly=True)

    r_leave_signature = fields.Binary('Refuse Signature', help='Signature received through the portal.', copy=False, attachment=True, readonly=True)
    r_leave_signed_by = fields.Char('Refuse Signed By', help='Name of the person that signed the task.', copy=False, readonly=True)
    r_leave_signed_date = fields.Date(string="Refuse Signature Date", readonly=True)

    def _default_access_token(self):
        return str(uuid.uuid4())


    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
    
    def has_to_be_signed(self):
        return not self.leave_signature

    def s_has_to_be_signed(self):
        return not self.s_leave_signature

    def has_to_be_signed2(self):
        return not self.r_leave_signature



    def update_timeoff_portal(self, values):
        dt_from = values['from']
        dt_to = values['to']
        duration = values['number_of_days']
        if dt_from:
            dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
        if dt_to:
            dt_to = datetime.strptime(dt_to, '%Y-%m-%d').date()
        if duration:
            dt_to = datetime.strptime(dt_from, '%Y-%m-%d').date()  + timedelta(days=duration)
        for timeoff in self:
            timeoff_values = {
                'holiday_status_id': int(values['timeoff_type']),
                'request_date_from': dt_from,
                'request_date_to': dt_to,
            }
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                if timeoff_rec:
                    timeoff_rec.sudo().write(timeoff_values)
                    timeoff_rec._onchange_request_parameters()
                    
    @api.model
    def create_timeoff_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        emp = self.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        if not (values['timeoff_type'] and values['from'] and values['to']):
            return {
                'errors': _('All fields are required !')
            }
        timeoff_type = values['timeoff_type']
        tftype = self.env['hr.leave.type'].search([('id', '=', timeoff_type)],
                                                limit=1)
        lead_time = tftype.lead_time
        timeoff_submission = tftype.submission
        max_con_duration = tftype.max_con_duration
        dt_from = values['from']
        dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
        dt_to = values['to']
        dt_to = datetime.strptime(dt_to, '%Y-%m-%d').date()
        dura_days = self._get_number_of_days(dt_from, dt_to, emp)['days']
        my_time = datetime.min.time()
        tz = self.env.user.tz if self.env.user.tz else 'UTC'  # custom -> already in UTC
        date_from = timezone(tz).localize(datetime.combine(dt_from, my_time)).astimezone(UTC).replace(tzinfo=None)
        date_to = timezone(tz).localize(datetime.combine(dt_to, my_time)).astimezone(UTC).replace(tzinfo=None)
        dura_days = self.portal_get_number_of_days(date_from, date_to, 'ex')
        dura_days = int(number_of_days['days'])


        if max_con_duration > 0 and max_con_duration <= dura_days :
            return {
                'errors': _('You Can Not Create Leave Continuous ' + str(dura_days) + ' Days')
            }

        if timeoff_submission == 'back':
            dt_from = values['from']
            date_object = datetime.strptime(dt_from, '%Y-%m-%d').date()
            today = datetime.today().strftime('%Y-%m-%d')
            today = datetime.strptime(today, '%Y-%m-%d').date()
            if date_object >= today :

                dt_from = values['from']
                date_object = datetime.strptime(dt_from, '%Y-%m-%d').date()
                today = datetime.today().strftime('%Y-%m-%d')
                today = datetime.strptime(today, '%Y-%m-%d').date()
                lead_tdate = today + timedelta(days=lead_time)
                if lead_time > 0 :
                    if date_object > lead_tdate:
                        dt_to = values['to']
                        if dt_from:
                            dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
                        if dt_to:
                            dt_to = datetime.strptime(dt_to, '%Y-%m-%d').date()
                        values = {
                            'holiday_status_id': int(values['timeoff_type']),
                            'request_date_from': values['from'],
                            'request_date_to': dt_to,
                            'timeoff_address':  values['timeoff_address'],
                        }
                        tmp_leave = self.env['hr.leave'].sudo().new(values)
                        tmp_leave._onchange_request_parameters()
                        values  = tmp_leave._convert_to_write(tmp_leave._cache)
                        mytimeoff = self.env['hr.leave'].sudo().create(values)
                        temp_id = self.env.ref('leave_cim.email_email_template_id')
                        temp_id.send_mail(mytimeoff.id, force_send=True)
                        return {
                            'id': mytimeoff.id
                        }
                    else:
                        return {
                            'errors': _('You Can Not Create Leave Before ' + str(lead_tdate))
                        }

                else:
                    dt_to = values['to']
                    if dt_from:
                        dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
                    if dt_to:
                        dt_to = datetime.strptime(dt_to, '%Y-%m-%d').date()
                    values = {
                        'holiday_status_id': int(values['timeoff_type']),
                        'request_date_from': values['from'],
                        'request_date_to': dt_to,
                        'timeoff_address':  values['timeoff_address'],
                    }
                    tmp_leave = self.env['hr.leave'].sudo().new(values)
                    tmp_leave._onchange_request_parameters()
                    values  = tmp_leave._convert_to_write(tmp_leave._cache)
                    mytimeoff = self.env['hr.leave'].sudo().create(values)
                    temp_id = self.env.ref('leave_cim.email_email_template_id')
                    temp_id.send_mail(mytimeoff.id, force_send=True)
                    return {
                        'id': mytimeoff.id
                    }

            else:
                return {
                    'errors': _('You Can Not Create Back Leave !')
                }





        if timeoff_submission == 'future':
            dt_from = values['from']
            date_object = datetime.strptime(dt_from, '%Y-%m-%d').date()
            today = datetime.today().strftime('%Y-%m-%d')
            today = datetime.strptime(today, '%Y-%m-%d').date()
            if date_object <= today :

                dt_from = values['from']
                date_object = datetime.strptime(dt_from, '%Y-%m-%d').date()
                today = datetime.today().strftime('%Y-%m-%d')
                today = datetime.strptime(today, '%Y-%m-%d').date()
                lead_tdate = today + timedelta(days=lead_time)
                if lead_time > 0 :
                    if date_object > lead_tdate:
                        dt_to = values['to']
                        if dt_from:
                            dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
                        if dt_to:
                            dt_to = datetime.strptime(dt_to, '%Y-%m-%d').date()
                        values = {
                            'holiday_status_id': int(values['timeoff_type']),
                            'request_date_from': values['from'],
                            'request_date_to': dt_to,
                            'timeoff_address':  values['timeoff_address'],
                        }
                        tmp_leave = self.env['hr.leave'].sudo().new(values)
                        tmp_leave._onchange_request_parameters()
                        values  = tmp_leave._convert_to_write(tmp_leave._cache)
                        mytimeoff = self.env['hr.leave'].sudo().create(values)
                        temp_id = self.env.ref('leave_cim.email_email_template_id')
                        temp_id.send_mail(mytimeoff.id, force_send=True)
                        return {
                            'id': mytimeoff.id
                        }
                    else:
                        return {
                            'errors': _('You Can Not Create Leave Before ' + str(lead_tdate))
                        }

                else:
                    dt_to = values['to']
                    if dt_from:
                        dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
                    if dt_to:
                        dt_to = datetime.strptime(dt_to, '%Y-%m-%d').date()
                    values = {
                        'holiday_status_id': int(values['timeoff_type']),
                        'request_date_from': values['from'],
                        'request_date_to': dt_to,
                        'timeoff_address':  values['timeoff_address'],
                    }
                    tmp_leave = self.env['hr.leave'].sudo().new(values)
                    tmp_leave._onchange_request_parameters()
                    values  = tmp_leave._convert_to_write(tmp_leave._cache)
                    mytimeoff = self.env['hr.leave'].sudo().create(values)
                    temp_id = self.env.ref('leave_cim.email_email_template_id')
                    temp_id.send_mail(mytimeoff.id, force_send=True)
                    return {
                        'id': mytimeoff.id
                    }

            else:
                return {
                    'errors': _('You Can Not Create Future Leave !')
                }




        if timeoff_submission == 'no':

            dt_from = values['from']
            date_object = datetime.strptime(dt_from, '%Y-%m-%d').date()
            today = datetime.today().strftime('%Y-%m-%d')
            today = datetime.strptime(today, '%Y-%m-%d').date()
            lead_tdate = today + timedelta(days=lead_time)
            if lead_time > 0 :
                if date_object > lead_tdate:
                    dt_to = values['to']
                    if dt_from:
                        dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
                    if dt_to:
                        dt_to = datetime.strptime(dt_to, '%Y-%m-%d').date()
                    values = {
                        'holiday_status_id': int(values['timeoff_type']),
                        'request_date_from': values['from'],
                        'request_date_to': dt_to,
                        'timeoff_address':  values['timeoff_address'],
                    }
                    tmp_leave = self.env['hr.leave'].sudo().new(values)
                    tmp_leave._onchange_request_parameters()
                    values  = tmp_leave._convert_to_write(tmp_leave._cache)
                    mytimeoff = self.env['hr.leave'].sudo().create(values)
                    temp_id = self.env.ref('leave_cim.email_email_template_id')
                    temp_id.send_mail(mytimeoff.id, force_send=True)
                    return {
                        'id': mytimeoff.id
                    }
                else:
                    return {
                        'errors': _('You Can Not Create Leave Before ' + str(lead_tdate))
                    }

            else:
                dt_to = values['to']
                if dt_from:
                    dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
                if dt_to:
                    dt_to = datetime.strptime(dt_to, '%Y-%m-%d').date()
                values = {
                    'holiday_status_id': int(values['timeoff_type']),
                    'request_date_from': values['from'],
                    'request_date_to': dt_to,
                    'timeoff_address':  values['timeoff_address'],
                }
                tmp_leave = self.env['hr.leave'].sudo().new(values)
                tmp_leave._onchange_request_parameters()
                values  = tmp_leave._convert_to_write(tmp_leave._cache)
                mytimeoff = self.env['hr.leave'].sudo().create(values)
                temp_id = self.env.ref('leave_cim.email_email_template_id')
                temp_id.send_mail(mytimeoff.id, force_send=True)
                return {
                    'id': mytimeoff.id
                }



    @api.model
    def number_of_days_portal(self, values):
        user = self.env.user
        emp = self.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        self = self.sudo()
        # timeoff_type = self.env['hr.leave.type'].sudo().browse(2)
        # if timeoff_type.exclude_weekends:
        #     data = self._get_number_of_days(values['start'], values['start'], None)

        if (values['start'] and values['end']):
            dt_from = values['start']
            end = values['end']
            timeoff_type = values['timeoff_type']
            dt_from = datetime.strptime(dt_from, '%Y-%m-%d').date()
            dt_to =  datetime.strptime(end, '%Y-%m-%d').date()
            leaves_ids = self.env['hr.leave'].search([('employee_id', '=', emp.id), ('holiday_status_id', '=', timeoff_type)])
            type_ids = self.env['hr.leave.type'].search([('id', '=', timeoff_type)])
           
            basic_balance =  type_ids.max_leaves
            remaining_balance =  type_ids.virtual_remaining_leaves

            number_of_days = self._get_number_of_days(dt_from, dt_to, emp)['days']
            my_time = datetime.min.time()
            tz = self.env.user.tz if self.env.user.tz else 'UTC'  # custom -> already in UTC
            date_from = timezone(tz).localize(datetime.combine(dt_from, my_time)).astimezone(UTC).replace(tzinfo=None)
            date_to = timezone(tz).localize(datetime.combine(dt_to, my_time)).astimezone(UTC).replace(tzinfo=None)
            number_of_days = self.portal_get_number_of_days(date_from, date_to, 'ex')
            number_of_days = int(number_of_days['days'])
            remaining = remaining_balance - number_of_days
            if number_of_days:
                return {
                    'id': number_of_days,
                    'date_to': number_of_days,
                    'current': remaining_balance,
                    'requested': number_of_days,
                    'remaining': remaining,
                }
            else:
                return {
                    'errors': _('Enter Start Date !')
                }
    def team_action_validate(self, values):
        random_code = random.randint(9, 50000)
        timenow = datetime.now() + timedelta(minutes=2)
        for timeoff in self:
            timeoff_values = {
                'conf_code': random_code,
                'expiry_conf_code': timenow,
                'conf_action_type': 'Validate',
            }
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                if timeoff_rec:
                    timeoff_rec.sudo().write(timeoff_values)
                    timeoff_rec._onchange_request_parameters()
                    temp_id = self.env.ref('employee_portal_timeoff.team_action_confirm_template_id')
                    temp_id.send_mail(timeoff_rec.id, force_send=True)



    def team_action_validate2(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['conf_code']):
            return {
                'errors': _('Code required !')
            }
        for timeoff in self:
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                code = values['conf_code']
                timenow = datetime.now()
                if code == timeoff_rec.conf_code and timenow < timeoff_rec.expiry_conf_code:
                    if timeoff_rec:
                        timeoff_rec.sudo().action_validate()
                        temp_id = self.env.ref('leave_cim.aprove_email_email_template_id')
                        temp_id.sudo().send_mail(timeoff_rec.id, force_send=True)
                        return {
                            'id': timeoff_rec.id
                        }
                else:
                    return {
                        'errors': _('Invalid Or Expired Code !')
                    }




    def team_action_ref(self, values):
        random_code = random.randint(9, 50000)
        timenow = datetime.now() + timedelta(minutes=2)
        for timeoff in self:
            timeoff_values = {
                'conf_code': random_code,
                'expiry_conf_code': timenow,
                'conf_action_type': 'Refuse',
            }
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                if timeoff_rec:
                    timeoff_rec.sudo().write(timeoff_values)
                    timeoff_rec._onchange_request_parameters()
                    temp_id = self.env.ref('employee_portal_timeoff.team_action_confirm_template_id')
                    temp_id.send_mail(timeoff_rec.id, force_send=True)



    def team_action_ref2(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['conf_code']):
            return {
                'errors': _('Code required !')
            }
        for timeoff in self:
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                code = values['conf_code']
                timenow = datetime.now()
                if code == timeoff_rec.conf_code and timenow < timeoff_rec.expiry_conf_code:
                    if timeoff_rec:
                        return {
                            'id': timeoff_rec.id
                        }
                else:
                    return {
                        'errors': _('Invalid Or Expired Code !')
                    }

    def team_action_ref2sign(self, task_id):
        team = self.env['hr.leave'].sudo().browse(task_id)
        team.sudo().action_refuse()
        temp_id = self.env.ref('leave_cim.refuse_email_email_template_id')
        temp_id.send_mail(task_id, force_send=True)





    def team_action_confirm(self, values):
        random_code = random.randint(9, 50000)
        timenow = datetime.now() + timedelta(minutes=2)
        for timeoff in self:
            timeoff_values = {
                'conf_code': random_code,
                'expiry_conf_code': timenow,
                'conf_action_type': 'Confirm',
            }
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                if timeoff_rec:
                    timeoff_rec.sudo().write(timeoff_values)
                    timeoff_rec._onchange_request_parameters()
                    temp_id = self.env.ref('employee_portal_timeoff.team_action_confirm_template_id')
                    temp_id.send_mail(timeoff_rec.id, force_send=True)



    def team_action_confirm2(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['conf_code']):
            return {
                'errors': _('Code required !')
            }
        for timeoff in self:
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                code = values['conf_code']
                timenow = datetime.now()
                if code == timeoff_rec.conf_code and timenow < timeoff_rec.expiry_conf_code:
                    if timeoff_rec:
                        timeoff_rec.sudo().action_confirm()
                        temp_id = self.env.ref('leave_cim.aprove_email_email_template_id')
                        temp_id.sudo().send_mail(timeoff_rec.id, force_send=True)
                        return {
                            'id': timeoff_rec.id
                        }
                else:
                    return {
                        'errors': _('Invalid Or Expired Code !')
                    }





    def team_action_approve(self, values):
        random_code = random.randint(9, 50000)
        timenow = datetime.now() + timedelta(minutes=2)
        for timeoff in self:
            timeoff_values = {
                'conf_code': random_code,
                'expiry_conf_code': timenow,
                'conf_action_type': 'Approve',
            }
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                if timeoff_rec:
                    timeoff_rec.sudo().write(timeoff_values)
                    timeoff_rec._onchange_request_parameters()
                    temp_id = self.env.ref('employee_portal_timeoff.team_action_confirm_template_id')
                    temp_id.send_mail(timeoff_rec.id, force_send=True)

                    
    def team_action_approve2(self, values):

        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['conf_code']):
            return {
                'errors': _('Code required !')
            }
        for timeoff in self:
            if values['timeoffID']:
                timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
                code = values['conf_code']
                timenow = datetime.now()
                if code == timeoff_rec.conf_code and timenow < timeoff_rec.expiry_conf_code:
                    if timeoff_rec:
                        return {
                            'id': timeoff_rec.id
                        }
                else:
                    return {
                        'errors': _('Invalid Or Expired Code !')
                    }
    def team_action_approveandsign(self, task_id):
        shash = random.getrandbits(128)

        newhash = str("%032x" % shash)
        team = self.env['hr.leave'].sudo().browse(task_id)
        team.sudo().write({'state': 'validate1'})
        temp_id = self.env.ref('leave_cim.aprove_email_email_template_id')
        today = datetime.today()
        team.sudo().write({'leave_signed_date': today})
        team.sudo().write({'s_leave_signed_date': today})
        team.sudo().write({'leave_signed_hash': newhash})
        temp_id.send_mail(task_id, force_send=True)

    def super_team_action_approveandsign(self, task_id):
        shash = random.getrandbits(128)

        newhash = str("%032x" % shash)
        team = self.env['hr.leave'].sudo().browse(task_id)
        team.sudo().action_validate()
        today = datetime.today()
        team.sudo().write({'s_leave_signed_date': today})
        team.sudo().write({'s_leave_signed_hash': newhash})
        temp_id = self.env.ref('leave_cim.aprove_email_email_template_id')
        temp_id.send_mail(task_id, force_send=True)


class LeaveType(models.Model):
    _inherit = "hr.leave.type"

    def name_get_only(self):
        if not self._context.get('employee_id'):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(LeaveType, self).name_get()
        res = []
        for record in self:
            name = record.name
            if record.allocation_type != 'no':
                name = "%(name)s" % {
                    'name': name,
                    'count': _('%g remaining out of %g') % (
                        float_round(record.virtual_remaining_leaves, precision_digits=2) or 0.0,
                        float_round(record.max_leaves, precision_digits=2) or 0.0,
                    ) + (_(' hours') if record.request_unit == 'hour' else _(' days'))
                }
            res.append((record.id, name))
        return res


class PermissionRequests(models.Model):
    _inherit = "hr.permission"



    permission_signature = fields.Binary('Signature', help='Signature received through the portal.', copy=False, attachment=True)
    permission_signed_by = fields.Char('Signed By', help='Name of the person that signed the task.', copy=False)

    r_permission_signature = fields.Binary('Signature', help='Signature received through the portal.', copy=False, attachment=True)
    r_permission_signed_by = fields.Char('Signed By', help='Name of the person that signed the task.', copy=False)

    def _default_access_token(self):
        return str(uuid.uuid4())


    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
    
    def has_to_be_signed(self):
        return not self.permission_signature

    def has_to_be_signed2(self):
        return not self.r_permission_signature
    def team_action_approveandsign(self, task_id):
        team = self.env['hr.permission'].sudo().browse(task_id)
        team.sudo().action_approve()
        temp_id = self.env.ref('employee_portal_timeoff.aprove_email_email_template_id')
        temp_id.send_mail(task_id, force_send=True)

    def team_action_ref2sign(self, task_id):
        team = self.env['hr.permission'].sudo().browse(task_id)
        team.sudo().action_refuse()
        temp_id = self.env.ref('employee_portal_timeoff.refuse_email_email_template_id')
        temp_id.send_mail(task_id, force_send=True)

    @api.model
    def create_permission_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['req_type'] and values['date_time'] and values['reason']):
            return {
                'errors': _('All fields are required !')
            }
        values = {
            'employee_id': self.env.user.employee_id.id,
            'req_type': values['req_type'],
            'date_time': values['date_time'],
            'reason': values['reason'],
        }
        tmp_leave = self.env['hr.permission'].sudo().new(values)
        values  = tmp_leave._convert_to_write(tmp_leave._cache)
        mytimeoff = self.env['hr.permission'].sudo().create(values)
        return {
            'id': mytimeoff.id
        }

class LeaveReturnDeclaration(models.Model):
    _inherit = "hr.leavereturn"
    
    @api.model
    def create_return_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['reference_ret'] and values['request_date'] and values['holiday_status_id']):
            return {
                'errors': _('All fields are required !')
            }

        reference = values['reference_ret']
        employee_id = self.env.user.employee_id.id
        leaves = self.env['hr.leave'].search([('reference', '=', reference),('employee_id', '=', employee_id)], limit=1)
        if reference:
            if leaves.id:
                values = {
                    'leave_related': values['reference_ret'],
                    'date_time': values['request_date'],
                }
                tmp_leave = self.env['hr.leavereturn'].sudo().new(values)
                values  = tmp_leave._convert_to_write(tmp_leave._cache)
                mytimeoff = self.env['hr.leavereturn'].sudo().create(values)
                return {
                    'id': mytimeoff.id
                }
            else:
                return {
                    'errors': _('There is no leaves related to this Reference !')
                }
