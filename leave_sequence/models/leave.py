# -*- coding: utf-8 -*-

import logging
import math

from collections import namedtuple

import datetime
from pytz import timezone, UTC

from odoo import api, fields, models, SUPERUSER_ID, tools
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class HolidaysRequest(models.Model):
    _name = "hr.leave"
    _inherit = "hr.leave"

    reference = fields.Char('Reference', readonly=True , default=lambda x: str('New')) #default=default_randint_value
    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        if not self._context.get('leave_fast_create'):
            employee_id = values.get('employee_id', False)
            leave_type_id = values.get('holiday_status_id')
            leave_type = self.env['hr.leave.type'].browse(leave_type_id)
            # Handle automatic department_id
            if not values.get('department_id'):
                values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})

            # Handle no_validation
            if leave_type.validation_type == 'no_validation':
                values.update({'state': 'confirm'})

            # Handle double validation
            if leave_type.validation_type == 'both':
                self._check_double_validation_rules(employee_id, values.get('state', False))
        if values.get('reference', _('New')) == _('New'):
            datetoday = datetime.date.today()
            monthstr = str('%02d' % datetoday.month)
            yearstr = str(datetoday.year)
            yearstr = yearstr[-2:]
            sequencenew = 'TMF-' + monthstr + yearstr + str(self.env['ir.sequence'].next_by_code('hr.leave'))
            values['reference'] = sequencenew or _('New')                

        holiday = super(HolidaysRequest, self.with_context(mail_create_nosubscribe=True)).create(values)
        if self._context.get('import_file'):
            holiday._onchange_leave_dates()
        if not self._context.get('leave_fast_create'):
            # FIXME remove these, as they should not be needed
            if employee_id:
                holiday.with_user(SUPERUSER_ID)._sync_employee_details()
            if 'number_of_days' not in values and ('date_from' in values or 'date_to' in values):
                holiday.with_user(SUPERUSER_ID)._onchange_leave_dates()

            # Everything that is done here must be done using sudo because we might
            # have different create and write rights
            # eg : holidays_user can create a leave request with validation_type = 'manager' for someone else
            # but they can only write on it if they are leave_manager_id
            holiday_sudo = holiday.sudo()
            holiday_sudo.add_follower(employee_id)
            if holiday.validation_type == 'manager':
                holiday_sudo.message_subscribe(partner_ids=holiday.employee_id.leave_manager_id.partner_id.ids)
            if leave_type.validation_type == 'no_validation':
                # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
                holiday_sudo.action_validate()
                holiday_sudo.message_subscribe(partner_ids=[holiday._get_responsible_for_approval().partner_id.id])
                holiday_sudo.message_post(body=_("The time off has been automatically approved"), subtype="mt_comment") # Message from OdooBot (sudo)
            elif not self._context.get('import_file'):
                holiday_sudo.activity_update()
        return holiday