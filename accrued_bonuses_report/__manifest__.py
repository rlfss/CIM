# -*- coding: utf-8 -*-
{
    'name': "Accrued Bonuses Report",
    'version': '0.1',
    'sequence': 1,
    'depends': ['base','hr','hr_contract','report_xlsx','hr_holidays'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'wizards/accrued_bonuses.xml',
        'reports/report.xml'
    ],
    'installable': True,
}
