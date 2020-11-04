from odoo import fields, models, api


class JobGroup(models.Model):
    _name = 'job.group'
    _description = 'Job Group'

    name = fields.Char("Job Group")

class HrJob(models.Model):
    _inherit = 'hr.job'

    job_group_id = fields.Many2one('job.group',"Job Group")

