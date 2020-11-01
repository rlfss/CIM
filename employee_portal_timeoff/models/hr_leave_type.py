from odoo import fields, models, api



class GetNumberOfDays(models.Model):
    _inherit = 'hr.leave.type'

    

    @api.model
    def get_days_all_request(self):
        super(GetNumberOfDays, self).get_days_all_request()
        leave_types = sorted(self.search([]).filtered(lambda x: x.virtual_remaining_leaves or x.max_leaves),
                             key=self._model_sorting_key, reverse=True)
        return [(lt.name, {
            'remaining_leaves': ('%.2f' % lt.remaining_leaves).rstrip('0').rstrip('.'),
            'virtual_remaining_leaves': ('%.2f' % lt.virtual_remaining_leaves).rstrip('0').rstrip('.'),
            'max_leaves': ('%.2f' % lt.max_leaves).rstrip('0').rstrip('.'),
            'leaves_taken': ('%.2f' % lt.leaves_taken).rstrip('0').rstrip('.'),
            'request_unit': lt.request_unit,
            'number_of_days': lt.remaining_leaves - lt.virtual_remaining_leaves,
        }, lt.allocation_type)
                for lt in leave_types]