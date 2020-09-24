# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo
from datetime import datetime


class Language(models.Model):
    _inherit = 'res.lang'

    @odoo.tools.ormcache(skiparg=1)
    def _get_languages_dir(self):
        langs = self.search([('active', '=', True)])
        return dict([(lg.code, lg.direction) for lg in langs])

    def get_languages_dir(self):
        return self._get_languages_dir()

    def write(self, vals):
        self._get_languages_dir.clear_cache(self)
        return super(Language, self).write(vals)

class EmployeeDate(models.Model):
    _inherit = 'hr.employee'

    # current_date = fields.Date('Date current action', required=False, readonly=False, select=True
    #                             ,default=lambda self: fields.datetime.now())
    current_time = fields.Datetime('Date current action', required=False, readonly=False, select=True
                                ,default=fields.Datetime.now)
