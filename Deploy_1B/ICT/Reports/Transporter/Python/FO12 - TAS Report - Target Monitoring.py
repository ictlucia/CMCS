from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

import acm, ael


def get_USD_Equiv(trade):
    jakarta = acm.FCalendar['Jakarta']
    strongerusd = ['CHF','KYD','GBP','JOD','OMR','BHD','KWD','EUR']
    trade_time = trade.TradeTimeDateOnly()
    trade_time_yesterday = acm.Time.DateAdjustPeriod(trade_time,'-1d',jakarta,2)
    if trade.Currency().Name() in strongerusd:
        prices = acm.FPrice.Select(f"instrument = '{trade.Currency().Name()}' and currency = 'USD' and market = 'EOD_MtM' and day = '{trade_time}'")
        if prices:
            return prices[0].Settle()
        else:
            prices = acm.FPrice.Select(f"instrument = '{trade.Currency().Name()}' and currency = 'USD' and market = 'EOD_MtM' and day = '{trade_time_yesterday}'")
            if prices:
                return prices[0].Settle()
    else:
        prices = acm.FPrice.Select(f"instrument= 'USD' and currency = '{trade.Currency().Name()}' and market = 'EOD_MtM' and day = '{trade_time}'")
        if prices:
            return 1/prices[0].Settle()
        else:
            prices = acm.FPrice.Select(f"instrument= 'USD' and currency = '{trade.Currency().Name()}' and market = 'EOD_MtM' and day = '{trade_time_yesterday}'")
            if prices:
                return 1/prices[0].Settle()


def idr_price_mtm_tradetime(trade):
    jakarta = acm.FCalendar['Jakarta']
    trade_time = trade.TradeTimeDateOnly()
    trade_time_yesterday = acm.Time.DateAdjustPeriod(trade_time,'-1d',jakarta,2)
    prices = acm.FPrice.Select(f"instrument = '{trade.Currency().Name()}' and currency = 'IDR' and market = 'EOD_MtM' and day = '{trade_time}'")
    if prices:
        return prices[0].Settle()
    else:
        prices = acm.FPrice.Select(f"instrument = '{trade.Currency().Name()}' and currency = 'IDR' and market = 'EOD_MtM' and day = '{trade_time_yesterday}'")
        if prices:
            return prices[0].Settle()

def get_prfnbr(portnames):

    portlist = []

    for portname in portnames:

        port = acm.FPhysicalPortfolio[portname]

        if port != None :

            port_id = port.Oid()

        portlist.append(port_id)

    return portlist


def convert_premium_to_USD(tradenumber):

    trade = acm.FTrade[tradenumber]
    
    if trade.Currency().Name() == 'USD':

        return trade.Premium()/1000000
    
    else:
        price = get_USD_Equiv(trade)
        if price:
            return price*trade.Premium()/1000000
        else:
            return trade.Premium()/1000000






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



def get_optkey4_name(optkey_id):

    optkey = acm.FChoiceList.Select('list=Category')

    for each in optkey:

        if each.Oid()== optkey_id:

            return each.Name()


def remove_trailing_zero(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value            


def get_PNLDaily(tradenumber):
    context = acm.GetDefaultContext()

    sheetType = 'FPortfolioSheet'

    ins = acm.FTrade[tradenumber]

    columnId = "Portfolio Total Profit and Loss Daily"

    calcSpace = acm.Calculations().CreateCalculationSpace(context, sheetType)

    result = calcSpace.CreateCalculation(ins, columnId).Value().Number()
    
    if ins.Currency().Name()== "IDR":
        return result/1000000000
    else:
        price = idr_price_mtm_tradetime(ins)
        if price:
            return (result*price)/1000000000
        else:
            return result/1000000000
    
def get_PNLMonthly(tradenumber):
    context = acm.GetDefaultContext()

    sheetType = 'FPortfolioSheet'

    ins = acm.FTrade[tradenumber]

    columnId = "Portfolio Theoretical Total Profit and Loss Monthly"

    calcSpace = acm.Calculations().CreateCalculationSpace(context, sheetType)

    result = calcSpace.CreateCalculation(ins, columnId).Value().Number()

    if ins.Currency().Name()== "IDR":
        return result/1000000000
    else:
        price = idr_price_mtm_tradetime(ins)
        if price:
            return (result*price)/1000000000
        else:
            return result/1000000000
    

def getPNLTrade(tradenumber):

    context = acm.GetDefaultContext()

    sheetType = 'FPortfolioSheet'

    ins = acm.FTrade[tradenumber]

    columnId = "Portfolio Theoretical Total Profit and Loss Yearly"

    calcSpace = acm.Calculations().CreateCalculationSpace(context, sheetType)

    result = calcSpace.CreateCalculation(ins, columnId).Value().Number()

    if ins.Currency().Name()== "IDR":
        return result/1000000000
    else:
        price = idr_price_mtm_tradetime(ins)
        if price:
            return (result*price)/1000000000
        else:
            return result/1000000000

    





ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'TAS Report - Target Monitoring'}







ael_variables=[

['report_name','Report Name','string', None, 'TAS Report - Target Monitoring', 1,0],

['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

['targetMTDPnL','Target Month PnL','float',None,'1000000',1,0],

['targetYTDPnL','Target Year PnL','float',None,'10000000',1,0],

['targetMTDVolume','Target Month Vol','float',None,'1000000',1,0],

['targetYTDVolume','Target Year Vol','float',None,'10000000',1,0],

['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],

]







             

def ael_main(parameter):

    html_gen = HTMLGenerator()

    xsl_gen = XSLFOGenerator()

    report_name = parameter['report_name']

    file_path = str(parameter['file_path'])

    output_file = parameter['output_file']

    targetMTDPnL = parameter['targetMTDPnL']

    targetYTDPnL = parameter['targetYTDPnL']

    targetMTDVolume = parameter['targetMTDVolume']

    targetYTDVolume = parameter['targetYTDVolume']

    

    prfid = ""

    

    style = """

    .title {

        color:black;

        text-align:left;

    }

    

    .bold {

        font-weight:bold;

    }

    

    

    """

    

    portnames = ['Wholesale FX & Derivative BO', 'Wholesale FX Branch', 'Wholesale SP', 'Retail FX BO', 'Retail FX Branch', 'Retail SP']

    

    optkey_list = [['SWAP', ['IRS', 'CCS']],

                    ['FX', ['TOD', 'TOM', 'SPOT', 'FWD', 'SWAP', 'OPT']],

                    ['SP', ['MDS', 'MDCI', 'MMLD']]]

    

    optkey_query = "("

    for i_optkey in range(len(optkey_list)):

        optkey = optkey_list[i_optkey]

        optkey_query += f"(t.optkey3_chlnbr = {str(get_optkey3_oid(optkey[0]))} AND (" if i_optkey == 0 else f" OR (t.optkey3_chlnbr = {str(get_optkey3_oid(optkey[0]))} AND ("

        for i_optkey4 in range(len(optkey[1])):

            optkey_query += f"t.optkey4_chlnbr = {str(get_optkey4_oid(optkey[1][i_optkey4]))}" if i_optkey4 == 0 else f" OR t.optkey4_chlnbr = {str(get_optkey4_oid(optkey[1][i_optkey4]))}"

        optkey_query += ")) "

    optkey_query += ")"

    

    # QUERY: Portfolio = All in Portnames

    

    # WHERE 

    query = ael.asql(f"""SELECT t.trdnbr, t.premium,p.prfid,i.insid, t.optkey4_chlnbr,t.curr

                        FROM trade t, portfolio p, instrument i

                        WHERE t.prfnbr=p.prfnbr

                        AND p.prfnbr IN {"('" + "', '".join([str(x) for x in get_prfnbr(portnames)]) + "')"}

                        AND t.value_day >= FIRSTDAYOFYEAR

                        AND t.status = 'BO-BO Confirmed'

                        AND t.curr = i.insaddr

                        AND {optkey_query}

                        ORDER BY p.prfid DESC""")
   
   
    data = []
    
    current_prfid = None
    
    combination = set()
    
    for row in query[1][0]:
        tradenumber,premium,portfolio,instrument,product,currency = row
        
        key = (portfolio,product)
        if key not in combination:
            combination.add(key)
        
            pnlmonthly = round(get_PNLMonthly(tradenumber),2)
            pnlyearly = round(getPNLTrade(tradenumber),2)
            
            mtdpnlpercent = round((pnlmonthly/targetMTDPnL)*100,2)
            ytdpnlpercent = round((pnlyearly/targetYTDPnL)*100,2)
            
            volumedaily = round(convert_premium_to_USD(tradenumber),2)
            volumemonthly = round(convert_premium_to_USD(tradenumber)*30,2)
            volumeyearly = round(convert_premium_to_USD(tradenumber)*365,2)
            
            mtdvolpercent = round((volumemonthly/targetMTDVolume)*100,2)
            ytdvolpercent = round((volumeyearly/targetYTDVolume)*100,2)
            
            
            if portfolio!=current_prfid:
                current_prfid = portfolio
                
                data.append({
                    "portfolio":portfolio,
                    "produk":get_optkey4_name(product),
                    "tpld":f"{round(get_PNLDaily(tradenumber),2):,}",
                    "tplm":f"{pnlmonthly:,}",
                    "tply":f"{pnlyearly:,}",
                    "targetm":f"{int(targetMTDPnL):,}",
                    "targety":f"{int(targetYTDPnL):,}",
                    "pnlmtdpercent":f"{mtdpnlpercent:,}",
                    "pnlytdpercent":f"{ytdpnlpercent:,}",
                    "vold":f"{abs(volumedaily):,}",
                    "volm":f"{abs(volumemonthly):,}",
                    "voly":f"{abs(volumeyearly):,}",
                    "targetvm":f"{int(targetMTDVolume):,}",
                    "targetvy":f"{int(targetYTDVolume):,}",
                    "volmtdpercent":f"{mtdvolpercent:,}",
                    "volytdpercent":f"{ytdvolpercent:,}"
                })
            else:
                data.append({
                    "portfolio":None,
                    "produk":get_optkey4_name(product),
                    "tpld":f"{round(get_PNLDaily(tradenumber),2):,}",
                    "tplm":f"{pnlmonthly:,}",
                    "tply":f"{pnlyearly:,}",
                    "targetm":f"{int(targetMTDPnL):,}",
                    "targety":f"{int(targetYTDPnL):,}",
                    "pnlmtdpercent":f"{mtdpnlpercent:,}",
                    "pnlytdpercent":f"{ytdpnlpercent:,}",
                    "vold":f"{abs(volumedaily):,}",
                    "volm":f"{abs(volumemonthly):,}",
                    "voly":f"{abs(volumeyearly):,}",
                    "targetvm":f"{int(targetMTDVolume):,}",
                    "targetvy":f"{int(targetYTDVolume):,}",
                    "volmtdpercent":f"{mtdvolpercent:,}",
                    "volytdpercent":f"{ytdvolpercent:,}"
                })
            

    current_date = get_current_date("")
    current_hour = get_current_hour("")

    date_today = acm.Time.DateToday()

    

    html_content = html_gen.create_base_html_content('TAS Report - Target Monitoring as per. '+ date_today,style)

    html_content = html_gen.prepare_html_table(html_content,'')

    

    xsl_fo_content = xsl_gen.prepare_xsl_fo_content('TAS Report - Target Monitoring as per. '+ date_today)

    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""



    html_content = html_gen.open_table_row(html_content)

    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)

        

    html_content = html_gen.add_cell_data(html_content,'P&L (in IDR Billion)','colspan=9 class="bold"')

    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'P&#38;L (in IDR Billion)','number-columns-spanned="9" font-weight="bold"')

    

    html_content = html_gen.add_cell_data(html_content,'Volume in USD (in million USD)','colspan=7 class="bold"')

    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'Volume in USD (in million USD)','number-columns-spanned="7" font-weight="bold"')

    

    html_content = html_gen.close_table_row(html_content)

    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)

    

    list_subtitle = ['Portfolio','Produk', 'Today','MTD','YTD','Target MTD','Target MTD%','Target YTD','Target YTD%','Today','MTD','YTD','Target MTD','Target MTD%','TargetYTD','Target YTD%']

    

    html_content = html_gen.add_data_row(html_content,[list_subtitle])

    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[list_subtitle])
    
    for each_data in data:
        if each_data["portfolio"] is not None:
            html_content = html_gen.open_table_row(html_content)
            xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
            
            html_content = html_gen.add_cell_data(html_content,each_data["portfolio"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["portfolio"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["produk"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["produk"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["tpld"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["tpld"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["tplm"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["tplm"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["tply"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["tply"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["targetm"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["targetm"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["pnlmtdpercent"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["pnlmtdpercent"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["targety"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["targety"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["pnlytdpercent"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["pnlytdpercent"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["vold"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["vold"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["volm"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["volm"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["voly"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["voly"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["targetvm"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["targetvm"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["volmtdpercent"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["volmtdpercent"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["targetvy"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["targetvy"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["volytdpercent"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["volytdpercent"])
            
            html_content = html_gen.close_table_row(html_content)
            xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
            
        else:
            html_content = html_gen.open_table_row(html_content)
            xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
            
            html_content = html_gen.add_cell_data(html_content,"")
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,"")
            
            html_content = html_gen.add_cell_data(html_content,each_data["produk"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["produk"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["tpld"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["tpld"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["tplm"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["tplm"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["tply"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["tply"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["targetm"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["targetm"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["pnlmtdpercent"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["pnlmtdpercent"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["targety"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["targety"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["pnlytdpercent"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["pnlytdpercent"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["vold"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["vold"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["volm"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["volm"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["voly"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["voly"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["targetvm"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["targetvm"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["volmtdpercent"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["volmtdpercent"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["targetvy"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["targetvy"])
            
            html_content = html_gen.add_cell_data(html_content,each_data["volytdpercent"])
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,each_data["volytdpercent"])
            
            html_content = html_gen.close_table_row(html_content)
            xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)

    xsl_fo_content = xsl_fo_content.replace("Wholesale FX & Derivative BO","Wholesale FX &#38; Derivative BO")

    

    html_content = html_gen.close_html_table(html_content)

    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)

    

    html_file = html_gen.create_html_file(html_content, file_path, report_name+" "+current_date+current_hour, current_date, True)

    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name+" "+current_date+current_hour,file_path, xsl_fo_content, current_date)

    

    

    for i in output_file:

        if i != '.pdf' :

            generate_file_for_other_extension(html_file, i)

        else:

            generate_pdf_from_fo_file(xsl_fo_file)
