# -*- coding: utf-8 -*-

from odoo import fields, models
from dateutil import relativedelta


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
            due_degree,due_salary,due_wage = self.get_degree_data(empl.id)
            print("due_salary",due_salary,"due_wage",due_wage)
            data['employee'].append({
                'employee_num' : empl.employee_num,
                'name': empl.name,
                'department_name' : empl.department_id.name,
                'work_start_date': empl.financial_statrted_date,
                'appointmentdegree' : empl.appointmentdegree.degree_no,
                'appointmentsalary' : empl.appointmentsalary.bonus,
                'appointmentwage' : empl.appointmentwage,
                'currentdegree' : empl.currentdegree.degree_no,
                'currentsalary' : empl.currentsalary.bonus,
                'currentwage' : empl.currentwage,
                'duedegree' : due_degree,
                'duesalary' : due_salary,
                'duewage' : due_wage,
            })

        return self.env.ref('accrued_bonuses_report.report_accrued_bounses_xls').report_action(self,data=data)


    def get_degree_data(self, employee_id):

        degree_ids = self.env['hr.employee'].search([('id', '=', employee_id)])
        current_work_date = degree_ids.financial_statrted_date
        current_degree = degree_ids.appointmentdegree
        current_salary = degree_ids.appointmentsalary
        current_wage = degree_ids.appointmentwage
        current_due_salary = current_degree.no_of_bonuses - current_salary.count
        y = relativedelta.relativedelta(self.date, current_work_date)
        no_years = y.years
        b = 1
        if no_years < b:
            new_degree = current_degree.degree_no
            get_degree = self.env['job.degree'].search([('degree_no', '=', new_degree)])
            due_degree = get_degree.degree_no
            due_salary = current_salary.count
            due_wage = current_wage
        elif no_years >= b and no_years <= current_due_salary:
            new_degree = current_degree.degree_no
            get_degree = self.env['job.degree'].search([('degree_no', '=', new_degree)])
            due_degree = get_degree.degree_no
            due_salary = current_salary.count + no_years
            due_wage = current_degree.basic_salary + (current_degree.bonuses_value * due_salary)
        elif no_years >=b and no_years > current_due_salary :
            new_degree = current_degree.degree_no + 1
            get_degree = self.env['job.degree'].search([('degree_no','=',new_degree)])
            due = (no_years - current_due_salary )
            print("no of bonuses",get_degree.no_of_bonuses,"due",due)
            if get_degree and due <= get_degree.no_of_bonuses:
                due_degree = get_degree.degree_no
                due_salary = (no_years - current_due_salary )
                due_wage = get_degree.basic_salary + (get_degree.bonuses_value * due_salary)
            elif get_degree and due > get_degree.no_of_bonuses:
                new_degree_2 = new_degree + 1
                get_degree_2 = self.env['job.degree'].search([('degree_no', '=', new_degree_2)])
                print("no of bonus",get_degree.no_of_bonuses,"new degree 2",new_degree_2)
                if get_degree_2:
                    due_degree = get_degree_2.degree_no
                    due_salary = (due - get_degree.no_of_bonuses)
                    due_wage = get_degree_2.basic_salary + (get_degree_2.bonuses_value * due_salary)
                else:
                    due_degree = current_degree.degree_no
                    due_salary = current_degree.no_of_bonuses
                    due_wage = current_degree.basic_salary + (current_degree.bonuses_value * due_salary)
            else:
                due_degree = current_degree.degree_no
                due_salary = current_degree.no_of_bonuses
                due_wage = current_degree.basic_salary + (current_degree.bonuses_value * due_salary)

        return due_degree,due_salary,due_wage



