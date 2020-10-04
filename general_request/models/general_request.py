# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GeneralRequest(models.Model):
    _name = 'general.request'
    _description = 'General Request'
    _rec_name = 'request_type'

    request_type = fields.Selection([('r_badge','Request Badge'),('r_papers','Request Papers')],default='r_badge')
    description = fields.Char('Description')
    type = fields.Char('Type')
    quantity = fields.Float('Quantity')
    employee_id = fields.Many2one('hr.employee',"Employee")

# class HrEmployee(models.AbstractModel):
#     _inherit = 'hr.employee.base'
#
#     name = fields.Char(string="Employee Name",translate=True)