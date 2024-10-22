import acm, ael, random, os, webbrowser
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from time import sleep, perf_counter, strftime, strptime
from datetime import datetime, date, timezone
from Python_MO_Custom_Fields import *

context = acm.GetDefaultContext( )
today = acm.Time.DateToday()
#all_trades = acm.FTrade.Select('')


rule_set_dicts = {}

cpty_util_calc_dicts = {

}

def create_html_file(file_name, file_path, list_table, title, current_datetime, current_date, folder_with_file_name=False, open_html=True) :
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    table {
      font-family: arial, sans-serif;
      border-collapse: collapse;
      white-space: nowrap;
      margin-left: 100px;
    }

    .side-by-side { 
      display: flex; 
    } 

    
    div { 
      margin-bottom: 5px; 
    } 

    

    td, th {
      border: 1px solid #000000;
      text-align: center;
      padding: 8px;
    }

    

    h1 {
        text-align: center;
    }
    </style>
    </head>
    <body>
    <center><h1><u>""" + str(title) + """</u></h1></center>
    <h1 style="text-align: left;">""" + current_date + """</h1>
    <h2 style="text-align: left;">USD Equivalent - Refinitiv SPOT Marketplace</h2>
    """

    

    for i in list_table :
        html_content += i + "<br>"

    

    html_content += "</body></html>"

    

    if folder_with_file_name:
        folder_path = file_path+"\\"+file_name+"\\"+current_datetime
    else:
        date,month,year=current_datetime[:2],current_datetime[2:4],current_datetime[4:]
        folder_path = file_path + "\\report" + year+month+date

    try:
        os.makedirs(folder_path)
    except:
        #print('Path too long')
        pass

    

    file_url = folder_path+"\\"+file_name+".html"
    f = open(file_url, "w")
    f.write(html_content)
    f.close()

    url = "file://" + file_url

    

    if open_html:
        webbrowser.open(file_url,new=2)

    
    return file_url

def create_xsl_fo_file(file_name, file_path, list_table, title, current_datetime, current_date, folder_with_file_name=False):

    xsl_fo_content = """<?xml version="1.1" encoding="utf-8"?>
<fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format">
 <fo:layout-master-set>
  <fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">
   <fo:region-body/>
  </fo:simple-page-master>
 </fo:layout-master-set>
 <fo:page-sequence master-reference="my_page">
  <fo:flow flow-name="xsl-region-body">
    <fo:block font-weight="bold" font-size="30px" margin-bottom="30px">"""+str(title)+"""</fo:block>
    <fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="left">"""+ current_date + """</fo:block>
    <fo:block font-weight="bold" font-size="24px" margin-bottom="30px" text-align="left">USD Equivalent - Refinitiv SPOT Marketplace</fo:block>
"""

  

    for i in list_table :
        xsl_fo_content += i +"\n"

        

    xsl_fo_content += """ </fo:flow>
 </fo:page-sequence>
</fo:root>
    """

    

    if folder_with_file_name:
        folder_path = file_path+"\\"+file_name+"\\"+current_datetime
    else:
        date,month,year=current_datetime[:2],current_datetime[2:4],current_datetime[4:]
        folder_path = file_path + "\\report" + year+month+date

        

    try:
        os.makedirs(folder_path)
    except:
        #print('Path too long')
        pass

    

    file_url = folder_path+"\\"+file_name+".fo"
    f = open(file_url, "w")
    f.write(xsl_fo_content)
    f.close()

    return file_url 



def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection

# ================ DATA FILTER COLUMN ================ 

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

def get_party_data_by_ael_sql(rule_set):
    ntl_rule = rule_set_dicts[rule_set]['NTL']
    crd_rule = rule_set_dicts[rule_set]['CEM']


    query1 = """
    Select a.target_seqnbr 
    from AppliedRule a, ComplianceRule c 
    where a.compliance_rule = c.seqnbr 
    and c.name='{}' 
    and inactive = 'No'
    """.format( crd_rule )
    
    pty_queries1 = ael.asql(query1)[1][0]
    pty_list1 = [ acm.FParty[ pty[0] ] for pty in pty_queries1 ]

    query2 = """
    Select a.target_seqnbr 
    from AppliedRule a, ComplianceRule c 
    where a.compliance_rule = c.seqnbr 
    and c.name='{}' 
    and inactive = 'No'
    """.format( ntl_rule )
    
    pty_queries2 = ael.asql(query2)[1][0]
    pty_list2 = [ acm.FParty[ pty[0] ] for pty in pty_queries2 ]
    
    pty_list = pty_list1.copy()

    for pty in pty_list2:
        if pty not in pty_list:
            pty_list.append(pty)

    rule_set_dicts[rule_set]['Parties'].extend(pty_list)
    rule_set_dicts[rule_set]['NTL Active Parties'].extend(pty_list2)
    rule_set_dicts[rule_set]['CEM Active Parties'].extend(pty_list1)

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


def cpty_trades_calc(key_name, column_type, calc_space, col_name):
    trades = cpty_util_calc_dicts[column_type][key_name + '_All Trades']
    total_val = 0.0
    for trd in trades:
        trd_val = get_trading_sheet_column_value(trd, calc_space, col_name)
        total_val += trd_val
    cpty_util_calc_dicts[column_type][key_name + '_Utilization'] = total_val
    return total_val


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


def get_product_rule_name(default_rule, rule_list, product_code):
    filtered_rules = [rule for rule in rule_list if product_code in rule]
    if len(filtered_rules) > 0:
        return filtered_rules[0]
    else:
        return default_rule

def compliance_rule_list(rule_def, rule_category):
    return [ comp_rule.Name() for comp_rule in acm.FComplianceRule.Select("definitionInfo='"+rule_def+"' and ruleCategory='"+rule_category+"'") ]

FXNTL_default_rules = "FXNTL_GRP_GR_USD"
FX_default_rules = "FX_GRP_GR_USD"

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'MO12 - Credit Risk - Counterparty Limit Utilization FX'}
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'MO12 - Credit Risk - Counterparty Limit Utilization FX', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output'],
['ntl_compliance_rule_name', 'Notional Compliance Rule', 'string', compliance_rule_list('PositionAndRiskControl', 'Pre-Deal'), FXNTL_default_rules, 0, 1, 'Select Compliance rule Name'],
['crd_compliance_rule_name', 'Credit Equivalent Compliance Rule', 'string', compliance_rule_list('PositionAndRiskControl', 'Pre-Deal'), FX_default_rules, 0, 1, 'Select Compliance rule Name']
]  
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']

    
    
    ntl_rules = list( parameter['ntl_compliance_rule_name'] )
    crd_rules = list( parameter['crd_compliance_rule_name'] )
    


    if len(crd_rules) >= len(ntl_rules):
        rule_set_range = len(crd_rules)
    else:
        rule_set_range = len(ntl_rules)

    for i in range(0,rule_set_range):
        rule_set_dicts['Rule Set ' + str(i+1)] = {
            'CEM': None,
            'NTL': None,
            'Parties': [],
            'NTL Active Parties': [],
            'CEM Active Parties': []
        }

        #FX
        if i < len(crd_rules):
             rule_set_dicts['Rule Set ' + str(i+1)]['CEM'] = crd_rules[i]
        if i < len(ntl_rules):
             rule_set_dicts['Rule Set ' + str(i+1)]['NTL'] = ntl_rules[i]
    
    for key in list( rule_set_dicts.keys() ):
        get_party_data_by_ael_sql(key)
    #party_list = [('Counterparty 2','United States',)]
    product_list = ['FX Tom', 'FX Spot','FX Forward','FX Swap', 'DNDF']
    
    


    titles = ['Customer Name','Group ID', 'Notional', 'Credit Equivalent', 'Status Limit', 'Limit Expiry', 'Status Limit Expiry', 'Notes']

    columns = ['Limit', 'Utilisasi', '1 Day Change', '% Utilization']
    
    calc_space2 = acm.Calculations().CreateCalculationSpace(context, 'FPortfolioSheet')
    
    rows = [columns*2]


    for key in list( rule_set_dicts.keys() ):
        all_ports = rule_set_dicts[key]['Parties']

        ntl_rule_name = rule_set_dicts[key]['NTL']
        crd_rule_name = rule_set_dicts[key]['CEM']


        for port in all_ports:
            temp_row = [port.Name()] #0
            obj = port

            rule_name = crd_rule_name
            rule_name2 = ntl_rule_name

            
            end_date = get_end_date_by_rule_name(obj, rule_name)
            
            
            temp_row.append(port.Id()) #1

            a_rule = get_applied_rule_by_target(obj, rule_name)
            try:
                tv_list = a_rule.ThresholdValues()
            except:
                tv_list = []
            
            if obj in rule_set_dicts[key]['NTL Active Parties']:
                
    

                util_val_obj = get_rule_value_by_rule_name(obj, rule_name2)
                prev_util_val_obj = get_prev_day_rule_val_by_rule_name(obj, rule_name2)

                
                
                temp_util_val = get_rule_watermark_value(util_val_obj)
                
                curr = get_currency_by_rule_name(rule_name2)
                cross_rate = get_cross_rate_by_rule_val(util_val_obj, curr)

                temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name2) * cross_rate ) ) #2

                try:
                    util_val = NaN_to_zero( temp_util_val ) 
                    util_val_res = util_val * cross_rate
                except:
                    util_val_res = 0.0
                temp_row.append( thousand_dot_sep( util_val_res ) ) #3

                temp_prev_util_val = get_rule_watermark_value(prev_util_val_obj)
                prev_cross_rate = get_cross_rate_by_rule_val(prev_util_val_obj, curr, False)
                try:
                    prev_util_val = NaN_to_zero( temp_prev_util_val ) * prev_cross_rate
                    dc_val = abs(util_val_res - prev_util_val)
                except:
                    dc_val = 0.0
                temp_row.append( thousand_dot_sep( dc_val ) ) #4

                threshold_val = get_war_threshold_value_by_rule_name(obj, rule_name2)
                percent_val = get_utilization_percentage_by_rule_name(threshold_val, util_val_res, cross_rate) + '%'
                temp_row.append( percent_val ) #5

            else:
                temp_row.append( '0,00' )
                temp_row.append( '0,00' )
                temp_row.append( '0,00' )
                temp_row.append( '0.00%' )

            if obj in rule_set_dicts[key]['CEM Active Parties']:
                
                util_val_obj2 = get_rule_value_by_rule_name(obj, rule_name)
                prev_util_val_obj2 = get_prev_day_rule_val_by_rule_name(obj, rule_name)

                temp_util_val2 = get_rule_watermark_value(util_val_obj2)

                curr2 = get_currency_by_rule_name(rule_name)
                cross_rate2 = get_cross_rate_by_rule_val(util_val_obj2, curr2)

                temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) * cross_rate2 ) ) #6


                try:
                    util_val2 = NaN_to_zero( temp_util_val2 ) * cross_rate2
                    util_val_res2 = util_val2
                except:
                    util_val_res2 = 0.0
                temp_row.append( thousand_dot_sep( util_val_res2 ) ) #7


                
                
                temp_prev_util_val2 = get_rule_watermark_value(prev_util_val_obj2)
                prev_cross_rate2 = get_cross_rate_by_rule_val(prev_util_val_obj2, curr2, False)
                try:
                    prev_util_val2 = NaN_to_zero( temp_prev_util_val2 ) * prev_cross_rate2
                    dc_val2 = abs(util_val_res2 - prev_util_val2)
                except:
                    dc_val2 = 0.0
                temp_row.append( thousand_dot_sep( dc_val2 ) ) #8
                
                try:
                    temp_row.append( get_expiry_status( end_date, today ) ) #12
                except:
                    temp_row.append( '-' ) #12
                
                
                
                threshold_val2 = get_vio_threshold_value_by_rule_name(obj, rule_name)
                percent_val2 = get_utilization_percentage_by_rule_name(threshold_val2, util_val_res2, cross_rate2) + '%'
                temp_row.insert( 9, percent_val2 ) #9
                
                if len(tv_list) > 0:
                    temp_row.insert( 10, limit_indicator( tv_list, util_val2 ) ) #10
                else:
                    temp_row.insert( 10, 'Green' ) #10
                temp_row.insert( 11, end_date ) #11
                
                
                temp_row.append( get_last_diary_note_by_rule_name(obj, rule_name) ) #13
            else:
                temp_row.append( '0,00' )
                temp_row.append( '0,00' )
                temp_row.append( '0,00' )
                temp_row.append( '0.00%' )
            
                temp_row.append( 'Green' )
                temp_row.append( '-' )
                temp_row.append( 'Green' )
                temp_row.append( '-' )
            
            if len(temp_row) > 1:
                rows.append(temp_row)    
        

    #print(rows[1][2])

    #print(rows[0])
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    
    table_xsl_fo = table_xsl_fo.replace('</fo:table-header>', '</fo:table-row>')
    table_xsl_fo = table_xsl_fo.replace('<fo:table-body>', '')
    table_xsl_fo = table_xsl_fo.replace('<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">', '<fo:table-body>\n\t<fo:table-row background-color="#99ff66" font-weight="bold">')

    for i in titles:
        if i == 'Notional' or i == 'Credit Equivalent':
            table_html = table_html.replace('<th>'+i+'</th>', '<th colspan="'+str(len(columns))+'" style="background-color: #99ff66;">'+i+'</th>')
            table_xsl_fo = table_xsl_fo.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{i}</fo:block></fo:table-cell>', 
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-columns-spanned="{len(columns)}"><fo:block>{i}</fo:block></fo:table-cell>')
        else:
            table_html = table_html.replace('<th>'+i+'</th>', '<th rowspan="2" style="background-color: #99ff66;">'+i+'</th>')
            table_xsl_fo = table_xsl_fo.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{i}</fo:block></fo:table-cell>', 
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-rows-spanned="2"><fo:block>{i}</fo:block></fo:table-cell>')
    
            
    for col in columns:
        table_html = table_html.replace('<td>'+col+'</td>', '<td style="background-color: #99ff66;"><b>'+col+'</b></td>')
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+col+'</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" background-color="#99ff66" font-weight="bold" text-align="center"><fo:block>'+col+'</fo:block></fo:table-cell>')
    
    for key in list( rule_set_dicts.keys() ):
        party_list = rule_set_dicts[key]['Parties']
        for pty in party_list:
            obj_name = pty.Name()
        
            table_html = table_html.replace('<td>'+obj_name+'</td>', '<td style="text-align: left;">'+obj_name+'</td>')
            table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+obj_name+'</fo:block></fo:table-cell>',
            '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>'+obj_name+'</fo:block></fo:table-cell>')
        
    #table_html = table_html.replace('<td>PERUSAHAAN LISTRIK NEGAR</td>', '<td style="text-align: left;">PERUSAHAAN LISTRIK NEGAR</td>')
    
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
    html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date, current_date2)
    
    xsl_fo_file = create_xsl_fo_file(report_name + " " +current_date+current_hour, file_path, [table_xsl_fo], report_name, current_date, current_date2)

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
