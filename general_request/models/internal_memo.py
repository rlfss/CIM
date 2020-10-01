from odoo import api, fields, models
from odoo.exceptions import AccessDenied



class GeneralRequest(models.Model):
    _name = 'general.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'General Request'
    _order = 'id desc'
    _rec_name = 'request_type'

    request_type = fields.Selection([('r_badge', 'Request Badge'), ('r_papers', 'Request Papers')], default='r_badge')
    description = fields.Char('Description')
    type = fields.Char('Type')
    quantity = fields.Float('Quantity')
    employee_id = fields.Many2one('hr.employee', "Employee")


    @api.model
    def create_request_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        self = self.sudo()
        request_type = values['request_type']
        description = values['description']
        type = values['type']
        quantity = values['quantity']
        employee_id = values['employee_id']


        values = {
            'request_type': request_type,
            'description': description,
            'type': type,
            'quantity': quantity,
            'employee_id': int(employee_id.id),

        }

        request = self.env['general.request'].sudo().create(values)

        return request.id
