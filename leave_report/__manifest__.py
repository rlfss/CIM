{
    'name': 'Leave Report',
    'version': '13.0',
    'summary': 'Generates Report PDF in leave.',
    'category': 'Report/PDF',
    'author': 'Sahara International group',
    'depends': ['hr_holidays'],
    'data': [
        'views/leave_report_view.xml',
        'views/templates.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
