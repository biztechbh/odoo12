# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime


class report_tax(models.AbstractModel):
    _name = 'report.flexipharmacy.tax_report_template'
    _description = 'Report Tax'

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     if not data.get('form') or not self.env.context.get('active_model'):
    #         raise UserError(_("Form content is missing, this report cannot be printed."))
    #
    #     account_result = {}
    #     self.model = self.env.context.get('active_model')
    #     docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
    #     display_account = data['form'].get('display_account')
    #     accounts = self.env['account.account'].search([])
    #     date_from = data.get('form') and data.get('form').get('date_from')
    #     date_to = data.get('form') and data.get('form').get('date_to')
    #     where_clause = ""
    #     SQL = """
    #         SELECT
    #           ait.tax_id as tax_id,
    #           ait.base as base,
    #           ait.amount as amount,
    #           at.name as name,
    #           at.type_tax_use as type
    #         FROM
    #           account_move_line as aml,
    #           account_move as am,
    #           account_move_line_account_tax_rel as tax_rel,
    #           account_invoice_tax as ait,
    #           account_invoice as ai,
    #           account_tax as at
    #         WHERE
    #           aml.move_id = am.id AND
    #           aml.invoice_id = ai.id AND
    #           aml.id = tax_rel.account_move_line_id AND
    #           ait.invoice_id = ai.id AND
    #           ait.tax_id = at.id AND
    #           at.type_tax_use in ('sale', 'purchase') AND
    #           am.state = 'posted'
    #     """
    #
    #     if date_from:
    #         where_clause += "AND am.date >= '%s' "% (date_from)
    #     if date_to:
    #         where_clause += "AND am.date <= '%s' "% (date_to)
    #     self.env.cr.execute(SQL + where_clause)
    #     res = self.env.cr.dictfetchall()
    #     groups = dict((tp, []) for tp in ['sale', 'purchase'])
    #     for row in res:
    #         tax_id = self.env['account.tax'].browse(row['tax_id'])
    #         if row['tax_id'] in list(account_result.keys()):
    #             account_result[row['tax_id']]['base'] += row.get('base')
    #             account_result[row['tax_id']]['amount'] += row.get('amount')
    #         else:
    #             account_result[row.pop('tax_id')] = row
    #     for each in account_result.values():
    #         groups[each['type']].append(each)

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form'],
            'lines': self.get_lines(data.get('form')),
        }

    def _sql_from_amls_one(self):
        sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                        FROM %s
                        WHERE %s AND "account_move_line".tax_exigible GROUP BY "account_move_line".tax_line_id"""
        return sql

    def _sql_from_amls_two(self):
        sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                     FROM %s
                     INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                     INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                     WHERE %s AND "account_move_line".tax_exigible GROUP BY r.account_tax_id"""
        return sql

    def _compute_from_amls(self, options, taxes):
        # compute the tax amount
        sql = self._sql_from_amls_one()
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['tax'] = abs(result[1])

        # compute the net amount
        sql2 = self._sql_from_amls_two()
        query = sql2 % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['net'] = abs(result[1])

    @api.model
    def get_lines(self, options):
        taxes = {}
        for tax in self.env['account.tax'].search([('type_tax_use', '!=', 'none')]):
            if tax.children_tax_ids:
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    taxes[child.id] = {'tax': 0, 'net': 0, 'name': child.name, 'type': tax.type_tax_use}
            else:
                taxes[tax.id] = {'tax': 0, 'net': 0, 'name': tax.name, 'type': tax.type_tax_use}
        self.with_context(date_from=options['date_from'], date_to=options['date_to'],
                          strict_range=True)._compute_from_amls(options, taxes)
        groups = dict((tp, []) for tp in ['sale', 'purchase'])
        for tax in taxes.values():
            if tax['tax']:
                groups[tax['type']].append(tax)
        return groups