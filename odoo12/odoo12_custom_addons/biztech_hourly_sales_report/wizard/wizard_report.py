
from odoo import models, fields, api
from collections import OrderedDict
import ast
from ast import literal_eval
import json
import datetime


class ReportWizardDownload(models.TransientModel):
    _name = 'report.hourly.sale.wizard.download'

    name = fields.Char(string='File Name', readonly=True)
    data = fields.Binary(string='File', readonly=True)
    data_pdf = fields.Text(string="Data")
    summary = fields.Text(string="Summary")

    @api.multi
    def get_data(self):
        if self.data_pdf:
            dict = eval(self.data_pdf)
            return dict

    @api.multi
    def get_sorted_data(self, data_old, is_per_date):
        if data_old and not is_per_date:
            return OrderedDict(sorted(data_old.items(), key=lambda t: int(t[0])))
        elif data_old and is_per_date:
            return OrderedDict(sorted(data_old.items(), key=lambda t: t[0]))

    @api.multi
    def get_summary(self):
        if self.summary:
            dict = eval(self.summary)
            return dict

