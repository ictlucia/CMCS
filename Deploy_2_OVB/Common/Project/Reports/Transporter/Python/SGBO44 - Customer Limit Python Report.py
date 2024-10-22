import acm, ael, random
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from time import sleep, perf_counter
from Python_MO_Custom_Fields import *

context = acm.GetDefaultContext( )
today = acm.Time.DateToday()
yesterday = acm.Time.DateAddDelta(today, 0, 0, -1)
next_month = acm.Time.DateAddDelta(today, 0, 1, 0)
next_year = acm.Time.DateAddDelta(today, 1, 0, 0)
all_trades = acm.FTrade.Select('')
stand_calc = acm.FStandardCalculationsSpaceCollection()
sheet_type = 'FRuleValueHistorySheet'

def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection

# ================ DATA FILTER COLUMN ================ 

dict_of_column_filter = {
    'Country': {
        'Calculation': 'Counterparty CEM Limit',
        'Keyword': 'Country Limit MO14'
    },
    'Counterparty': {
        'Calculation': 'Portfolio Position',
        'Keyword': 'All transaction'
    },
    'FX': {
        'Calculation': 'Counterparty CEM Limit',
        'Keyword': 'FX'
    },
    'Bonds': {
        'Calculation': 'Portfolio Position',
        'Keyword': 'Bond'
    },
    'Money Market': {
        'Calculation': 'Counterparty CEM Limit',
        'Keyword': 'Money Market'
    },
    'Option': {
        'Calculation': 'Counterparty CEM Limit',
        'Keyword': 'Option'
    },
    'IRS': {
        'Calculation': 'Counterparty CEM Limit',
        'Keyword': 'IRS'
    },
    'CCS': {
        'Calculation': 'Counterparty CEM Limit',
        'Keyword': 'CCS'
    }
}


def get_countries_by_ael_sql(pty_list):
    country_list = []
    for pty in pty_list:
        if acm.FParty[ pty[0] ].RiskCountry() not in country_list:
            country_list.append( acm.FParty[ pty[0] ].RiskCountry() )
    return country_list

def get_party_data_by_ael_sql(pty_list, country_name):
    country_pty_list = [ acm.FChoiceList[country_name] ]
    for pty in pty_list:
        if pty[1] == country_name:
            country_pty_list.append(acm.FParty[ pty[0] ])
    return country_pty_list


def get_trading_sheet_column_value(obj, calc_space, col_name):
    col_val = calc_space.CreateCalculation(obj, col_name).Value()
    try:
        num = float(col_val.Number())
        res_val = thousand_dot_sep(num)
    except:
        res_val = '-'
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
    
def limit_indicator(val):
    if val < 75.0:
        return 'Green'
    elif val >= 75.0 and val < 100:
        return 'Yellow'
    else:
        return 'Red'

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'MO14 - Credit Risk - Country Limit Utilization'}
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'MO14 - Credit Risk - Country Limit Utilization', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output']
]  
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    
    #party_list = ael.asql("Select p.ptyid, c.entry from Party p, ChoiceList c where p.risk_country_chlnbr=c.seqnbr and p.type = 'Counterparty'")[1][0]
    #party_list = [('Bank of America Frankfurt','United States',),('Bank of America New York','United States',)]
    party_list = [('#100003','United States',)]
    country_list = get_countries_by_ael_sql(party_list)
    
    product_list = ['FX', 'Bonds', 'Money Market', 'Option', 'IRS' , 'CCS']
    
    all_ports = []
    for i in country_list:
        if i is not None:
            all_ports = all_ports + get_party_data_by_ael_sql(party_list, i.Name())
    
    

    titles = ['Country', 'Limit', 'Utilisasi', '1 Day Change', '% Utilization', 'Status Limit', 'Limit Expiry', 'Status Limit Expiry', 'Notes']
    
    columns = ['Limit', 'Utilisasi', '1 Day Change', '%']
    
    
    calc_space = acm.Calculations().CreateCalculationSpace(acm.GetDefaultContext(), sheet_type)
    calc_space2 = acm.Calculations().CreateCalculationSpace(acm.GetDefaultContext(), 'FAppliedRuleSheet')
    
    rows = []
    for port in all_ports:
        if port.ClassName().Text() == 'FChoiceList':
            calculation = dict_of_column_filter['Country']['Calculation']
            keyword = dict_of_column_filter['Country']['Keyword']
            rule_name = keyword
            obj = port
            temp_row = [port.Name()]
            try:
                temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
            except:
                temp_row.append( '-' )
                temp_row.append( '-' )
            
            rule_val = get_rule_value_by_rule_name(obj, rule_name)
            if rule_val is None:
                temp_row.append('-')
                temp_row.append('-')
            else:
                temp_row.append( get_trading_sheet_column_value(rule_val, calc_space, '1DayChange_Country') )
                temp_row.append( get_trading_sheet_column_value(rule_val.ResultHistory().AppliedRule(), calc_space2, 'StatusExpiry') )
            
            percent_val = get_utilization_percentage_by_rule_name(obj, rule_name)
            temp_row.insert( 4, percent_val )
            temp_row.insert( 5, limit_indicator( percentage_removal(percent_val) ) )
            temp_row.insert( 6, get_end_date_by_rule_name(obj, rule_name) )
            temp_row.append( '-' )
            
            if len(temp_row) > 1:
                rows.append(temp_row)
                
        else:
            calculation = dict_of_column_filter['Counterparty']['Calculation']
            keyword = dict_of_column_filter['Counterparty']['Keyword']
            obj = port
            rule_name = obj.Name() + ' ' + keyword
            temp_row = [port.Name()]
            
            try:
                temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
            except:
                temp_row.append( '-' )
                temp_row.append( '-' )
            
            rule_val = get_rule_value_by_rule_name(obj, rule_name)
            if rule_val is None:
                temp_row.append('-')
                temp_row.append('-')
            else:
                temp_row.append( get_trading_sheet_column_value(rule_val, calc_space, '1DayChange_Counterparty') )
                temp_row.append( get_trading_sheet_column_value(rule_val.ResultHistory().AppliedRule(), calc_space2, 'StatusExpiry') )
            
            percent_val = get_utilization_percentage_by_rule_name(obj, rule_name)
            temp_row.insert( 4, percent_val )
            temp_row.insert( 5, limit_indicator( percentage_removal(percent_val) ) )
            temp_row.insert( 6, get_end_date_by_rule_name(obj, rule_name) )
            temp_row.append( '-' )
            
            if len(temp_row) > 1:
                rows.append(temp_row)
            
            for prod in product_list:
                calculation = dict_of_column_filter[prod]['Calculation']
                keyword = dict_of_column_filter[prod]['Keyword']
                obj = port
                rule_name = obj.Name() + ' ' + keyword
                temp_row = [prod]
                
                try:
                    temp_row.append( thousand_dot_sep( get_threshold_limit_by_rule_name(obj, rule_name) ) )
                    temp_row.append( thousand_dot_sep( get_utilization_val_by_rule_name(obj, rule_name) ) )
                except:
                    temp_row.append( '-' )
                    temp_row.append( '-' )
                
                rule_val = get_rule_value_by_rule_name(obj, rule_name)
                if rule_val is None:
                    temp_row.append('-')
                    temp_row.append('-')
                else:
                    temp_row.append( get_trading_sheet_column_value(rule_val, calc_space, '1DayChange_Counterparty') )
                    temp_row.append( get_trading_sheet_column_value(rule_val.ResultHistory().AppliedRule(), calc_space2, 'StatusExpiry') )
                
                percent_val = get_utilization_percentage_by_rule_name(obj, rule_name)
                temp_row.insert( 4, percent_val )
                temp_row.insert( 5, limit_indicator( percentage_removal(percent_val) ) )
                temp_row.insert( 6, get_end_date_by_rule_name(obj, rule_name) )
                temp_row.append( '-' )
                
                if len(temp_row) > 1:
                    rows.append(temp_row)
        
        
    
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    
    for i in titles:
        table_html = table_html.replace('<th>'+i+'</th>', '<th style="background-color: #99ff66;">'+i+'</th>')
    
    
    for port in all_ports:
        obj_name = port.Name()
        
        table_html = table_html.replace('<td>'+obj_name+'</td>', '<td style="text-align: left;">'+obj_name+'</td>') 
        #table_html = table_html.replace('<td>'+obj.Name()+'</td>', '<td style="text-align: left;">'+obj.Name()+'</td>')  
        
        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+obj_name+'</fo:block></fo:table-cell>',
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>'+obj_name+'</fo:block></fo:table-cell>')
        #table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+obj.Name()+'</fo:block></fo:table-cell>',
        #'<fo:table-cell border-width="1px" border-style="solid" padding="8pt" text-align="left"><fo:block>'+obj.Name()+'</fo:block></fo:table-cell>')
        
    
    #HTML Table Customization    
    table_html = table_html.replace('<td>Green</td>', '<td style="background-color: #00cc66;"></td>')
    table_html = table_html.replace('<td>Yellow</td>', '<td style="background-color: #ffcc00;"></td>')
    table_html = table_html.replace('<td>Red</td>', '<td style="background-color: #ff0000;"></td>')
    table_html = table_html.replace('&', '&amp;')
    table_html = table_html.replace('%', '&#37;')
    
    #XSLFO Table Customization
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
    
    html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date)
    html_f = open(html_file, "r")
    html_contents = html_f.read().replace('''td, th {
      border: 1px solid #dddddd;
      text-align: center;
      padding: 8px;
    }''',
            ''' td, th {
      border: 1px solid #000000;
      text-align: center;
      padding: 8px;
    }''')
    html_f = open(html_file, "w")
    html_f.write(html_contents)
    html_f.close()
    
    xsl_fo_file = create_xsl_fo_file(report_name + " " +current_date+current_hour, file_path, [table_xsl_fo], report_name, current_date)

    xsl_f = open(xsl_fo_file, "r")

    xsl_contents = xsl_f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">')
    xsl_contents = xsl_contents.replace('<fo:block font-weight="bold" font-size="30px" margin-bottom="30px">'+report_name+'</fo:block>',
    '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="center">'+report_name+'</fo:block>')
    xsl_contents = xsl_contents.replace('''<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">
    <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Country</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Limit</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Utilisasi</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>1 Day Change</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>% Utilization</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Status Limit</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Limit Expiry</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Status Limit Expiry</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Notes</fo:block></fo:table-cell>
        </fo:table-header>
    <fo:table-body>''',
    '''<fo:table-body>
    <fo:table-row background-color="#99ff66" font-weight="bold">
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Country</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Limit</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Utilisasi</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>1 Day Change</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>% Utilization</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Status Limit</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Limit Expiry</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Status Limit Expiry</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Notes</fo:block></fo:table-cell>
    </fo:table-row>''')

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
