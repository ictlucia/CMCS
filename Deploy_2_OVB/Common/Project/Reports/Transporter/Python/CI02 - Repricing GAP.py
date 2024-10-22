import ael, acm
from datetime import date, timedelta, datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

##################################################################################################
# RUNNING QUERY FUNCTION
##################################################################################################

# Creating Base Query Format 
def run_query_asql(filter, db_from, date):
    query = f"""
        SELECT
            trdnbr 
        FROM 
            {db_from}
        WHERE
            {date} AND
            {filter}
    """
    ## Running query using AEL ASQL
    val_list =  ael.asql(query)[1][0]
    
    ## Saving Trade Number to list
    trdnbr_list = []
    for i in val_list:
        trdnbr_list.append(i[0])
        
    return trdnbr_list 

# Creating Query Filter Base On optkey3_chlnbr & optkey4_chlnbr
"""
Filter Format
1) ((DISPLAY_ID(tr, 'optkey3_chlnbr') = '{optkey3 value}' AND DISPLAY_ID(tr, 'optkey4_chlnbr') = '{optkey4 value})' OR ....)
2) ((DISPLAY_ID(tr, 'optkey3_chlnbr') = '{optkey3 value}' AND DISPLAY_ID(tr, 'optkey4_chlnbr') IN ('{optkey4 list}')) OR ....)
"""
def filter_query(d_info):
    d_filter = {}
    
    for key, list_vals in d_info.items():
        list_filter = [] 
        for list_val in list_vals:
            filter_1 = f"DISPLAY_ID({list_val[0][0][:2]}, '{list_val[0][1]}') = '{list_val[0][2]}'" ## Filtering for optkey3_chlnbr
            if not isinstance(list_val[1][2], list) : ## Check optkey4_chlnbr Value type (List / String)
                if list_val[1][2] != None:
                    filter_2 = f"DISPLAY_ID({list_val[1][0][:2]}, '{list_val[1][1]}') = '{list_val[1][2]}'" ## Filtering for optkey4_chlnbr (String)
                else :
                    filter_2 = ""
            else :
                join_val = "('" + "', '".join(list_val[1][2]) + "')"
                filter_2 = f"DISPLAY_ID({list_val[1][0][:2]}, '{list_val[1][1]}') IN {join_val}" ## Filtering for optkey4_chlnbr (List)
            list_filter.append(" AND ".join([filter_1, filter_2]))
        d_filter[key] = "(" + ") OR (".join(list_filter) + ")"
    
    return d_filter

# Creating Time range for filtering and List Month-Year
def get_time_range(date):
    today_date = datetime.strptime(date, "%Y-%m-%d")
    list_date = [today_date + timedelta(days=31 * i) for i in range(12)] + [today_date.replace(year=today_date.year + i) for i in range(1, 6)] # Get date range from <= 1 Month until >60 Month

    list_date_new = [date.replace(day=1).strftime('%d/%m/%Y') for date in list_date] # Change date format to dd/mm/yyyy to fit with 'value_day' format in ASQL
    list_month_year = [date.replace(day=1).strftime('%b-%y') for date in list_date][1:] + ["", "Dalam Juta USD", ""] # Creating List for column month-year 

    filter_months = [ f"(value_day >= '{list_date_new[i]}' AND value_day < '{list_date_new[i+1]}')"
        if i + 1 < len(list_date_new)
        else f"(value_day >= '{list_date_new[i]}')"
        for i in range(len(list_date_new))
        ] # Create a filtering format for value_day
    
    return filter_months, list_month_year, list_date[0].replace(day=1).strftime('%b-%y')

##################################################################################################
# HTML TABLE FUNCTION
##################################################################################################
def info_table(curr, date):
    html_code = f"""
    <tr class="info">
            <td>Repricing Gap</td>
            <td>{curr}</td>
        </tr>
        <tr class="info">
            <td>Neraca</td>
            <td>{date}</td>
        </tr>
    """

    return html_code

def month_html_func(list_month):
    open_tr_month = '<tr class="month">\n'
    close_tr_month = '</tr>'
    null_col = '<td></td>\n'
    list_month_td = []

    for month in list_month:
        list_month_td.append(f'<td>{month}</td>')
    
    str_month_td = "\n".join(list_month_td)
    return open_tr_month + null_col + str_month_td + close_tr_month

def header_html_func(list_header):
    open_tr_head = '<tr class="header">\n'
    close_tr_head = '</tr>'
    list_head_td = []

    for header in list_header:
         list_head_td.append(f'<td class="header-val">{header}</td>')

    str_head_td = "\n".join(list_head_td)
    return open_tr_head + str_head_td + close_tr_head

def content_html_func(caption, list_content, list_agg):
    caption_html = f'<tr>\n<td class="caption">{caption}</td>\n</tr>\n'
    
    list_content_tr = []
    for content in list_content:
        list_content_td = []
        key = f'<td class="content-val">&emsp;{content[0]}</td>'
        list_content_td.append(key)

        for val_content in content[1]:
            val_html = f'<td class="number-cell">{int(val_content):,}</td>'
            list_content_td.append(val_html)
        
        str_content_td = "<tr>" + "\n".join(list_content_td) + "</tr>"
        list_content_tr.append(str_content_td)
    
    str_content = "\n".join(list_content_tr)

    list_agg_td = []
    key_agg = f'<td class="agg">{list_agg[0]}</td>'
    list_agg_td.append(key_agg)
    for agg_val in list_agg[1]:
        list_agg_td.append(f'<td class="number-cell-agg">{int(agg_val):,}</td>')
    
    str_agg = "\n".join(list_agg_td)
    str_agg_tr = "<tr>" + str_agg + "</tr>"

    return caption_html + str_content + str_agg_tr

def balance_info_func(list_balance):
    open_tr_bal = '<tr>\n'
    close_tr_bal = '</tr>'
    list_bal_td = []
    list_bal_td.append(f'<td class="balance-title">{list_balance[0]}</td>')

    for bal in list_balance[1]:
         list_bal_td.append(f'<td class="number-cell-balance">{int(bal):,}</td>')

    str_bal_td = "\n".join(list_bal_td)
    return open_tr_bal + str_bal_td + close_tr_bal

def footer_info_func(list_footer):
    footer = []
    for footers in list_footer:
        open_tr_foot = '<tr class="footer">\n'
        close_tr_foot = '</tr>'
        list_foot_td = []
        list_foot_td.append(f'<td class="caption">{footers[0]}</td>')

        for val_footers in footers[1]:
            list_foot_td.append(f'<td class="number-cell-footer">{int(val_footers):,}</td>')
        str_foot_td = open_tr_foot + "\n".join(list_foot_td) + close_tr_foot
        footer.append(str_foot_td)
    
    str_footer =  "\n".join(footer)
    
    return str_footer

def html_generate(table):
    open_code_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <style>
            table{
                border-collapse: collapse;
            }
            .info{
                font-weight: bold;
                text-align: left;
            }
            .month{
                font-weight: bold;
                text-align: center;
            }
            .header-val{
                font-weight: bold;
                border: 2px solid black;
                text-align: center;
            }
            .caption{
                font-weight: bold;
            }
            .agg{
                font-weight: bold;
                text-align: center;
            }
            .number-cell, .content-val{
                border-bottom: 2px solid black;
            }
            .number-cell-balance, .balance-title {
                border-bottom: 2px solid black;
            }
            .balance-title {
                border-left: 2px solid black;
            }
            .number-cell, .number-cell-agg, .number-cell-balance, .number-cell-footer {
                text-align: right;
            }
            .balance-title{
                font-weight: bold;
            }
        </style>
        
    </head>
    <body>
        <table>
    """

    close_code_html = """
        </table>
        
        </body>
        </html>
    """

    return open_code_html + table + close_code_html

##################################################################################################
# FILTER QUERY (OPTKEY3 & OPTKEY4) - DICTIONARY
##################################################################################################
d_filter_aset = {
    '1.1 Kas' : [[
        ['trade', 'optkey3_chlnbr', 'DL'], 
        ['trade', 'optkey4_chlnbr', "OVT"]]],
    '1.2 Penempatan pada Bank Indonesia' : [[
        ['trade', 'optkey3_chlnbr', 'DL'], 
        ['trade', 'optkey4_chlnbr', "OVT"]]],
    '1.3 Penempatan pada Bank Lain' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', "OVP"]]],
    '1.4 Tagihan Sport dan Derivative' : [
        [['trade', 'optkey3_chlnbr', 'FX'], 
        ['trade', 'optkey4_chlnbr', "SPOT"]],
        [['trade', 'optkey3_chlnbr', 'SWAP'], 
        ['trade', 'optkey4_chlnbr', ['CCD', 'IRS']]]],
    '1.5 Surat berharga yang dimiliki' : [[
        ['trade', 'optkey3_chlnbr', 'BOND'],
        ['trade', 'optkey4_chlnbr', ["BILlS", "UST", "CBUSD", "ROI", "INDOIS"]]]],
    '1.6 S/B Reverse Repo' : [[
        ['trade', 'optkey3_chlnbr', 'REPO'],
        ['trade', 'optkey4_chlnbr', ["IWFGOV", "IWFOTH"]]]],
    '1.7 Kredit yang diberikan' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', "CMP"]]],
    '1.8 OKPN' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', "CMP"]]],
    '1.9 Tagihan Akseptasi' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', "CMP"]]],
    '1.10 Aktiva Tetap dan Inventaris' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', "CMP"]]],
    '1.11 Rupa Rupa Aktiva' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', "CMP"]]],
}

d_filter_kewajiban = {
    '2.1. Giro' : [[
        ['trade', 'optkey3_chlnbr', 'DL'], 
        ['trade', 'optkey4_chlnbr', ""]]],
    '2.2. Tabungan' : [[
        ['trade', 'optkey3_chlnbr', 'DL'], 
        ['trade', 'optkey4_chlnbr', ""]]],
    '2.3. Depo Berjangka' : [[
        ['trade', 'optkey3_chlnbr', 'DL'], 
        ['trade', 'optkey4_chlnbr', ""]]],
    '2.4. Kewajiban Kepada BI' : [[
        ['trade', 'optkey3_chlnbr', 'BOND'],
        ['trade', 'optkey4_chlnbr', ""]]],
    '2.5. Kewajiban Kepada Bank Lain' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', ""]]],
    '2.6. Kewajiban Spot dan Derivative' : [
        [['trade', 'optkey3_chlnbr', 'FX'], 
        ['trade', 'optkey4_chlnbr', "SPOT"]],
        [['trade', 'optkey3_chlnbr', 'SWAP'], 
        ['trade', 'optkey4_chlnbr', ['CCS', 'IRS']]]],
    '2.7. Kewajiban Surat Berharga (Repo)' : [[
        ['trade', 'optkey3_chlnbr', 'REPO'],
        ['trade', 'optkey4_chlnbr', ["IWFGOV", "IWFOTH"]]]],
    '2.8. Kewajiban Akseptasi' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', "CMP"]]],
    '2.9. Pinjaman Diterima' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', ""]]],
    '2.10. Kewajiban Lain-Lain' : [[
        ['trade', 'optkey3_chlnbr', 'DL'],
        ['trade', 'optkey4_chlnbr', ""]]]
}

##################################################################################################
# TABLE CONTENT
##################################################################################################
list_header = ["Skala Waktu", "&#8804;1 Mo", ">1 Mo - 2 Mo", ">2 Mo - 3 Mo", ">3 Mo - 4 Mo", ">4 Mo - 5 Mo",
          ">5 Mo - 6 Mo", ">6 Mo - 7 Mo", ">7 Mo - 8 Mo", ">8 Mo - 9 Mo", ">9 Mo - 10 Mo", ">10 Mo - 11 Mo",
          ">10 Mo - 11 Mo", ">12 Mo - 24 Mo", ">24 Mo - 36 Mo", ">36 Mo - 48 Mo", ">48 Mo - >60 Mo", ">60",
          "Non Rate Sensitive Items", "TOTAL"]
##################################################################################################
# GENERATE TABLE
##################################################################################################

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'CI02 - Repricing GAP'}
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'CI02 - Repricing GAP', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Output Files','string', ['.html', '.xls'], '.html', 0 , 1, 'Select Output Extension Type'],
['date','Date','string',None,acm.Time.DateToday(),0,1]
]

def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = "".join(parameter['output_file'])
    date = "".join(parameter['date'])
    
    filter_months, list_month_year, neraca_date = get_time_range(date)
    
    ## TABLE CONTENT FOR ASET
    caption_aset = "1. Aset"

    context = acm.GetDefaultContext()
    sheetType = 'FTradeSheet'
    columnId = 'Portfolio Position'
    list_content_aset = []
    for key, val in d_filter_aset.items():
        sql_filter = filter_query(d_filter_aset)
        list_total_per_date = []
        for date in filter_months:
            trdnbr_query_result = run_query_asql(sql_filter[key], 'trade tr', date)

            calcSpace = acm.Calculations().CreateCalculationSpace(context, sheetType)
            port_value = []
            for trade_num in trdnbr_query_result:    
                dataTrade = acm.FTrade[trade_num]
                calculation = calcSpace.CreateCalculation(dataTrade, columnId)
                result = calculation.FormattedValue()
                if result == "" : result = "0"
                num_result = float(result.replace(".", ""))
                if num_result >= 0 : port_value.append(num_result)
            
            list_total_per_date.append(sum(port_value))
            
        for x in [0, sum(list_total_per_date)]:
            list_total_per_date.append(x)
        list_content_aset.append([key, list_total_per_date])

    list_agg_asset = ["TOTAL ASSET"]
    agg_val_aset = []

    for i in range(len(list_content_aset[0][1])):
        agg_val_aset.append(sum([list_content_aset[x][1][i] for x in range(len(list_content_aset))]))
        
    list_agg_asset.append(agg_val_aset)

    ## TABLE CONTENT FOR KEWAJIBAN
    caption_kewajiban = "2. Kewajiban"

    list_content_kewajiban = []
    for key, val in d_filter_kewajiban.items():
        sql_filter = filter_query(d_filter_kewajiban)
        list_total_per_date = []
        for date in filter_months:
            trdnbr_query_result = run_query_asql(sql_filter[key], 'trade tr', date)

            calcSpace = acm.Calculations().CreateCalculationSpace(context, sheetType)
            port_value = []
            for trade_num in trdnbr_query_result:    
                dataTrade = acm.FTrade[trade_num]
                PrimaryIssuance = dataTrade.PrimaryIssuance()
                Direction = dataTrade.Direction()
                loan_cond = key in ['2.5.Kewajiban Kepada Bank Lain', '2.9.Pinjaman Diterima'] and Direction == 'Loan'
                depo_cond = key == '2.3. Depo Berjangka' and Direction == 'Deposit'
                thick_primary_cond = key == '2.4. Kewajiban Kepada BI' and PrimaryIssuance == True
                normal_cond = key in ['2.1. Giro', '2.2. Tabungan', '2.6. Kewajiban Spot dan Derivative', '2.7. Kewajiban Surat Berharga (Repo)', '2.8. Kewajiban Akseptasi', '2.10. Kewajiban Lain-Lain']
                if (loan_cond) or (depo_cond) or (thick_primary_cond) or (normal_cond):
                    calculation = calcSpace.CreateCalculation(dataTrade, columnId)
                    result = calculation.FormattedValue()
                    if result == "" : result = "0"
                    num_result = float(result.replace(".", ""))
                    if num_result <= 0 : port_value.append(abs(num_result))
            
            list_total_per_date.append(sum(port_value))
            
        for x in [0, sum(list_total_per_date)]:
            list_total_per_date.append(x)
        list_content_kewajiban.append([key, list_total_per_date])

    list_agg_kewajiban = ["TOTAL LIABILITIES"]
    agg_val_kewajiban = []

    for i in range(len(list_content_kewajiban[0][1])):
        agg_val_kewajiban.append(sum([list_content_kewajiban[x][1][i] for x in range(len(list_content_kewajiban))]))
    list_agg_kewajiban.append(agg_val_kewajiban)

    list_balance = ['4. Off Balance Sheet', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    periodic_gap = [agg_val_aset[0] - agg_val_kewajiban[0]]
    cummulative_gap = [agg_val_aset[0] - agg_val_kewajiban[0]]
    for i in range(len(agg_val_aset)-1):    
        periodic_gap.append(agg_val_aset[i+1] - agg_val_kewajiban[i+1])
        cummulative_gap.append(cummulative_gap[i] + agg_val_aset[i+1])

    list_footer = [
        ['PERIODIC GAP', periodic_gap],
        ['CUMMULATIVE GAP', cummulative_gap]]
    
    filter_months, list_month_year, neraca_date = get_time_range(date)
    
    skip_row = '<tr><td>&nbsp;</td></tr>'

    table_info = info_table("USD", neraca_date) + skip_row
    Asset = month_html_func(list_month_year) + header_html_func(list_header) + content_html_func(caption_aset, list_content_aset, list_agg_asset)
    kewajiban = skip_row + header_html_func(list_header) + content_html_func(caption_kewajiban, list_content_kewajiban, list_agg_kewajiban)
    balance = skip_row + header_html_func(list_header) + balance_info_func(list_balance)
    footer = skip_row  + footer_info_func(list_footer)
    table_html_full = table_info + "\n" +Asset + "\n" + kewajiban + "\n" + balance + "\n" + footer
    full_code_html = html_generate(table_html_full)
    
    if output_file == ".html" :
        generate_html = HTMLGenerator().create_html_file(full_code_html, file_path, report_name, date, False)
    elif output_file == ".xls" :
        generate_html = HTMLGenerator().create_html_file(full_code_html, file_path, report_name, date, False)
        generate_file_for_other_extension(generate_html, '.xls')
        os.remove(os.path.join(file_path, f"report_{date}", f"{report_name}.html"))

