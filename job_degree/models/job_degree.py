# -*- coding: utf-8 -*-

from odoo import models, fields, api


class JobDegree(models.Model):
    _name = 'job.degree'
    _rec_name = "degree_no"
    _description = 'Job Degree'

    #degree_name = fields.Char(string="Degree Name",required=True ,tracking=True)
    degree_no = fields.Integer(string="Degree Number",required=True,tracking=True)
    no_of_bonuses = fields.Float(string="No of Bonuses",required=True,tracking=True)
    bonuses_value = fields.Float(string="Value of the annual increase",required=True,tracking=True)
    basic_salary = fields.Float(string="Basic Salary",required=True,tracking=True)
    no_of_years = fields.Integer(string="Minimum job upgrade per ( year )",required=True,tracking=True)
    bonuses_lines = fields.One2many('generate.bonuses', 'l_bonuses', string="Bonuses")
    # degree_seq = fields.Integer(string='No', required=True, copy=False,readonly=True,index=True)

    @api.onchange('no_of_bonuses','bonuses_value')
    def _update_generate_bonuses(self):
        i=1
        lines = [(5, 0, 0)]
        while i <= self.no_of_bonuses:
            vals = {
                'bonus' : str(i),
                'value': self.bonuses_value,
                'count' : i,
            }
            lines.append((0,0,vals))
            i += 1
        self.bonuses_lines = lines





    # @api.model
    # def create(self, vals):
    #     vals['degree_seq'] = self.env['ir.sequence'].get('job.degree.sequence')
    #     return super(JobDegree, self).create(vals)


class GenerateBonuses(models.Model):
    _name = 'generate.bonuses'
    _rec_name = "bonus"

    l_bonuses = fields.Many2one('job.degree', string="bonuses lines")

    bonus = fields.Char(string="Bonus")
    value = fields.Float(string="Value")
    count = fields.Integer(string="count")

