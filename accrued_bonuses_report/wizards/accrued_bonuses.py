# -*- coding: utf-8 -*-

from odoo import fields, models


class CreateWizard(models.TransientModel):
    _name = 'accrued.bonuses'
    _description = 'Accrued Bonuses'

    type = fields.Selection([
        ('all_employees', 'All Employees'),
        ('employee', 'Employee'),
        ('department', 'Department')
    ], string="For", default='all_employees')
    employee_name = fields.Many2many('hr.employee',string="Employee Name")
    department_name = fields.Many2many('hr.department',string="Department Name")
    date = fields.Date("Date",default=fields.Date.today(),required=True)

    def print_report_excel(self):
        if self.type == 'employee':
            exist_employee = self.env['hr.employee'].search([('id','in' ,self.employee_name.ids)])
        elif self.type == 'department':
            exist_employee = self.env['hr.employee'].search([('department_id', 'in', self.department_name.ids)])
        elif self.type == 'all_employees':
            exist_employee = self.env['hr.employee'].search([])

        data = {'employee': []}
        for empl in exist_employee:
            data['employee'].append({
                'employee_num' : empl.employee_num,
                'name': empl.name,
                'department_name' : empl.department_id.name,
                'appointmentdegree' : empl.appointmentdegree.name,
                'currentdegree' : empl.currentdegree.name
            })

        return self.env.ref('accrued_bonuses_report.report_accrued_bounses_xls').report_action(self,data=data)



