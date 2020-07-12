# -*- coding: utf-8 -*-
# from docutils.nodes import row
from io import BytesIO
import xlwt,  base64
from odoo import models



class PatientCardXlsx(models.AbstractModel):
    _name = 'report.vacation_balance_report.report_vacation_balance_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size':13,'align':'center','bold':True,'bg_color':'#c1bebe'})
        format2 = workbook.add_format({'font_size': 9, 'align': 'center'})
        format3 = workbook.add_format({'font_size':9,'align':'center','bg_color':'yellow'})
        date_format = workbook.add_format({'font_size':13,'align':'center','bold':True,'valign': 'vcenter'})
        date_format2 = workbook.add_format({'font_size':12,'align':'center','bold':True,'font_color':'green','num_format': 'dd/mm/yyyy','valign': 'vcenter'})
        header_format = workbook.add_format({'font_size': 17, 'align': 'left','bold':True,'valign': 'vcenter','font_color':'blue'})
        sheet = workbook.add_worksheet('تقرير أرصدة الأجازات')
        sheet.right_to_left()
        sheet.set_column(0,0,5)
        sheet.set_column(1,1,18)
        sheet.set_column(2,2, 18)
        sheet.set_column(3,3, 18)
        sheet.set_column(4,4, 18)
        sheet.set_column(5,5, 18)
        sheet.set_column(6, 6, 8)
        sheet.merge_range('A1:D2','تقرير أرصدة الأجازات الى غاية',header_format)
        sheet.merge_range('E1:E2',lines.date,date_format2)
        row = 2
        col = 0
        sheet.write(row, col, 'م', format1)
        sheet.write(row,col+1,'رقم الموظف',format1)
        sheet.write(row,col+2,'اسم الموظف',format1)
        sheet.write(row,col+3, 'القسم', format1)
        sheet.write(row,col+4, 'نوع الاجازة', format1)
        sheet.write(row,col+5, 'الرصيد المتبقي', format1)
        sheet.write(row,col+6, 'الوحدة', format1)

        #sheet.write(row,col+5, 'الدرجة الحالية', format1)
        #sheet.write(row,col+6, 'الدرجة المستحقة', format1)
        row +=1
        col = 0
        no = 1
        print("-------",data)
        for rec in data['employee']:
            sheet.write(row, col, no, format2)
            sheet.write(row,col+1,rec['employee_num'], format2)
            sheet.write(row,col+2, rec['name'], format2)
            sheet.write(row,col+3, rec['department_name'], format2)
            for leave in rec['leaves']:
                sheet.write(row, col+4, leave['leave_name'], format3)
                sheet.write(row, col+5, leave['remaining_days'], format3)
                sheet.write(row, col+6, leave['unit'], format3)
                row += 1

            row += 1
            no +=1


        # sheet.write(1, 6, lines.employee.name, format2)