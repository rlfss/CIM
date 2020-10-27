# -*- coding: utf-8 -*-
{
    'name' : 'hr employee info',
    'version' : '1.0',
    'sequence': 1,
    'depends' : ['hr','hr_contract','job_degree','hr_holidays','base','helpdesk'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/hr_employee_info.xml',
        'views/contract.xml',
        'views/settings.xml',
        'views/employee_certificates.xml',
        'views/help_desk.xml',
        'data/retirement_schdule_data.xml'
    ],
    'installable': True,
}
