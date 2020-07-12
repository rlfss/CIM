# -*- coding: utf-8 -*-
# from docutils.nodes import row
from io import BytesIO
import xlwt,  base64
from odoo import models



class PatientCardXlsx(models.AbstractModel):
    _name = 'report.accrued_bonuses_report.report_accrued_bounses_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size':13,'align':'center','bold':True,'bg_color':'#c1bebe'})
        format2 = workbook.add_format({'font_size': 9, 'align': 'center'})
        header_format = workbook.add_format({'font_size': 17, 'align': 'center','bold':True,'valign': 'vcenter','font_color':'blue'})
        sheet = workbook.add_worksheet('تقرير العلاوات المستحقة')
        sheet.right_to_left()
        sheet.set_column(0,0,5)
        sheet.set_column(1,1,18)
        sheet.set_column(2,2, 18)
        sheet.set_column(3,3, 18)
        sheet.set_column(4,4, 18)
        sheet.set_column(5,5, 18)
        sheet.set_column(6, 6, 18)
        sheet.merge_range('A1:G2','تقرير العلاوات المستحقة',header_format)
        row = 2
        col = 0
        sheet.write(row, col, 'م', format1)
        sheet.write(row,col+1,'رقم الموظف',format1)
        sheet.write(row,col+2,'اسم الموظف',format1)
        sheet.write(row,col+3, 'القسم', format1)
        sheet.write(row,col+4, 'الدرجة عند التعيين', format1)
        sheet.write(row,col+5, 'الدرجة الحالية', format1)
        sheet.write(row,col+6, 'الدرجة المستحقة', format1)
        row +=1
        col = 0
        no = 1
        for rec in data['employee']:
            sheet.write(row, col, no, format2)
            sheet.write(row,col+1,rec['employee_num'], format2)
            sheet.write(row,col+2, rec['name'], format2)
            sheet.write(row,col+3, rec['department_name'], format2)
            sheet.write(row,col+4, rec['appointmentdegree'], format2)
            sheet.write(row,col+5, rec['currentdegree'], format2)
            row += 1
            no +=1
        # sheet.write(1, 6, lines.employee.name, format2)