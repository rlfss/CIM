{
    "name" : "HR Leave CIM",
    "version" : "1.0",
    "category" : "hr",
    "depends" : ["base","hr","hr_holidays", "leave_sequence"],
    "data" : [
        'data/mail.xml',
        'view/leave.xml',
        'view/templates.xml',
        'wizards/hr_review.xml',
    ],
    'qweb': [
        "static/src/xml/home.xml",
    ],
    "installable": True
}
