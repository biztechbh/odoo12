# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2020-Today(www.slecherpsolution.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def sltech_check_duplicate_lines(self):
        for line in self.order_line:
            if [x for x in self.order_line if x.product_id.id == line.product_id.id and x.id != line.id]:
                raise ValidationError('Please choose one item in one line only!')

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        res.sltech_check_duplicate_lines()
        return res

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        self.sltech_check_duplicate_lines()
        return res
