# -*- coding: utf-8 -*-

import logging
import math

from collections import namedtuple

from datetime import datetime, time
from pytz import timezone, UTC

from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class HolidaysType(models.Model):
    _name = "hr.leave.type"
    _inherit = "hr.leave.type"

    max_con_duration = fields.Float(string='Maximum Continuous Duration')
    max_int_duration = fields.Float(string='Maximum Intermittent Duration')
    lead_time = fields.Float(string='Lead Time')


    use_2fa = fields.Boolean(string="Enable 2FA Verification")

    exclude_weekends = fields.Boolean(string="Exclude Week End Holidays", default=True)

    validation_type = fields.Selection([
        ('no_validation', 'No Validation'),
        ('hr', 'Time Off Officer'),
        ('manager', 'Team Leader'),
        ('supermanager', 'Team Leader and Upper Manager'),
        ('both', 'Team Leader and Time Off Officer')], default='hr', string='Validation')

class Employee(models.Model):
    _inherit = 'hr.employee'


    is_g_manager = fields.Boolean('Is Manager')

    supermanager_id = fields.Many2one('hr.employee', 'Upper Manager')

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        for holiday in self:
            holiday.supermanager_id = holiday.parent_id.parent_id.id

class Holidays(models.Model):
    _name = "hr.leave"
    _inherit = "hr.leave"

    timeoff_address = fields.Char(string='Address During Time Off')


    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        for holiday in self:
            if holiday.holiday_status_id.validation_type == 'supermanager':
                current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                if current_employee.id == self.department_id.manager_id.id or  current_employee.id == self.employee_id.department_id.parent_id.manager_id.id:
                    if current_employee.id == self.department_id.manager_id.id:
                        if current_employee.id == self.department_id.parent_id.manager_id.id:
                            if current_employee.is_g_manager:
                                holiday.can_approve = True
                            else:
                                holiday.can_approve = False
                        else:
                            holiday.can_approve = True
                    else:
                        holiday.can_approve = True
                else:
                    holiday.can_approve = False
            else:
                try:
                    if holiday.state == 'confirm' and holiday.holiday_status_id.validation_type == 'both':
                        holiday._check_approval_update('validate1')
                    else:
                        holiday._check_approval_update('validate')
                except (AccessError, UserError):
                    holiday.can_approve = False
                else:
                    holiday.can_approve = True

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_reset(self):
        for holiday in self:
            if holiday.holiday_status_id.validation_type == 'supermanager':
                current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                if current_employee.id == self.department_id.manager_id.id or  current_employee.id == self.employee_id.department_id.parent_id.manager_id.id:
                    if current_employee.id == self.department_id.manager_id.id:
                        if current_employee.id == self.department_id.parent_id.manager_id.id:
                            if current_employee.is_g_manager:
                                holiday.can_reset = True
                            else:
                                holiday.can_reset = False
                        else:
                            holiday.can_reset = True
                    else:
                        holiday.can_reset = True
                else:
                    holiday.can_reset = False
            else:
                try:
                    holiday._check_approval_update('draft')
                except (AccessError, UserError):
                    holiday.can_reset = False
                else:
                    holiday.can_reset = True

    def _get_number_of_days(self, date_from, date_to, employee_id):
        if self.holiday_status_id.exclude_weekends :
            """ Returns a float equals to the timedelta between two dates given as string."""
            if employee_id:
                employee = self.env['hr.employee'].browse(employee_id)
                return employee._get_work_days_data(date_from, date_to)

            today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
                datetime.combine(date_from.date(), time.min),
                datetime.combine(date_from.date(), time.max), resource=None, domain=None, tz=None)

            hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to, resource=None, domain=None, tz=None)

            return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}
        else:
            total = date_to - date_from
            total = str(total)
            if len(total) > 7:
                days , hours = total.split(', ')
                day , d = days.split(' ')
                hour , m , s = hours.split(':')
                newdays = float(day) + 1.0
                # raise ValidationError(_(str(days) + ' ' + str(hours)))
                return {'days': newdays, 'hours': float(hour)}
            else:
                hour , m , s = total.split(':')
                # raise ValidationError(_(str(days) + ' ' + str(hours)))
                return {'days': float(1), 'hours': float(hour)}

    def portal_get_number_of_days(self, date_from, date_to, titype):
        if titype == 'ex' :
            """ Returns a float equals to the timedelta between two dates given as string."""
            today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
                datetime.combine(date_from, time.min),
                datetime.combine(date_from, time.max),
                False)

            hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to)

            return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}
        if titype == 'in' :
            total = date_to - date_from
            total = str(total)
            if len(total) > 7:
                days , hours = total.split(', ')
                day , d = days.split(' ')
                hour , m , s = hours.split(':')
                newdays = float(day) + 1.0
                # raise ValidationError(_(str(days) + ' ' + str(hours)))
                return {'days': newdays, 'hours': float(hour)}
            else:
                hour , m , s = total.split(':')
                # raise ValidationError(_(str(days) + ' ' + str(hours)))
                return {'days': float(1), 'hours': float(hour)}
