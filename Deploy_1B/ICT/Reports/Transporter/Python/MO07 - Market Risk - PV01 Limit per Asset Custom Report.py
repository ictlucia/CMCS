import acm, ael, random
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from time import sleep, perf_counter
from datetime import datetime, date, timezone

context = acm.GetDefaultContext( )
today = acm.Time.DateToday()
trade_statuses = ["FO Confirmed", "BO Confirmed", "BO-BO Confirmed"]
#all_trades = [trade for trade in acm.FTrade.Select('') if trade.Status() in trade_statuses and trade.OptKey3() is not None and trade.OptKey4() is not None]
sheet_type = 'FPortfolioSheet'

query_name = '[Trade Set] '
product_list = ['Plain Vanilla', 'Cross Currency Swap', 'FX Option', 'Par Forward', 'Bonds', 'Interest Rate Swap', 'Bond Forward', 
                'Bond Option', 'Forward Rate Agreement', 'Other Structured Product']

not_compound_port_dicts = {}
compound_port_dicts = {}

def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection

# ================ DATA FILTER COLUMN ================ 
fx_transaction_trades = acm.FStoredASQLQuery[query_name + product_list[0]].Query().Select()
ccs_trades = acm.FStoredASQLQuery[query_name + product_list[1]].Query().Select()
fx_opt_trades = acm.FStoredASQLQuery[query_name + product_list[2]].Query().Select()
par_fwd_trades = acm.FStoredASQLQuery[query_name + product_list[3]].Query().Select()
bond_trades = acm.FStoredASQLQuery[query_name + product_list[4]].Query().Select()
irs_trades = acm.FStoredASQLQuery[query_name + product_list[5]].Query().Select()
bond_fwd_trades = acm.FStoredASQLQuery[query_name + product_list[6]].Query().Select()
bond_opt_trades = acm.FStoredASQLQuery[query_name + product_list[7]].Query().Select()
fra_trades = acm.FStoredASQLQuery[query_name + product_list[8]].Query().Select()
sp_trades = acm.FStoredASQLQuery[query_name + product_list[9]].Query().Select()

qf_trade_dicts = {
    'FX Transaction': fx_transaction_trades,
    'CCS': ccs_trades,
    'Option': fx_opt_trades,
    'Par FWD': par_fwd_trades,
    'Surat Berharga/Fixed Income': bond_trades,
    'IRS': irs_trades,
    'Bond Forward': bond_fwd_trades,
    'Bond Option': bond_opt_trades,
    'FRA': fra_trades,
    'Other Structured Product': sp_trades

}

pattern_dict_list = {
    'TREASURY HO': {
        'Begin': ['TREASURY'],
        'End': ['HO']
    },
    'PDN': {
        'Begin': [''],
        'End': ['PDN']
    },
    'FXT': {
        'Begin': ['FXT'],
        'End': ['']
    },
    'IRT': {
        'Begin': ['IRT'],
        'End': ['']
    },
    'CLIENT_BOOK': {
        'Begin': ['CLIENT','','Banknotes','Wholesale','Retail', 'Clients'],
        'End': ['BOOK','Marktra','','','','']
    },
    'OVERSEAS': {
        'Begin': ['','BM','BM'],
        'End': ['OVERSEAS','Trading','Banking']
    }

}

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

def get_portfolio_trades(port):
    trades = [trade for trade in all_trades if trade.Portfolio() is port]
    return trades
    
def get_portfolio_instruments(product_name):
    final_instruments = []
    prod_trades = qf_trade_dicts[product_name]
    instruments = [trade.Instrument() for trade in prod_trades if trade.Instrument().InsType() != 'Curr']
    for ins in instruments:
        if ins not in final_instruments:
            final_instruments.append(ins)
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
    col_val = calc_space.CreateCalculation(obj, col_name).Value()
    try:
        num = NaN_to_zero(col_val.Number())
        res_val = num
    except:
        res_val = 0.0
    return res_val
    
def get_trading_sheet_column_value2(obj, calc_space, col_name):
    col_val = calc_space.CreateCalculation(obj, col_name).Value()
    try:
        num = float(col_val)
        res_val = thousand_dot_sep(num)
    except:
        res_val = thousand_dot_sep( 0.0 )
    return res_val

def thousand_dot_sep(val):
    if abs(val) >= 1000.0:
        res_val = "{:,.2f}".format(val).replace(',',' ').replace('.',',').replace(' ','.')
    else:
        res_val = "{:,.2f}".format(val).replace('.',',')
    return res_val
    


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'MO07 - Market Risk - PV01 Limit per Asset'}
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'MO07 - Market Risk - PV01 Limit per Asset', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output']
]  
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    
    qf_name = "MO07 Asset"
    
    all_ports = []
    for key in list( qf_trade_dicts.keys() ):
        all_ports.append(key)
    

    titles = ['Hierarchy','Market Value Of Portfolio', 'PV01', 'Convexity', 'CS01']
    

    columns = ['Utilisasi', '1 Day Change','Utilisasi', '1 Day Change','Utilisasi', '1 Day Change']
    
    columns_pv = columns[:2]
    columns_conven = columns[2:4]
    columns_cs = columns[4:]
    
    
    calc_space = acm.Calculations().CreateCalculationSpace(context, sheet_type)
    
    rows = [columns]
    for port in all_ports:
        temp_row = [port]
        
        product_trades = qf_trade_dicts[port]
        product_instruments = get_portfolio_instruments(port)
        
        mkt_value = port_trades_calculation(product_trades, calc_space, 'Portfolio Market Value')
        mkt_value_res = thousand_dot_sep( mkt_value )
        
        pv01_val = port_trades_calculation(product_trades, calc_space, 'Portfolio Delta Yield')
        pv01_val_res = thousand_dot_sep( pv01_val )
        
        pv01_1dc_val = abs( pv01_val - port_trades_calculation(product_trades, calc_space, '1DayChange_PV01') )
        pv01_1dc_val_res = thousand_dot_sep( pv01_1dc_val )
        
        convex_val = port_trades_calculation(product_instruments, calc_space, 'Portfolio Convex')
        convex_val_res = thousand_dot_sep( convex_val )
        
        convex_1dc_val = abs( convex_val - port_trades_calculation(product_instruments, calc_space, '1DayChange_Convexity') )
        #convex_1dc_val = 0.0
        convex_1dc_val_res = thousand_dot_sep( convex_1dc_val )
        
        cs_val = port_trades_calculation(product_instruments, calc_space, 'Flat Credit Spread Delta')
        cs_val_res = thousand_dot_sep( cs_val )
        
        cs_1dc_val = abs( cs_val - port_trades_calculation(product_instruments, calc_space, '1DayChange_CS01') )
        cs_1dc_val_res = thousand_dot_sep( cs_1dc_val )
        
        temp_row.extend( [mkt_value_res, pv01_val_res, pv01_1dc_val_res, convex_val_res, convex_1dc_val_res, cs_val_res, cs_1dc_val_res] )
        
        if len(temp_row) > 1:
            rows.append(temp_row)
    
    #print(rows[1][2])

    #print(rows[0])
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    
    for i in titles[:2]:
        table_html = table_html.replace('<th>'+i+'</th>', '<th rowspan="2" style="background-color: #99ff66;">'+i+'</th>')

    for i in titles[2:]:
        table_html = table_html.replace('<th>'+i+'</th>', '<th colspan="'+str(len(columns_pv))+'" style="background-color: #99ff66;">'+i+'</th>')
    
    for col in columns:
        table_html = table_html.replace('<td>'+col+'</td>', '<td style="background-color: #99ff66;"><b>'+col+'</b></td>')
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+col+'</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#99ff66" font-weight="bold" text-align="center"><fo:block>'+col+'</fo:block></fo:table-cell>')
    
    for key in qf_trade_dicts:
        table_html = table_html.replace('<td>'+key+'</td>', '<td style="text-align: left;">'+key+'</td>')
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+key+'</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>'+key+'</fo:block></fo:table-cell>')
    
    
    table_html = table_html.replace('&', '&amp;')
    table_html = table_html.replace('%', '&#37;')
    
    table_xsl_fo = table_xsl_fo.replace('&', '&amp;')
    table_xsl_fo = table_xsl_fo.replace('%', '&#37;')
    
    current_hour = get_current_hour("")
    current_date = get_current_date("")
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
    '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="center">'+report_name+'</fo:block>' +
    '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="left">'+current_date2+'</fo:block>'+
    '<fo:block font-weight="bold" font-size="24px" margin-bottom="30px" text-align="left">USD Equivalent - Refinitiv SPOT Marketplace</fo:block>')
    
    xsl_contents = xsl_contents.replace('</fo:table-header>', '</fo:table-row>')
    xsl_contents = xsl_contents.replace('<fo:table-body>', '')
    xsl_contents = xsl_contents.replace('<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">', 
    '<fo:table-body>\n\t<fo:table-row background-color="#99ff66" font-weight="bold">')

    for ttl in titles:
        if ttl in ['PV01', 'Convexity', 'CS01']:
            xsl_contents = xsl_contents.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{ttl}</fo:block></fo:table-cell>', 
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-columns-spanned="{len(columns_pv)}"><fo:block>{ttl}</fo:block></fo:table-cell>')
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
