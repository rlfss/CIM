from odoo import fields, models, api


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    max_number = fields.Integer("Max Number For National ID",required=True)

    def set_values(self):
        super(ConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('hr_employee_info.max_number',
                                                         self.max_number)

    @api.model
    def get_values(self):
        res = super(ConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        max_numbers = params.get_param('hr_employee_info.max_number')
        res.update(
            max_number = int(max_numbers)
        )
        return res

