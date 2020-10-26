from odoo import fields, models, api


class EmployeeCertifications(models.Model):
    _name = 'hr.employee.certification'

    name = fields.Char("Certification")
