from odoo import api, fields, models


class InternalMemo(models.Model):
    _name = "internal.memo"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Internal memo"
    _order = 'name desc, id desc'
    _mail_post_access = 'read'

    name = fields.Char(string='Title', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee')
    manager_id = fields.Many2one('hr.employee', 'Manager')
    message = fields.Text(string='Message')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.manager_id = self.employee_id.parent_id.id



    @api.model
    def create_memo_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        name = values['name']
        message = values['message']
        employee_id = values['employee_id']

        values = {
            'name': name,
            'message': message,
            'employee_id': int(values['employee_id']),
        }
        memo = self.env['internal.memo'].sudo().create(values)
        return memo.id
