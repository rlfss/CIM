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

class PermissionRequests(models.Model):
    _name = "hr.permission"
    _description = "Permission Requests"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'


    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True, compute_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)

    name = fields.Char('Reference', readonly=True , default=lambda x: str('New')) #default=default_randint_value
    reason = fields.Text(string='Reason') #default=default_randint_value

    req_type = fields.Selection([
        ('in', 'In Late'),
        ('out', 'Out Early')], string='Permission Type', required=True)

    date_time = fields.Datetime('Date & time', default=fields.Datetime.now,required=True)
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
    
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True, ondelete="restrict",)


    manager_id = fields.Many2one('hr.employee', compute='_onchange_employee_id')
    
    def _onchange_employee_id(self):
        for holiday in self:
            holiday.manager_id = holiday.employee_id.parent_id.id

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.permission') or _('New')                
            result = super(PermissionRequests, self).create(vals)
            return result




    def action_approve(self):
        self.write({'state': 'validate'})
        return True

    def action_refuse(self):
        self.write({'state': 'refuse'})
        return True
        
    def action_draft(self):
        self.write({'state': 'draft'})
        return True
