# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PartnerForm(CustomerPortal):

    def get_domain_my_team_leaves(self, user):
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)

        return [
            '|', ('manager_id', '=', emp and emp.id or False), ('manager_id.parent_id', '=', emp and emp.id or False),
        ]

    @http.route(['/my/request','/my/request/page/<int:page>'], type='http', auth="public", website=True)
    def partner_form(self,page=1, sortby=None, **post):

        GeneralRequest = request.env['general.request']
        domain = self.get_domain_my_leaves(request.env.user)
        request_type_id = GeneralRequest.search(domain)



        return request.render("general_request.tmp_request_form", {'request_type_id':request_type_id})



    @http.route(['/my/request/submit'], type='http', auth="public", website=True)
    def customer_form_submit(self, **post):
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.uid)])
        request_type_id = request.env['general.request'].sudo().search([])
        request_id = request.env['general.request'].create({
            'request_type': post.get('request_type'),
            'description': post.get('description'),
            'type': post.get('type'),
            'quantity': post.get('quantity'),
            'employee_id' : employee_id.id
        })
        vals = {
            'request': request_id,
        }

        return request.render("general_request.tmp_request_form_success", vals)

    # @http.route(['/my/request', '/my/request/page/<int:page>'], type='http', auth="user", website=True)
    # def portal_my_internal_memo(self, page=1, sortby=None, access_token=None, **kw):
    #     values = self._prepare_portal_layout_values()
    #     GeneralRequest = request.env['general.request']
    #
    #     domain = [('employee_id.user_id', '=', request.env.user.id)]
    #
    #     searchbar_sortings = {
    #         'write_date': {'label': _('Last Modified on'), 'order': 'write_date desc'},
    #         'employee_id': {'label': _('Employee'), 'order': 'employee_id desc'},
    #     }
    #     # default sort by order
    #     if not sortby:
    #         sortby = 'write_date'
    #     order = searchbar_sortings[sortby]['order']
    #
    #     archive_groups = self._get_archive_groups('general.request', domain)
    #
    #     # count for pager
    #     request_count = GeneralRequest.search_count(domain)
    #     # pager
    #     pager = portal_pager(
    #         url="/my/memo",
    #         url_args={'sortby': sortby},
    #         total=request_count,
    #         page=page,
    #         step=self._items_per_page
    #     )
    #     # content according to pager and archive selected
    #     request_type_id = GeneralRequest.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
    #     request.session['my_memo_history'] = request_type_id.ids[:100]
    #
    #     values.update({
    #         # 'date': date_begin,
    #         'request_type_id': request_type_id,
    #         'page_name': 'internal memo',
    #         'pager': pager,
    #         'archive_groups': archive_groups,
    #         'default_url': '/my/request',
    #         'searchbar_sortings': searchbar_sortings,
    #         'sortby': sortby,
    #     })
    #     return request.render("general_request.tmp_request_form", values)

