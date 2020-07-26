# -*- coding: utf-8 -*-


import random
from odoo import api, fields, models, _
from datetime import datetime, time, timedelta
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError, ValidationError
from pytz import timezone, UTC
from datetime import datetime, timedelta

import uuid

class CreateWizard(models.TransientModel):
    _name = 'hr.review'
    _description = 'Hr Review'

    hr_leave_signature = fields.Binary('HR Review Signature', copy=False, attachment=True, required=True)



    def leave_signature(self):
        hr_leave_signature = self.hr_leave_signature
        hr_leave_signed_by = self.env.user.name
        shash = random.getrandbits(128)
        ranshash = random.getrandbits(128)
        newhash = str("%032x" % shash)
        today = datetime.today()
        timeoff_values = {
            'hr_leave_signature': hr_leave_signature,
            'hr_leave_signed_by': hr_leave_signed_by,
            'hr_leave_signed_date': today,
            'hr_leave_signed_hash': newhash,
        }
        ginv = self.env['hr.leave'].browse(self.env.context.get('active_id'))
        timeoff_rec = self.env['hr.leave'].sudo().browse(ginv.id)
        if timeoff_rec:
            timeoff_rec.sudo().write(timeoff_values)
            ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
            self.ensure_one()
            template_id = self.env['ir.model.data'].xmlid_to_res_id('leave_cim.mail_template_leave_review', raise_if_not_found=False)
            lang = self.env.context.get('lang')
            template = self.env['mail.template'].browse(template_id)
            ctx = {
                'default_model': 'hr.leave',
                'default_res_id': timeoff_rec.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "mail.mail_notification_paynow",
                'proforma': self.env.context.get('proforma', False),
                'force_email': True,
            }
            timeoff_rec.write({'review_status': 'reviewed'})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }

