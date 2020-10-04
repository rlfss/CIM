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

class LeaveReturnDeclaration(models.Model):
    _name = "hr.leavereturn"
    _description = "Leave Return Declaration"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'



    name = fields.Char('Reference', readonly=True , default=lambda x: str('New')) #default=default_randint_value
    leave_related = fields.Char(string='Related Leave') #default=default_randint_value

    leave_id = fields.Many2one("hr.leave", string="Time Off ID", compute='_onchange_leave_related')
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, readonly=True, index=True)

    holiday_status_id = fields.Many2one("hr.leave.type", string="Time Off Type", compute='_onchange_leave_related')

    date_time = fields.Date('Return Date', required=True)
    user_id = fields.Many2one('res.users')

    @api.onchange('leave_related')
    def _onchange_leave_related(self):
        leaves = self.env['hr.leave'].search([('reference', '=', self.leave_related),('employee_id', '=', self.employee_id.id)], limit=1)
        if self.leave_related:
            if leaves.id:
                for leave in leaves:
                        for line in self:
                            line.leave_id = leaves.id
                            line.holiday_status_id = leave.holiday_status_id.id
            else:
                raise UserError(_('There is no leaves related to this Reference'))




    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, tracking=True, copy=False, default='draft',
        help="The status is set to 'To Submit', when a time off request is created." +
        "\nThe status is 'To Approve', when time off request is confirmed by user." +
        "\nThe status is 'Refused', when time off request is refused by manager." +
        "\nThe status is 'Approved', when time off request is approved by manager.")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.leavereturn') or _('New')
            result = super(LeaveReturnDeclaration, self).create(vals)
            return result



    def action_confirm(self):
        self.write({'state': 'confirm'})
        return True

    def action_approve(self):
        self.write({'state': 'validate1'})
        return True

    def action_validate(self):
        self.write({'state': 'validate'})
        return True

    def action_refuse(self):
        self.write({'state': 'refuse'})
        return True
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_return_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id('hr_permission.mail_template_leave_return', raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        ctx = {
            'default_model': 'hr.leavereturn',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            #'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }