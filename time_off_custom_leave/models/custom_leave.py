# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil import relativedelta
import datetime
from odoo.exceptions import ValidationError


class CustomLeave(models.Model):
    _inherit = 'hr.leave.type'
    _description = 'Custom Leaves'

    custom_leave = fields.Boolean(string="Custom Leave", default=False)
    fixed_period = fields.Float(string="Fixed Period", default=1)
    only_time_granted = fields.Boolean(string="Only time Granted", default=False)
    applicable_for = fields.Selection(
        [('both', 'Both'),
         ('female', 'Female')], string="Applicable For", default='both')
    allocated_method = fields.Selection(
        [('manual', 'Manual'),
         ('auto', 'Automated')], string="Allocated Method", default='manual')
    automated_allocation = fields.Selection([('based', 'Based on Experience'), ('custom', 'Custom Period')],
                                            default='based')
    number_per_interval = fields.Float("Number of unit per interval", default=1)
    interval_number = fields.Integer("Number of unit between two intervals", default=1)
    unit_per_interval = fields.Selection([
        ('days', 'Day(s)')
    ], string="Unit of time added at each interval", default='days')
    interval_unit = fields.Selection([
        ('months', 'Month'),
        ('years', 'Year')
    ], string="Unit of time between two intervals", default='months')
    date_to = fields.Date()


class AddAttachment(models.Model):
    _inherit = 'hr.leave'
    _description = 'Add Attachment'

    attachment = fields.Many2many('ir.attachment', string="Attachment", copy=False)
    cus_level = fields.Boolean(string="cus level", related='holiday_status_id.custom_leave')

    @api.onchange('holiday_status_id')
    def _get_fixed_period(self):
        if self.holiday_status_id:
            if self.holiday_status_id.custom_leave == True:
                self.number_of_days = self.holiday_status_id.fixed_period

    # to make employee can't request this type again
    def action_approve(self):
        res = super(AddAttachment, self).action_approve()
        if self.holiday_status_id.custom_leave == True and self.holiday_status_id.applicable_for == 'both' and self.holiday_status_id.only_time_granted == True:
            if self.employee_id.employee_time_granted == False:
                self.employee_id.employee_time_granted = True
        return res

    @api.constrains('holiday_status_id')
    def _check_holiday_custom(self):
        for rec in self:
            # for leaves die only
            if (
                    rec.holiday_status_id.custom_leave == True and rec.holiday_status_id.applicable_for == 'both' and rec.holiday_status_id.only_time_granted == False):
                if rec.employee_id.gender == 'male' or rec.employee_id.gender == 'female':
                    if rec.number_of_days > rec.holiday_status_id.fixed_period:
                        raise ValidationError(_("Duration must be ") + str(rec.holiday_status_id.fixed_period))
            # for wedding and hej
            elif (
                    rec.holiday_status_id.custom_leave == True and rec.holiday_status_id.applicable_for == 'both' and rec.holiday_status_id.only_time_granted == True):
                if rec.employee_id.gender == 'male' or rec.employee_id.gender == 'female':
                    if rec.employee_id.employee_time_granted == True:
                        raise ValidationError(_("This type only time granted "))
                    elif rec.number_of_days > rec.holiday_status_id.fixed_period:
                        raise ValidationError(_("Duration must be ") + str(rec.holiday_status_id.fixed_period))

            # for women only
            elif rec.holiday_status_id.custom_leave == True and rec.holiday_status_id.applicable_for == 'female':
                if rec.employee_id.gender == 'female':
                    if rec.number_of_days > rec.holiday_status_id.fixed_period:
                        raise ValidationError(_("Duration must be ") + str(rec.holiday_status_id.fixed_period))
                elif rec.employee_id.gender != 'female':
                    raise ValidationError(_("This leave Applicable for only Female"))


class HrAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.model
    def create_employee_allocation(self):
        Employees = self.env['hr.employee'].search([])
        Timeeofftyp = self.env['hr.leave.type'].search(
            [('allocated_method', '=', 'auto'), ('automated_allocation', '=', 'based')], limit=1)
        today = datetime.datetime.today()
        t_today = today.day
        for employee in Employees:
            if employee.contract_id.state == 'open':
                started_date = datetime.datetime.strptime(
                    employee.started_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
                s_today = started_date.day
                if t_today == s_today:
                    allocation_vals = {
                        'name': _('Annual Leave for ') + employee.name,
                        'holiday_status_id': Timeeofftyp.id,
                        'allocation_type': 'regular',
                        'holiday_type': 'employee',
                        'number_of_days': employee.legal_leave_monthly_allocation,
                        'employee_id': employee.id
                    }
                    self.env['hr.leave.allocation'].create(allocation_vals)

    @api.model
    def create_holiday_custom_allocation(self):
        Employees = self.env['hr.employee'].search([])
        Timeeofftyp = self.env['hr.leave.type'].search(
            [('allocated_method', '=', 'auto'), ('automated_allocation', '=', 'custom'),
             ('unit_per_interval', '=', 'days'),('interval_unit','=','years')])
        today = datetime.datetime.today()
        t_today = today.day
        t_month = today.month
        for employee in Employees:
            for tmf in Timeeofftyp:
                if employee.contract_id.state == 'open':
                    if t_today == 1 and t_month == 1:
                        allocation_vals = {
                            'name': _('Custom Leave for ') + employee.name,
                            'holiday_status_id': tmf.id,
                            'allocation_type': 'regular',
                            'holiday_type': 'employee',
                            'number_of_days': tmf.number_per_interval,
                            'employee_id': employee.id
                        }
                        self.env['hr.leave.allocation'].create(allocation_vals)
