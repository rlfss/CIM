{
    "name" : "HR Leave CIM",
    "version" : "1.0",
    "category" : "hr",
    "depends" : ["base","hr","hr_holidays", "leave_sequence",'leave_report'],
    "data" : [
        'data/mail.xml',
        'view/leave.xml',
        'wizards/hr_review.xml',
    ],
    "installable": True
}
