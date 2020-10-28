# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Contract(models.Model):
    _inherit = 'hr.contract'

    hiring_date = fields.Date('Hiring Date', default=fields.Date.today,
        help="hiring date.")
    started_date = fields.Date('Work Start Date', default=fields.Date.today,
        help="Work Started date.")
    first_work_date = fields.Date('First Work Date', default=fields.Date.today,
        help="First Work Date.")
    position_type = fields.Many2one('hr.contract.positiontype', string="Hiring Type")


    appointment_decision = fields.Char('Appointment Decision No.')

class ContractPositionType(models.Model):
    _name = 'hr.contract.positiontype'
    _description = 'Contract Position Type'

    name = fields.Char(string='Position Type', required=True)
