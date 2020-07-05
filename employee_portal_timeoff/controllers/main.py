# Part of odoo. See LICENSE file for full copyright and licensing details

from collections import OrderedDict
from operator import itemgetter
from odoo import fields
from odoo import http
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.translate import _
from odoo.exceptions import AccessError, MissingError
import binascii
import functools
import logging

import json

import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo import registry as registry_get

from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect

def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        kw.pop('debug', False)
        if not kw:
            return """<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = l.pathname + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                if (r == l.pathname) {
                    r = '/';
                }
                window.location = r;
            </script></head><body></body></html>"""
        return func(self, *a, **kw)
    return wrapper

class OAuthController(http.Controller):

    @http.route('/auth_oauth/signin', type='http', auth='none')
    @fragment_to_query_string
    def signin(self, **kw):
        state = json.loads(kw['state'])
        dbname = state['d']
        if not http.db_filter([dbname]):
            return BadRequest()
        provider = state['p']
        context = state.get('c', {})
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, context)
                credentials = env['res.users'].sudo().auth_oauth(provider, kw)
                cr.commit()
                action = state.get('a')
                menu = state.get('m')
                redirect = werkzeug.url_unquote_plus(state['r']) if state.get('r') else False
                url = '/my/home'
                if redirect:
                    url = redirect
                elif action:
                    url = '/web#action=%s' % action
                elif menu:
                    url = '/web#menu_id=%s' % menu
                resp = login_and_redirect(*credentials, redirect_url=url)
                # Since /web is hardcoded, verify user has right to land on it
                if werkzeug.urls.url_parse(resp.location).path == '/web' and not request.env.user.has_group('base.group_user'):
                    resp.location = '/my/home'
                return resp
            except AttributeError:
                # auth_signup is not installed
                _logger.error("auth_signup not installed on database %s: oauth sign up cancelled." % (dbname,))
                url = "/web/login?oauth_error=1"
            except AccessDenied:
                # oauth credentials not valid, user could be on a temporary session
                _logger.info('OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies')
                url = "/web/login?oauth_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception as e:
                # signup error
                _logger.exception("OAuth2: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return set_cookie_and_redirect(url)

class WebsiteAccount(CustomerPortal):

    def get_domain_my_leaves(self, user):
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        return [
            ('employee_id', '=', emp and emp.id or False),
        ]
    def get_domain_my_team_leaves(self, user):
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)

        return [
            '|', ('manager_id', '=', emp and emp.id or False), ('manager_id.parent_id', '=', emp and emp.id or False),
        ]

    def _prepare_portal_layout_values(self):
        values = super(WebsiteAccount, self)._prepare_portal_layout_values()
        leave_count = request.env['hr.leave'].search_count(self.get_domain_my_leaves(request.env.user))
        values.update({
            'leave_count': leave_count,
        })
        return values

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leaves(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        HrLeave = request.env['hr.leave']
        HrPerm = request.env['hr.permission']
        Timeoff_sudo = request.env['hr.leave'].sudo()
        domain = self.get_domain_my_leaves(request.env.user)

        holiday_domain=(['&', ('virtual_remaining_leaves', '>', 0),
                        '|', ('allocation_type', 'in', ['fixed_allocation', 'no']),
                        '&',('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')
                        ])
        holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        values.update({
            'holiday_types':holiday_type_ids.with_context({'employee_id':emp and emp.id or False}).name_get_only()})
        # fileter  By
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'confirm': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            'validate1': {'label': _('Second Approval'), 'domain': [('state', '=', 'validate1')]},
            'validate': {'label': _('Approved'), 'domain': [('state', '=', 'validate')]},
        }
        # sort By
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        # group By
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'timeoff': {'input': 'timeoff', 'label': _('Time Off Type')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('hr.leave', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # pager
        leave_count = HrLeave.search_count(domain)
        pager = request.website.pager(
            url="/my/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )
        get_days_all_request = request.env['hr.leave.type'].get_days_all_request()
        # default groupby
        if groupby == 'timeoff':
            order = "holiday_status_id, %s" % order
        # content according to pager and archive selected
        leaves = HrLeave.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        perms = HrPerm.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'none':
            grouped_timeoff = []
            if leaves:
                grouped_timeoff = [leaves]
        else:
            grouped_timeoff = [Timeoff_sudo.concat(*g) for k, g in groupbyelem(leaves, itemgetter('holiday_status_id'))]
        values.update({
            'date': date_begin,
            'leaves': leaves,
            'perms': perms,
            'grouped_timeoff': grouped_timeoff,
            'page_name': 'leave',
            'timeoffs':get_days_all_request,
            'archive_groups': archive_groups,
            'default_url': '/my/leaves',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("employee_portal_timeoff.portal_my_leaves_details", values)




    @http.route(['''/my/timeoff/<model('hr.leave'):timeoff>'''], type='http', auth="user", website=True)
    def portal_my_timeoff(self, timeoff, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        holiday_domain=(['&', ('virtual_remaining_leaves', '>', 0),
                        '|', ('allocation_type', 'in', ['fixed_allocation', 'no']),
                        '&',('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')
                        ])
        holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
        return request.render(
            "employee_portal_timeoff.portal_my_timeoff", {
                'timeoff': timeoff,
                'holiday_types':holiday_type_ids.with_context({'employee_id':emp and emp.id or False}).name_get_only(),
                'emp_id': emp and emp.id or False
            })

    @http.route(['/my/leaves/summary'], type='http', auth="user", website=True)
    def leaves_summary(self):
        get_days_all_request = request.env['hr.leave.type'].get_days_all_request()
        return request.render(
            "employee_portal_timeoff.my_leaves_summary",{
                'timeoffs':get_days_all_request})
        
    @http.route(['''/my/permission_req/<model('hr.permission'):permission_req>'''], type='http', auth="user", website=True)
    def portal_my_permission_req(self, permission_req, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        return request.render(
            "employee_portal_timeoff.portal_my_permission_req", {
                'permission_req': permission_req,
                'emp_id': emp and emp.id or False
            })
    @http.route(['''/my/return_req/<model('hr.leavereturn'):return_req>'''], type='http', auth="user", website=True)
    def portal_my_return_req(self, return_req, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        return request.render(
            "employee_portal_timeoff.portal_my_return_req", {
                'return_req': return_req,
                'emp_id': emp and emp.id or False
            })






    @http.route(['/my/team/leaves', '/my/team/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_team_leaves(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        HrLeave = request.env['hr.leave']
        Timeoff_sudo = request.env['hr.leave'].sudo()
        domain = self.get_domain_my_team_leaves(request.env.user)

        holiday_domain=(['&', ('virtual_remaining_leaves', '>', 0),
                        '|', ('allocation_type', 'in', ['fixed_allocation', 'no']),
                        '&',('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')
                        ])
        holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        values.update({
            'holiday_types':holiday_type_ids.with_context({'employee_id':emp and emp.id or False}).name_get_only()})
        # fileter  By
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'confirm': {'label': _('To Approve'), 'domain': [('state', '=', 'confirm')]},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            'validate1': {'label': _('Second Approval'), 'domain': [('state', '=', 'validate1')]},
            'validate': {'label': _('Approved'), 'domain': [('state', '=', 'validate')]},
        }
        # sort By
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        # group By
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'timeoff': {'input': 'timeoff', 'label': _('Time Off Type')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('hr.leave', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # pager
        leave_count = HrLeave.search_count(domain)
        pager = request.website.pager(
            url="/my/team/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )
        get_days_all_request = request.env['hr.leave.type'].get_days_all_request()
        # default groupby
        if groupby == 'timeoff':
            order = "holiday_status_id, %s" % order
        # content according to pager and archive selected
        leaves = HrLeave.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'none':
            grouped_timeoff = []
            if leaves:
                grouped_timeoff = [leaves]
        else:
            grouped_timeoff = [Timeoff_sudo.concat(*g) for k, g in groupbyelem(leaves, itemgetter('holiday_status_id'))]
        values.update({
            'date': date_begin,
            'leaves': leaves,
            'grouped_timeoff': grouped_timeoff,
            'page_name': 'leave',
            'timeoffs':get_days_all_request,
            'archive_groups': archive_groups,
            'default_url': '/my/team/leaves',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("employee_portal_timeoff.my_team_portal_my_leaves_details", values)




    @http.route(['''/my/team/leaves/<model('hr.leave'):timeoff>'''], type='http', auth="user", website=True)
    def portal_my_timeoff_team(self, timeoff, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        holiday_domain=(['&', ('virtual_remaining_leaves', '>', 0),
                        '|', ('allocation_type', 'in', ['fixed_allocation', 'no']),
                        '&',('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')
                        ])
        holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
        return request.render(
            "employee_portal_timeoff.portal_my_timeoff_team", {
                'timeoff': timeoff,
                'holiday_types':holiday_type_ids.with_context({'employee_id':emp and emp.id or False}).name_get_only(),
                'emp_id': emp and emp.id or False
            })

    @http.route(['/my/team/leaves/<int:task_id>/aprove_sign'], type='json', auth="public", website=True)
    def portal_sign(self, task_id, access_token=None, source=False, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            task_sudo = self._document_check_access('hr.leave', task_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid .')}

        if not task_sudo.has_to_be_signed():
            return {'error': _('The  is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            task_sudo.write({
                'leave_signature': signature,
                'leave_signed_by': name,
            })
            task_sudo.team_action_approveandsign(task_id)

        except (TypeError, binascii.Error):
            return {'error': _('Invalid signature data.')}

        query_string = '?&message=sign_ok'
        url = '/my/team/leaves/'+str(task_id)+'?&message=sign_ok&aprove'
        return {
            'force_refresh': True,
            'redirect_url': url,
        }

    @http.route(['/my/team/leaves/<int:task_id>/super_aprove_sign'], type='json', auth="public", website=True)
    def super_portal_sign(self, task_id, access_token=None, source=False, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            task_sudo = self._document_check_access('hr.leave', task_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid .')}

        if not task_sudo.s_has_to_be_signed():
            return {'error': _('The  is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            task_sudo.write({
                's_leave_signature': signature,
                's_leave_signed_by': name,
            })
            task_sudo.super_team_action_approveandsign(task_id)

        except (TypeError, binascii.Error):
            return {'error': _('Invalid signature data.')}

        query_string = '?&message=sign_ok'
        url = '/my/team/leaves/'+str(task_id)+'?&message=sign_ok&aprove'
        return {
            'force_refresh': True,
            'redirect_url': url,
        }

    @http.route(['/my/team/leaves/<int:task_id>/refuse_sign'], type='json', auth="public", website=True)
    def portal_sign_r(self, task_id, access_token=None, source=False, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            task_sudo = self._document_check_access('hr.leave', task_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid .')}

        if not task_sudo.has_to_be_signed2():
            return {'error': _('The  is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            task_sudo.write({
                'r_leave_signature': signature,
                'r_leave_signed_by': name,
            })
            task_sudo.team_action_ref2sign(task_id)

        except (TypeError, binascii.Error):
            return {'error': _('Invalid signature data.')}

        query_string = '?&message=sign_ok'
        url = '/my/team/leaves/'+str(task_id)+'?&message=sign_ok&refuse'
        return {
            'force_refresh': True,
            'redirect_url': url,
        }







    @http.route(['/my/team/permission', '/my/team/permission/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_team_permission(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        HrLeave = request.env['hr.permission']
        Timeoff_sudo = request.env['hr.permission'].sudo()
        domain = self.get_domain_my_team_leaves(request.env.user)

        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        # fileter  By
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            'validate': {'label': _('Approved'), 'domain': [('state', '=', 'validate')]},
        }
        # sort By
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        # group By
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'timeoff': {'input': 'timeoff', 'label': _('Time Off Type')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('hr.permission', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # pager
        leave_count = HrLeave.search_count(domain)
        pager = request.website.pager(
            url="/my/team/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )
        # default groupby
        if groupby == 'timeoff':
            order = "holiday_status_id, %s" % order
        # content according to pager and archive selected
        leaves = HrLeave.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'none':
            grouped_timeoff = []
            if leaves:
                grouped_timeoff = [leaves]
        else:
            grouped_timeoff = [Timeoff_sudo.concat(*g) for k, g in groupbyelem(leaves, itemgetter('holiday_status_id'))]
        values.update({
            'date': date_begin,
            'leaves': leaves,
            'grouped_timeoff': grouped_timeoff,
            'page_name': 'leave',
            'archive_groups': archive_groups,
            'default_url': '/my/team/permission',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("employee_portal_timeoff.my_team_portal_my_permission_details", values)















    @http.route(['''/my/team/permission/<model('hr.permission'):timeoff>'''], type='http', auth="user", website=True)
    def portal_my_permission_team(self, timeoff, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        return request.render(
            "employee_portal_timeoff.portal_my_permission_team", {
                'timeoff': timeoff,
                'emp_id': emp and emp.id or False
            })

    @http.route(['/my/team/permission/<int:task_id>/aprove_sign'], type='json', auth="public", website=True)
    def portal_permission_sign(self, task_id, access_token=None, source=False, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            task_sudo = self._document_check_access('hr.permission', task_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid .')}

        if not task_sudo.has_to_be_signed():
            return {'error': _('The  is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            task_sudo.write({
                'permission_signature': signature,
                'permission_signed_by': name,
            })
            task_sudo.team_action_approveandsign(task_id)

        except (TypeError, binascii.Error):
            return {'error': _('Invalid signature data.')}

        query_string = '?&message=sign_ok'
        url = '/my/team/permission/'+str(task_id)+'?&message=sign_ok&aprove'
        return {
            'force_refresh': True,
            'redirect_url': url,
        }


    @http.route(['/my/team/permission/<int:task_id>/refuse_sign'], type='json', auth="public", website=True)
    def portal_permission_sign_r(self, task_id, access_token=None, source=False, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            task_sudo = self._document_check_access('hr.permission', task_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid .')}

        if not task_sudo.has_to_be_signed2():
            return {'error': _('The  is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            task_sudo.write({
                'r_permission_signature': signature,
                'r_permission_signed_by': name,
            })
            task_sudo.team_action_ref2sign(task_id)

        except (TypeError, binascii.Error):
            return {'error': _('Invalid signature data.')}

        query_string = '?&message=sign_ok'
        url = '/my/team/permission/'+str(task_id)+'?&message=sign_ok&refuse'
        return {
            'force_refresh': True,
            'redirect_url': url,
        }
