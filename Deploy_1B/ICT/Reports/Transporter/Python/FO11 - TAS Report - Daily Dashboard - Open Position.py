from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from Report_Python import get_cross_rate
from Report_Python import usd_price_mtm, idr_price_mtm

import ael
import acm,csv
from datetime import datetime, timedelta

from itertools import groupby

def get_ins_num(insid):
    instrument = acm.FInstrument[insid]
    return instrument.Oid()

def get_ins_name(insid):
    instrument = acm.FInstrument[insid]
    return instrument.Name()
    

def get_optkey3_oid(optkey_string):
    optkey = acm.FChoiceList.Select('list=Product Type')
    for name in optkey:
        if name.Name()== optkey_string:
            return name.Oid()

def get_optkey4_oid(optkey_string):
    optkey = acm.FChoiceList.Select('list=Category')
    for name in optkey:
        if name.Name()== optkey_string:
            return name.Oid()

def get_ctype_name(free2_oid):
    all_ctype = acm.FChoiceList.Select('list = Customer Type')
    for each_ctype in all_ctype:
        if each_ctype.Oid()== free2_oid:
            return each_ctype.Name()
            
def get_top10_count(trades,date):
    counterparty_totals = {}
    for transaction in trades:
        counterparty_name = transaction['counterparty']
        currency = transaction['currency']
        if currency == "USD":
            quantity_usd = transaction['quantity']
        else:
            quantity_usd = get_cross_rate(currency,date)*transaction['quantity'] 
        
        if counterparty_name not in counterparty_totals:
            counterparty_totals[counterparty_name] = 0
        
        counterparty_totals[counterparty_name] += quantity_usd

    sorted_counterparties = sorted(counterparty_totals.items(), key=lambda x: x[1], reverse=True)
    return sorted_counterparties[:10]
    
def scrap_csv_openpos(csvpath,csvname):
    with open(csvpath+"\\"+csvname+".csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)
        
    return data

    
    
html_gen = HTMLGenerator()

div_side_by_side = '<tr>'

end_div_side_by_side = '</tr>'

additional_style = """

.bold-with-border {

    border: 3px solid black;

    font-weight: bold;

    border-collapse: collapse;

}

.bold {

    font-weight: bold;

}

table {

        margin-left: 10px;

    }

    

#marktra {

    padding: 0px 20px 0px 20px;

    width: 100%;

    margin: 0px 0px 20px 50px;

    font-size: 24pt;

    font-size: 24pt;

    font-weight: bold;

}

"""

CALENDAR = acm.FCalendar["Jakarta"]
today = acm.Time.DateToday()


def prepare_open_position1_table(html_content, date,prev_op):
    
    
    currencypair = ['AUD/USD', 'EUR/USD', 'GBP/USD','USD/JPY','USD/CHF','NZD/USD','USD/IDR']
    
    row_name = []    
    no = 0
    
    open_pos_tod = {}
    
    egan = ['EUR','GBP','AUD','NZD']
    
    for each_curr_pair_usd in currencypair:
        curr1 = each_curr_pair_usd.split('/')[0]
        curr2 = each_curr_pair_usd.split('/')[1]
        if curr1 == 'USD':
            main_curr = curr2
        else:
            main_curr = curr1
        
        net_amount = 0
        
        rawdata = acm.FStoredASQLQuery['Marktra_Open_Position_2']
        
        for each_trade in rawdata.Query().Select():
            trade_curr1 = each_trade.Instrument().Name()
            trade_curr2 = each_trade.Currency().Name()
            quantity = each_trade.Quantity()
            premium = each_trade.Premium()
            
            if trade_curr1 in egan and trade_curr2 in egan:
                if main_curr == trade_curr1:
                    net_amount += quantity
                    
                elif main_curr == trade_curr2:
                    net_amount += premium
                
                else:
                    net_amount += 0
            
            elif trade_curr1 in egan and trade_curr2 not in egan:
                if quantity < 0:
                
                    if main_curr == trade_curr1:
                        net_amount += abs(quantity)*-1
                        
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)*-1
                        
                elif quantity > 0:
                    
                    if main_curr == trade_curr1:
                        net_amount += abs(quantity)
                    
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)
                    
            
            elif trade_curr1 not in egan and trade_curr2 not in egan:
                if quantity < 0:
                    if main_curr == trade_curr1:
                        net_amount += abs(get_cross_rate(trade_curr1,date)*quantity)
                    elif main_curr == trade_curr2:
                        net_amount +=abs(get_cross_rate(trade_curr2,date)*premium)*-1
                        
                elif quantity > 0:
                    if main_curr == trade_curr1:
                        net_amount += abs(get_cross_rate(trade_curr1,date)*quantity)*-1
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)
        
        open_pos_tod[each_curr_pair_usd] = net_amount
        
        for each_op in prev_op:
            if each_op[0] == each_curr_pair_usd:
                open_pos_tod[each_curr_pair_usd] += float(each_op[1])
        
            
        no+=1
        row_name.append([no,each_curr_pair_usd,f"{round(open_pos_tod[each_curr_pair_usd],2):,}"])
        
        
    col_name = ["No", "CCY Pair", "Amount"]
    html_content += "<td style='border:0px;' colspan='3'>"
    html_content = html_gen.prepare_html_table(html_content, col_name)
    html_content += "<caption style='font-weight:bold;'>Open Position 1</caption>"
    html_content = html_gen.add_data_row(html_content, row_name)
    html_content = html_gen.close_html_table(html_content)
    html_content += "</td>"
    html_content += "<td style='border:0px;'>"
    html_content += "</td>"
    return html_content

def prepare_open_position2_table(html_content, date,prev_op):
    currencypair = ['USD/SGD', 'USD/CAD', 'USD/HKD', 'USD/SAR', 'USD/MYR', 'USD/THB', 'USD/CNY', 'USD/NOK', 'USD/SEK', 'USD/DKK']
    row_name = []    
    no = 0
    open_pos_tod = {}
    egan = ['EUR','GBP','AUD','NZD']
    
    for each_curr_pair_usd in currencypair:
        curr1 = each_curr_pair_usd.split('/')[0]
        curr2 = each_curr_pair_usd.split('/')[1]
        if curr1 == 'USD':
            main_curr = curr2
        else:
            main_curr = curr1
        
        net_amount = 0
        
        rawdata = acm.FStoredASQLQuery['Marktra_Open_Position_2']
        
        for each_trade in rawdata.Query().Select():
            trade_curr1 = each_trade.Instrument().Name()
            trade_curr2 = each_trade.Currency().Name()
            quantity = each_trade.Quantity()
            premium = each_trade.Premium()
            
            if trade_curr1 in egan and trade_curr2 in egan:
                if main_curr == trade_curr1:
                    net_amount += quantity
                    
                elif main_curr == trade_curr2:
                    net_amount += premium
                
                else:
                    net_amount += 0
            
            elif trade_curr1 in egan and trade_curr2 not in egan:
                if quantity < 0:
                
                    if main_curr == trade_curr1:
                        net_amount += abs(quantity)*-1
                        
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)*-1
                        
                elif quantity > 0:
                    
                    if main_curr == trade_curr1:
                        net_amount += abs(quantity)
                    
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)
                    
            
            elif trade_curr1 not in egan and trade_curr2 not in egan:
                if quantity < 0:
                    if main_curr == trade_curr1:
                        net_amount += abs(get_cross_rate(trade_curr1,date)*quantity)
                    elif main_curr == trade_curr2:
                        net_amount +=abs(get_cross_rate(trade_curr2,date)*premium)*-1
                        
                elif quantity > 0:
                    if main_curr == trade_curr1:
                        net_amount += abs(get_cross_rate(trade_curr1,date)*quantity)*-1
                    elif main_curr == trade_curr2:
                        net_amount += abs(get_cross_rate(trade_curr2,date)*premium)
            
            
        open_pos_tod[each_curr_pair_usd] = net_amount
        
        for each_op in prev_op:
            if each_op[0] == each_curr_pair_usd:
                open_pos_tod[each_curr_pair_usd] += float(each_op[1])
        
            
        no+=1
        row_name.append([no,each_curr_pair_usd,f"{round(open_pos_tod[each_curr_pair_usd],2):,}"])
    
    col_name = ["No", "CCY Pair", "Amount"]
    html_content += "<td style='border:0px;' colspan='3'>"
    html_content = html_gen.prepare_html_table(html_content, col_name)
    html_content += "<caption style='font-weight:bold;'>Open Position 2</caption>"
    html_content = html_gen.add_data_row(html_content, row_name)
    html_content = html_gen.close_html_table(html_content)
    html_content += "</td>"
    return html_content

def prepare_marktra_html_title(html_content):
    html_content += div_side_by_side
    html_content += "<td style='border:0px;'>"

    col_name = ["Tanggal Hari ini"]
    html_content = html_gen.prepare_html_table(html_content, col_name, row_style="style='background-color: blue'", header_style="style='color:white'")
    
    row_data = [[get_current_date("/")]]
    html_content = html_gen.add_data_row(html_content, row_data, row_class="style='background-color: lightblue'")
    html_content = html_gen.close_html_table(html_content)
    
    html_content += "</td>"
    
    html_content += "<td style='border:0px;'></td><td style='border:0px;'></td>"
    html_content += "<td id='marktra' colspan='10' rowspan='2' style='text-align:center'>Dashboard Marktra</td>"
    html_content += end_div_side_by_side

    return html_content


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Marktra Generator'}
                    
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'Marktra Dashboard', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Output Files','string', ['.html', '.xls'], '.html',0,1, 'Select Output Extension Type'],
['date','Date','string',None,acm.Time.DateToday(),0,1]
] 

def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    
    date = parameter['date'][0]
    total_nasabah_jual_valas = 0
    total_nasabah_beli_valas = 0
    
    
    open_pos_data = scrap_csv_openpos(file_path,"openpos")
    
    html_content = html_gen.create_base_html_content("", additional_styles=additional_style)

    html_content += "<table>"

    html_content += prepare_marktra_html_title(html_content)

    html_content += "<tr></tr><tr></tr>"

    html_content = prepare_open_position1_table(html_content, date,open_pos_data)

    html_content = prepare_open_position2_table(html_content, date,open_pos_data)

    html_content += end_div_side_by_side

    html_content += "</table>"

    current_hour = get_current_hour("")
    current_date = get_current_date("")

    folder_with_file_name = True

    if report_name == "":

        folder_with_file_name = True

    

    if '.html' in output_file:

        open_html = True

    else:

        open_html = False

    file_url = html_gen.create_html_file(html_content, file_path, report_name+' '+current_date+current_hour, current_date, open_html=open_html)

    

    if '.xls' in output_file:

        generate_file_for_other_extension(file_url , ".xls")

    else:

        pass

