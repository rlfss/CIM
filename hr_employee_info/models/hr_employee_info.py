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

class HrEmployeeInfo(models.Model):
    _name = "hr.employee.info"
    _description = "Employee info"


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_num = fields.Char(string="Employee Number", store=True)

    employee_status = fields.Many2one('hr.employee.status', string="Employee Status", store=True)

    health_status = fields.Char(string="Health Status", store=True)
    mother_name = fields.Char(string="Mother Name", store=True)
    mobile = fields.Char(string="Private Mobile", groups="hr.group_hr_user")

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
    financial_id = fields.Char(string='Financial number', groups="hr.group_hr_user", tracking=True)
    warranty_id = fields.Char(string='Warranty card number', groups="hr.group_hr_user", tracking=True)

    family_registration_id = fields.Char(string='Family Registration Number', groups="hr.group_hr_user", tracking=True)
    family_booklet_id = fields.Char(string='Family Booklet Number', groups="hr.group_hr_user", tracking=True)

    issuing_booklet = fields.Char(string='Issuing authority', groups="hr.group_hr_user", tracking=True)
    family_paper_id = fields.Char(string='Family paper number', groups="hr.group_hr_user", tracking=True)

    family_id = fields.Many2one(
        'hr.employee.family', 'Family', groups="hr.group_hr_user", tracking=True)

    qualifications = fields.Many2one(
        'hr.employee.qualifications', 'Qualifications', groups="hr.group_hr_user", tracking=True)


class EmployeeStatus(models.Model):
    _name = 'hr.employee.status'
    _description = "Employee status"

    name = fields.Char(string="Employee Status", store=True)


class EmployeeFamily(models.Model):
    _name = 'hr.employee.family'
    _description = "Employee Family"

    name = fields.Char(string="Name", store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", default="male", tracking=True)
    birthday = fields.Date('Date of Birth', groups="hr.group_hr_user", tracking=True)

    relation = fields.Char(string="Relative Relation", store=True)
    relation_status = fields.Char(string="Social and occupational status", store=True)
    national_id = fields.Char(string='National No', groups="hr.group_hr_user", tracking=True)




class EmployeeQualifications(models.Model):
    _name = 'hr.employee.qualifications'
    _description = "Employee Qualifications"

    educational_level = fields.Many2one(
        'hr.employee.educational', 'Educational level', groups="hr.group_hr_user", tracking=True)


    specialization = fields.Char(string="Specialization", store=True)
    graduation_place = fields.Date('Graduation place', groups="hr.group_hr_user", tracking=True)

    graduation_date = fields.Date(string="Graduation Date", groups="hr.group_hr_user", tracking=True)

    graduation_type = fields.Selection([
        ('general', 'General'),
        ('private', 'Private')
    ], string="Type", default="general", tracking=True)


class EmployeeEducational(models.Model):
    _name = 'hr.employee.educational'
    _description = "Employee Educational"

    name = fields.Char(string="Educational level", store=True)

