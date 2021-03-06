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
    employee_branch = fields.Many2one('hr.employee.branch', string="Employee Branch", store=True)

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
    id_issue_place = fields.Char(string="Identification issue place", groups="hr.group_hr_user", tracking=True)

    passport_issue_date = fields.Date(string="Passport issue date", groups="hr.group_hr_user", tracking=True)
    passport_issue_place = fields.Char(string="Passport issue place", groups="hr.group_hr_user", tracking=True)

    driver_license_id = fields.Char(string='Driver License No', groups="hr.group_hr_user", tracking=True)
    driver_license_type = fields.Char(string='Driver License Type', groups="hr.group_hr_user", tracking=True)


    national_id = fields.Char(string='National No', groups="hr.group_hr_user", tracking=True)
    financial_id = fields.Char(string='Financial number', groups="hr.group_hr_user", tracking=True)
    warranty_id = fields.Char(string='Warranty card number', groups="hr.group_hr_user", tracking=True)

    family_registration_id = fields.Char(string='Family Registration Number', groups="hr.group_hr_user", tracking=True)
    family_booklet_id = fields.Char(string='Family Booklet Number', groups="hr.group_hr_user", tracking=True)

    issuing_booklet = fields.Char(string='Issuing authority', groups="hr.group_hr_user", tracking=True)
    family_paper_id = fields.Char(string='Family paper number', groups="hr.group_hr_user", tracking=True)

    social_situation = fields.Selection([
        ('single', 'اعزب'),
        ('married', 'متزوج'),
        ('marriedch', 'متزوج ويعول'),
        ('divorced', 'مطلق'),
    ], string='Social Situation', tracking=True)

    family_id = fields.One2many(
        'hr.employee.family', 'employee_id', string="Family", groups="hr.group_hr_user", tracking=True)

    qualifications = fields.One2many(
        'hr.employee.qualifications', 'employee_id', string="Qualifications", groups="hr.group_hr_user", tracking=True)
    training = fields.One2many(
        'hr.employee.training', 'employee_id', string="Training Courses", groups="hr.group_hr_user", tracking=True)


    guardianship = fields.One2many(
        'hr.employee.guardianship', 'employee_id', string="Guardianship", groups="hr.group_hr_user", tracking=True)




 
    appointmentdegree = fields.Many2one('hr.employee.appointmentdegree', string="Appointment Degree", tracking=True)
    appointmentsalary = fields.Many2one('hr.employee.appointmentsalary', string="Appointment Salary", tracking=True)

    currentdegree = fields.Many2one('hr.employee.currentdegree', string="Current Degree", tracking=True)
    currentdegree_date = fields.Date(string="Date of acquiring Current Degree", groups="hr.group_hr_user", tracking=True)
    
    currentsalary = fields.Many2one('hr.employee.currentsalary', string="Current Salary", tracking=True)
    currentsalary_date = fields.Date(string="Date of acquiring Current Salary", groups="hr.group_hr_user", tracking=True)




    hiring_date = fields.Date('Hiring Date', compute='_compute_contract_data', readonly=True)
    started_date = fields.Date('Work Started Date', compute='_compute_contract_data', readonly=True)
    first_work_date = fields.Date('First Work Date', compute='_compute_contract_data', readonly=True)
    position_type = fields.Many2one('hr.contract.positiontype', compute='_compute_contract_data', string="Position Type", readonly=True)


    appointment_decision = fields.Char('Appointment Decision No.', compute='_compute_contract_data', readonly=True)

    def _compute_contract_data(self):
        """ get the lastest contract """
        Contract = self.env['hr.contract']
        for employee in self:
            mycontract = Contract.search([('employee_id', '=', employee.id)], order='date_start desc', limit=1)
            employee.hiring_date = None
            employee.started_date = None
            employee.first_work_date = None
            employee.position_type = None
            employee.appointment_decision = None
            for line in mycontract:
                if employee.hiring_date:
                    employee.hiring_date = line.hiring_date
                if employee.started_date:
                    employee.started_date = line.started_date
                if employee.first_work_date:
                    employee.first_work_date = line.first_work_date
                if employee.position_type:
                    employee.position_type = line.position_type
                if employee.appointment_decision:
                    employee.appointment_decision = line.appointment_decision


class EmployeeDegreeAppointment(models.Model):
    _name = 'hr.employee.appointmentdegree'
    _description = "Employee Appointment Degree"

    name = fields.Char(string="Appointment Degree", store=True)


class EmployeesalaryAppointment(models.Model):
    _name = 'hr.employee.appointmentsalary'
    _description = "Employee Appointment Salary"

    name = fields.Char(string="Appointment Salary", store=True)

class EmployeeDegreeCurrent(models.Model):
    _name = 'hr.employee.currentdegree'
    _description = "Employee Current degree"

    name = fields.Char(string="Current Degree", store=True)

class Employeesalarycurrent(models.Model):
    _name = 'hr.employee.currentsalary'
    _description = "Employee Current Salary"

    name = fields.Char(string="Current Salary", store=True)


class EmployeeStatus(models.Model):
    _name = 'hr.employee.status'
    _description = "Employee status"

    name = fields.Char(string="Employee Status", store=True)

class EmployeeBranch(models.Model):
    _name = 'hr.employee.branch'
    _description = "Employee Branch"

    name = fields.Char(string="Employee Branch", store=True)


class EmployeeFamily(models.Model):
    _name = 'hr.employee.family'
    _description = "Employee Family"

    employee_id = fields.Many2one('hr.employee', string="Employee")
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
    employee_id = fields.Many2one('hr.employee', string="Employee")

    educational_level = fields.Many2one(
        'hr.employee.educational', 'Educational level', groups="hr.group_hr_user", tracking=True)


    specialization = fields.Many2one(
        'hr.employee.educational.specialization', string="Specialization", tracking=True)
    graduation_place = fields.Many2one(
        'hr.employee.educational.place', 'Graduation place', groups="hr.group_hr_user", tracking=True)

    graduation_date = fields.Char(string="Graduation Date", groups="hr.group_hr_user", tracking=True)

    graduation_type = fields.Selection([
        ('general', 'General'),
        ('private', 'Private')
    ], string="Type", tracking=True)


class EmployeeEducational(models.Model):
    _name = 'hr.employee.educational'
    _description = "Employee Educational"

    name = fields.Char(string="Educational level", store=True)


class EmployeeEducationalSpecialization(models.Model):
    _name = 'hr.employee.educational.specialization'
    _description = "Employee Specialization"

    name = fields.Char(string="Educational Specialization", store=True)

class EmployeeEducationalplace(models.Model):
    _name = 'hr.employee.educational.place'
    _description = "Employee place"

    name = fields.Char(string="Educational place", store=True)


class EmployeeTrainingCourses(models.Model):
    _name = 'hr.employee.training'
    _description = "Employee Training Courses"


    employee_id = fields.Many2one('hr.employee', string="Employee")

    training_type = fields.Selection([
        ('in', 'In Country'),
        ('out', 'Out Country')
    ], string="Type", default="general", tracking=True)
    course_field = fields.Char(string="Course field", store=True)

    training_date_from = fields.Date(string="Date From", groups="hr.group_hr_user", tracking=True)
    training_date_to = fields.Date(string="Date To", groups="hr.group_hr_user", tracking=True)
    training_place = fields.Char('Training place', groups="hr.group_hr_user", tracking=True)

    degree = fields.Char(string="Degree", store=True)

class EmployeeTrainingGuardianship(models.Model):
    _name = 'hr.employee.guardianship'
    _description = "Employee Guardianship"

    employee_id = fields.Many2one('hr.employee', string="Employee")


    guardianship_type = fields.Many2one(
        'hr.employee.guardianship.type', 'Type', groups="hr.group_hr_user", tracking=True)


    receipt_date = fields.Date(string="Receipt Date", groups="hr.group_hr_user", tracking=True)
    lock_date = fields.Date(string="Lock Date", groups="hr.group_hr_user", tracking=True)
    statement = fields.Char(string="Statement", store=True)

    value = fields.Char(string="Value", store=True)

class EmployeeTrainingGuardianshipType(models.Model):
    _name = 'hr.employee.guardianship.type'
    _description = "Employee Guardianship Type"

    name = fields.Char(string="Guardianship Type", store=True)

