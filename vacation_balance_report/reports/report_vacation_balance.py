# -*- coding: utf-8 -*-

from odoo import models

class PatientCardXlsx(models.AbstractModel):
    _name = 'report.vacation_balance_report.report_vacation_balance_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size':13,'align':'center','bold':True,'bg_color':'#c1bebe','border':1})
        format2 = workbook.add_format({'font_size': 9, 'align': 'center','border':1})
        format3 = workbook.add_format({'font_size':9,'align':'center','bg_color':'#f2f3f4','border':1})
        format4 = workbook.add_format({'font_size':10,'align':'center','bold':True,'border':1,'bg_color':'yellow'})
        date_format2 = workbook.add_format({'font_size':12,'align':'center','bold':True,'font_color':'green','num_format': 'dd/mm/yyyy','valign': 'vcenter'})
        header_format = workbook.add_format({'font_size': 17, 'align': 'left','bold':True,'valign': 'vcenter','font_color':'blue'})
        sheet = workbook.add_worksheet('تقرير أرصدة الأجازات')
        sheet.right_to_left()
        sheet.set_column(0,0,5)
        sheet.set_column('B:D',18)
        sheet.set_column('E:AZ',6)

        sheet.merge_range('A1:D2','تقرير أرصدة الأجازات الى غاية',header_format)
        sheet.merge_range('E1:G2',lines.date,date_format2)
        row = 3
        l_row = 2
        col = 0
        f_col = 4
        l_col = 6
        sheet.write(row, col, 'م', format1)
        sheet.write(row,col+1,'رقم الموظف',format1)
        sheet.write(row,col+2,'اسم الموظف',format1)
        sheet.write(row,col+3, 'القسم', format1)

        for leave in data['employee'][0]['leaves']:
            sheet.merge_range(l_row, f_col,l_row,l_col, leave['leave_name'], format4)
            f_col += 3
            l_col += 3

        row +=1
        b_col = 4
        c_col = 5
        r_col = 6
        n_row = 4
        b_row = 3
        col = 0
        no = 1

        for rec in data['employee']:
            sheet.write(row, col, no, format2)
            sheet.write(row,col+1,rec['employee_num'], format2)
            sheet.write(row,col+2, rec['name'], format2)
            sheet.write(row,col+3, rec['department_name'], format2)
            for leave in rec['leaves']:
                sheet.write(b_row,b_col,"أساسي", format1)
                sheet.write(n_row, b_col, leave['basic_balance'], format3)
                b_col += 3
            for leave in rec['leaves']:
                sheet.write(b_row, c_col, "مستهلك", format1)
                sheet.write(n_row,c_col, leave['balance_consumed'], format3)
                c_col += 3
            for leave in rec['leaves']:
                sheet.write(b_row, r_col, "متبقي", format1)
                sheet.write(n_row,r_col, leave['remaining_days'], format3)
                r_col += 3

            row += 1
            n_row += 1
            b_col = 4
            c_col = 5
            r_col = 6
            no += 1
        workbook.close()







