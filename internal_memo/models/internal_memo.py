from odoo import api, fields, models
from odoo.exceptions import AccessDenied


class InternalMemo(models.Model):
    _name = "internal.memo"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Internal memo"
    _order = 'name desc, id desc'
    _mail_post_access = 'read'

    name = fields.Char(string='Title', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee')
    manager_id = fields.Many2one('hr.employee', 'Manager')
    to = fields.Char(string='To')
    via = fields.Char(string='Via')
    message = fields.Text(string='Message')
    date = fields.Date(string="Date", readonly=True, default=fields.Date.context_today)
    template_id = fields.Many2one('memo.template',"Template")

    @api.onchange('template_id')
    def _onchange_template_id(self):
        self.message = self.template_id.description

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.manager_id = self.employee_id.parent_id.id

    @api.model
    def create_memo_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        self = self.sudo()
        name = values['name']
        to = values['to']
        via = values['via']
        message = values['message']
        employee_id = values['employee_id']
        manager_id = values['manager_id']
        template_id = values['template_id']

        values = {
            'name': name,
            'to': to,
            'via': via,
            'message': message,
            'employee_id': int(employee_id.id),
            'manager_id': int(manager_id.parent_id.id),
            'template_id': template_id
        }

        memo = self.env['internal.memo'].sudo().create(values)

        return memo.id

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s ' %  self.name

class MemoTemplate(models.Model):
    _name = 'memo.template'
    _rec_name = 'template'

    template = fields.Char('Template')
    description = fields.Text('Description')