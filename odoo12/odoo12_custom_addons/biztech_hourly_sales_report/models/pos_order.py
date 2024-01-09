

from odoo import models
import calendar, xlwt, base64
from datetime import datetime, timedelta
from io import BytesIO


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_hourly_sales_data(self, from_dt, to_dt, categ_id, product_id, shop_id):
        tz_new = self.env.user.tz
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d 00:00:00')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d 23:59:59')
        domain = f"(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date >= '{start_date}' AND (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date <= '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        if shop_id:
            domain += " AND po.shop_id = (%s)" % (shop_id)
        SQL = f'''
            select count(po.id), po.id, to_char((po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date, 'YYYY-MM-DD') as date_order,
                to_char((po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}'), 'HH24') as hour, round(sum(pol.price_subtotal), 3) as gross, round(sum(pol.discount), 3) as discount,
                round(SUM(pol.price_subtotal_incl - pol.price_subtotal), 3) as lumsum, round(sum(pol.price_subtotal_incl), 3) as bill_amount,
                poc.name as categ_name, round(po.rounding, 3) as round
                from pos_order_line as pol
                left join pos_order as po on po.id = pol.order_id
                left join product_product pp on pp.id = pol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join pos_category poc on poc.id = pt.pos_categ_id
            where {domain}
            group by po.date_order, pol.discount, pol.price_subtotal_incl, poc.name, po.id
            order by po.date_order
        '''
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        result_dict = {}
        for each1 in result:
            start = str(each1.get('hour'))
            start += ' - ' + (str('0' + str(int(each1.get('hour')) + 1) if int(each1.get('hour')) + 1 < 10 else int(each1.get('hour')) + 1))
            if start not in result_dict:
                result_dict[start] = {
                    'count': each1.get('count'),
                    'round': round(each1.get('round'), 3),
                    'id': each1.get('id'),
                    'hour': each1.get('hour'),
                    'gross': round(each1.get('gross'), 3),
                    'discount': round(each1.get('discount'), 3),
                    'lumsum': round(each1.get('lumsum'), 3),
                    'bill_amount': round(each1.get('bill_amount'), 3),
                    'time': start
                }
            else:
                result_dict[start].update({
                    'id': each1.get('id'),
                    'count': result_dict[start].get('count') if each1.get('id') == result_dict[start].get('id') else result_dict[start].get('count') + each1.get('count'),
                    'round': round(result_dict[start].get('round'), 3) if each1.get('id') == result_dict[start].get('id') else round((result_dict[start].get('round') + each1.get('round')), 3),
                    'gross': round((result_dict[start].get('gross') + each1.get('gross')), 3),
                    'discount': round((result_dict[start].get('discount') + each1.get('discount')), 3),
                    'lumsum': round((result_dict[start].get('lumsum') + each1.get('lumsum')), 3),
                    'bill_amount': round((result_dict[start].get('bill_amount') + each1.get('bill_amount')), 3),
                    'time': start
                })
            result_dict
        return result_dict

    def export_as_pdf_report_hourly_sales(self, from_dt, to_dt, categ_id, product_id, shop_id):

        data = self.get_hourly_sales_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            d = from_dt + ' TO ' + to_dt

            rep_name = 'Hourly Sales Report'
            summary = {
                'report_name': rep_name,
                'data': d
            }
            report_id = self.env['report.hourly.sale.wizard.download'].create({
                'name': 'Hourly Sales Report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'data_pdf': data,
                'summary': summary,
            })
            return report_id.id
        else:
            return False

    def export_as_excel_report_hourly_sales(self, from_dt, to_dt, categ_id, product_id, shop_id):
        currency = self.env.user.company_id.currency_id.symbol
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Report')
        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        heading = xlwt.easyxf('font: bold on, height 300; align: horiz center;')
        bold = xlwt.easyxf('font: bold on;')
        bold1 = xlwt.easyxf('font: bold on;align: horiz right;')
        cell = xlwt.easyxf('align: horiz right;')
        cell1 = xlwt.easyxf('align: horiz left;')
        data = self.get_hourly_sales_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            sheet.col(0).width = 256 * 20
            sheet.col(1).width = 256 * 20
            sheet.col(2).width = 256 * 20
            sheet.col(4).width = 256 * 20
            sheet.col(3).width = 256 * 20
            sheet.col(5).width = 256 * 20
            sheet.write_merge(0, 1, 0, 6, 'Hourly Sales Report', heading)
            i = 3
            g_tot_count = g_tot_gross = g_tot_discount = g_tot_round = g_tot_lumsum = g_tot_bill_amt = 0
            i = i + 2
            sheet.write(i, 0, "Time", bold1)
            sheet.write(i, 1, "No. of Patients", bold1)
            sheet.write(i, 2, "Gross", bold1)
            sheet.write(i, 3, "Discount", bold1)
            sheet.write(i, 4, "R/OFF", bold1)
            sheet.write(i, 5, "Lumsum", bold1)
            sheet.write(i, 6, "Bill Amount", bold1)
            i = i + 1
            for da in data.values():
                sheet.write(i, 0, str(da.get('time')), cell1)
                sheet.write(i, 1, str(da.get('count')), cell)
                g_tot_count += float(da.get('count'))
                sheet.write(i, 2, str("%0.3f" % da.get('gross')) + ' ' + currency, cell)
                g_tot_gross += float(da.get('gross'))
                sheet.write(i, 3, str("%0.3f" % da.get('discount')) + ' ' + currency, cell)
                g_tot_discount += float(da.get('discount'))
                sheet.write(i, 4, str("%0.3f" % da.get('round')) + ' ' + currency, cell)
                g_tot_round += float(da.get('round'))
                sheet.write(i, 5, str("%0.3f" % da.get('lumsum')) + ' ' + currency, cell)
                g_tot_lumsum += float(da.get('lumsum'))
                sheet.write(i, 6, str("%0.3f" % da.get('bill_amount')) + ' ' + currency, cell)
                g_tot_bill_amt += float(da.get('bill_amount'))
                i += 1
            sheet.write(i + 2, 0, 'Total:', bold)
            sheet.write(i + 2, 1, "%s" % int(g_tot_count), bold1)
            sheet.write(i + 2, 2, "%0.3f" % g_tot_gross + ' ' + currency, bold1)
            sheet.write(i + 2, 3, "%0.3f" % g_tot_discount + ' ' + currency, bold1)
            sheet.write(i + 2, 4, "%0.3f" % g_tot_round + ' ' + currency, bold1)
            sheet.write(i + 2, 5, "%0.3f" % g_tot_lumsum + ' ' + currency, bold1)
            sheet.write(i + 2, 6, "%0.3f" % g_tot_bill_amt + ' ' + currency, bold1)
            sheet.write(i + 2, 7, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.hourly.sale.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Hourly Sales Report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}
        else:
            False

