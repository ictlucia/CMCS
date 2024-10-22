import acm, ael, random
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from time import sleep, perf_counter
from datetime import datetime, date, timezone
from Python_MO_Custom_Fields import *

context = acm.GetDefaultContext( )
today = acm.Time.DateToday()
trade_statuses = ["FO Confirmed", "BO Confirmed", "BO-BO Confirmed"]
#all_trades = [trade for trade in acm.FTrade.Select('') if trade.Status() in trade_statuses and trade.OptKey3() is not None and trade.OptKey4() is not None]
all_trades = acm.FStoredASQLQuery['Queries_Report_PV01'].Query().Select()
sheet_type = 'FPortfolioSheet'    

portfolio_keywords = ['FXT', 'IRT', 'CLIENT_BOOK']
fxt_departments = ['Dept Head', 'Derivatives', 'Specialist', 'Spot Emerging', 'Spot Major']
irt_departments = ['DCM', 'Dept Head', 'Derivative', 'MM', 'Specialist']
client_book_departments = ['TAS', 'TRC', 'TWC']
trc_departments = ['Banknotes', 'Client Bonds', 'FX Retail']

not_compound_port_dicts = {}
compound_port_dicts = {}

def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection

# ================ DATA FILTER COLUMN ================ 
pattern_dict_list = {
    'TREASURY HO': {
        'Begin': ['TREASURY'],
        'End': ['HO']
    },
    'FXT': {
        'Begin': ['FXT'],
        'End': ['']
    },
    'IRT': {
        'Begin': ['IRT'],
        'End': ['']
    },
    'OVERSEAS': {
        'Begin': [''],
        'End': ['OVERSEAS']
    }

}

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

def get_port_calculation_by_comp2(port, calc_space, col_name):
    if port.Compound():
        return 0.0
    else:
        port_trades = get_portfolio_instruments(port)
        trade_calc = port_trades_calculation(port_trades, calc_space, col_name)
        
        return trade_calc


def comp_port_calculation2(comp_port, calc_space, col_name, ind):
    res_ports = compound_port_dicts[comp_port.Name()]
    total_calc = 0.0
    for port in res_ports:
        if not_compound_port_dicts[port.Name()][ind] is None:
            port_trades = get_portfolio_instruments(port)
            trade_calc = port_trades_calculation(port_trades, calc_space, col_name)
            not_compound_port_dicts[port.Name()][ind] = trade_calc
        else:
            trade_calc = not_compound_port_dicts[port.Name()][ind]
        '''
        port_trades = get_portfolio_trades(port.Name())
        product_port_trades = get_trades_by_product_name(port_trades, product_name)
        trade_calc = get_trading_sheet_column_value(product_port_trades, calc_space, col_name)
        '''
        
        total_calc += trade_calc
    return total_calc

def get_port_calculation_by_comp(port, calc_space, col_name):
    if port.Compound():
        #return comp_port_calculation([port], calc_space, col_name)
        return 0.0
    else:
        
        port_trades = get_portfolio_trades(port)
        trade_calc = port_trades_calculation(port_trades, calc_space, col_name)
        '''
        port_instruments = get_portfolio_instruments(port.Name())
        trade_calc = port_trades_calculation(port_instruments, calc_space, col_name)
        '''
        return trade_calc

def port_trades_calculation(port_trades, calc_space, col_name):
    total_calc = 0.0
    for trade in port_trades:
        trade_calc = get_trading_sheet_column_value(trade, calc_space, col_name)
        
        total_calc += trade_calc
    return total_calc
        

def comp_port_calculation(comp_port, calc_space, col_name, ind):
    res_ports = compound_port_dicts[comp_port.Name()]
    total_calc = 0.0
    for port in res_ports:
        if not_compound_port_dicts[port.Name()][ind] is None:
            port_trades = get_portfolio_trades(port)
            trade_calc = port_trades_calculation(port_trades, calc_space, col_name)
            not_compound_port_dicts[port.Name()][ind] = trade_calc
        else:
            trade_calc = not_compound_port_dicts[port.Name()][ind]
        '''
        if port.Name() in not_compound_port_dicts:
            trade_calc = not_compound_port_dicts[port.Name()][ind]
        else:
            port_trades = get_portfolio_trades(port)
            trade_calc = port_trades_calculation(port_trades, calc_space, col_name)
            not_compound_port_dicts[port.Name()][ind] = trade_calc
        '''

        total_calc += trade_calc
    return total_calc



def get_portfolios_by_comp_portfolio(comp_port_name):
    portfolio_links = acm.FPortfolioLink.Select("ownerPortfolio='"+comp_port_name+"'")
    ports = [ port_link.MemberPortfolio() for port_link in portfolio_links ]
    return ports
    
def isAllCompound(ports):
    bool_ports = [port.Compound() for port in ports]
    if True in bool_ports:
        return True
    else:
        return False
   
def not_compound_port_calculations(port):
    port_list = compound_port_dicts[port.Name()]
    for port in port_list:
        if port.Name() not in not_compound_port_dicts.keys():
            not_compound_port_dicts[port.Name()] = [None, None, None, None, None]
 
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

def get_FArray(array_list):
    acm_array_list = acm.FArray()
    acm_array_list.AddAll(array_list)
    return acm_array_list

def get_portfolio_trades(port):
    trades = [trade for trade in all_trades if trade.Portfolio() is port]
    #trades = get_FArray(trades1)
    return trades
    
def get_portfolio_instruments(port):
    
    final_instruments = []
    instruments = [trade.Instrument() for trade in get_portfolio_trades(port) if trade.Instrument().InsType() != 'Curr']
    for ins in instruments:
        if ins not in final_instruments:
            final_instruments.append(ins)
    '''
    final_instruments = acm.FArray()
    instruments = [trade.Instrument() for trade in get_portfolio_trades(port) if trade.Instrument().InsType() != 'Curr']
    for ins in instruments:
        if not final_instruments.Includes(ins):
            final_instruments.AddFirst(ins)
    '''
    return final_instruments
    
def get_trades_by_product_name(trades, product_name):
    product_types = dict_of_column_filter[product_name]['Product Type']
    categories = dict_of_column_filter[product_name]['Category']
    
    filtered_trades = [ trade for trade in trades if trade.OptKey3().Name() in product_types and trade.OptKey4().Name() in categories ]
    return filtered_trades


def get_portfolios_by_ael_sql(port_pattern_begin, port_pattern_end):
    port_list = ael.asql("SELECT p.prfid, p.prfnbr FROM Portfolio p WHERE p.prfid like '"+port_pattern_begin+"%"+port_pattern_end+"'")[1][0]
    return port_list

def NaN_to_zero(val):
    check_val = str(val)
    if check_val.lower() == 'nan':
        return 0.0
    else:
        return float(val)


def get_trading_sheet_column_value(obj, calc_space, col_name):
    col = calc_space.CreateCalculation(obj, col_name)
    col_val = col.Value()
    #print(col_val)
    try:
        num = NaN_to_zero(col_val.Number())
        res_val = num
    except:
        res_val = 0.0
    return res_val
    
def get_trading_sheet_column_value2(obj, calc_space, col_name):
    col_val = calc_space.CreateCalculation(obj, col_name).Value()
    #print(col_val)
    try:
        num = NaN_to_zero(col_val)
        #print(num)
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

    
def percentage_removal(val):
    val = val.replace(',','.')
    res = float(val[:-1])
    return res

def compliance_rule_list(rule_def, rule_category):
    return [ comp_rule.Name() for comp_rule in acm.FComplianceRule.Select("definitionInfo='"+rule_def+"' and ruleCategory='"+rule_category+"'") ]


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'MO07 - Market Risk - PV01 Limit per Hierarchy'}
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'MO07 - Market Risk - PV01 Limit per Hierarchy', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output'],
['compliance_rule_name', 'Compliance Rule', 'string', compliance_rule_list('Exposure', 'Pre-Deal'), 'PV01 Limit - ADE', 0, 0, 'Select Compliance rule Name']
]  
def ael_main(parameter):
    start_time = perf_counter()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    rule_name = str(parameter['compliance_rule_name'])
    #rule_name = "PV01 Limit - Ade"

    fxt_ports = ael.asql(f"""Select p.prfnbr, p.prfid from Portfolio p where p.prfid like 'FXT%' and p.prfid not like '%{" and p.prfid not like '%".join( [x + "'" for x in fxt_departments[1:] ] )} and p.compound='yes'""")[1][0]
    irt_ports = ael.asql(f"""Select p.prfnbr, p.prfid from Portfolio p where p.prfid like 'IRT%' and p.prfid not like '%{" and p.prfid not like '%".join( [x + "'" for x in irt_departments ] )} and p.compound='yes'""")[1][0]
    client_book_ports = ael.asql("Select p.prfnbr, p.prfid from Portfolio p where p.prfid like 'CLIENT_BOOK%'")[1][0]
    
    
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


    #all_ports1 = ael.asql("Select a.target_seqnbr from AppliedRule a, ComplianceRule c where a.compliance_rule = c.seqnbr and c.name = '"+rule_name+"'")[1][0]
    #all_ports = [ acm.FPhysicalPortfolio[ port[0] ] for port in all_ports1 ]

    titles = ['Hierarchy','Market Value Of Portfolio', 'PV01', 'Convexity', 'CS01']
    
    columns = ['Limit', 'Utilisasi', '1 Day Change', '%', 'Status']
    
    for port in all_ports:
        if port.Compound():
            compound_port_dicts[port.Name()] = get_portfolios([port])
            #print(compound_port_dicts[port])
        
    
    calc_space = acm.Calculations().CreateCalculationSpace(context, sheet_type)
    
    rows = [columns]
    for port in all_ports:
        obj = port
        #qf = acm.FStoredASQLQuery['MO07_' + obj.Name()]
        temp_row = [obj]
        #temp_row = [obj.Name()]

        a_rule = get_applied_rule_by_target(obj, rule_name)
        if a_rule is not None:
            tv_list = a_rule.ThresholdValues()
        else:
            tv_list = []
        
        mkt_value = get_port_calculation_by_comp(obj, calc_space, 'Portfolio Market Value')
        market_value = thousand_dot_sep( mkt_value )
        #market_value = '-'
            
        threshold_limit = thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) )
        rule_val = get_port_calculation_by_comp(obj, calc_space, 'Portfolio Delta Yield')
        utilization = thousand_dot_sep( rule_val )
        #utilization = '-'
        
        pv_day_change = abs( rule_val - get_port_calculation_by_comp(obj, calc_space, '1DayChange_PV01') )
        day_change = thousand_dot_sep( pv_day_change )
        #day_change = '-'
        
        threshold_val = get_vio_threshold_value_by_rule_name(obj, rule_name)
        #rule_val = get_utilization_val_by_rule_name(obj, rule_name)
        
        percent_val = get_utilization_percentage_by_rule_name(threshold_val, rule_val) + '%'
        
        if len(tv_list) > 0:     
            limit_ind = limit_indicator( tv_list, rule_val )
        else:
            limit_ind = 'Green'
        
        convex = get_port_calculation_by_comp2(obj, calc_space, 'Portfolio Convex')
        convexity = thousand_dot_sep( convex )
        #convexity = '-'
        
        cs_dlt = get_port_calculation_by_comp2(obj, calc_space, 'Flat Credit Spread Delta')
        cs_delta = thousand_dot_sep( cs_dlt )
        
        if not obj.Compound():
            not_compound_port_dicts[obj.Name()] = [mkt_value, rule_val, pv_day_change, convex, cs_dlt]
        else:
            not_compound_port_calculations(obj)
        

        
        temp_row.extend([market_value, threshold_limit, utilization, day_change, percent_val, limit_ind, convexity, cs_delta])
        
        if len(temp_row) > 1:
            rows.append(temp_row)
            '''
            if obj.Compound():
                compound_port_dicts[obj.Name()] = rows.index(temp_row)
            '''
            
    for row in rows[1:]:
        obj = row[0]
        if obj.Compound():
            a_rule = get_applied_rule_by_target(obj, rule_name)
            if a_rule is not None:
                tv_list = a_rule.ThresholdValues()
            else:
                tv_list = []

            row[1] = thousand_dot_sep( comp_port_calculation(obj, calc_space, 'Portfolio Market Value', 0) )
            
            rule_val = comp_port_calculation(obj, calc_space, 'Portfolio Delta Yield', 1)
            row[3] = thousand_dot_sep( rule_val )
            
            pv_day_change = abs( rule_val - comp_port_calculation(obj, calc_space, '1DayChange_PV01', 2) )
            row[4] = thousand_dot_sep( pv_day_change )
            
            threshold_val = get_vio_threshold_value_by_rule_name(obj, rule_name)
            row[5] = get_utilization_percentage_by_rule_name(threshold_val, rule_val) + '%'
            
            if len(tv_list) > 0:     
                row[6] = limit_indicator( tv_list, rule_val )
            else:
                row[6] = 'Green'
            
            row[7] = thousand_dot_sep( comp_port_calculation2(obj, calc_space, 'Portfolio Convex', 3) )
            row[8] = thousand_dot_sep( comp_port_calculation2(obj, calc_space, 'Flat Credit Spread Delta', 4) )
        row[0] = obj.Name()
      
    
    
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    
    for i in titles:
        if i != 'PV01':
            table_html = table_html.replace('<th>'+i+'</th>', '<th rowspan="2" style="background-color: #99ff66;">'+i+'</th>')
        else:
            table_html = table_html.replace('<th>'+i+'</th>', '<th colspan="'+str(len(columns))+'" style="background-color: #99ff66;">'+i+'</th>')
            
    for col in columns:
        table_html = table_html.replace('<td>'+col+'</td>', '<td style="background-color: #99ff66;"><b>'+col+'</b></td>')
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+col+'</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#99ff66" font-weight="bold" text-align="center"><fo:block>'+col+'</fo:block></fo:table-cell>')
    
    #Html table customization
    #---
    table_html = table_html.replace('<td>Green</td>', '<td style="background-color: #00cc66;"></td>')
    table_html = table_html.replace('<td>Yellow</td>', '<td style="background-color: #ffcc00;"></td>')
    table_html = table_html.replace('<td>Red</td>', '<td style="background-color: #ff0000;"></td>')
    table_html = table_html.replace('&', '&amp;')
    table_html = table_html.replace('%', '&#37;')
    
    #Xsl-fo table customization
    #---
    table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Green</fo:block></fo:table-cell>',
    '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#00cc66"><fo:block></fo:block></fo:table-cell>')
    table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Yellow</fo:block></fo:table-cell>',
    '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#ffcc00"><fo:block></fo:block></fo:table-cell>')
    table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>Red</fo:block></fo:table-cell>',
    '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#ff0000"><fo:block></fo:block></fo:table-cell>')
    table_xsl_fo = table_xsl_fo.replace('&', '&amp;')
    table_xsl_fo = table_xsl_fo.replace('%', '&#37;')

    #Hierarchy Portfolio
    for port_name in all_ports_name:
        table_html = table_html.replace(f'<td>{port_name}</td>', f'<td style="text-align: left;">{port_name}</td>')
        table_xsl_fo = table_xsl_fo.replace(
            f'<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>{port_name}</fo:block></fo:table-cell>',
            f'<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>{port_name}</fo:block></fo:table-cell>'
            )
    
    current_hour = get_current_hour("")
    current_date = get_current_date("")
    current_date2 = "Report Date: " + datetime.now().strftime("%d-%m-%Y")
    
    #report_name = report_name + " - " + filter_currency
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
    '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="center">'+report_name+'</fo:block>' +
    '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="left">'+current_date2+'</fo:block>'+
    '<fo:block font-weight="bold" font-size="24px" margin-bottom="30px" text-align="left">USD Equivalent - Refinitiv SPOT Marketplace</fo:block>')

    xsl_contents = xsl_contents.replace('</fo:table-header>', '</fo:table-row>')
    xsl_contents = xsl_contents.replace('<fo:table-body>', '')
    xsl_contents = xsl_contents.replace('<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">', 
    '<fo:table-body>\n\t<fo:table-row background-color="#99ff66" font-weight="bold">')

    for ttl in titles:
        if ttl == 'PV01':
            xsl_contents = xsl_contents.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{ttl}</fo:block></fo:table-cell>', 
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-columns-spanned="{len(columns)}"><fo:block>{ttl}</fo:block></fo:table-cell>')
        else:
            xsl_contents = xsl_contents.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{ttl}</fo:block></fo:table-cell>', 
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-rows-spanned="2"><fo:block>{ttl}</fo:block></fo:table-cell>')


    xsl_f = open(xsl_fo_file, "w")
    xsl_f.write(xsl_contents)
    xsl_f.close()

    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
    '''
    try:
        os.remove(xsl_fo_file)
    except:
        pass
    '''
    end_time = perf_counter()
    print(f'MO07 - Market Risk - PV01 Limit, It took {end_time- start_time: 0.2f} second(s) to complete.')
