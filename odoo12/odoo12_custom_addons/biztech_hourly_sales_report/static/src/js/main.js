odoo.define('biztech_hourly_sales_report.main', function (require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    var HourlySalesReport = AbstractAction.extend(ControlPanelMixin, {
        title: core._t('Hourly Sales Report'),
        template: 'HourlySalesReport',
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
                method: 'export_as_excel_report_hourly_sales',
                args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                },$.blockUI({
					css: {
						cursor:'wait',
						border:'none',
						backgroundColor:'transparent'
					},
					message: '<img src="/biztech_hourly_sales_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
				}), {async: false}).then(function (res) {
                if (res && res.report_id){
                    $.unblockUI();
                    self.do_action({
                        name: _t('Report'),
                        type: 'ir.actions.act_window',
                        res_model: 'report.hourly.sale.wizard.download',
                        views: [[false, 'form']],
                        target: 'new',
                        res_id: res.report_id,
                    });
                }else{
                    $.unblockUI();
                }
            });
        },
        export_as_pdf : function(){
            var self = this;
            var context = self.params.context;
            rpc.query({
                model: 'pos.order',
                method: 'export_as_pdf_report_hourly_sales',
                args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                },$.blockUI({
					css: {
						cursor:'wait',
						border:'none',
						backgroundColor:'transparent'
					},
					message: '<img src="/biztech_hourly_sales_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
				}), {async: false}).then(function (res) {
                if (res){
                    $.unblockUI();
                    self.do_action('biztech_hourly_sales_report.action_hourly_sales_dashboard_report',{additional_context:{
                        active_ids:[res],
                    }})
                }else{
                    $.unblockUI();
                }
            });
        },
        reopen_report : function(){
            var self = this;
            self.do_action('biztech_hourly_sales_report.action_hourly_sales_dashboard_wizard')
        },
        renderElement: function () {
            var self = this;
            this._super.apply(this, arguments);
            var context = self.params.context;
            if (context.from_date && context.to_date){
                $(self.$el.find('.summary')).show();
                $(self.$el.find('.report_name')).html('<span><b>Hourly Sales Report</b></span>');
                if (context.from_date && context.to_date ){
                    var d = context.from_date + '<b> TO </b>' + context.to_date;
                }
                else{
                    d = ''
                }
                $(self.$el.find('.dates')).html('<span><b>Date:</b>'+ d +'</span>');
                rpc.query({
                    model: 'pos.order',
                    method: 'get_hourly_sales_data',
                    args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                    }, $.blockUI({
							css: {
								cursor:'wait',
								border:'none',
								backgroundColor:'transparent'
							},
							message: '<img src="/biztech_hourly_sales_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
						}),{async: false}).then(function (res) {
                        if (res){
                        	$.unblockUI();
                        	var g_tot_count = 0;var g_tot_gross = 0;var g_tot_discount = 0;var g_tot_round = 0;var g_tot_lumsum = 0;var g_tot_bill_amt = 0;
                            var columns = [
                              {"name":"time","title":"Time"},
                              {"name":"count","title":"No. of Patients","type": "number","thousandSeparator":","},
                              {"name":"gross","title":"Gross","type": "number","decimalSeparator": ".","thousandSeparator":","},
                              {"name":"discount","title":"Discount","type": "number","decimalSeparator": ".","thousandSeparator":","},
                              {"name":"round","title":"R/OFF","type": "number","decimalSeparator": ".","thousandSeparator":","},
                              {"name":"lumsum","title":"LUMSUM","type": "number","decimalSeparator": ".","thousandSeparator":","},
                              {"name":"bill_amount","title":"Bill Amount","type": "number","decimalSeparator": ".","thousandSeparator":","},
                            ]

                            var class_name = 'hourly_sale';
                            var html = '<div class="card">';
                            html += '<div class="card-header">';
                            html += '<h4 class="card-title">';
                            html += '<a class="accordion-toggle" data-toggle="collapse" href="#'+class_name+'">';
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
								self.$el.find('.hourly_sale').footable({
									"columns": columns,
									"rows": Object.values(res),
									'on': {
										'ready.ft.table': function(e, ft) {
											var rows = ft.rows.all;
											for (var i = 0, l = rows.length, row; i < l; i++){
												row = rows[i].val();
												g_tot_count += parseInt(row["count"]);
												g_tot_gross += parseFloat(row["gross"]);
												g_tot_discount += parseFloat(row["discount"]);
												g_tot_round += parseFloat(row["round"]);
												g_tot_lumsum += parseFloat(row["lumsum"]);
												g_tot_bill_amt += parseFloat(row["bill_amount"]);
											}
										},
									}
								});
                            var g_html = '<th/>';
							g_html += '<th/>';
							g_html += '<th/>';
							g_html += '<th/>';
							g_html += '<th>'+ g_tot_count.toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_gross.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_discount.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_round.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_lumsum.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_bill_amt.toFixed(3).toLocaleString('en') +'</th>';
							self.$el.find('.grand_table_per_date_container .tr_grand_total').append(g_html);
							self.$el.find('.grand_table_per_date_container').show();
                        }
                });
            }
            else{
                self.do_action('biztech_hourly_sales_report.action_hourly_sales_dashboard_wizard')
            }
        },
    });
    core.action_registry.add('open_hourly_sales_report_view', HourlySalesReport);
    return {
        HourlySalesReport: HourlySalesReport,
    };
});
