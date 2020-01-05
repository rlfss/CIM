# -*- coding: utf-8 -*-

import base64
from random import choice
from string import digits
import itertools
from werkzeug import url_encode
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from odoo.addons.resource.models.resource_mixin import timezone_datetime

class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_num = fields.Char(string="Employee Number", store=True)

    employee_status = fields.Many2one('hr.employee.status', string="Employee Status", store=True)

    health_status = fields.Char(string="Health Status", store=True)
    mother_name = fields.Char(string="Mother Name", store=True)

    blood_group = fields.Selection([
        ('ap', 'A+'),
        ('an', 'A-'),
        ('bp', 'B+'),
        ('bn', 'B-'),
        ('op', 'O+'),
        ('on', 'O-'),
        ('abp', 'AB+'),
        ('abn', 'AB-')
    ], string='Blood Group', tracking=True)


    id_issue_date = fields.Date(string="Identification issue date", groups="hr.group_hr_user", tracking=True)

    passport_issue_date = fields.Date(string="Passport issue date", groups="hr.group_hr_user", tracking=True)
    
    national_id = fields.Char(string='National No', groups="hr.group_hr_user", tracking=True)




class EmployeeStatus(models.Model):
    _name = 'hr.employee.status'
    _description = "Employee status"

    name = fields.Char(string="Employee Status", store=True)
