{
    'name': 'Internal memo',
    'version': '13.0',
    'depends': ['hr_holidays', 'portal','leave_report'],
    'data': [
        'data/mail_data.xml',
        'security/ir.model.access.csv',
        'views/internal_memo_views.xml',
        'views/portal_templates.xml',
        'views/memo_report.xml'
    ],
}
