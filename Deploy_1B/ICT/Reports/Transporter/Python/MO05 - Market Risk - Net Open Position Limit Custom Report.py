import acm, ael, random, os
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from time import sleep, perf_counter
from datetime import datetime, date, timezone
from Python_MO_Custom_Fields import *

context = acm.GetDefaultContext( )
today = acm.Time.DateToday()
sheet_type = 'FPortfolioSheet'    

portfolio_keywords = ['FXT', 'IRT', 'CLIENT_BOOK']
fxt_departments = ['Dept Head', 'Derivatives', 'Specialist', 'Spot Emerging', 'Spot Major']
irt_departments = ['DCM', 'Dept Head', 'Derivative', 'MM', 'Specialist']
client_book_departments = ['TAS', 'TRC', 'TWC']
trc_departments = ['Banknotes', 'Client Bonds', 'FX Retail']


all_non_comp_ports1 = ael.asql("select p.prfid from Portfolio p where p.compound='no'")[1][0]
all_non_comp_ports = [ port[0] for port in all_non_comp_ports1 ]

if '' in all_non_comp_ports:
    all_non_comp_ports.remove('')

def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection

def get_applied_rule_qf(qf, report_code):
    qf_def_name = qf.Name()
    qf_name = report_code +  '_Calculation_' + qf_def_name
    cur_qf = acm.FStoredASQLQuery[qf_name]

    if cur_qf is not None:
        cur_qf.Delete()

    cur_qf = qf.Clone()
    #xml_text = qf.Text()
    #new_xml_text = xml_text.replace(old_text, new_text)
    #ur_qf.Text(new_xml_text)
    cur_qf.Name(qf_name)
    cur_qf.Commit()
    
    return cur_qf 


# ================ DATA FILTER COLUMN ================
comp_ports_dict = {}
non_comp_port_calc_dict = {}


qf_trade_dicts = {
    "Plain Vanilla": {},
    "CCS": {},
    "Par FWD": {},
    "Other Structured Product": {},
    "Surat Berharga/Fixed Income": {},
    "IRS": {},
    "Bond Forward": {},
    "Bond Option": {},
    "Forward Rate Agreement": {}
}

qf_index_dicts = {
    "[Trade Set] Plain Vanilla": ["[Trade Set] Plain Vanilla", 0, 0, "Plain Vanilla", True],
    "[Trade Set] Cross Currency Swap": ["[Trade Set] Cross Currency Swap", 0, 0, "CCS", True],
    "[Trade Set] Par Forward": ["[Trade Set] Par Forward", 0, 0, "Par FWD", True],
    "[Trade Set] Other Structured Product": ["[Trade Set] Other Structured Product", 0, 0, "Other Structured Product", False],
    "[Trade Set] Bonds": ["[Trade Set] Bonds", 0, 0, "Surat Berharga/Fixed Income", True],
    "[Trade Set] Interest Rate Swap": ["[Trade Set] Interest Rate Swap", 0, 0, "IRS", True],
    "[Trade Set] Bond Forward": ["[Trade Set] Bond Forward", 0, 0, "Bond Forward", True],
    "[Trade Set] Bond Option": ["[Trade Set] Bond Option", 0, 0, "Bond Option", False],
    "[Trade Set] Forward Rate Agreement": ["[Trade Set] Forward Rate Agreement", 0, 0, "Forward Rate Agreement", True]
}

all_queries = [ query[0] for query in list(qf_index_dicts.values()) ]


def get_status_color_by_threshold_type(threshold_val):
    if threshold_val.Threshold().Type().Name() == 'Warning':
        return 'Yellow'
    elif threshold_val.Threshold().Type().Name() == 'Violation':
        return 'Red'
    else:
        return 'Orange'

def get_comparison_result_from_threshold_and_util_value(threshold_val, util_val):
    comparison_type = threshold_val.Threshold().ComparisonType()
    threshold_limit = threshold_val.ValueAdjusted()
    if comparison_type == 'Greater':
        return threshold_limit < util_val
    elif comparison_type == 'Greater or Equal':
        return threshold_limit <= util_val
    elif comparison_type == 'Less':
        return threshold_limit > util_val
    elif comparison_type == 'Less or Equal':
        return threshold_limit >= util_val
    elif comparison_type == 'Equal':
        return threshold_limit == util_val
    elif comparison_type == 'Not Equal':
        return threshold_limit != util_val
    else:
        return None

def get_threshold_value_by_type(tv_list, selected_type):
    filtered_tv_list = [ tv for tv in tv_list if tv.Threshold().Type().Name() == selected_type ]
    if len(filtered_tv_list) > 0:
        return filtered_tv_list[-1]
    else:
        return None

def final_nop_pv(qf, calc_space, rule_obj):
    #column_id = rule_obj.Definition().Column().OriginalColumnId().AsString()
    column_id = 'Final NOP Portfolio(old)'

    return get_trading_sheet_column_value(qf, calc_space, column_id)

def fxt_portfolios(fxt_portnbr):
    fxt_port = acm.FPhysicalPortfolio[fxt_portnbr]
    fxt_ports = [fxt_port]
    fxt_dept_ports = get_portfolios_by_comp_portfolio(fxt_port.Name())
    for port in fxt_dept_ports:
        fxt_ports.append(port)
        if any(x in port.Name() for x in fxt_departments[1:] ) and port.Compound():
            temp_fxt_ports = get_portfolios_by_comp_portfolio(port.Name())
            fxt_ports.extend(temp_fxt_ports)
    return fxt_ports

def irt_portfolios(irt_portnbr):
    irt_port = acm.FPhysicalPortfolio[irt_portnbr]
    irt_ports = [irt_port]
    irt_dept_ports = get_portfolios_by_comp_portfolio(irt_port.Name())
    for port in irt_dept_ports:
        irt_ports.append(port)
        if any(x in port.Name() for x in irt_departments) and port.Compound():
            temp_irt_ports = get_portfolios_by_comp_portfolio(port.Name())
            irt_ports.extend(temp_irt_ports)
    return irt_ports

def client_book_portfolios(cb_portnbr):
    cb_port = acm.FPhysicalPortfolio[cb_portnbr]
    cb_ports = [cb_port]
    cb_dept_ports = get_portfolios_by_comp_portfolio(cb_port.Name())
    for port in cb_dept_ports:
        cb_ports.append(port)
        if any(x in port.Name() for x in client_book_departments) and port.Compound():
            temp_cb_ports = get_portfolios_by_comp_portfolio(port.Name())
            for port2 in temp_cb_ports:
                cb_ports.append(port2)
                if any( y in port2.Name() for y in trc_departments) and port2.Compound():
                    temp_cb_ports2 = get_portfolios_by_comp_portfolio(port2.Name())
                    cb_ports.extend(temp_cb_ports2)
    return cb_ports

def isAllCompound(ports):
    bool_ports = [port.Compound() for port in ports]
    if True in bool_ports:
        return True
    else:
        return False

def get_portfolios(ports):
    final_ports = ports
    
    allCompound = True
    for port in final_ports:
        if port.Compound():
            final_ports.extend( get_portfolios_by_comp_portfolio( port.Name() ) )
            port_ind = final_ports.index(port)
            final_ports.pop(port_ind)
            #print(final_ports)
    allCompound = isAllCompound(final_ports)
    if allCompound:
        return get_portfolios(final_ports)
    else:
        return final_ports

def get_portfolios_by_comp_portfolio(comp_port_name):
    portfolio_links = acm.FPortfolioLink.Select("ownerPortfolio='"+comp_port_name+"'")
    ports = [ port_link.MemberPortfolio() for port_link in portfolio_links ]
    return ports

def set_portfolio_value_from_external_file(key, cell_contents):
    start_ind = qf_index_dicts[key][1]
    end_ind = qf_index_dicts[key][2]
    prod_key = qf_index_dicts[key][3]

    for cell in cell_contents[start_ind:end_ind]:
        if '#' not in cell[1] and 'NaN' not in cell[1]:
            qf_trade_dicts[prod_key][cell[0]] = float(cell[1])


def comp_port_calculation(comp_port, key_name):
    res_ports = comp_ports_dict[comp_port.Name()]
    total_calc = 0.0
    for port in res_ports:
        trade_calc = non_comp_port_calc_dict[port.Name()][key_name]
        total_calc += trade_calc
    return total_calc

def NaN_to_zero(val):
    check_val = str(val)
    if check_val.lower() == 'nan':
        return 0.0
    else:
        return float(val)

def get_trading_sheet_column_value(obj, calc_space, col_name):
    #col_val = calc_space.CreateCalculation(obj, col_name).Value()
    #print(col_val)
    try:
        col_val = calc_space.CreateCalculation(obj, col_name).Value()
        num = NaN_to_zero( col_val.Number() )
        #num = float(col_val.Number())
        res_val = num
    except:
        res_val = 0.0
    return res_val


def thousand_dot_sep(val):
    if abs(val) >= 1000.0:
        res_val = "{:,.2f}".format(val).replace(',',' ').replace('.',',').replace(' ','.')
    else:
        res_val = "{:,.2f}".format(val).replace('.',',')
    return res_val
    
def total_nop(products):
    total = 0.0
    for i in products:
        total = total + i
    return total

def percentage_removal(val):
    val = val.replace(',','.')
    res = float(val[:-1])
    return res
        

def limit_indicator(tv_list, util_val):
    reporting_tv = get_threshold_value_by_type(tv_list, 'Reporting')
    violation_tv = get_threshold_value_by_type(tv_list, 'Violation')
    warning_tv = get_threshold_value_by_type(tv_list, 'Warning')

    if reporting_tv is not None:
        rep_compa_result = get_comparison_result_from_threshold_and_util_value(reporting_tv, util_val)
    else:
        rep_compa_result = False

    if violation_tv is not None:
        vio_compa_result = get_comparison_result_from_threshold_and_util_value(violation_tv, util_val)
    else:
        vio_compa_result = False

    if warning_tv is not None:
        war_compa_result = get_comparison_result_from_threshold_and_util_value(warning_tv, util_val)
    else:
        war_compa_result = False


    if rep_compa_result:
        return 'Green'
    else:
        if vio_compa_result:
            return 'Red'
        else:
            if war_compa_result:
                return 'Yellow'
            else:
                return 'Green'

def compliance_rule_list(rule_def, rule_category):
    return [ comp_rule.Name() for comp_rule in acm.FComplianceRule.Select("definitionInfo='"+rule_def+"' and ruleCategory='"+rule_category+"'") ]

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'MO05 - Market Risk - Net Open Position Limit'}

#settings.FILE_EXTENSIONS

ael_variables=[
['report_name','Report Name','string', None, 'MO05 - Market Risk - Net Open Position Limit', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['raw_data_name','Raw Data Name','string', None, 'NOP_old_Calculation_RawData', 1,0],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output'],
['compliance_rule_name', 'Compliance Rule', 'string', compliance_rule_list('Exposure', 'Compliance'), 'NOP Limit - UAT (Tito)', 0, 0, 'Select Compliance rule Name']
]  

def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    raw_data_name = parameter['raw_data_name']
    output_file = parameter['output_file']
    rule_name = str(parameter['compliance_rule_name'])
    
    #rule_name = "NOP Limit - UAT (Tito)"

    raw_data_dir_name = os.path.join(file_path, raw_data_name + '.csv')

    if os.path.exists(raw_data_dir_name):

        fxt_ports = ael.asql(f"""Select p.prfnbr, p.prfid from Portfolio p where p.prfid like 'FXT%' and p.prfid not like '%{" and p.prfid not like '%".join( [x + "'" for x in fxt_departments[1:] ] )} and p.compound='yes'""")[1][0]
        irt_ports = ael.asql(f"""Select p.prfnbr, p.prfid from Portfolio p where p.prfid like 'IRT%' and p.prfid not like '%{" and p.prfid not like '%".join( [x + "'" for x in irt_departments ] )} and p.compound='yes'""")[1][0]
        client_book_ports = ael.asql("Select p.prfnbr, p.prfid from Portfolio p where p.prfid like 'CLIENT_BOOK%'")[1][0]
        
        rd_file = open(raw_data_dir_name, 'r')
        contents = rd_file.read()
        rd_file.close()

        cell_contents = [ list(content.split(',')) for content in list(contents.split('\n'))]

        filtered_cells = []
        for cell in cell_contents:
            if cell[0] in all_queries or cell[0] in all_non_comp_ports:
                filtered_cells.append(cell)

        for key, value in qf_index_dicts.items():
    
            for i in range(0, len(filtered_cells)):
                if value[0] in filtered_cells[i]:
                    value[1] = i+1

        key_list = [ valid_item for valid_item in list(qf_index_dicts.keys()) if qf_index_dicts[valid_item][4] ]

        for i in range( len(key_list) ):
            if i+1 < len(key_list):
                qf_index_dicts[key_list[i]][2] = qf_index_dicts[key_list[i+1]][1] - 1
            else:
                qf_index_dicts[key_list[i]][2] = len(filtered_cells)

        for key in key_list:
            set_portfolio_value_from_external_file(key, filtered_cells)
        
        range_num = len(fxt_ports)
        
        all_ports_nbr, all_ports_name = [], []
        for i in range(0, range_num):
            all_ports_nbr.append( (fxt_ports[i][0], 'FXT') )
            all_ports_name.append( fxt_ports[i][1] )
            if i < len(irt_ports):
                all_ports_nbr.append( (irt_ports[i][0], 'IRT') )
                all_ports_name.append( irt_ports[i][1] )
            if i < len(client_book_ports):
                all_ports_nbr.append( (client_book_ports[i][0], 'Client Book') )
                all_ports_name.append( client_book_ports[i][1] )
        
        

        all_ports = []
        for port_set in all_ports_nbr:
            if port_set[1] ==  'FXT':
                all_ports.extend( fxt_portfolios(port_set[0]) )
            elif port_set[1] == 'IRT':
                all_ports.extend( irt_portfolios(port_set[0]) )
            elif port_set[1] == 'Client Book':
                all_ports.extend( client_book_portfolios(port_set[0]) )
        
        for port in all_ports:
            if port.Compound():
                comp_ports_dict[port.Name()] = get_portfolios([port])


        titles = ['','NOP Operational', 'NOP IR Related']
        additional_columns = ['Total', 'Limit', '%', 'Status']
        

        
        
        
        rule_obj = acm.FComplianceRule[rule_name]

        columns = []

        for key, val in qf_trade_dicts.items():
            columns.append(key)

            

        columns_oper = columns[:4]
        columns_ir = columns[4:]

        columns_oper = columns_oper + additional_columns
        columns_ir = columns_ir + additional_columns
        
        columns = columns_oper + columns_ir
        
        calc_space = acm.Calculations().CreateCalculationSpace(context, sheet_type)

        

        rows = [columns]
        for port in all_ports:
            obj = port
            temp_row = [ obj ]
            temp_nop = []
            temp_dicts = {}

            a_rule = get_applied_rule_by_target(obj, rule_name)
            if a_rule is not None:
                tv_list = a_rule.ThresholdValues()
            else:
                tv_list = []
            
            for ins in columns_oper[:4]:
                if obj.Name() in qf_trade_dicts[ins]:
                    nop_val = qf_trade_dicts[ins][obj.Name()]
                else:
                    nop_val = 0.0

                num = nop_val
                temp_nop.append(num)
                temp_dicts[ins] = num
                
                res = thousand_dot_sep(num)
                

                temp_row.append(res)
            
                
            rule_val = total_nop(temp_nop)
            temp_dicts['FXT Total'] = rule_val
            temp_row.append( thousand_dot_sep( rule_val ) )
            
            threshold_val = get_vio_threshold_value_by_rule_name(obj, rule_name)
            
            temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
        
        
            percent_val = get_utilization_percentage_by_rule_name(threshold_val, rule_val) + '%'
            temp_row.append( percent_val )
            if len(tv_list) > 0:
                temp_row.append( limit_indicator( tv_list, rule_val ) )
            else:
                temp_row.append( 'Green' )

            temp_nop = []
            for ins in columns_ir[:5]:
                if obj.Name() in qf_trade_dicts[ins]:
                    nop_val = qf_trade_dicts[ins][obj.Name()]
                else:
                    nop_val = 0.0

                num = nop_val
                temp_nop.append(num)
                temp_dicts[ins] = num

                res = thousand_dot_sep(num)
                
                
                temp_row.append(res)
                
            

            rule_val = total_nop(temp_nop)
            temp_row.append( thousand_dot_sep( rule_val ) )
            temp_dicts['IRT Total'] = rule_val
            


            temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
        
            percent_val = get_utilization_percentage_by_rule_name(threshold_val, rule_val) + '%'
            temp_row.append( percent_val )
            if len(tv_list) > 0:
                temp_row.append( limit_indicator( tv_list, rule_val ) )
            else:
                temp_row.append( 'Green' )
                
            if not obj.Compound():
                non_comp_port_calc_dict[obj.Name()] = temp_dicts

            if len(temp_row) > 1:
                rows.append(temp_row)
        

        fx_columns = columns_oper[:4]
        ir_columns = columns_ir[:5]

        for row in rows[1:]:
            obj = row[0]
            if obj.Compound():
                a_rule = get_applied_rule_by_target(obj, rule_name)
                if a_rule is not None:
                    tv_list = a_rule.ThresholdValues()
                else:
                    tv_list = []

                threshold_val = get_vio_threshold_value_by_rule_name(obj, rule_name)

                fx_rows = row[1:5]
                
                for i in range( len(fx_rows) ):
                    row[i+1] = thousand_dot_sep( comp_port_calculation( obj, fx_columns[i] ) )
                
                rule_val = comp_port_calculation( obj, 'FXT Total' )
                row[5] = thousand_dot_sep( rule_val )

                row[7] = get_utilization_percentage_by_rule_name(threshold_val, rule_val) + '%'
                if len(tv_list) > 0:
                    row[8] = limit_indicator( tv_list, rule_val )
                else:
                    row[8] = 'Green'

                ir_rows = row[9:14]
                for i in range( len(ir_rows) ):
                    row[9+i] = thousand_dot_sep( comp_port_calculation( obj, ir_columns[i] ) )
                
                rule_val = comp_port_calculation( obj, 'IRT Total' )
                row[14] = thousand_dot_sep( rule_val )

                row[16] = get_utilization_percentage_by_rule_name(threshold_val, rule_val) + '%'
                if len(tv_list) > 0:
                    row[17] = limit_indicator( tv_list, rule_val )
                else:
                    row[17] = 'Green'

            row[0] = obj.Name()


        #print(rows[0])
        table_html = create_html_table(titles, rows)
        table_xsl_fo = create_xsl_fo_table(titles, rows)

        

        for i in titles:
            if i != '':
                if 'Operational' in i:
                    table_html = table_html.replace('<th>'+i+'</th>', '<th colspan="'+str(len(columns_oper))+'" style="background-color: #66ccff;">'+i+'</th>')
                else:
                    table_html = table_html.replace('<th>'+i+'</th>', '<th colspan="'+str(len(columns_ir))+'" style="background-color: #66ccff;">'+i+'</th>')
            else:
                table_html = table_html.replace('<th>'+i+'</th>', '<th rowspan="2" style="background-color: #ff9966;">'+i+'</th>')

                

        for oper in columns_oper:
            table_html = table_html.replace('<td>'+oper+'</td>', '<td style="background-color: #66ccff;"><b>'+oper+'</b></td>')
            table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+oper+'</fo:block></fo:table-cell>',
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#66ccff" font-weight="bold" text-align="center"><fo:block>'+oper+'</fo:block></fo:table-cell>')

            
        for ir in columns_ir:
            table_html = table_html.replace('<td>'+ir+'</td>', '<td style="background-color: #66ccff;"><b>'+ir+'</b></td>')
            table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+ir+'</fo:block></fo:table-cell>',
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#66ccff" font-weight="bold" text-align="center"><fo:block>'+ir+'</fo:block></fo:table-cell>')

        #Hierarchy Portfolio
        for port_name in all_ports_name:
            table_html = table_html.replace(f'<td>{port_name}</td>', f'<td style="text-align: left;">{port_name}</td>')
            table_xsl_fo = table_xsl_fo.replace(
                f'<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>{port_name}</fo:block></fo:table-cell>',
                f'<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>{port_name}</fo:block></fo:table-cell>'
                )
        
        #Html table customization
        table_html = table_html.replace('<td>Green</td>', '<td style="background-color: #00cc66;"></td>')
        table_html = table_html.replace('<td>Yellow</td>', '<td style="background-color: #ffcc00;"></td>')
        table_html = table_html.replace('<td>Red</td>', '<td style="background-color: #ff0000;"></td>')
        table_html = table_html.replace('&', '&amp;')
        table_html = table_html.replace('%', '&#37;')
        
        
        #XSLFO table customization
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Green</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#00cc66"><fo:block></fo:block></fo:table-cell>')
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Yellow</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#ffcc00"><fo:block></fo:block></fo:table-cell>')
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Red</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#ff0000"><fo:block></fo:block></fo:table-cell>')
        table_xsl_fo = table_xsl_fo.replace('&', '&amp;')
        table_xsl_fo = table_xsl_fo.replace('%', '&#37;')
        
        current_hour = get_current_hour("")
        current_date = get_current_date("")
        #current_date2 = "Report Date: " + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + f" UTC+{datetime.now().hour - datetime.now(timezone.utc).hour:02d}:00"
        current_date2 = "Report Date: " + datetime.now().strftime("%d-%m-%Y")
        

        html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date)
        html_f = open(html_file, "r")
        
        html_contents = html_f.read().replace('border: 1px solid #dddddd;', 'border: 1px solid #000000;')
        html_contents =  html_contents.replace('<table>','<h1 style="text-align: left;">'+ current_date2 +'</h1><h2 style="text-align: left;">USD Equivalent - Refinitiv SPOT Marketplace</h2><table>')
        html_f = open(html_file, "w")
        html_f.write(html_contents)
        html_f.close()

        xsl_fo_file = create_xsl_fo_file(report_name + " " +current_date+current_hour, file_path, [table_xsl_fo], report_name, current_date)

        xsl_f = open(xsl_fo_file, "r")

        xsl_contents = xsl_f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">')
        xsl_contents = xsl_contents.replace('<fo:block font-weight="bold" font-size="30px" margin-bottom="30px">'+report_name+'</fo:block>',
        '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="center">'+report_name+'</fo:block>'+
        '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="left">'+current_date2+'</fo:block>'+
        '<fo:block font-weight="bold" font-size="24px" margin-bottom="30px" text-align="left">USD Equivalent - Refinitiv SPOT Marketplace</fo:block>')
        xsl_contents = xsl_contents.replace('</fo:table-header>', '</fo:table-row>')
        xsl_contents = xsl_contents.replace('<fo:table-body>', '')
        xsl_contents = xsl_contents.replace('<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">', 
        '<fo:table-body>\n\t<fo:table-row font-weight="bold">')
        xsl_contents = xsl_contents.replace('<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block></fo:block></fo:table-cell>', 
        '<fo:table-cell padding="8pt" border-width="1px" border-style="solid" background-color="#ff9966" text-align="center" number-rows-spanned="2"><fo:block></fo:block></fo:table-cell>')
        xsl_contents = xsl_contents.replace('<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>NOP Operational</fo:block></fo:table-cell>', 
        f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" background-color="#66ccff" text-align="center" number-columns-spanned="{len(columns_oper)}"><fo:block>NOP Operational</fo:block></fo:table-cell>')
        xsl_contents = xsl_contents.replace('<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>NOP IR Related</fo:block></fo:table-cell>', 
        f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" background-color="#66ccff" text-align="center" number-columns-spanned="{len(columns_ir)}"><fo:block>NOP IR Related</fo:block></fo:table-cell>')


        xsl_f = open(xsl_fo_file, "w")
        xsl_f.write(xsl_contents)
        xsl_f.close()
        
        for i in output_file:
            if i != '.pdf' :
                generate_file_for_other_extension(html_file, i)
            else:
                generate_pdf_from_fo_file(xsl_fo_file)
        
        os.remove(raw_data_dir_name)
        '''
        try:
            os.remove(xsl_fo_file)
        except:
            pass
        '''
    else:
        print('You do not have "', raw_data_dir_name, '" file in a local directory ')