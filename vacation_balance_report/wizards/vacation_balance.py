# -*- coding: utf-8 -*-

from odoo import fields, models


class CreateWizard(models.TransientModel):
    _name = 'vacation.balance'
    _description = 'Vacation Balance'

    type = fields.Selection([
        ('all_employees', 'All Employees'),
        ('employee', 'Employee'),
        ('department', 'Department')
    ], string="For", default='all_employees')
    employee_name = fields.Many2many('hr.employee', string="Employee Name")
    department_name = fields.Many2many('hr.department', string="Department Name")
    leave_name = fields.Many2many('hr.leave.type', string="Leave Name")
    leave_type = fields.Selection([
        ('all_time_off', 'All Time Off'),
        ('s_time_off', 'Specific Time Off')

    ], string="Leave Type", default='all_time_off',readonly=False)
    date = fields.Date("Date", default=fields.Date.today(), required=True)

    def print_report_excel(self):
        exist_employee = []

        if self.type == 'employee':
            exist_employee = self.env['hr.employee'].search([('id', 'in', self.employee_name.ids)])
        elif self.type == 'department':
            exist_employee = self.env['hr.employee'].search([('department_id', 'in', self.department_name.ids)])
        elif self.type == 'all_employees':
            exist_employee = self.env['hr.employee'].search([])

        data = {'employee': []}
        for empl in exist_employee:
            employees = {
                'employee_num': empl.employee_num,
                'name': empl.name,
                'department_name': empl.department_id.name,
                'leaves': []

            }
            leaves_id = self.leave_name if self.leave_type == 's_time_off' else self.env['hr.leave.type'].search([])
            for leave in leaves_id :
                total_leave_days, total_time_off, remaining_days = self.get_leave_data(empl.id,leave)
                employees['leaves'].append({
                    'leave_name': leave.name,
                    'basic_balance': total_time_off,
                    'balance_consumed': total_leave_days,
                    'remaining_days': remaining_days,
                })
            data['employee'].append(employees)


        return self.env.ref('vacation_balance_report.report_vacation_balance_xls').report_action(self, data=data)

    def get_leave_data(self, employee_id, leave_type_id):

        leaves_ids = self.env['hr.leave'].search(
            [('employee_id', '=', employee_id), ('holiday_status_id', '=', leave_type_id.id)])
        total_leave_days = sum(leaves_ids.mapped('number_of_days'))
        total_time_off = leave_type_id.max_leaves
        remaining_days = total_time_off - total_leave_days

        return total_leave_days, total_time_off, remaining_days