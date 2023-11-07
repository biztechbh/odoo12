# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api


class ir_actions_report(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def print_action_for_report_name(self, report_name, data=None):
        """ Returns if the action is a direct print or pdf Called from js """
        report = self._get_report_from_name(report_name)
        if not report:
            return {}

        serializable_result = {}

        if data and data.get('form') and data.get('form').get('print_behaviour') \
            and data.get('form').get('printing_printer_id'):

            serializable_result = {
                'action': data.get('form').get('print_behaviour'),
                'printer_name': self.env['printer.printer'].browse([data.get('form').get('printing_printer_id')[0]]).name}
        return serializable_result

    @api.model
    def print_document(self, record_ids, report_name, html=None, data=None):
        """ Print a document, do not return the document file """
        report = self._get_report_from_name(report_name)

        document = report.with_context(must_skip_send_to_printer=True).render_qweb_pdf(record_ids, data=data)

        if data and data.get('form') and data.get('form').get('printing_printer_id'):
            printer = self.env['printer.printer'].browse([data.get('form').get('printing_printer_id')[0]])

        if not printer:
            raise exceptions.Warning(_('No printer configured to print this report.'))

        return printer.print_document(report, document[0], report.report_type)

    @api.multi
    def _can_print_report(self, behaviour, printer, document):
        """Predicate that decide if report can be sent to printer
        If you want to prevent `get_pdf` to send report you can set
        the `must_skip_send_to_printer` key to True in the context
        """
        if self.env.context.get('must_skip_send_to_printer'):
            return False

        if behaviour['action'] == 'server' and printer and document:
            return True
        return False

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        """ Generate a PDF and returns it.
        If the action configured on the report is server, it prints the
        generated document as well.
        """
        printer = False
        document = super(ir_actions_report, self).render_qweb_pdf(res_ids=res_ids, data=data)
        report = self._get_report_from_name(self.report_name)
        if data and data.get('form') and data.get('form').get('print_behaviour') and data.get('form').get('printing_printer_id'):
            printer = self.env['printer.printer'].browse([data.get('form').get('printing_printer_id')[0]])
            behaviour = {
                'action': data.get('form').get('print_behaviour'),
                'printer': printer}

            can_print_report = self._can_print_report(behaviour, printer, document)
            if can_print_report:
                printer.print_document(report, document[0], report.report_type)
        return document

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
