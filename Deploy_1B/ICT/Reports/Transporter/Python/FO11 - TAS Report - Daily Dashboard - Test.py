from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from Report_Python import get_cross_rate
import ael,acm,csv,math
from datetime import datetime, timedelta


current_date = get_current_date("")
current_hour = get_current_hour("")
date_today = acm.Time.DateToday()
date,month,year = current_date[:2],current_date[2:4],current_date[4:]


qf_list = [
            'Marktra_Buy_Valas',
            'Marktra_Sell_Valas',
            'Marktra_Non_IDR_Query',
            'Marktra_MDS_Query',
            'Marktra_Swap_Query',
            'Marktra_FX_Tod_Query',
            'Marktra_FX_Tom_Query',
            'Marktra_FX_Spot_Query',
            'Marktra_Fwd_7Days',
            'Marktra_Fwd_7To14Days',
            'Marktra_Fwd_14To30Days',
            'Marktra_Fwd_30To90Days',
            'Marktra_Fwd_90Days',
            'Marktra_Banknotes_Volume',
            'Marktra_Retail_Volume',
            'Marktra_Wholesale_Volume'
            ]
            
qf_list_top10 = [
                'Marktra_Top10_Buy',
                'Marktra_Top10_Sell'
                ]
qf_list_op = [
                'Marktra_Open_Position_1',
                'Marktra_Open_Position_2'
            ]
        
def scrap_csv(csvpath,csvname):
    with open(csvpath+"\\report"+year+month+date+"\\"+csvname+".csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        for _ in range(9):
            next(reader)
        
        # Read the remaining lines into a list
        data = list(reader)
    return data
    

def get_items(data,today):
    mapped_item = {}
    current_category = None
    
    for each_item in data:
        if each_item[0] in qf_list:
            current_category = each_item[0]
            mapped_item[current_category] = 0
            
        if current_category is not None:                    
            if each_item[1]:
                try:
                    volume = abs(float(each_item[1]))
                    curr = each_item[2]
                    if curr == "USD":
                        mapped_item[current_category] += volume
                    else:
                        try:
                            eqv_usd = volume * get_cross_rate(curr,today)
                            mapped_item[current_category] += abs(eqv_usd)
                        except:
                            print("There are no rate for Currency ", each_item[2],"/ USD in ",today)
                        
                except KeyError:
                    mapped_item[current_category] = 0
            
                    
    return mapped_item
    
def get_top10(data,today):
    top10_item = {}
    current_counterparty = None
    current_category = None
    
    for each_item in data:
        if each_item[0] in qf_list_top10:
            current_category = each_item[0]
            continue
        
        if each_item[1] == '' and each_item[2] == '' and current_category is not None:
            current_counterparty = each_item[0]
            top10_item[current_category + " - " + current_counterparty] = 0
        
        if current_counterparty is not None and current_category is not None and each_item[1] and each_item[2]:
            try:
                volume = abs(float(each_item[1]))
                curr = each_item[2]
                if curr == "USD":
                    top10_item[current_category + " - " + current_counterparty] += abs(volume)
                else:
                    try:
                        eqv_usd = volume * get_cross_rate(curr,today)
                        top10_item[current_category + " - " + current_counterparty] += abs(eqv_usd)
                    except:
                        print("There are no rate for Currency ", each_item[2],"/ USD in ",today)
            except KeyError:
                top10_item[current_category + " - " + current_counterparty] = 0
    
    sorted_counterparties = sorted(top10_item.items(), key=lambda x: x[1], reverse=True)
    return sorted_counterparties[:10]


def get_average_rate(data):
    category = [
                'Marktra_Average_Buy',
                'Marktra_Average_Sell'
                ]
    mapped_rate = {}
    sum_price_buy = 0
    sum_price_sell = 0
    count_price_buy = 0
    count_price_sell = 0
    current_rate = None
    
    for each_data in data:
        if each_data[0] in category:
            current_rate = each_data[0]
            mapped_rate[current_rate] = 0
        
        if current_rate is not None:
            if "Average_Buy" in current_rate:
                if each_data[3]:
                    try:
                        sum_price_buy += float(each_data[3])
                        count_price_buy += 1
                    except KeyError:
                        sum_price_buy += 0
                else:
                    sum_price_buy += 0
                    
            elif "Average_Sell" in current_rate:
                if each_data[3]:
                    try:
                        sum_price_sell += float(each_data[3])
                        count_price_sell += 1
                    except KeyError:
                        sum_price_sell += 0
                else:
                   sum_price_sell += 0
    
    
    if count_price_buy > 0:
        mapped_rate['Marktra_Average_Buy'] = sum_price_buy/count_price_buy
    else:
        mapped_rate['Marktra_Average_Buy'] = 0
    if count_price_sell > 0:
        mapped_rate['Marktra_Average_Sell'] = sum_price_sell/count_price_sell
    else:
        mapped_rate['Marktra_Average_Sell'] = 0
    
    return mapped_rate



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

def prepare_sum_vol_1_table(html_content,result_dict):
    
    row_name = [["Jual-Beli Non IDR", result_dict["Non IDR"]], ["MDS", result_dict["MDS"]], ["Nasabah Beli Valas", result_dict["Valas Beli"]], ["Nasabah Jual Valas", result_dict["Valas Jual"]], ["Swap", result_dict["Swap"]], ["Grand Total", result_dict["Sum of Vol 1"]]]

    col_name = ["", "Sum of VOL(USD)"]

    

    html_content += "<td style='border:0px;' colspan='2'>"

    

    html_content = html_gen.prepare_html_table(html_content, col_name)

    html_content = html_gen.add_data_row(html_content, row_name)

    html_content = html_gen.close_html_table(html_content)

    html_content += "</td>"

    html_content += "<td style='border:0px;'></td>"

    

    return html_content

    

def prepare_sum_vol_2_table(html_content, result_dict):
    row_name = [["Banknotes", result_dict["Banknotes"]], ["Retail", result_dict["Retail"]], ["Wholesale", result_dict["Wholesale"]], ["Grand Total", result_dict["Sum of Vol 2"]]]

    col_name = ["", "Sum of VOL(USD)"]

    html_content += "<td style='border:0px;' colspan='2'>"

    html_content = html_gen.prepare_html_table(html_content, col_name)

    html_content = html_gen.add_data_row(html_content, row_name)

    html_content = html_gen.close_html_table(html_content)

    html_content += "</td>"

    html_content += "<td style='border:0px;'></td>"

    return html_content


def prepare_nasabah_jual_table(html_content, date,top10_sell):
    row_name=[]
    count = 1
    for each_item in top10_sell:
        if 'Sell' in each_item[0]:
            cpty_name = each_item[0].split("Sell - ")[1]
            row_name.append([count,cpty_name,f"{float(each_item[1]):,}"])
            count+=1
        
    col_name = ["No", "Nasabah Jual", "Volume Amount"]

    html_content += "<td style='border:0px;' colspan='3'>"

    html_content = html_gen.prepare_html_table(html_content, col_name)

    html_content = html_gen.add_data_row(html_content, row_name)

    html_content = html_gen.close_html_table(html_content)

    html_content += "</td>"

    html_content += "<td style='border:0px;'></td>"

    return html_content

    
#NASABAH CODE 
def prepare_nasabah_beli_table(html_content, date,top10_buy):
    row_name=[]
    count = 1
    for each_item in top10_buy:
        if 'Buy' in each_item[0]:
            cpty_name = each_item[0].split("Buy - ")[1]
            row_name.append([count,cpty_name,f"{float(each_item[1]):,}"])
            count+=1

    col_name = ["No", "Nasabah Beli", "Volume Amount"]

    html_content += "<td style='border:0px;' colspan='3'>"

    html_content = html_gen.prepare_html_table(html_content, col_name)

    html_content = html_gen.add_data_row(html_content, row_name)

    html_content = html_gen.close_html_table(html_content)

    html_content += "</td>"

    

    return html_content

    

def prepare_average_rate(html_content, result_dict):

    row_name = [["P", result_dict["Average Buy"]], ["S", result_dict["Average Sell"]]]

    col_name = ["P/S", "Average Rate"]

    

    html_content += "<td style='border:0px;' colspan='2'>"

    html_content = html_gen.prepare_html_table(html_content, col_name)

    html_content = html_gen.add_data_row(html_content, row_name)

    

    spread_row = [["Spread", result_dict['Spread']]]

    html_content = html_gen.add_data_row(html_content, spread_row, "class='bold-with-border'")

    html_content = html_gen.close_html_table(html_content)

    html_content += "</td>"

    html_content += "<td style='border:0px;'>"

    html_content += "</td>"

    return html_content

    

def prepare_sum_open_table(html_content, result_dict):
    row_name = [["1. Today", result_dict["TOD"]], ["2. Tom", result_dict["TOM"]], ["3. Spot++", result_dict["SPOT ++"]]]

    col_name = ["", "Sum of OPEN"]

    

    html_content += "<td style='border:0px;' colspan='2'>"

    html_content = html_gen.prepare_html_table(html_content, col_name)

    html_content += "<br>"

    html_content = html_gen.add_data_row(html_content, row_name)

    

    open_position = [["Open Position", result_dict['sum_open_position']]]

    html_content = html_gen.add_data_row(html_content, open_position, "class='bold-with-border'")


    non_today_gapping = [["Non Today Gapping", result_dict['sum_non_today_gaping']]]

    html_content = html_gen.add_data_row(html_content, non_today_gapping, "class='bold-with-border'")

    html_content = html_gen.close_html_table(html_content)

    html_content += "</td>"

    html_content += "<td style='border:0px;'>"

    html_content += "</td>"

    return html_content

    

def prepare_outstanding_table(html_content, result_dict):
    row_name = [["1. < 7 days", result_dict["< 7 Days"]], ["2. 7 days - < 14 days", result_dict["7 - 14 Days"]], ["3. 14 days - < 30 days", result_dict["14 - 30 Days"]], ["4. 30 days - < 90 days", result_dict["30 - 90 Days"]], ["5. >= 90 days", result_dict[">= 90 Days"]], ["Grand Total", result_dict["Outstanding Total"]]]

    col_name = ["Row Labels", "Sum of AMOUNT"]

    html_content += "<td style='border:0px;' colspan='2'>"

    html_content = html_gen.prepare_html_table(html_content, col_name)

    html_content += "<caption style='font-weight:bold;'>Outstanding Nasabah Buy Sell Forward</caption>"

    html_content = html_gen.add_data_row(html_content, row_name)

    html_content = html_gen.close_html_table(html_content)

    html_content += "</td>"

    html_content += "<td style='border:0px;'>"

    html_content += "</td>"

    return html_content

    


def prepare_open_position1_table(html_content, date):
    
    
    currencypair = ['AUD/USD', 'EUR/USD', 'GBP/USD','USD/JPY','USD/CHF','NZD/USD','USD/IDR']
    
    row_name = []    
    no = 0
    
    
    
    egan = ['EUR','GBP','AUD','NZD']
    for each_curr_pair_usd in currencypair:
        curr1 = each_curr_pair_usd.split('/')[0]
        curr2 = each_curr_pair_usd.split('/')[1]
        if curr1 == 'USD':
            main_curr = curr2
        else:
            main_curr = curr1
        
        net_amount = 0
        
        alltime_query = ael.asql(f"""
                            SELECT t.quantity,display_id(t,'insaddr'),t.trdnbr,display_id(t,'curr'),t.premium
                            FROM trade t,portfolio p where display_id(t,'optkey3_chlnbr') = 'FX'
                            AND display_id(t,'optkey4_chlnbr') IN ('TOD','TOM','SPOT','FWD')
                            AND t.prfnbr = p.prfnbr and p.prfid = 'Marktra'
                            AND (display_id(t,'insaddr') = '{main_curr}'
                            or display_id(t,'curr') = '{main_curr}')
                            """)
       
        
        for each_trade in alltime_query[1][0]:
            trade_curr1 = each_trade[1]
            trade_curr2 = each_trade[3]
            quantity = each_trade[0]
            premium = each_trade[4]
            
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
                        
                        
            
        no+=1
        row_name.append([no,each_curr_pair_usd,f"{round(net_amount,2):,}"])
        
        
    row_name.append(['','',''])
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

def prepare_open_position2_table(html_content, date):
    currencypair = ['USD/SGD', 'USD/CAD', 'USD/HKD', 'USD/SAR', 'USD/MYR', 'USD/THB', 'USD/CNY', 'USD/NOK', 'USD/SEK', 'USD/DKK']
    row_name = []    
    no = 0
    
    egan = ['EUR','GBP','AUD','NZD']
    for each_curr_pair_usd in currencypair:
        curr1 = each_curr_pair_usd.split('/')[0]
        curr2 = each_curr_pair_usd.split('/')[1]
        if curr1 == 'USD':
            main_curr = curr2
        else:
            main_curr = curr1
        
        net_amount = 0
        
        alltime_query = ael.asql(f"""
                            SELECT t.quantity,display_id(t,'insaddr'),t.trdnbr,display_id(t,'curr'),t.premium
                            FROM trade t,portfolio p where display_id(t,'optkey3_chlnbr') = 'FX'
                            AND display_id(t,'optkey4_chlnbr') IN ('TOD','TOM','SPOT','FWD')
                            AND t.prfnbr = p.prfnbr and p.prfid = 'TESTINGLIQ18'
                            AND (display_id(t,'insaddr') = '{main_curr}'
                            or display_id(t,'curr') = '{main_curr}')
                            """)
                            
        for each_trade in alltime_query[1][0]:
            trade_curr1 = each_trade[1]
            trade_curr2 = each_trade[3]
            quantity = each_trade[0]
            premium = each_trade[4]
            
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
            
            
        
            
                
        no+=1
        row_name.append([no,each_curr_pair_usd,f"{round(net_amount,2):,}"])
    
    row_name.append(['','',''])
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


def filter_trade_by_date(date,data,rate):
    
    non_idr_result = 0
    mds_result = 0
    valas_beli_result = 0
    valas_jual_result = 0
    swap_result = 0
    fx_buy = 0
    fx_sell = 0
    fx_buy_count = 0
    fx_sell_count = 0
    banknotes_vol = 0
    retail_vol = 0
    wholesale_vol = 0
    open_tod = 0
    open_tom = 0
    open_spot = 0
    outstanding_1 = 0
    outstanding_2 = 0
    outstanding_3 = 0
    outstanding_4 = 0
    outstanding_5 = 0
    sum_non_today_gaping = 0
    sum_open_position = 0
    average_buy_value = 0
    average_sell_value = 0
    

    
    valas_beli_result=data['Marktra_Buy_Valas']
    valas_jual_result=data['Marktra_Sell_Valas']
    non_idr_result = data['Marktra_Non_IDR_Query']
    mds_result = data['Marktra_MDS_Query']
    swap_result = data['Marktra_Swap_Query']
    open_tod = data['Marktra_FX_Tod_Query']
    open_tom = data['Marktra_FX_Tom_Query']
    open_spot = data['Marktra_FX_Spot_Query']
    outstanding_1 = data['Marktra_Fwd_7Days']
    outstanding_2 = data['Marktra_Fwd_7To14Days']
    outstanding_3 = data['Marktra_Fwd_14To30Days']
    outstanding_4 = data['Marktra_Fwd_30To90Days']
    outstanding_5 = data['Marktra_Fwd_90Days']
    banknotes_vol=data['Marktra_Banknotes_Volume']
    retail_vol=data['Marktra_Retail_Volume']
    wholesale_vol=data['Marktra_Wholesale_Volume']
    
    
    
    sum_open_position = open_tod + open_tom + open_spot
    
    sum_non_today_gaping = open_tom + open_spot
    
    sum_of_vol_1 = non_idr_result + mds_result + valas_beli_result + valas_jual_result + swap_result
    sum_of_vol_2 = banknotes_vol + retail_vol + wholesale_vol
    
    
    
    average_buy_value=rate['Marktra_Average_Buy']
    average_sell_value=rate['Marktra_Average_Sell']
    
    spread_value = f"{round(abs(average_buy_value - average_sell_value),2):,}"
    
    outstanding_total = outstanding_1 + outstanding_2 + outstanding_3 + outstanding_4 + outstanding_5
    result_dict = {
        "Non IDR" : f"{round(non_idr_result,2):,}",
        "MDS" : f"{round(mds_result,2):,}",
        "Valas Beli" : f"{round(valas_beli_result,2):,}",
        "Valas Jual" : f"{round(valas_jual_result,2):,}",
        "Swap" : f"{swap_result:,}",
        "Sum of Vol 1" : f"{round(sum_of_vol_1,2):,}",
        "Banknotes" : f"{round(banknotes_vol,2):,}",
        "Retail" : f"{round(retail_vol,2):,}",
        "Wholesale" : f"{round(wholesale_vol,2):,}",
        "Sum of Vol 2" : f"{round(sum_of_vol_2,2):,}",
        "Average Buy" : f"{average_buy_value:,}",
        "Average Sell" : f"{average_sell_value:,}",
        "Spread" : spread_value,
        "TOD"  : f"{round(open_tod,2):,}",
        "TOM"  : f"{round(open_tom,2):,}",
        "SPOT ++"  : f"{round(open_spot,2):,}",
        "< 7 Days" : f"{round(outstanding_1,2):,}",
        "7 - 14 Days" : f"{round(outstanding_2,2):,}",
        "14 - 30 Days" : f"{round(outstanding_3,2):,}",
        "30 - 90 Days" : f"{round(outstanding_4,2):,}",
        ">= 90 Days" : f"{round(outstanding_5,2):,}",
        'sum_open_position' : f"{round(sum_open_position,2):,}",
        'sum_non_today_gaping' : f"{round(sum_non_today_gaping,2):,}",
        "Outstanding Total" : f"{round(outstanding_total,2):,}",
    }

    return result_dict

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Marktra Generator'}
                    
#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'Marktra Dashboard', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['csv_name','CSV File Name','string',None,'FO11 - Volume',1,0], 
['csv_name_cpty','CSV File Name','string',None,'FO11 - Counterparty',1,0],
['output_file','Output Files','string', ['.html', '.xls'], '.html',0,1, 'Select Output Extension Type'],
['date','Date','string',None,acm.Time.DateToday(),0,1]
] 

def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    csvname = parameter['csv_name']
    csvname_cpty = parameter['csv_name_cpty']
    
    date = parameter['date'][0]
    total_nasabah_jual_valas = 0
    total_nasabah_beli_valas = 0
    
    all_data_volume = scrap_csv(file_path,csvname)
    all_volume = get_items(all_data_volume,date)
     
    
    all_data_cpty = scrap_csv(file_path,csvname_cpty)
    all_top10 = get_top10(all_data_cpty,date)
    
    
    rate_data = get_average_rate(all_data_volume)
    
    
    
    result_dict = filter_trade_by_date(date,all_volume,rate_data)
    
    html_content = html_gen.create_base_html_content("", additional_styles=additional_style)

    html_content += "<table>"

    html_content += prepare_marktra_html_title(html_content)

    html_content += "<tr></tr><tr></tr>"

    html_content += div_side_by_side

    html_content = prepare_sum_vol_1_table(html_content, result_dict)

    html_content = prepare_sum_vol_2_table(html_content, result_dict)

    html_content = prepare_nasabah_jual_table(html_content, date,all_top10)

    html_content = prepare_nasabah_beli_table(html_content, date,all_top10)

    html_content += end_div_side_by_side

    html_content += "<tr></tr>"

    html_content += "<tr>"

    html_content = prepare_average_rate(html_content, result_dict)

    html_content += "</tr>"

    html_content += "<tr></tr>"

    html_content += div_side_by_side

    html_content = prepare_sum_open_table(html_content, result_dict)

    html_content = prepare_outstanding_table(html_content, result_dict)

    html_content = prepare_open_position1_table(html_content, date)

    html_content = prepare_open_position2_table(html_content, date)

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

