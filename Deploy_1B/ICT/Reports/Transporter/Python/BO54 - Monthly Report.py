import ael, acm, calendar
from Report_Python_BO import amountBaseOnCategory, currencyBaseOnCategory
from datetime import datetime, date, timedelta
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import locale
locale.setlocale(locale.LC_ALL, 'en_us')

###################################################################################################################################
# GET CALCULATE DATA ( FREQUENCY & NOMINAL ) FOR EACH MONTH PER PRODUCT
###################################################################################################################################
def run_query_asql(year_data, from_month, to_month):
    list_month = list(calendar.month_name)
    from_month_i, to_month_i = list_month.index(from_month), list_month.index(to_month)
    month_list_str = ", ".join([f"'{month}'" for month in list_month[from_month_i : to_month_i + 1]])
    
    query_day = f"convert('date', t.time, '%B') IN ({month_list_str}) AND convert('date', t.time, '%Y') = {year_data} AND time_to_day(t.time) < TODAY" 
    query_day2 = f"convert('date', p.Day, '%B') IN ({month_list_str}) AND convert('date', p.Day, '%Y') = {year_data}" 
    
    query = f"""
       SELECT DISTINCT
            to_int(convert('date', p.day, '%d')) 'day',
            convert('date', p.day, '%B') 'month',
            convert('date', p.day, '%Y') 'year',
            p.insaddr,
            p.settle
        INTO
            price_use
        FROM
            price p, instrument i
        WHERE
            i.insaddr = p.insaddr AND
            DISPLAY_ID(p, 'ptynbr') LIKE 'EOD_MtM' AND
            DISPLAY_ID(p, 'curr') = 'IDR' AND
            p.historical = 'yes' AND
            i.instype = 'curr' AND
            convert('date', p.day, '%Y') = '2024'

        SELECT 
            p.month, MAX(p.day) 'day'
        INTO
            last_day_price 
        FROM 
            price_use p
        GROUP BY
            p.month

        SELECT 
            p.month, p.year, p.insaddr, p.settle
        INTO
            used_price
        FROM 
            price_use p, last_day_price d
        WHERE
            p.day = d.day AND
            p.month = d.month

    SELECT DISTINCT
        t.trdnbr,
        convert('date', t.time, '%B') 'month',
        convert('date', t.time, '%Y') 'year',
        time_to_day(t.time + 25200) 'trade_date',
        i.instype 'instype',
        to_string(DISPLAY_ID(t, 'optkey3_chlnbr'), '|', DISPLAY_ID(t, 'optkey4_chlnbr')) 'status_product',
        DISPLAY_ID(t, 'curr') 'ccy',
        (DISPLAY_ID(t, 'curr') = 'IDR' ? 1 : p.settle) * abs(i.instype IN ('BasketRepo/Reverse', 'Deposit') ? t.premium : t.quantity * i.contr_size ) 'amount'
    INTO
        used_data
    FROM 
        trade t,
        instrument i,
        used_price p
    WHERE
        t.insaddr = i.insaddr AND
        t.curr *= p.insaddr AND
        convert('date', t.time, '%B') *= p.month AND
        {query_day} AND
        t.status = 'BO-BO Confirmed' AND
        t.category = 'None' AND
        NOT (i.instype = 'DEPOSIT' and DISPLAY_ID(t, 'optkey3_chlnbr') = 'SP')

    SELECT
        month,
        sum(status_product IN ('NOST|NTRF') ? 1 : 0) 'Replenishment (C)',
        sum(instype IN ('Commodity', 'Curr') and status_product NOT IN ('NOST|NTRF') ? 1 : 0) 'FX (C)',
        sum(instype IN ('Deposit') ? 1 : 0) 'MM (C)',
        sum(instype IN ('Bill', 'Bond', 'FRN', 'Fund', 'MBS/ABS') ? 1 : 0) 'Bonds (C)',
        sum(instype IN ('BasketRepo/Reverse') ? 1 : 0) 'Repo (C)',
        sum(instype IN ('Option', 'Swap', 'CurrSwap', 'Future/Forward') ? 1 : 0) 'Derivative (C)',
        sum(status_product IN ('NOST|NTRF') ? amount : 0) 'Replenishment (S)',
        sum(instype IN ('Commodity', 'Curr') and status_product NOT IN ('NOST|NTRF') ? amount : 0) 'FX (S)',
        sum(instype IN ('Deposit') ? amount : 0) 'MM (S)',
        sum(instype IN ('Bill', 'Bond', 'FRN', 'Fund') ? amount : 0) 'Bonds (S)',
        sum(instype IN ('BasketRepo/Reverse') ? amount : 0) 'Repo (S)',
        sum(instype IN ('Option', 'Swap', 'CurrSwap', 'Future/Forward') ? amount : 0) 'Derivative (S)'
    FROM 
        used_data
    GROUP BY
        month    
    UNION
    SELECT
        year,
        sum(instype IN ('Replenishment') ? 1 : 0),
        sum(instype IN ('Commodity', 'Curr') ? 1 : 0),
        sum(instype IN ('Deposit') ? 1 : 0),
        sum(instype IN ('Bill', 'Bond', 'FRN', 'Fund') ? 1 : 0),
        sum(instype IN ('BasketRepo/Reverse') ? 1 : 0),
        sum(instype IN ('Option', 'Swap', 'CurrSwap', 'Future/Forward') ? 1 : 0),
        sum(instype IN ('Replenishment') ? amount : 0),
        sum(instype IN ('Commodity', 'Curr') ? amount : 0),
        sum(instype IN ('Deposit') ? amount : 0),
        sum(instype IN ('Bill', 'Bond', 'FRN', 'Fund') ? amount : 0),
        sum(instype IN ('BasketRepo/Reverse') ? amount : 0),
        sum(instype IN ('Option', 'Swap', 'CurrSwap', 'Future/Forward') ? amount : 0)
    FROM 
        used_data
    GROUP BY
        year
    """
    result_query = ael.asql(query)[1][0] + ael.asql(query)[1][1]
    #print(query)
    return result_query

def list_to_dict(from_month, to_month, result_query):
    list_month = list(calendar.month_name)
    from_month_i, to_month_i = list_month.index(from_month), list_month.index(to_month)
    
    dict_data = {}
    for month in list_month[from_month_i : to_month_i + 1] : 
        dict_data[month] = [0] * 12
    
    for result in result_query :
        val_list = list(result[1:])
        
        dict_data[result[0]] = val_list
        
    return dict_data

###################################################################################################################################
# REPORT TEMPLATE XLS
###################################################################################################################################
def html_header(html_gen, html_content):
    header_list = ["YEAR", "MONTH", "FREQUENCY", "VOLUME"]
    subheader_list = ["Replenishment", "FX", "MM", "Bonds", "Repo", "Derivative"] * 2
    
    html_content += "<tr>"
    for i, header in enumerate(header_list) :
        span = 'rowspan="2" ' if i < 2 else 'colspan="6" '
        style = f"style = 'font-weight : bold; background-color: {'#83C2DE' if i < 3 else '#FF73CB'}'"
        html_content = html_gen.add_cell_data(html_content, header, span + style)
    html_content += "</tr>"
    
    html_content += "<tr>"
    for i, subheader in enumerate(subheader_list) :
        style = f"style = 'font-weight : bold; width : 800px; background-color: {'#83C2DE' if i < 6 else '#FF73CB'}'"
        html_content = html_gen.add_cell_data(html_content, subheader, style)
    html_content += "</tr>"
    
    return html_content

def prepare_template_xls(title, data_dict, file_path, year_data):
    html_gen = HTMLGenerator()
    
    html_content = html_gen.create_base_html_content(title) + "<table>"
    html_content = html_header(html_gen, html_content)
    
    total_month = len(list(data_dict.keys())) - 1
    
    data_total = []
    for i, (month, list_data) in enumerate(data_dict.items()):
        html_content += "<tr>"
        
        if i == 0 :
                html_content = html_gen.add_cell_data(html_content, year_data, f"rowspan='{total_month}' style='background-color: #8FD6F5; font-weight: bold'")
        
        if i != total_month:
            html_content = html_gen.add_cell_data(html_content, month.upper())
        else : 
            html_content = html_gen.add_cell_data(html_content, "Total " + month, "colspan='2' style='font-weight:bold'")
        
        for j, data in enumerate(list_data):
            val = f"{int(data):.0f}" if j > 5 else int(data)
            
            if j > 5 :
                if i != total_month :
                    html_content = html_gen.add_cell_data(html_content, locale.format('%d', int(val), 1), 'style="text-align: right"')
                else :
                    html_content = html_gen.add_cell_data(html_content, locale.format('%d', int(val), 1), 'style="text-align: right; font-weight:bold"')
            else :
                if i != total_month :
                    html_content = html_gen.add_cell_data(html_content, locale.format('%d', int(val), 1))
                else :
                    html_content = html_gen.add_cell_data(html_content, locale.format('%d', int(val), 1), 'style="font-weight:bold"')
        
        html_content += "</tr>"
    
    html_content += "</table>"
    
    today_date = date.today().strftime("%Y%m%d")
    html_file = html_gen.create_html_file(html_content, file_path, title, today_date, True, True)
    
    f = open(html_file.replace(".html", ".xls"), "w")
    f.write(html_content)
    f.close()
    return html_file

###################################################################################################################################
# TASK TO RUN REPORT ON GUI
###################################################################################################################################

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BO54 - Monthly Report'}

year_list = [datetime.now().year - x for x in range(25)]
list_month = list(calendar.month_name)
month_now = list_month[datetime.now().month]

ael_variables=[
['report_name', 'Report Name', 'string', None, 'BO54 - Monthly Report', 1,0],
['year', 'Year', 'string', year_list, year_list[0], 1,0],
['month_from', 'From (Start Month)', 'string', list_month[1:], list_month[1], 1,0],
['month_to', 'To (End Month)', 'string', list_month[1:], month_now, 1, 0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls', 1, 1, 'Select Secondary Extensions Output']
]

def ael_main(parameter) :
    xsl_gen = XSLFOGenerator()
    report_name = str(parameter['report_name'])
    year_data = str(parameter['year'])
    month_from = str(parameter['month_from'])
    month_to = str(parameter['month_to'])
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    
    result_query = run_query_asql(year_data, month_from, month_to)    
    dict_data = list_to_dict(month_from, month_to, result_query)
    
    for ext in output_file:
        if ext == ".xls" :
            prepare_template_xls(report_name, dict_data, file_path, year_data)
            



