from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PortalGeneralRequest(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalGeneralRequest, self)._prepare_portal_layout_values()
        values['general_request_count'] = request.env['general.request'].search_count(
            [('employee_id.user_id', '=', request.env.user.id)])
        return values

    # ------------------------------------------------------------
    # My internal memo
    # ------------------------------------------------------------

    def _request_get_page_view_values(self, request, access_token, **kwargs):
        values = {
            'page_name': 'General Request',
            'request': request,
        }
        return self._get_page_view_values(request, access_token, values, 'my_request_history', False, **kwargs)

    @http.route(['/my/request', '/my/request/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_general_request(self, page=1, sortby=None, access_token=None, **kw):
        values = self._prepare_portal_layout_values()
        GeneralRequest = request.env['general.request']

        domain = [('employee_id.user_id', '=', request.env.user.id)]

        searchbar_sortings = {
            'write_date': {'label': _('Last Modified on'), 'order': 'write_date desc'},
            'employee_id': {'label': _('Employee'), 'order': 'employee_id desc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'write_date'
        order = searchbar_sortings[sortby]['order']

        #archive_groups = self._get_archive_groups('general.request', domain)

        # count for pager
        request_count = GeneralRequest.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/request",
            url_args={'sortby': sortby},
            total=request_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        general_request = GeneralRequest.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_request_history'] = general_request.ids[:100]

        values.update({
            # 'date': date_begin,
            'general_request': general_request,
            'page_name': 'General Request',
            'pager': pager,
            #'archive_groups': archive_groups,
            'default_url': '/my/request',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("general_request.portal_my_general_request", values)

    @http.route(['/my/request/<int:request_id>'], type='http', auth="public", website=True)
    def portal_my_internal_memo_detail(self, request_id, report_type=None, access_token=None, download=False, **kw):
        try:
            request_sudo = self._document_check_access('general.request', request_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._request_get_page_view_values(request_sudo, access_token, **kw)
        return request.render("general_request.portal_general_request_page", values)

    @http.route('/request_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def memo_form(self, model_name, **kwargs):
        vals = {}
        vals['request_type'] = kwargs['request_type']
        vals['description'] = kwargs['description']
        vals['type'] = kwargs['type']
        vals['quantity'] = kwargs['quantity']
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.uid)])
        vals['employee_id'] = employee_id
        recid = request.env['general.request'].sudo().create_memo_portal(vals)
        url = '/my/request/' + str(recid)
        return request.redirect(url)
