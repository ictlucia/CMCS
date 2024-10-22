import acm, ael, random
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from time import sleep, perf_counter, strftime, strptime
from datetime import datetime, date, timezone
from Python_MO_Custom_Fields import *

context = acm.GetDefaultContext( )
today = acm.Time.DateToday()
trade_statuses = ["FO Confirmed", "BO Confirmed", "BO-BO Confirmed"]
#all_trades = acm.FTrade.Select('')


#all_instruments = [ins for ins in acm.FInstrument.Select('') if ins.Issuer() is not None] 

def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection

# ================ DATA FILTER COLUMN ================ 


issuer_util_calc_dicts = {}
issuer_list = []



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

def eod_or_refinitiv_by_datetime(util_datetime):
    if util_datetime != '':
        parsing_list = util_datetime.split(' ')
        eod_datetime = parsing_list[0] + ' 15:00:00'
        eod_datetime = strftime('%Y-%m-%d %H:%M:%S', strptime( eod_datetime, '%Y-%m-%d %H:%M:%S' ) )
        util_datetime = strftime('%Y-%m-%d %H:%M:%S', strptime( util_datetime, '%Y-%m-%d %H:%M:%S' ) )
        if util_datetime >= eod_datetime:
            return 'EOD_MtM'
        else:
            return 'REFINITIV_SPOT'
    else:
        return ''

def get_rule_value_date(rule_val):
    if rule_val is not None:
        return rule_val.Start()
    else:
        return today + ' 15:00:00'

def get_rule_watermark_value(rule_val):
    if rule_val is not None:
        return rule_val.WatermarkValue()
    else:
        return 0.0

def get_prev_day_rule_val_by_rule_name(obj, rule_name):
    alert_set = get_alert_by_rule_name(obj, rule_name)
    alert = alert_set[0]
    alert_type = alert_set[1]
    try:
        if alert_type == 'Rule Result History':
            breaches = alert.ValuesHistory()
        elif alert_type == 'Alert':
            breaches = alert.Breaches()
        else:
            breaches = []
    except:
        breaches = []
    if len(breaches) > 0:
        latest_breach = breaches[-1]
        new_today = strftime('%Y-%m-%d', strptime( latest_breach.Start(), '%Y-%m-%d %H:%M:%S' ) )
        if new_today == today:
            filtered_breaches = []
            for breach in breaches:
                temp_date = strftime('%Y-%m-%d', strptime( breach.Start(), '%Y-%m-%d %H:%M:%S' ) )
                if new_today != temp_date:
                    filtered_breaches.append( breach )
            if len(filtered_breaches) > 0:
                return filtered_breaches[-1]
            else:
                return None
        else:
            return latest_breach
    else:
        return None

def get_prev_day_util_val(obj, rule_name):
    prev_rule_val = get_prev_day_rule_val_by_rule_name(obj, rule_name)
    if prev_rule_val is not None:
        return prev_rule_val.WatermarkValue()
    else:
        return 0.0


def get_cross_rate_by_rule_val(rule_val, curr, latest_rule_val=True):
    if rule_val is not None:
        currency = curr
        trade_datetime = get_rule_value_date(rule_val)
        if latest_rule_val:
            price_market = eod_or_refinitiv_by_datetime(trade_datetime)
        else:
            price_market = 'EOD_MtM'
        return get_cross_rate(currency, trade_datetime, price_market)
    else:
        return 1.0

def get_settle_price(price_entry, market_name):
    if market_name == 'EOD_MtM':
        return price_entry.Settle()
    elif market_name == 'REFINITIV_SPOT':
        return ( price_entry.Bid() + price_entry.Ask() ) / 2
    else:
        return 1.0

def get_cross_rate(curr,tradedate,price_market):
    currency1 = curr
    currency2 = "USD"
    trade_time = strftime('%Y-%m-%d', strptime( tradedate, '%Y-%m-%d %H:%M:%S' ) )
    jakarta = acm.FCalendar['Jakarta']
    trade_time_yesterday = acm.Time.DateAdjustPeriod(trade_time,'-1d',jakarta,2)
    
    price = acm.FPrice.Select(f"instrument = '{currency1}' and currency = '{currency2}' and market = '{price_market}' and day = '{trade_time}'")
    if price:
        return get_settle_price(price[0], price_market)
    else:
        price_yesterday = acm.FPrice.Select(f"instrument = '{currency1}' and currency = '{currency2}' and market = '{price_market}' and day = '{trade_time_yesterday}'")
        if price_yesterday:
            return get_settle_price(price_yesterday[0], price_market)
        else:
            price_inv = acm.FPrice.Select(f"instrument = '{currency2}' and currency = '{currency1}' and market = '{price_market}' and day = '{trade_time}'")
            if price_inv:
                return 1/get_settle_price(price_inv[0], price_market)
            else:
                price_inv_yesterday = acm.FPrice.Select(f"instrument = '{currency2}' and currency = '{currency1}' and market = '{price_market}' and day = '{trade_time_yesterday}'")
                if price_inv_yesterday:
                    return 1/get_settle_price(price_inv_yesterday[0], price_market)
                else:
                    rate1 = acm.FPrice.Select(f"instrument = '{currency1}' and currency = 'IDR' and market = '{price_market}' and day = '{trade_time}'")
                    
                    rate2 = acm.FPrice.Select(f"instrument = 'USD' and currency = 'IDR' and market = '{price_market}' and day = '{trade_time}'")
                    if rate1 and rate2:
                        return get_settle_price(rate1[0], price_market)/get_settle_price(rate2[0], price_market)
                    else:
                        rate1 = acm.FPrice.Select(f"instrument = '{currency1}' and currency = 'IDR' and market = '{price_market}' and day = '{trade_time_yesterday}'")
                    
                        rate2 = acm.FPrice.Select(f"instrument = 'USD' and currency = 'IDR' and market = '{price_market}' and day = '{trade_time_yesterday}'")
                        if rate1 and rate2:
                            return get_settle_price(rate1[0], price_market)/get_settle_price(rate2[0], price_market)
                        else:
                            return 1.0

    

def get_party_data_by_ael_sql(pty_name):
    pty = acm.FParty[pty_name]
    
    pty_list = [pty]

    return pty_list

def NaN_to_zero(val):
    check_val = str(val)
    if check_val.lower() == 'nan':
        return 0.0
    else:
        return float(val)

def get_trading_sheet_column_value(obj, calc_space, col_name):
    col_val = calc_space.CreateCalculation(obj, col_name).Value()
    #print(col_val)
    try:
        num = NaN_to_zero(col_val.Number())
        res_val = num
    except:
        res_val = 0.0
    return res_val

def get_FArray(array_list):
    acm_array_list = acm.FArray()
    acm_array_list.AddAll(array_list)
    return acm_array_list

def ins_trades_calc(issuer_name, ins_name, calc_space, col_name):
    trades = issuer_util_calc_dicts[issuer_name]['Instruments'][ins_name]
    total_val = 0.0
    for trd in trades:
        if trd.AdditionalInfo().LimitPartyTarget() is trd.Instrument().Issuer():
            trd_val = get_trading_sheet_column_value(trd, calc_space, col_name)
        else:
            trd_val = 0.0
        total_val += trd_val
    issuer_util_calc_dicts[issuer_name]['Instruments'][ins_name] = total_val
    return total_val
    
def issuer_util_calc(issuer_name):
    util_dict = issuer_util_calc_dicts[issuer_name]
    total_val = 0.0
    for key, val in util_dict.items():
        if key != 'All Trades' and key != '1 Day Change':
            total_val = total_val + val
    return total_val

def thousand_dot_sep(val):
    if abs(val) >= 1000.0:
        res_val = "{:,.2f}".format(val).replace(',',' ').replace('.',',').replace(' ','.')
    else:
        res_val = "{:,.2f}".format(val).replace('.',',')
    return res_val
    
def percentage_removal(val):
    val = val.replace(',','.')
    res = float(val[:-1])
    return res
    
def get_date_difference(date1, date2):
    return acm.Time.DateDifference(date1, date2)
    
def get_expiry_status(end_date, today):
    date_diff = get_date_difference(end_date, today)
    if date_diff > 0:
        return 'Green'
    else:
        if end_date in ['', '-']:
            return 'Green'
        else:
            return 'Red'
    
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

def get_currency_by_rule_name(rule_name):
    rule_obj = acm.FComplianceRule[rule_name]
    if rule_obj is not None:
        try:
            curr = rule_obj.Definition().Column().Configuration().ParamDict()['columnParameters']['FixedCurr'].Name()
        except:
            curr = 'USD'
        return curr
    else:
        return 'USD'

def compliance_rule_list(rule_def, rule_category):
    return [ comp_rule.Name() for comp_rule in acm.FComplianceRule.Select("definitionInfo='"+rule_def+"' and ruleCategory='"+rule_category+"'") ]

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'MO13 - Credit Risk - Issuer Limit Utilization'}
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'MO13 - Credit Risk - Issuer Limit Utilization', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output'],
['compliance_rule_name', 'Compliance Rule', 'string', compliance_rule_list('PositionAndRiskControl', 'Pre-Deal'), 'FI_GRP_IDR', 0, 0, 'Select Compliance rule Name']
]  
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    
    rule_name = str(parameter['compliance_rule_name'])
    
    party_list = ael.asql("Select a.target_seqnbr from AppliedRule a, ComplianceRule c where a.compliance_rule = c.seqnbr and c.name = '"+rule_name+"' and inactive = 'No'")[1][0]
    #party_list = [('PERTAMINA PERSERO PT',),('PERUSAHAAN LISTRIK NEGAR',)]
    
    rule_obj = acm.FComplianceRule[rule_name]
    

    all_ports = []
    for pty in party_list:
        all_ports = all_ports + get_party_data_by_ael_sql(pty[0])
    
    titles = ['Customer Name','Group ID', 'Limit', 'Utilisasi', '1 Day Change', '% Utilization', 'Status Limit', 'Limit Expiry', 'Status Limit Expiry', 'Notes']
    

    columns = ['Limit', 'Utilisasi', '1 Day Change', '%']
    

    #rule_name = "FI_GRP_IDR"
    
    calc_space2 = acm.Calculations().CreateCalculationSpace(context, 'FPortfolioSheet')

    
    rows = []
    for port in all_ports:
        temp_row = [port.Name()]

        temp_row.append(port.Id())
        end_date = get_end_date_by_rule_name(port, rule_name)
        
        a_rule = get_applied_rule_by_target(port, rule_name)
        tv_list = a_rule.ThresholdValues()

        util_val_obj = get_rule_value_by_rule_name(port, rule_name)
        prev_util_val_obj = get_prev_day_rule_val_by_rule_name(port, rule_name)

        curr = get_currency_by_rule_name(rule_name)
        cross_rate = get_cross_rate_by_rule_val(util_val_obj, curr)

        temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(port, rule_name) * cross_rate ) )
        

        util_val = get_rule_watermark_value(util_val_obj)
        util_val_res = util_val * cross_rate
        temp_row.append( thousand_dot_sep( util_val_res ) ) #3


        prev_util_val = get_rule_watermark_value(prev_util_val_obj) * get_cross_rate_by_rule_val(prev_util_val_obj, curr, False)
        dc_val = abs(util_val_res - prev_util_val) 
        temp_row.append( thousand_dot_sep( dc_val ) )
        
        
        
        
        try:
            temp_row.append( get_expiry_status( end_date, today ) )
        except:
            temp_row.append( '-' )

        threshold_val = get_vio_threshold_value_by_rule_name(port, rule_name)    
        percent_val = get_utilization_percentage_by_rule_name(threshold_val, util_val_res, cross_rate) + '%'
        temp_row.insert( 5, percent_val )
        if len(tv_list) > 0:
            temp_row.insert( 6, limit_indicator( tv_list, util_val ) )
        else:
            temp_row.insert( 6, 'Green' )
        temp_row.insert( 7, end_date )
        
        temp_row.append( get_last_diary_note_by_rule_name(port, rule_name) ) 
        
        if len(temp_row) > 1:
            rows.append(temp_row)
    

    
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    
    for i in titles:
        table_html = table_html.replace('<th>'+i+'</th>', '<th style="background-color: #99ff66;">'+i+'</th>')
    
    for pty in party_list:
        pty_obj = acm.FParty[pty[0]]
        table_html = table_html.replace('<td>'+pty_obj.Name()+'</td>', '<td style="text-align: left;">'+pty_obj.Name()+'</td>')
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+pty_obj.Name()+'</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>'+pty_obj.Name()+'</fo:block></fo:table-cell>')
        
    
    #HTML Table Customization
    table_html = table_html.replace('<td>Green</td>', '<td style="background-color: #00cc66;"></td>')
    table_html = table_html.replace('<td>Yellow</td>', '<td style="background-color: #ffcc00;"></td>')
    table_html = table_html.replace('<td>Red</td>', '<td style="background-color: #ff0000;"></td>')
    table_html = table_html.replace('&', '&amp;')
    table_html = table_html.replace('%', '&#37;')
    
    #XSL-FO Table Customization
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
    current_date2 = "Report Date: " + datetime.now().strftime("%d-%m-%Y")
    #report_name = report_name + " - " + filter_currency
    html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date)
    html_f = open(html_file, "r")
    #contents = f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">')
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
    xsl_contents = xsl_contents.replace('<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">', '<fo:table-body>\n\t<fo:table-row background-color="#99ff66" font-weight="bold">')

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
