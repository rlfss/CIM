from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class PortalInternalMemo(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalInternalMemo, self)._prepare_portal_layout_values()
        values['internal_memo_count'] = request.env['internal.memo'].search_count(
            [('employee_id.user_id', '=', request.env.user.id)])
        return values

    # ------------------------------------------------------------
    # My internal memo
    # ------------------------------------------------------------

    def _memo_get_page_view_values(self, memo, access_token, **kwargs):
        values = {
            'page_name': 'Internal memo',
            'memo': memo,
        }
        return self._get_page_view_values(memo, access_token, values, 'my_memo_history', False, **kwargs)

    @http.route(['/my/memo', '/my/memo/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_internal_memo(self, page=1, sortby=None, access_token=None, **kw):
        values = self._prepare_portal_layout_values()
        InternalMemo = request.env['internal.memo']

        domain = [('employee_id.user_id', '=', request.env.user.id)]

        searchbar_sortings = {
            'write_date': {'label': _('Last Modified on'), 'order': 'write_date desc'},
            'employee_id': {'label': _('Employee'), 'order': 'employee_id desc'},
            'name': {'label': _('Title'), 'order': 'name asc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'write_date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('internal.memo', domain)

        # count for pager
        memo_count = InternalMemo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/memo",
            url_args={'sortby': sortby},
            total=memo_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        internal_memo = InternalMemo.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_memo_history'] = internal_memo.ids[:100]

        values.update({
            # 'date': date_begin,
            'internal_memo': internal_memo,
            'page_name': 'internal memo',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/memo',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("internal_memo.portal_my_internal_memo", values)

    @http.route(['/my/memo/<int:memo_id>'], type='http', auth="public", website=True)
    def portal_my_internal_memo_detail(self, memo_id, access_token=None, **kw):
        try:
            memo_sudo = self._document_check_access('internal.memo', memo_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._memo_get_page_view_values(memo_sudo, access_token, **kw)
        return request.render("internal_memo.portal_internal_memo_page", values)

    @http.route('/memo_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def memo_form(self, model_name, **kwargs):
        vals = {}
        vals['name'] = kwargs['subject']
        vals['message'] = kwargs['message']
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.uid)])
        vals['employee_id'] = employee_id.id
        if employee_id.parent_id:
            vals['manager_id'] = employee_id.parent_id.id
        recid = request.env['internal.memo'].sudo().create_memo_portal(vals)
        # template = request.env.ref('internal_memo.mail_memo_receipt', raise_if_not_found=False)
        # if employee_id.parent_id:
            # template.sudo().with_context(lang=employee_id.parent_id.user_id.lang,user=employee_id.parent_id.user_id).send_mail(employee_id.parent_id.user_id.id, force_send=True, raise_exception=True)
            # template.sudo().with_context(lang=request.env.user.employee_id.parent_id.user_id.lang).send_mail(
            #     self.env.user.employee_id.parent_id.user_id.id, force_send=True, raise_exception=True)
        _logger.warning(recid)
        _logger.warning(recid)
        _logger.warning(recid)
        url = '/my/memo/'+str(recid)
        return request.redirect(url)
