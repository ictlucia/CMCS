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


def prepare_nasabah_jual_table(html_content, date):
    row_name=[]
    topsell_nasabah_query = ael.asql(f"""SELECT p.ptyid, abs(t.premium),t.curr,t.insaddr,abs(t.quantity)
                                FROM trade t, party p, portfolio pf 
                                WHERE t.prfnbr = pf.prfnbr and t.counterparty_ptynbr = p.ptynbr and 
                                (pf.prfid = 'Wholesale FX & Derivative BO' or pf.prfid='Wholesale FX Branch' or
                                pf.prfid = 'Retail FX BO' or pf.prfid='Retail FX Branch') AND t.quantity > 0 
                                AND t.time >='{str(date)}' and t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' 
                                AND t.optkey3_chlnbr='{str(get_optkey3_oid('FX'))}' AND display_id(t,'optkey4_chlnbr') IN 
                                ('TOD','TOM','SPOT','FWD') AND (t.status ~='Internal' and t.status~='Void')
                                AND display_id(t,'curr')='IDR' AND p.ptyid NOT LIKE '%CONSUMERCARD%' 
                                AND p.ptyid NOT LIKE '%MEBG%' ORDER BY 1 DESC
                                """)

    all_sell_nasabah=[]
    
    for row in topsell_nasabah_query[1][0]:
        counterparty,premium,currency,ins,quantity = row
        all_sell_nasabah.append({
            'counterparty':counterparty,
            'quantity':quantity,
            'currency':get_ins_name(ins)
        })
        
    top10_sell = get_top10_count(all_sell_nasabah,date)
    
    for i, pair in enumerate(top10_sell):
        row_name.append([i+1, pair[0], f"{round(pair[1],2):,}"])

    col_name = ["No", "Nasabah Jual", "Volume Amount"]

    html_content += "<td style='border:0px;' colspan='3'>"

    html_content = html_gen.prepare_html_table(html_content, col_name)

    html_content = html_gen.add_data_row(html_content, row_name)

    html_content = html_gen.close_html_table(html_content)

    html_content += "</td>"

    html_content += "<td style='border:0px;'></td>"

    return html_content

    
#NASABAH CODE 
def prepare_nasabah_beli_table(html_content, date):
    row_name=[]
    topbuy_nasabah_query = ael.asql(f"""SELECT p.ptyid, abs(t.premium),t.curr,t.insaddr,abs(t.quantity) FROM trade t, party p, portfolio pf 
                                WHERE t.prfnbr = pf.prfnbr and t.counterparty_ptynbr = p.ptynbr and 
                                (pf.prfid = 'Wholesale FX & Derivative BO' or pf.prfid='Wholesale FX Branch' or
                                pf.prfid = 'Retail FX BO' or pf.prfid='Retail FX Branch') AND t.quantity < 0 
                                AND t.time >='{str(date)}' and t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' 
                                AND t.optkey3_chlnbr='{str(get_optkey3_oid('FX'))}' AND display_id(t,'optkey4_chlnbr') IN 
                                ('TOD','TOM','SPOT','FWD') AND (t.status ~='Internal' and t.status~='Void')
                                AND display_id(t,'curr')='IDR' AND p.ptyid NOT LIKE '%CONSUMERCARD%' 
                                AND p.ptyid NOT LIKE '%MEBG%' ORDER BY 1 DESC
                                """)

    all_buy_nasabah=[]
    
    for row in topbuy_nasabah_query[1][0]:
        counterparty,premium,currency,ins,quantity = row
        all_buy_nasabah.append({
            'counterparty':counterparty,
            'quantity':quantity,
            'currency':get_ins_name(ins)
        })
            
    top10_buy = get_top10_count(all_buy_nasabah,date)
    
    for i, pair in enumerate(top10_buy):
        row_name.append([i+1, pair[0], f"{round(pair[1],2):,}"])

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

def get_USD_nominal(date, currpair, quantity):
    curr1 = currpair.Currency1()
    curr2 = currpair.Currency2()
    if curr1.Name() == 'USD':
        return quantity
    else:
        return quantity * curr1.MtMPrice(date, "USD")

def filter_trade_by_date(date):

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
    
    beli_jual_valas = ael.asql(f""" SELECT t.quantity, t.insaddr
                                FROM trade t, portfolio p WHERE
                                t.time >= '{str(date)}'
                                and t.time < '{acm.Time.DateAddDelta(date,0,0,1)}'
                                and t.curr = '{str(get_ins_num('IDR'))}'
                                AND t.prfnbr = p.prfnbr
                                AND display_id(t, 'optkey3_chlnbr') = 'FX'
                                AND (display_id(t, 'optkey4_chlnbr') = 'TOD' 
                                OR display_id(t, 'optkey4_chlnbr') = 'TOM'
                                OR display_id(t, 'optkey4_chlnbr') = 'SPOT'
                                OR display_id(t, 'optkey4_chlnbr') = 'FWD')
                                and (t.status ~='Internal' or t.status ~='Void')
                                AND (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                                """)
                                
    if len(beli_jual_valas[1][0])>0:
        for volume,curr in beli_jual_valas[1][0]:
            if get_ins_name(curr)== "USD":
                if volume < 0:
                    valas_beli_result+=abs(volume)
                else:
                    valas_jual_result+=abs(volume)
            else:
                if volume < 0:
                    valas_beli_result+=get_cross_rate(get_ins_name(curr),date)*abs(volume)
                else:
                    valas_jual_result+=get_cross_rate(get_ins_name(curr),date)*abs(volume)
    else:
        valas_beli_result =0
        valas_jual_result=0
    
    non_idr_query = ael.asql(f"""SELECT t.quantity, t.insaddr 
                            FROM trade t, portfolio p WHERE 
                            t.time >= '{str(date)}'
                            AND t.time < '{acm.Time.DateAddDelta(date,0,0,1)}'
                            AND t.insaddr ~='{str(get_ins_num('IDR'))}'
                            AND t.curr ~= '{str(get_ins_num('IDR'))}'
                            AND t.prfnbr = p.prfnbr
                            AND (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                            AND display_id(t, 'optkey3_chlnbr') = 'FX'
                            AND (display_id(t, 'optkey4_chlnbr') = 'TOD' 
                            OR display_id(t, 'optkey4_chlnbr') = 'TOM'
                            OR display_id(t, 'optkey4_chlnbr') = 'SPOT'
                            OR display_id(t, 'optkey4_chlnbr') = 'FWD')
                            and (t.status ~='Internal' or t.status ~='Void')
                        """)
                        
    if len(non_idr_query[1][0])>0:
        for volume,curr in non_idr_query[1][0]:
            if get_ins_name(curr)== "USD":
                non_idr_result+=abs(volume)
            else:
                non_idr_result+=get_cross_rate(get_ins_name(curr),date)*abs(volume)
    else:
        non_idr_result = 0
        
    mds_query = ael.asql(f"""SELECT abs(t.quantity),t.insaddr 
                        FROM trade t,instrument i, portfolio p
                        WHERE t.insaddr = i.insaddr and i.instype='Curr' 
                        AND t.prfnbr = p.prfnbr and t.time>='{str(date)}' and 
                        t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' 
                        and t.optkey3_chlnbr={str(get_optkey3_oid('SP'))} and 
                        t.optkey4_chlnbr={str(get_optkey4_oid('MDS'))}
                        AND (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                        """)
    
    if len(mds_query[1][0])>0:
        for volume,curr in mds_query[1][0]:
            if get_ins_name(curr)== "USD":
                mds_result+=volume
            else:
                mds_result+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        mds_result = 0
    
    swap_query = ael.asql(f"""SELECT abs(t.quantity),t.insaddr
                        FROM trade t, portfolio p WHERE t.time>='{str(date)}'
                        AND t.time<'{acm.Time.DateAddDelta(date,0,0,1)}'
                        AND t.prfnbr = p.prfnbr AND (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                        AND display_id(t, 'optkey3_chlnbr') = 'FX'
                        AND (display_id(t, 'optkey4_chlnbr') = 'SWAP')
                        AND (t.status ~='Internal' or t.status ~='Void')
                    """)
    
    if len(swap_query[1][0])>0:
        for volume,curr in swap_query[1][0]:
            if get_ins_name(curr)== "USD":
                swap_result+=volume
            else:
                swap_result+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        swap_result = 0

    tod_query = ael.asql(f"""SELECT t.quantity,t.insaddr
                        FROM trade t, portfolio p WHERE t.value_day = '{str(date)}'
                        AND t.prfnbr = p.prfnbr
                        AND p.prfid = 'Marktra'
                        AND display_id(t,'optkey3_chlnbr') = 'FX'
                        AND display_id(t,'optkey4_chlnbr') = 'TOD'
                        """)
                        
    if len(tod_query[1][0])>0:
        for volume,curr in tod_query[1][0]:
            if get_ins_name(curr)== "USD":
                open_tod+=volume
            else:
                open_tod+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        open_tod = 0
        
    tom_query = ael.asql(f"""SELECT t.quantity,t.insaddr
                        FROM trade t, portfolio p WHERE t.value_day = '{str(date)}'
                        AND t.prfnbr = p.prfnbr
                        AND p.prfid = 'Marktra'
                        AND display_id(t,'optkey3_chlnbr') = 'FX'
                        AND display_id(t,'optkey4_chlnbr') = 'TOM'
                        """)
                        
    if len(tom_query[1][0])>0:
        for volume,curr in tom_query[1][0]:
            if get_ins_name(curr)== "USD":
                open_tom+=volume
            else:
                open_tom+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        open_tom = 0
    
    spot_query = ael.asql(f"""SELECT t.quantity,t.insaddr
                        FROM trade t, portfolio p WHERE t.value_day = '{str(date)}'
                        AND t.prfnbr = p.prfnbr
                        AND p.prfid = 'Marktra'
                        AND display_id(t,'optkey3_chlnbr') = 'FX'
                        AND display_id(t,'optkey4_chlnbr') = 'SPOT'
                        """)
                        
    if len(spot_query[1][0])>0:
        for volume,curr in spot_query[1][0]:
            if get_ins_name(curr)== "USD":
                open_spot+=volume
            else:
                open_spot+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        open_spot = 0
    
    sevendays = acm.Time.DateAdjustPeriod(today,'7d',CALENDAR,1)
    
    outstanding_lower_7day_query = ael.asql(f"""
                                            select t.quantity , t.insaddr 
                                            from TRADE t, PORTFOLIO p
                                            where display_id(t,'optkey3_chlnbr') = 'FX'
                                            AND display_id(t,'optkey4_chlnbr') = 'FWD'
                                            AND t.prfnbr = p.prfnbr
                                            AND t.value_day >= TODAY
                                            AND t.value_day < '{sevendays}'
                                            AND p.prfid = 'Marktra'
                                            """)
                                            
    if len(outstanding_lower_7day_query[1][0])>0:
        for volume,curr in outstanding_lower_7day_query[1][0]:
            if get_ins_name(curr)== "USD":
                outstanding_1+=volume
            else:
                outstanding_1+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        outstanding_1 = 0

    
    fourteendays = acm.Time.DateAdjustPeriod(today,'14d',CALENDAR,1)
    
    outstanding_lower_7to14day_query = ael.asql(f"""
                                            select t.quantity , t.insaddr 
                                            from TRADE t, PORTFOLIO p
                                            where display_id(t,'optkey3_chlnbr') = 'FX'
                                            AND display_id(t,'optkey4_chlnbr') = 'FWD'
                                            AND t.prfnbr = p.prfnbr
                                            AND t.value_day >= '{sevendays}'
                                            AND t.value_day < '{fourteendays}'
                                            AND p.prfid = 'Marktra'
                                            """)
                                            
    if len(outstanding_lower_7to14day_query[1][0])>0:
        for volume,curr in outstanding_lower_7to14day_query[1][0]:
            if get_ins_name(curr)== "USD":
                outstanding_2+=volume
            else:
                outstanding_2+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        outstanding_2 = 0
    
    thirtyday = acm.Time.DateAdjustPeriod(today,'30d',CALENDAR,1)
    
    outstanding_lower_14to30day_query = ael.asql(f"""
                                            select t.quantity , t.insaddr 
                                            from TRADE t, PORTFOLIO p
                                            where display_id(t,'optkey3_chlnbr') = 'FX'
                                            AND display_id(t,'optkey4_chlnbr') = 'FWD'
                                            AND t.prfnbr = p.prfnbr
                                            AND t.value_day >= '{fourteendays}'
                                            AND t.value_day < '{thirtyday}'
                                            AND p.prfid = 'Marktra'
                                            """)
                                            
    if len(outstanding_lower_14to30day_query[1][0])>0:
        for volume,curr in outstanding_lower_14to30day_query[1][0]:
            if get_ins_name(curr)== "USD":
                outstanding_3+=volume
            else:
                outstanding_3+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        outstanding_3 = 0
       
    ninetyday = acm.Time.DateAdjustPeriod(today,'90d',CALENDAR,1)
        
    outstanding_lower_30to90day_query = ael.asql(f"""
                                            select t.quantity , t.insaddr 
                                            from TRADE t, PORTFOLIO p
                                            where display_id(t,'optkey3_chlnbr') = 'FX'
                                            AND display_id(t,'optkey4_chlnbr') = 'FWD'
                                            AND t.prfnbr = p.prfnbr
                                            AND t.value_day >= '{thirtyday}'
                                            AND t.value_day < '{ninetyday}'
                                            AND p.prfid = 'Marktra'
                                            """)
                                            
    if len(outstanding_lower_30to90day_query[1][0])>0:
        for volume,curr in outstanding_lower_30to90day_query[1][0]:
            if get_ins_name(curr)== "USD":
                outstanding_4+=volume
            else:
                outstanding_4+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        outstanding_4 = 0
        
    outstanding_higher90day_query = ael.asql(f"""
                                            select t.quantity , t.insaddr 
                                            from TRADE t, PORTFOLIO p
                                            where display_id(t,'optkey3_chlnbr') = 'FX'
                                            AND display_id(t,'optkey4_chlnbr') = 'FWD'
                                            AND t.prfnbr = p.prfnbr
                                            AND t.value_day >= '{ninetyday}'
                                            AND p.prfid = 'Marktra'
                                            """)
                                            
    if len(outstanding_higher90day_query[1][0])>0:
        for volume,curr in outstanding_higher90day_query[1][0]:
            if get_ins_name(curr)== "USD":
                outstanding_5+=volume
            else:
                outstanding_5+=get_cross_rate(get_ins_name(curr),date)*volume
    else:
        outstanding_5 = 0
   
    banknote_trade = ael.asql(f"""SELECT abs(t.quantity),t.insaddr,t.curr,t.premium FROM trade t, 
                            instrument i, portfolio p WHERE t.insaddr = i.insaddr and t.prfnbr = p.prfnbr 
                            and t.time>='{str(date)}' and t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' 
                            and (p.prfid = 'Banknotes Branch Settlement' or p.prfid='Banknotes Interbank')
                            and (t.status ~='Internal' or t.status ~='Void') AND display_id(t,'curr')='IDR' 
                            """)
                            
    if len(banknote_trade[1][0])>0:
        for volume,curr,curr2,prem in banknote_trade[1][0]:
            if get_ins_name(curr)== "USD":
                banknotes_vol+=volume
            else:
                if get_cross_rate(get_ins_name(curr),date):
                    banknotes_vol+=get_cross_rate(get_ins_name(curr),date)*volume
                else:
                    banknotes_vol+=get_cross_rate(get_ins_name(curr2),date)*prem
    else:
        banknotes_vol = 0
    
    
    retail_trade = ael.asql(f"""SELECT abs(t.quantity),t.insaddr,t.curr,t.premium FROM trade t, 
                            instrument i, portfolio p WHERE t.insaddr = i.insaddr and t.prfnbr = p.prfnbr 
                            and t.time>='{str(date)}' and t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' 
                            and (p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                            and (t.status ~='Internal' or t.status ~='Void') AND display_id(t,'curr')='IDR' 
                            """)
                            
    if len(retail_trade[1][0])>0:
        for volume,curr,curr2,prem in retail_trade[1][0]:
            if get_ins_name(curr)== "USD":
                retail_vol+=volume
            else:
                if get_cross_rate(get_ins_name(curr),date):
                    retail_vol+=get_cross_rate(get_ins_name(curr),date)*volume
                else:
                    retail_vol+=get_cross_rate(get_ins_name(curr2),date)*prem
    else:
        retail_vol = 0
        
        
    wholesale_trade = ael.asql(f"""SELECT abs(t.quantity),t.insaddr,t.curr,t.premium FROM trade t, 
                            instrument i, portfolio p WHERE t.insaddr = i.insaddr and t.prfnbr = p.prfnbr 
                            and t.time>='{str(date)}' and t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' 
                            and (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO')
                            and (t.status ~='Internal' or t.status ~='Void') AND display_id(t,'curr')='IDR' 
                            """)
                    
    if len(wholesale_trade[1][0])>0:
        for volume,curr,curr2,prem in wholesale_trade[1][0]:
            if get_ins_name(curr)== "USD":
                wholesale_vol+=volume
            else:
                if get_cross_rate(get_ins_name(curr),date):
                    wholesale_vol+=get_cross_rate(get_ins_name(curr),date)*volume
                else:
                    wholesale_vol+=get_cross_rate(get_ins_name(curr2),date)*prem
    else:
        wholesale_vol = 0
    
    sum_open_position = open_tod + open_tom + open_spot
    
    sum_non_today_gaping = open_tom + open_spot
    
    sum_of_vol_1 = non_idr_result + mds_result + valas_beli_result + valas_jual_result + swap_result
    sum_of_vol_2 = banknotes_vol + retail_vol + wholesale_vol
    
    average_buy_value = ael.asql(f"""SELECT avg(abs(t.premium/t.quantity)) 
                                FROM trade t,portfolio p where t.time>='{str(date)}' and 
                                t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' and 
                                t.insaddr = '{str(get_ins_num('USD'))}' and t.curr = 
                                '{str(get_ins_num('IDR'))}' and t.quantity>0 and 
                                t.optkey4_chlnbr~='{str(get_optkey4_oid('FWD'))}' and t.optkey4_chlnbr~='{str(get_optkey4_oid('SWAP'))}' and t.optkey4_chlnbr~='{str(get_optkey4_oid('NS'))}'
                                and t.prfnbr = p.prfnbr and (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                                and (t.status ~='Internal' or t.status ~='Void')
                                """)
    average_buy_value = average_buy_value[1][0][0][0] if len(average_buy_value[1][0])>0 else 0
    
    average_sell_value = ael.asql(f"""SELECT avg(abs(t.premium/t.quantity)) 
                                FROM trade t,portfolio p where t.time>='{str(date)}' and 
                                t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' and 
                                t.insaddr = '{str(get_ins_num('USD'))}' and t.curr = 
                                '{str(get_ins_num('IDR'))}' and t.quantity<0 and 
                                t.optkey4_chlnbr~='{str(get_optkey4_oid('FWD'))}'and t.optkey4_chlnbr~='{str(get_optkey4_oid('SWAP'))}' and t.optkey4_chlnbr~='{str(get_optkey4_oid('NS'))}'
                                and t.prfnbr = p.prfnbr and (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                                and (t.status ~='Internal' or t.status ~='Void')
                                """)
    average_sell_value = average_sell_value[1][0][0][0] if len(average_sell_value[1][0])>0 else 0
    
    
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
    
    result_dict = filter_trade_by_date(date)
    
    html_content = html_gen.create_base_html_content("", additional_styles=additional_style)

    html_content += "<table>"

    html_content += prepare_marktra_html_title(html_content)

    html_content += "<tr></tr><tr></tr>"

    html_content += div_side_by_side

    html_content = prepare_sum_vol_1_table(html_content, result_dict)

    html_content = prepare_sum_vol_2_table(html_content, result_dict)

    html_content = prepare_nasabah_jual_table(html_content, date)

    html_content = prepare_nasabah_beli_table(html_content, date)

    html_content += end_div_side_by_side

    html_content += "<tr></tr>"

    html_content += "<tr>"

    html_content = prepare_average_rate(html_content, result_dict)

    html_content += "</tr>"

    html_content += "<tr></tr>"

    html_content += div_side_by_side

    html_content = prepare_sum_open_table(html_content, result_dict)

    html_content = prepare_outstanding_table(html_content, result_dict)

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

