from odoo import api, fields, models, tools, exceptions


class LeaveReport(models.Model):
    _inherit = 'hr.leave'

    def _default_leave_report(self):
        return self.env['hr.leave.report'].search([('employee_id.id','=',self.employee_id.id)])

    leave_report= fields.Many2one('hr.leave.report', string="Leave Report", default=_default_leave_report)
