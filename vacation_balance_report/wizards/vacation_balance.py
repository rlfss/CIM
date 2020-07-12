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

    ], string="Leave Type", default='all_time_off')
    date = fields.Date("Date", default=fields.Date.today(), required=True)

    def print_report_excel(self):
        exist_employee = []

        if self.type == 'employee':
            exist_employee = self.env['hr.employee'].search([('id', 'in', self.employee_name.ids)])
        elif self.type == 'department':
            exist_employee = self.env['hr.employee'].search([('department_id', 'in', self.department_name.ids)])
        elif self.type == 'all_employees':
            exist_employee = self.env['hr.employee'].search([])
        # if self.leave_type == 's_time_off':
        #     leaves_ids = self.env['hr.leave.type'].search([('id','in' ,self.leave_name.ids)])

        data = {'employee': []}
        for empl in exist_employee:
            leave_report = self.env['hr.leave.allocation'].with_context({'default_employee_id':empl.id}).search([('employee_id', '=', empl.id)])

            if self.type == 's_time_off' :
                leaves = leave_report.filtered(lambda l: l.holiday_status_id.id in self.leave_name.ids)
            else :
                leaves = leave_report.filtered(lambda l: l.holiday_status_id.id > 0)
            # leaves = list(dict.fromkeys(leaves))
            res = []
            for i in leaves:
                if i not in res:
                    res.append(i)

            data['employee'].append({
                'employee_num': empl.employee_num,
                'name': empl.name,
                'department_name': empl.department_id.name,
                'leaves': [{
                    'leave_name': leave.holiday_status_id.name,
                    'remaining_days': leave.holiday_status_id.remaining_leaves,
                    'unit' : leave.holiday_status_id.request_unit
                } for leave in res]

            })

        # leave_data = {'s_time_off' :[]}
        # for leave in leaves_ids:
        #     leave_data['s_time_off'].append({
        #         'leave_n': leave.holiday_status_id.name
        #
        #     })

        return self.env.ref('vacation_balance_report.report_vacation_balance_xls').report_action(self, data=data)
