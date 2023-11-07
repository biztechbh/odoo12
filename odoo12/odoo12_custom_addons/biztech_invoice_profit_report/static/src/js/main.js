odoo.define('biztech_invoice_profit_report.main', function (require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    var InvoiceProfitReport = AbstractAction.extend(ControlPanelMixin, {
        title: core._t('Invoice Profit Report'),
        template: 'InvoiceProfitReport',
        events: {
            'click .export_to_excel': 'export_as_excel',
            'click .export_to_pdf': 'export_as_pdf',
            'click .click_to_refresh': 'reopen_report',
        },
        init: function (parent, params) {
            this._super.apply(this, arguments);
            var self = this;
            this.action_manager = parent;
            this.params = params;
        },
        start: function () {
            this._super.apply(this, arguments);
            var breadcrumbs = this.action_manager && this.action_manager._getBreadcrumbs() || [{
                title: this.title,
                action: this
            }];
            this.update_control_panel({breadcrumbs: breadcrumbs, search_view_hidden: true}, {clear: true});
        },
        export_as_excel : function(){
            var self = this;
            var context = self.params.context;
            rpc.query({
                model: 'pos.order',
                method: 'export_as_excel_report_invoice_profit',
                args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false],
                },$.blockUI({
					css: {
						cursor:'wait',
						border:'none',
						backgroundColor:'transparent'
					},
					message: '<img src="/biztech_invoice_profit_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
				}), {async: false}).then(function (res) {
                if (res && res.report_id){
                    $.unblockUI();
                    self.do_action({
                        name: _t('Report'),
                        type: 'ir.actions.act_window',
                        res_model: 'report.invoice.profit.wizard.download',
                        views: [[false, 'form']],
                        target: 'new',
                        res_id: res.report_id,
                    });
                }
            });
        },
        export_as_pdf : function(){
            var self = this;
            var context = self.params.context;
            rpc.query({
                model: 'pos.order',
                method: 'export_as_pdf_report_invoice_profit',
                args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false],
                },$.blockUI({
					css: {
						cursor:'wait',
						border:'none',
						backgroundColor:'transparent'
					},
					message: '<img src="/biztech_invoice_profit_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
				}), {async: false}).then(function (res) {
                if (res){
                    $.unblockUI();
                    self.do_action('biztech_invoice_profit_report.action_invoice_dashboard_report',{additional_context:{
                        active_ids:[res],
                    }})
                }
            });
        },
        reopen_report : function(){
            var self = this;
            self.do_action('biztech_invoice_profit_report.action_invoice_dashboard_wizard')
        },
        renderElement: function () {
            var self = this;
            this._super.apply(this, arguments);
            var context = self.params.context;
            if (context.from_date && context.to_date){
                $(self.$el.find('.summary')).show();
                $(self.$el.find('.report_name')).html('<span><b>Invoice Profit Report</b></span>');
                if (context.from_date && context.to_date ){
                    var d = context.from_date + '<b> TO </b>' + context.to_date;
                }
                else{
                    d = ''
                }
                $(self.$el.find('.dates')).html('<span><b>Date:</b>'+ d +'</span>');
                rpc.query({
                    model: 'pos.order',
                    method: 'get_invoice_profit_data',
                    args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false],
                    }, $.blockUI({
							css: {
								cursor:'wait',
								border:'none',
								backgroundColor:'transparent'
							},
							message: '<img src="/biztech_invoice_profit_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
						}),{async: false}).then(function (res) {
                        if (res){
                        	$.unblockUI();
                        	var g_tot_qty = 0;var g_tot_cost = 0;var g_tot_inv_amt = 0;var g_tot_profit = 0;var g_tot_profit_per = 0;
                            var columns = [
                                  {"name":"invoice_date","title":"Date"},
                                  {"name":"invoice_number","title":"Invoice No."},
                                  {"name":"barcode","title":"Barcode"},
                                  {"name":"product","title":"Product"},
                                  {"name":"qty","title":"QTY","type": "number","decimalSeparator": ".","thousandSeparator":","},
                                  {"name":"cost","title":"Cost","type": "number","decimalSeparator": ".","thousandSeparator":","},
                                  {"name":"invoice_amount","title":"Sale Amount","type": "number","decimalSeparator": ".","thousandSeparator":","},
                                  {"name":"profit_amount","title":"Profit Amount","type": "number","decimalSeparator": ".","thousandSeparator":","},
                                  {"name":"profit_per","title":"Profit %","type": "number","decimalSeparator": ".","thousandSeparator":","}
                            ]
                            var class_name = 'invoice_profit_report';
                            var html = '<div class="card">';
                            html += '<div class="card-header">';
                            html += '<h4 class="card-title">';
                            html += '</h4>';
                            html += '</div>';
                            html += '<div id="'+class_name+'" class="panel-collapse collapse show">';
                            html += '<div class="card-body">';
                            html += '<table class="table table-bordered table-hover '+class_name+' per_table" data-paging="true" data-filtering="true" data-sorting="true"/>'
                            html += '</div>';
                            html += '</div>';
                            html += '</div>';
                            self.$el.find('.table_per_date_container').append(html)
                            var selected_total_amount_list = [];
							var g_selected_total_amount_list = [];
							var selected_list = [];
							var g_selected_list = [];
								self.$el.find('.'+class_name).footable({
									"columns": columns,
									"rows": res,
									'on': {
										'ready.ft.table': function(e, ft) {
											var rows = ft.rows.all;
											for (var i = 0, l = rows.length, row; i < l; i++){
												row = rows[i].val();
												g_tot_qty += parseInt(row["qty"]);
												g_tot_cost += parseFloat(row["cost"]);
												g_tot_inv_amt += parseFloat(row["invoice_amount"]);
												g_tot_profit += parseFloat(row["profit_amount"]);
												g_tot_profit_per += parseFloat(row["profit_per"]);
											}
										},
									}
								});
							}
                            var g_html = '<th/>';
							g_html += '<th/>';
							g_html += '<th/>';
							g_html += '<th/>';
							g_html += '<th/>';
							g_html += '<th>'+ g_tot_qty.toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_cost.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_inv_amt.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_profit.toFixed(3).toLocaleString('en') +'</th>';
							self.$el.find('.grand_table_per_date_container .tr_grand_total').append(g_html);
							self.$el.find('.grand_table_per_date_container').show();
                });
            }
            else{
                self.do_action('biztech_invoice_profit_report.action_invoice_dashboard_wizard')
            }
        },
    });
    core.action_registry.add('open_invoice_profit_report_view', InvoiceProfitReport);
    return {
        InvoiceProfitReport: InvoiceProfitReport,
    };
});