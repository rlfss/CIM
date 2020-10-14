from odoo import fields, models, api, _


class HrRetirement(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def create_employee_retirement(self):
        for contract in self.search([('state','=','open')]):
            if contract.employee_id.gender == 'male' and contract.employee_id.employee_age >= 65:
                contract.write({
                    'state': 'cancel'
                })
            elif contract.employee_id.gender == 'female' and contract.employee_id.employee_age >= 60:
                contract.write({
                    'state': 'cancel'
                })


