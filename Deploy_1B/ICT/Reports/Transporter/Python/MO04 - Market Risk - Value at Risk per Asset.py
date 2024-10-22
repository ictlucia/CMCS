import acm,csv,math
from datetime import datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

current_date = get_current_date("")
current_hour = get_current_hour("")
date_today = acm.Time.DateToday()
date,month,year = current_date[:2],current_date[2:4],current_date[4:]



product = {
        "[Trade Set] Plain Vanilla",
        "[Trade Set] Cross Currency Swap",
        "[Trade Set] FX Option",
        "[Trade Set] Bonds",
        "[Trade Set] Interest Rate Swap",
        "[Trade Set] Par Forward",
        "[Trade Set] Bond Forward",
        "[Trade Set] Bond Option",
        "[Trade Set] Forward Rate Agreement"
        }


def get_items(csvpath,csvname):
    with open(csvpath+"\\report"+year+month+date+"\\"+csvname+".csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        for _ in range(9):
            next(reader)
        
        # Read the remaining lines into a list
        data = list(reader)
    return data
    
    
def get_market_value_port(data,prods):
    list_data = []
    data_dict = {}
    for each_data in data:
        if each_data[0] in prods:
            prod = each_data[0]
            list_data.append([prod,each_data[1]])
    
    for item,value in list_data:
        if value.lower() == "nan":
            value = 0
        if item in data_dict:
            data_dict[item]+=float(f"{value}")
        else:
            data_dict[item]=float(f"{value}")

    return data_dict
    

def get_1DChange(qf_operation):
    jakarta = acm.FCalendar['Jakarta']
    today = acm.Time.DateToday()
    yesterday = acm.Time.DateAdjustPeriod(today,'-1d',jakarta,2)
    watermark_today = {}
    watermark_yesterday = {}
    threshold_value = {}
    oneday_change = {}
    for each_qf_item in qf_operation.Query().Select():
        watermark = each_qf_item.WatermarkValue()
        timestamp = each_qf_item.CreateTime()
        target_name = each_qf_item.ResultHistory().AppliedRule().Target().Name()
        threshold = each_qf_item.Threshold()
        type = each_qf_item.ResultHistory().ThresholdValue().Threshold().Type().Name()
        if datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d') == today:
            if target_name not in watermark_today or timestamp > watermark_today[target_name][1]:
                watermark_today[target_name] = (watermark,timestamp,type)
                threshold_value[target_name] = threshold
        if datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d') == yesterday:
            if target_name not in watermark_yesterday or timestamp > watermark_yesterday[target_name][1]:
                watermark_yesterday[target_name] = (watermark,timestamp)
                
    for each_ts,wm_items in watermark_today.items():
        for each_ts2,wm_items2 in watermark_yesterday.items():
            if each_ts == each_ts2:
                oneday_change[each_ts] = wm_items[0] - wm_items2[0]
                
    
        
    
    return oneday_change,watermark_today,threshold_value


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Value at Risk per Asset'}

ael_variables=[
['report_name','Report Name','string', None, 'MO04 - Market Risk - Value at Risk per Asset', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['csv_name','CSV File Name','string',None,'MO04 - Market Risk - Value at Risk',1,0], 
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
]  


def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    csvname = parameter['csv_name']
    output_file = parameter['output_file']
    
    all_data = get_items(file_path,csvname)
    market_value = get_market_value_port(all_data,product)
    
    hvar_obj = acm.FStoredASQLQuery['MO04 - Utilization Historical per Asset']
    net_watermark_hvar,watermark_today_hvar,threshold_value_hvar = get_1DChange(hvar_obj)
    
    marginal_obj = acm.FStoredASQLQuery['MO04 - Utilization Marginal']
    net_watermark_marg,watermark_today_marg,threshold_value_marg = get_1DChange(marginal_obj)
    
    incremental_obj = acm.FStoredASQLQuery['MO04 - Utilization Incremental']
    net_watermark_inc,watermark_today_inc,threshold_value_inc = get_1DChange(incremental_obj)
    
    ir_var_obj = acm.FStoredASQLQuery['MO04 - Utilization IR']
    net_watermark_ir,watermark_today_ir,threshold_value_ir = get_1DChange(ir_var_obj)
    
    fx_var_obj = acm.FStoredASQLQuery['MO04 - Utilization FX']
    net_watermark_fx,watermark_today_fx,threshold_value_fx = get_1DChange(fx_var_obj)
    
    var_cr_obj = acm.FStoredASQLQuery['MO04 - Utilization Credit']
    net_watermark_cr,watermark_today_cr,threshold_value_cr = get_1DChange(var_cr_obj)
    
    sf_obj = acm.FStoredASQLQuery['MO04 - Utilization Expected Shortfall']
    net_watermark_sf,watermark_today_sf,threshold_value_sf = get_1DChange(sf_obj)
    
    title_style = """
            .title {
                color: #800000;
                text-align: center;   
            }

            .subtitle-1 {
                color: #0000FF;
                font-size: 20px;
                text-align: left;
                font-weight: bold;

            }

            .subtitle-2 {
                color: #000080;
                font-size: 16px;
                text-align: left;
            }
            
            .bold {
                font-weight: bold;
            }
            
            .red {
                background-color:red;
            }
        
            .green {
                background-color:green;
            }
            
            .yellow {
                background-color:yellow;
            }

        """

    html_content = html_gen.create_base_html_content("MO04 - Market Risk - Value At Risk per Asset as per " + date_today, title_style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("MO04 - Market Risk - Value At Risk per Asset as per " + date_today)

    html_content = html_gen.prepare_html_table(html_content,'')
    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""

    title = ['Hierarchy','Market Value of Portfolio','Historical Var Simulation Total','Marginal VaR','Incremental VaR','VaR Interest Rate Risk Factor','VaR Foreign Exchange Risk Factor','VaR Credit Risk Factor','Expected Shortfall']

    subtitle = ['Utilisasi','1 Day Change','Utilisasi','1 Day Change','Utilisasi','1 Day Change','Utilisasi','1 Day Change','Utilisasi','1 Day Change','Utilisasi','1 Day Change','Utilisasi','1 Day Change']
                
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    
    for index in range(len(title)):
        if index == 0 or index == 1:
            html_content = html_gen.add_cell_data(html_content,title[index],'rowspan=2 class="bold"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,title[index],'number-rows-spanned="2" font-weight="bold"')
        else:
            html_content = html_gen.add_cell_data(html_content,title[index],'colspan=2 class="bold"')
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,title[index],'number-columns-spanned="2" font-weight="bold"')

    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)

    html_content = html_gen.add_data_row(html_content,[subtitle])
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[subtitle])
    
    for each_ts,items in market_value.items():
        utilisasi = 0
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        
        html_content = html_gen.add_cell_data(html_content,each_ts)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_ts)
        
        html_content = html_gen.add_cell_data(html_content,f"{round(items,2):,}")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{round(items,2):,}")
        
        #HVar
        try:        
            utilisasi = watermark_today_hvar[each_ts][0]
            html_content = html_gen.add_cell_data(html_content,f"{float(utilisasi):,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{float(utilisasi):,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
        try:        
            onedaychange_hvar = net_watermark_hvar[each_ts]
            html_content = html_gen.add_cell_data(html_content,f"{onedaychange_hvar:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{onedaychange_hvar:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
            
        #Marginal VAR
        try:        
            utilisasi_marginal = watermark_today_marg[each_ts][0]
            html_content = html_gen.add_cell_data(html_content,f"{utilisasi_marginal:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{utilisasi_marginal:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
        
        try:        
            onedaychange_marginal = net_watermark_marg[each_ts]
            html_content = html_gen.add_cell_data(html_content,f"{onedaychange_marginal:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{onedaychange_marginal:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
            
            
            
        #Incremental VAR    
        try:        
            utilisasi_incremental = watermark_today_inc[each_ts][0]
            html_content = html_gen.add_cell_data(html_content,f"{utilisasi_incremental:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{utilisasi_incremental:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
        try:        
            onedaychange_incremental = net_watermark_inc[each_ts]
            html_content = html_gen.add_cell_data(html_content,f"{onedaychange_incremental:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{onedaychange_incremental:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
            
            
        #IR VAR
        try:        
            utilisasi_ir = watermark_today_ir[each_ts][0]
            html_content = html_gen.add_cell_data(html_content,f"{utilisasi_ir:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{utilisasi_ir:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
        try:        
            onedaychange_ir = net_watermark_ir[each_ts]
            html_content = html_gen.add_cell_data(html_content,f"{onedaychange_ir:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{onedaychange_ir:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
        
        
        
        #FX VAR
        try:        
            utilisasi_fx = watermark_today_fx[each_ts][0]
            html_content = html_gen.add_cell_data(html_content,f"{utilisasi_fx:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{utilisasi_fx:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
        try:        
            onedaychange_fx = net_watermark_fx[each_ts]
            html_content = html_gen.add_cell_data(html_content,f"{onedaychange_fx:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{onedaychange_fx:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
            
        #Credit Risk VAR
        try:        
            utilisasi_cr = watermark_today_cr[each_ts][0]
            html_content = html_gen.add_cell_data(html_content,f"{utilisasi_cr:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{utilisasi_cr:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
        try:        
            onedaychange_cr = net_watermark_cr[each_ts]
            html_content = html_gen.add_cell_data(html_content,f"{onedaychange_cr:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{onedaychange_cr:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
            
        #SF VAR
        try:        
            utilisasi_sf = watermark_today_sf[each_ts][0]
            html_content = html_gen.add_cell_data(html_content,f"{utilisasi_sf:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{utilisasi_sf:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
            
        try:        
            onedaychange_sf = net_watermark_sf[each_ts]
            html_content = html_gen.add_cell_data(html_content,f"{onedaychange_sf:,}")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,f"{onedaychange_sf:,}")
        except KeyError:
            html_content = html_gen.add_cell_data(html_content,0)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0)
        
        
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)

    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)

    html_file = html_gen.create_html_file(html_content, file_path, report_name+" "+current_date+current_hour, current_date, True)
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name+" "+current_date+current_hour,file_path, xsl_fo_content, current_date)


    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
