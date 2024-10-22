import acm,ael
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

today = acm.Time.DateToday()

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


def get_curr_name(oid):
    currname = acm.FCurrency[oid]
    return currname.Name()

def get_ins_name(oid):
    if oid and oid>0:
        ins_name = acm.FInstrument[oid]
        return ins_name.Name()


def get_amount(buy_queries,sell_queries):
    buy_list = buy_queries.copy()  # Copy to avoid modifying the original list
    today = acm.Time.DateToday()
    excluded_buys = []  # List to store excluded buy queries
    future_fwds = []  # List to store future FWD buy queries that should not appear in the final output

    for sell_query in sell_queries:
        sell_outstanding = abs(sell_query[5])  # Convert sell Outstanding to positive
        sell_prfid = sell_query[0]
        sell_insid = sell_query[1]
        sell_und_insaddr = sell_query[9]
        sell_optkey4 = sell_query[8]

        if sell_optkey4 == get_optkey4_oid('FWD'):
            # Match based on und_insaddr for sell with insid for buy
            filtered_buy_list = [buy for buy in buy_list if buy[0] == sell_prfid and buy[1] == get_ins_name(sell_und_insaddr)]
        else:
            # Match based on normal insid
            filtered_buy_list = [buy for buy in buy_list if buy[0] == sell_prfid and buy[1] == sell_insid]

        while sell_outstanding > 0 and filtered_buy_list:
            buy_query = filtered_buy_list[0]  # Get the earliest buy amount and its fields
            buy_outstanding = buy_query[5]
            
            buy_value_day = str(buy_query[7])

            buy_optkey4 = buy_query[8]

            # Exclude buy queries where the optkey4_chlnbr is "FWD" and the value_day is earlier than today
            if buy_optkey4 == get_optkey4_oid('FWD') and buy_value_day_date < today:
                excluded_buys.append(buy_query)
                filtered_buy_list.pop(0)  # Remove this buy from the list and skip it
                buy_list.remove(buy_query)
                continue

            if buy_outstanding > sell_outstanding:
                updated_buy_query = (
                    buy_query[0], buy_query[1], buy_query[2], buy_query[3],
                    buy_query[4], buy_outstanding - sell_outstanding, buy_query[6], buy_query[7],
                    buy_query[8], buy_query[9]
                )
                # Update the remaining buy amount in place
                buy_list[buy_list.index(buy_query)] = updated_buy_query
                sell_outstanding = 0
            else:
                sell_outstanding -= buy_outstanding  # Fully subtract this buy amount
                buy_list.remove(buy_query)  # Remove this buy from the list

            # Re-filter the buy list based on the current sell query's criteria
            if sell_optkey4 == get_optkey4_oid('FWD'):
                filtered_buy_list = [buy for buy in buy_list if buy[0] == sell_prfid and buy[1] == get_ins_name(sell_und_insaddr)]
            else:
                filtered_buy_list = [buy for buy in buy_list if buy[0] == sell_prfid and buy[1] == sell_insid]

    # Include excluded buys in the final output but exclude future FWDs
    remaining_buys = buy_list + excluded_buys
    remaining_buys = [buy for buy in remaining_buys if not (buy[8] == 'FWD' and buy[7] >= today)]

    return remaining_buys



def get_outstanding_usd(currname):
    jakarta = acm.FCalendar['Jakarta']
    yesterday = acm.Time.DateAdjustPeriod(today,'-1d',jakarta,2)
    strongerusd = ['CHF','KYD','GBP','JOD','OMR','BHD','KWD','EUR']
    if currname == "USD":
        return 1
    else:
        if currname in strongerusd:
            prices = acm.FPrice.Select(f"instrument = '{currname}' and currency = 'USD' and market = 'EOD_MtM' and day = '{today}'")
            if prices:
                return prices[0].Settle()
            else:
                prices = acm.FPrice.Select(f"instrument = '{currname}' and currency = 'USD' and market = 'EOD_MtM' and day = '{yesterday}'")
                if prices:
                    return prices[0].Settle()
                else:
                    return 0
        else:
            prices = acm.FPrice.Select(f"instrument = 'USD' and currency = '{currname}' and market = 'EOD_MtM' and day = '{today}'")
            if prices:
                return 1/prices[0].Settle()
            else:
                prices = acm.FPrice.Select(f"instrument = 'USD' and currency = '{currname}' and market = 'EOD_MtM' and day = '{yesterday}'")
                if prices:
                    return 1/prices[0].Settle()
                else:
                    return 0
                    

ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'FO05 - FXT FX Report Requirement - Bond Holding Period'}



ael_variables=[

['report_name','Report Name','string', None, 'FO05 - FXT FX Report Requirement - Bond Holding Period', 1,0],

['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output']

]

def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    title_style = """
        .subtitle {
            background-color:#91B3D5;
            font-weight:bold;
        }
    """

    today = acm.Time.DateToday()

    html_content = html_gen.create_base_html_content("FXT FX Report Requirement - Bond Holding Period. "+today,title_style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("FXT FX Report Requirement - Bond Holding Period "+today)
    
    title = [['PORTFOLIO','SECID','TRADENO','DEALDATE','CURRENCY','Outstanding in Original Currency','Outstanding e.q. USD','Holding Period','Limit Holding Period','(%)','Status']]

    html_content = html_gen.prepare_html_table(html_content,'')
    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""

    html_content = html_gen.add_data_row(html_content,title,'class="subtitle"')
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,title)
    
    buying_qf = acm.FStoredASQLQuery['BHP_FO05_BuyQuery']
    selling_qf = acm.FStoredASQLQuery['BHP_FO05_SellQuery']
    buy_result = []
    sell_result = []
    if buying_qf is not None:
        buyer_qf = buying_qf.Query().Select()
    
        for buy_qf in buyer_qf:
            buy_port = buy_qf.Portfolio().Name()
            
            buy_ins = buy_qf.Instrument().Name()
            
            buy_nbr = buy_qf.Oid()
            
            buy_time = buy_qf.TradeTimeDateOnly()
            
            buy_curr = buy_qf.Currency().Name()
            
            buy_outstanding = buy_qf.Quantity()*buy_qf.Instrument().ContractSize()
            
            buy_quantity = buy_qf.Quantity()
            
            buy_valueday = buy_qf.ValueDay()
            
            buy_tk4 = buy_qf.OptKey4AsEnum()
            
            buy_und = None
            
            if buy_qf.Instrument().Underlying():
                buy_und = buy_qf.Instrument().Underlying().Currency().Name()
            
            buy_result.append([buy_port,buy_ins,buy_nbr,buy_time,buy_curr,buy_outstanding,buy_quantity,buy_valueday,buy_tk4,buy_und])
            
    if selling_qf is not None:
        seller_qf = selling_qf.Query().Select()
        for sell_qf in seller_qf:
            sell_port = sell_qf.Portfolio().Name()
            
            sell_ins = sell_qf.Instrument().Name()
            
            sell_nbr = sell_qf.Oid()
            
            sell_time = sell_qf.TradeTimeDateOnly()
            
            sell_curr = sell_qf.Currency().Name()
            
            sell_outstanding = sell_qf.Quantity()*sell_qf.Instrument().ContractSize()
            
            sell_quantity = sell_qf.Quantity()
            
            sell_valueday = sell_qf.ValueDay()
            
            sell_tk4 = sell_qf.OptKey4AsEnum()
            
            sell_und = None
            
            if sell_qf.Instrument().Underlying():
                sell_und = sell_qf.Instrument().Underlying().Currency().Name()
                
            sell_result.append([sell_port,sell_ins,sell_nbr,sell_time,sell_curr,sell_outstanding,sell_quantity,sell_valueday,sell_tk4,sell_und])
        
    netted_buy_amount = get_amount(buy_result,sell_result)
    
    '''
    #Buy Bonds
    buyquery = f"""
            SELECT p.prfid,i.insid, t.trdnbr,t.time,t.curr,t.quantity*i.contr_size 'Outstanding', t.quantity,  t.value_day, t.optkey4_chlnbr, i.und_insaddr
            FROM trade t, instrument i,portfolio p
            where t.insaddr = i.insaddr
            and t.prfnbr = p.prfnbr
            and t.optkey3_chlnbr = {str(get_optkey3_oid('BOND'))}
            and (status = 'FO Confirmed' or status = 'BO Confirmed' or status = 'BO-BO Confirmed')
            and t.quantity > 0 
            and (
            p.prfid='FXT Specialist 1' or 
            p.prfid='FXT Specialist 2' or 
            p.prfid='FXT Specialist 3' or
            p.prfid='FXT Specialist 4'
            )
            order by p.prfid, i.insid, t.time,t.value_day
            """
    buyresult = ael.asql(buyquery)[1][0]
    #Sell Bonds
    sellquery = f"""
            SELECT p.prfid,i.insid, t.trdnbr,t.time,t.curr,t.quantity*i.contr_size 'Outstanding', t.quantity,  t.value_day, t.optkey4_chlnbr, i.und_insaddr
            FROM trade t, instrument i,portfolio p
            where t.insaddr = i.insaddr
            and t.prfnbr = p.prfnbr
            and t.optkey3_chlnbr = {str(get_optkey3_oid('BOND'))}
            and (status = 'FO Confirmed' or status = 'BO Confirmed' or status = 'BO-BO Confirmed')
            and (p.prfid='FXT Specialist 1' or
            p.prfid='FXT Specialist 2' or
            p.prfid='FXT Specialist 3' or
            p.prfid='FXT Specialist 4')
            and t.quantity < 0
            order by p.prfid, i.insid, t.time,t.value_day
            """
    sellresult = ael.asql(sellquery)[1][0]
    
    netted_buy_amount = get_amount(buyresult,sellresult)
    '''
    
    
    for i in range(len(netted_buy_amount)):
        origin_date = netted_buy_amount[i][3].split(' ')[0]
        list_date = origin_date.split('-')
        new_date_format = list_date[0]+'/'+list_date[1]+'/'+list_date[2]
        
        curr_name = str(get_curr_name(netted_buy_amount[i][4]))
        
        outstanding_amount = round(get_outstanding_usd(curr_name) * int(netted_buy_amount[i][5]),2)
        
        holding = acm.Time.DateDifference(today,netted_buy_amount[i][3])
        
        limit_holding = 186
        
        percentage = int((holding/limit_holding)*100)
        
        status = ""
        
        if percentage < 85:
            status = "green"
        elif percentage >= 85 and percentage < 100:
            status = "yellow"
        else:
            status = "red"
        
        html_content = html_gen.add_data_row(html_content,[[netted_buy_amount[i][0],netted_buy_amount[i][1], netted_buy_amount[i][2],new_date_format,curr_name,f"{int(netted_buy_amount[i][5]):,}",f"{outstanding_amount:,}",str(holding)+'d',limit_holding,str(percentage)+'%',status]])
        xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[[netted_buy_amount[i][0],netted_buy_amount[i][1],netted_buy_amount[i][2],new_date_format,curr_name,f"{int(netted_buy_amount[i][5]):,}",f"{outstanding_amount:,}",str(holding)+'d',limit_holding,str(percentage)+'%',status]])
    
    html_content = html_content.replace('<td >green</td>','<td style=background-color:green></td>')
    html_content = html_content.replace('<td >yellow</td>','<td style=background-color:yellow></td>')
    html_content = html_content.replace('<td >red</td>','<td style=background-color:red></td>')
    
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    current_hour = get_current_hour("")
    current_date = get_current_date("")

    html_file = html_gen.create_html_file(html_content, file_path, report_name+' '+current_date+current_hour, current_date, True)
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name+' '+current_date+current_hour,file_path,xsl_fo_content,current_date)
    
    
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
    
   
