# -*- coding: utf-8 -*-

from odoo import models



class PatientCardXlsx(models.AbstractModel):
    _name = 'report.accrued_bonuses_report.report_accrued_bounses_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size':13,'align':'center','bold':True,'bg_color':'#c1bebe','border':1})
        format2 = workbook.add_format({'font_size': 9, 'align': 'center','border':1})
        format2_bold = workbook.add_format({'font_size': 9, 'align': 'center','border':1,'bold':True})
        format3 = workbook.add_format({'font_size': 9, 'align': 'center','border':1,'font_color':'red','bold':True})
        format4 = workbook.add_format({'font_size': 9, 'align': 'center','border':1,'bg_color':'yellow','bold':True})
        header_format = workbook.add_format({'font_size': 17, 'align': 'left','bold':True,'valign': 'vcenter','font_color':'blue'})
        date_format2 = workbook.add_format({'font_size':12,'align': 'center','bold':True,'font_color':'green','num_format': 'dd/mm/yyyy','valign': 'vcenter'})
        sheet = workbook.add_worksheet('تقرير العلاوات المستحقة')
        sheet.right_to_left()
        sheet.set_column(0,0,5)
        sheet.set_column(1,1,15)
        sheet.set_column(2,2, 18)
        sheet.set_column(3,3, 18)
        sheet.set_column(4,4, 12)
        sheet.set_column(5,5, 14)
        sheet.set_column(6, 6, 14)
        sheet.set_column(7, 7, 14)
        sheet.set_column(8, 8, 12)
        sheet.set_column(9, 9, 12)
        sheet.set_column(10, 10, 12)
        sheet.set_column(11, 11, 12)
        sheet.set_column(12, 12, 12)
        sheet.set_column(13, 13, 12)
        sheet.set_column(14, 14, 12)
        sheet.merge_range('A1:D2','تقرير العلاوات المستحقة الى غاية',header_format)
        sheet.merge_range('E1:E2', lines.date, date_format2)
        row = 2
        col = 0
        sheet.write(row, col, 'م', format1)
        sheet.write(row,col+1,'رقم الموظف',format1)
        sheet.write(row,col+2,'اسم الموظف',format1)
        sheet.write(row,col+3, 'القسم', format1)
        sheet.write(row,col+4, 'تاريخ بدء العمل', format1)
        sheet.write(row,col+5, 'الدرجة عند التعيين', format1)
        sheet.write(row,col+6, 'العلاوة عند التعيين', format1)
        sheet.write(row,col+7, 'الراتب عند التعيين', format1)
        sheet.write(row,col+8, 'الدرجة الحالية', format1)
        sheet.write(row,col+9, 'العلاوة الحالية', format1)
        sheet.write(row,col+10, 'الراتب الحالي', format1)
        sheet.write(row,col+11, 'الدرجة المستحقة', format1)
        sheet.write(row,col+12, 'العلاوة المستحقة', format1)
        sheet.write(row,col+13, 'الراتب المستحق', format1)
        row +=1
        col = 0
        no = 1
        for rec in data['employee']:
            sheet.write(row, col, no, format2)
            if rec['employee_num']:
                sheet.write(row,col+1,rec['employee_num'], format2)
            if rec['name']:
                sheet.write(row,col+2, rec['name'], format2)
            if rec['department_name']:
                sheet.write(row,col+3, rec['department_name'], format2)
            if rec['work_start_date']:
                sheet.write(row,col+4, rec['work_start_date'], format2_bold)
            if rec['appointmentdegree']:
                degree = str(rec['appointmentdegree']) + " الدرجة "
                sheet.write(row,col+5, degree, format2_bold)
            if rec['appointmentsalary']:
                bonus = str(rec['appointmentsalary']) + " علاوة "
                sheet.write(row,col+6, bonus , format2_bold)
            if rec['appointmentwage']:
                sheet.write(row,col+7, rec['appointmentwage'], format2_bold)
            if rec['currentwage'] == rec['duewage']:
                if rec['currentdegree']:
                    degree2 = str(rec['currentdegree']) + " الدرجة "
                    sheet.write(row,col+8, degree2, format2_bold)
                if rec['currentsalary']:
                    bonus2 = str(rec['currentsalary']) + " علاوة "
                    sheet.write(row,col+9, bonus2, format2_bold)
                if rec['currentwage']:
                    sheet.write(row,col+10, rec['currentwage'], format2_bold)
            elif rec['currentwage'] != rec['duewage']:
                if rec['currentdegree']:
                    degree3 = str(rec['currentdegree']) + " الدرجة "
                    sheet.write(row,col+8, degree3, format3)
                if rec['currentsalary']:
                    bonus2 = str(rec['currentsalary']) + " علاوة "
                    sheet.write(row,col+9, bonus2, format3)
                if rec['currentwage']:
                    sheet.write(row,col+10, rec['currentwage'], format3)
            if rec['duedegree'] and rec['appointmentdegree']:
                degree4 = str(rec['duedegree']) + " الدرجة "
                sheet.write(row,col+11, degree4, format4)
            if rec['duesalary'] and rec['appointmentsalary']:
                bonus3 = str(rec['duesalary']) + " علاوة "
                sheet.write(row,col+12, bonus3, format4)
            if rec['duewage'] and rec['appointmentwage']:
                sheet.write(row,col+13, rec['duewage'], format4)
            row += 1
            no +=1

        workbook.close()