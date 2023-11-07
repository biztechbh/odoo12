odoo.define('biztech_monthly_sales_report.main', function (require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    var SalesMonthlyDashboardReport = AbstractAction.extend(ControlPanelMixin, {
        title: core._t('Sales Monthly Dashboard Report'),
        template: 'SalesMonthlyDashboardReport',
        events: {
            'click .export_to_monthly_excel': 'export_as_monthly_excel',
            'click .export_to_monthly_pdf': 'export_as_monthly_pdf',
            'click .click_to_monthly_refresh': 'reopen_monthly_report',
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
        export_as_monthly_excel : function(){
            var self = this;
            var context = self.params.context;
            rpc.query({
                model: 'pos.order',
                method: 'export_as_excel_monthly_report_sales',
                args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                },$.blockUI({
					css: {
						cursor:'wait',
						border:'none',
						backgroundColor:'transparent'
					},
					message: '<img src="/biztech_daily_sales_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
				}), {async: false}).then(function (res) {
                if (res && res.report_id){
                    $.unblockUI();
                    self.do_action({
                        name: _t('Report'),
                        type: 'ir.actions.act_window',
                        res_model: 'report.monthly.wizard.download',
                        views: [[false, 'form']],
                        target: 'new',
                        res_id: res.report_id,
                    });
                }
            });
        },
        export_as_monthly_pdf : function(){
            var self = this;
            var context = self.params.context;
            rpc.query({
                model: 'pos.order',
                method: 'export_as_pdf_monthly_report_sales',
                args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                },$.blockUI({
					css: {
						cursor:'wait',
						border:'none',
						backgroundColor:'transparent'
					},
					message: '<img src="/biztech_daily_sales_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
				}), {async: false}).then(function (res) {
                if (res){
                    $.unblockUI();
                    self.do_action('biztech_monthly_sales_report.action_sales_monthly_dashboard_report',{additional_context:{
                        active_ids:[res],
                    }})
                }
            });
        },
        reopen_monthly_report : function(){
            var self = this;
            self.do_action('biztech_monthly_sales_report.action_monthly_pos_sales_report')
        },
        renderElement: function () {
            var self = this;
            this._super.apply(this, arguments);
            var context = self.params.context;
            if (context.from_date && context.to_date){
                $(self.$el.find('.summary')).show();
                $(self.$el.find('.report_name')).html('<span><b>Monthly Sales Report</b></span>');
                if (context.from_date && context.to_date ){
                    var d = context.from_date + '<b> TO </b>' + context.to_date;
                }
                else{
                    d = ''
                }
                $(self.$el.find('.dates')).html('<span><b>Date:</b>'+ d +'</span>');
                rpc.query({
                    model: 'pos.order',
                    method: 'get_monthly_sales_data',
                    args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                    }, $.blockUI({
							css: {
								cursor:'wait',
								border:'none',
								backgroundColor:'transparent'
							},
							message: '<img src="/biztech_monthly_sales_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
						}),{async: false}).then(function (res) {
                        if (res){
                        	$.unblockUI();
                        	var g_untax = 0;var g_tax = 0;var g_total = 0;var g_tot_mar = 0;var g_tot_per_mar = 0;var g_so = 0;
                        	var g_tot_qty = 0;var g_tot_rate = 0;var g_tot_vat = 0;var g_tot_discount = 0;var g_tot_amt = 0;
                            for (var prop in res) {
								var columns = [
									  {"name":"barcode","title":"Barcode"},
									  {"name":"product_id","title":"Product"},
									  {"name":"unit","title":"Unit","decimalSeparator": ".","thousandSeparator":","},
									  {"name":"qty","title":"QTY","type": "number","decimalSeparator": ".","thousandSeparator":","},
									  {"name":"with_out_amount","title":"Vat","type": "number","decimalSeparator": ".","thousandSeparator":","},
									  {"name":"net_amount","title":"Net Amount","type": "number","decimalSeparator": ".","thousandSeparator":","}
								]
								var class_name = res[prop][0]['card_title'] || 'Non-Defined';
								var html = '<div class="card">';
								html += '<div class="card-header">';
								html += '<h4 class="card-title">';
								html += '<a class="accordion-toggle" data-toggle="collapse" href="#'+class_name+'">';
								html += res[prop][0]['card_title'] || 'Non-Defined';
								html += '</a>';
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
									"rows": res[prop],
									'on': {
										'after.ft.paging': function(e, ft, filter) {
											if (filter && filter.total == filter.page){
												var rows = ft.rows.all;
												var tot_qty = 0;var tot_rate = 0;var tot_vat = 0;var tot_discount = 0;var tot_amt = 0;
												for (var i = 0, l = rows.length, row; i < l; i++){
													row = rows[i].val();
													tot_qty += parseFloat(row["qty"]);
													tot_rate += parseFloat(row["rate"]);
													tot_vat += parseFloat(row["with_out_amount"]);
													tot_discount += parseFloat(row["discount"]);
													tot_amt += parseFloat(row["net_amount"]);
												}
												var html = '<tr class=total_due_table_'+ class_name +'>';
												html += '<td></td>';
												html += '<td></td>';
												html += '<td></td>';
												html += '<td><b>Total: '+ tot_qty.toFixed(3) +'</b></td>';
												html += '<td><b>Total: '+ tot_vat.toFixed(3) +'</b></td>';
												html += '<td><b>Total: '+ tot_amt.toFixed(3) +'</b></td>';
												html += '</tr>';
												var foot = self.$el.find('.' + ft.classes[3] + ' tfoot');
												foot.prepend(html);
											}
										},
										'after.ft.filtering': function(e, ft, filter) {
											if (typeof filter !== 'undefined' && filter.length > 0) {
												if (typeof self.$el.find('.' + ft.classes[3] + ' tfoot .total_due_table_'+ft.classes[3]).html() !== 'undefined'){
													self.$el.find('.' + ft.classes[3] + ' tfoot .total_due_table_'+ft.classes[3]).hide();
												}
											}
											else{
												if (typeof self.$el.find('.' + ft.classes[3] + ' tfoot .total_due_table_'+ft.classes[3]).html() !== 'undefined'){
													self.$el.find('.' + ft.classes[3] + ' tfoot .total_due_table_'+ft.classes[3]).show();
												}
											}
										},
										'ready.ft.table': function(e, ft) {
											var rows = ft.rows.all;
											if (rows.length <= 10){
												var tot_qty = 0;var tot_rate = 0;var tot_vat = 0;var tot_discount = 0;var tot_amt = 0;
												for (var i = 0, l = rows.length, row; i < l; i++){
													row = rows[i].val();
													tot_qty += parseFloat(row["qty"]);
													tot_rate += parseFloat(row["rate"]);
													tot_vat += parseFloat(row["with_out_amount"]);
													tot_discount += parseFloat(row["discount"]);
													tot_amt += parseFloat(row["net_amount"]);
												}
												var html = '<tr class=total_due_table_'+ class_name +'>';
												html += '<td></td>';
												html += '<td></td>';
												html += '<td></td>';
												html += '<td><b>Total: '+ tot_qty.toFixed(3) +'</b></td>';
												html += '<td><b>Total: '+ tot_vat.toFixed(3) +'</b></td>';
												html += '<td><b>Total: '+ tot_amt.toFixed(3) +'</b></td>';
												html += '</tr>';
												var foot = self.$el.find('.' + ft.classes[3] + ' tfoot');
												foot.prepend(html);
											}
											for (var i = 0, l = rows.length, row; i < l; i++){
												row = rows[i].val();
												g_tot_qty += parseFloat(row["qty"]);
												g_tot_rate += parseFloat(row["rate"]);
												g_tot_vat += parseFloat(row["with_out_amount"]);
												g_tot_discount += parseFloat(row["discount"]);
												g_tot_amt += parseFloat(row["net_amount"]);
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
							g_html += '<th>'+ g_tot_qty.toFixed(3).toLocaleString('es') +'</th>';
							g_html += '<th>'+ g_tot_vat.toFixed(3).toLocaleString('es') +'</th>';
							g_html += '<th>'+ g_tot_amt.toFixed(3).toLocaleString('es') +'</th>';
							self.$el.find('.grand_table_per_date_container .tr_grand_total').append(g_html);
							self.$el.find('.grand_table_per_date_container').show();
                        }
                });
            }
            else{
                self.do_action('biztech_monthly_sales_report.action_monthly_pos_sales_report')
            }
        },
    });
    core.action_registry.add('open_sales_monthly_dashboard_report_view', SalesMonthlyDashboardReport);
    return {
    	SalesMonthlyDashboardReport: SalesMonthlyDashboardReport,
    };
});
