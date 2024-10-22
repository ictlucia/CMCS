from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import ael, acm

import datetime

import locale

locale.setlocale(locale.LC_ALL, '')  # Sets the thousand separator to be from Windows settings

CURRENT_YEAR = datetime.date.today().year

html_gen = HTMLGenerator()

div_side_by_side = '<tr>'

end_div_side_by_side = '</tr>'

additional_style = """

table {

        margin-left: 10px;

    }

    

#title {

    padding: 0px 20px 0px 20px;

    width: 100%;

    margin: 0px 0px 20px 50px;

    font-size: 24pt;

    font-weight: bold;

    background:#002060;

    color:white;

}

.blue-table {

    background: #ddebf7;

    color: black;

    border: 0px;

    margin: 0px;        

}

.green-table {

    background: #e2efda;

    color: black;

    border: 0px;

    margin: 0px;

}
.data-table {

    border: 1px black double;

    border-bottom: 1px black double;

    border-collapse: none;

}
"""

def get_price_in_idr(val,curr):
    if curr == 'USD':
        return val
        
    else:
        price = acm.FPrice.Select(f"currency={curr} and market='REFINITIV_SPOT' and instrument='USD'")
        
        if len(price) > 0:
            nominal = val * price.First().Settle()
            if str(nominal) == 'nan':
                return 0
                
            return nominal  
            
        else:
            for price in acm.FPrice.Select(f"instrument='USD' and currency={curr}"):
                nominal = val * price.Settle() 
                if str(nominal) == 'nan':
                    return 0
                return nominal
        
            return 0
            
def get_trader_data(effective_from, effective_to):
    
    first_day_of_year = acm.Time.FirstDayOfYear(acm.Time.DateNow())
    # QUERY: Trade Key 3 = FX, Trade Key 4 = TOD or TOM or SPOT or SWAP or FWD or OPT
    fx_trades = acm.FTrade.Select(f"optKey3='FX' AND optKey4 IN ('TOD', 'TOM', 'SPOT', 'SWAP', 'FWD', 'OPT') AND tradeTime>={first_day_of_year}")
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MDS    
    mds_trades = acm.FTrade.Select(f"optKey3='SP' AND optKey4='MDS' AND tradeTime>={first_day_of_year}")    
    
    trader_data = {}
    for trade in fx_trades:
        if trade.AdditionalInfo().RTM() is not None:  # Trades should not have RTM filled in
            continue
        
        trader = trade.TraderId()
        nominal = abs(trade.Nominal())
        currency = trade.Currency().Name()
        trade_date = trade.TradeTimeDateOnly()
        
        if trade_date == acm.Time.DateNow():
            nominal = get_price_in_idr(nominal, currency)
            if trader not in trader_data.keys():
                trader_data[trader] = {'FX_YTD': nominal, 'MDS_YTD': 0, 'frequency_YTD': 0, 'FX_TOD': nominal, 'MDS_TOD': 0, 'frequency_TOD': 1}

            else:
                trader_data[trader]['FX_TOD'] += nominal
                trader_data[trader]['frequency_TOD'] += 1
        
        if trade_date >= effective_from and trade_date <= effective_to:
            nominal = get_price_in_idr(nominal, currency)
            
            if trader not in trader_data.keys():
                trader_data[trader] = {'FX_YTD': nominal, 'MDS_YTD': 0, 'frequency_YTD': 1, 'FX_TOD': 0, 'MDS_TOD': 0, 'frequency_TOD': 0}

            else:

                trader_data[trader]['FX_YTD'] += nominal

                trader_data[trader]['frequency_YTD'] += 1
            
    for trade in mds_trades:
        trader = trade.TraderId()
        nominal = abs(trade.Nominal())
        currency = trade.Currency().Name()
        trade_date = trade.TradeTimeDateOnly()
        
        if trade_date == acm.Time.DateNow():
            nominal = get_price_in_idr(nominal, currency)
            
            if trader not in trader_data.keys():
                trader_data[trader] = {'FX_YTD': 0, 'MDS_YTD': nominal, 'frequency_YTD': 0, 'FX_TOD': 0, 'MDS_TOD': nominal, 'frequency_TOD': 1}

            else:
                trader_data[trader]['MDS_TOD'] += nominal
                trader_data[trader]['frequency_TOD'] += 1

        if trade_date >= effective_from and trade_date <= effective_to:     
            nominal = get_price_in_idr(nominal, currency)
            
            if trader not in trader_data.keys():
                trader_data[trader] = {'FX_YTD': 0, 'MDS_YTD': nominal, 'frequency_YTD': 1, 'FX_TOD': 0, 'MDS_TOD': 0, 'frequency_TOD': 0}

            else:
                trader_data[trader]['MDS_YTD'] += nominal
                trader_data[trader]['frequency_YTD'] += 1
                
    return trader_data
def prepare_title(html_content):

    html_content += "<td style='border:0px;'>"
    
    header_list = [""]

    html_content = html_gen.prepare_html_table(html_content,header_list, '', "style='border:0px;'")

    row_data = [["DASHBOARD PERFORMANCE CLIENT DEALING"]]

    html_content = html_gen.add_data_row(html_content, row_data, "id='title'", "colspan='20'")

    hhtml_content = html_gen.close_html_table(html_content) 

    html_content += "</td>"

    return html_content



def prepare_workdays_table(html_content):

    header_list = ["Today", get_current_date("/")]

    row_data = [[f"WD {CURRENT_YEAR}", ''], ["Current WD", '']]  



    html_content += "<td colspan='2' style='border:0px;' colspan='2'>"



    html_content = html_gen.prepare_html_table(html_content, header_list, table_styling="class='blue-table'")

    html_content = html_gen.add_data_row(html_content, row_data)

    html_content = html_gen.close_html_table(html_content)



    html_content += "</td>"

    return html_content



def prepare_vol_today_table(html_content):

    #TODO: VOLUME TODAY, FREQ TODAY

    header_list = ["Volume Today", "VOLUME_TOD"]

    row_data = [["Target Volume Today", ''], ["Freq Today", "FREQ_TOD"]]



    html_content += "<td colspan='2' style='border:0px;'>"



    html_content = html_gen.prepare_html_table(html_content, header_list, table_styling="class='blue-table'")

    html_content = html_gen.add_data_row(html_content, row_data)

    html_content = html_gen.close_html_table(html_content)



    html_content += "</td>"

    return html_content



def prepare_vol_yearly_table(html_content):

    header_list = [f"Target Vol {CURRENT_YEAR}", '']

    row_data = [["Target Volume YTD", ''], ["Volume YTD", "VOLUME_YTD"]]



    html_content += "<td colspan='2' style='border:0px;'>"



    html_content = html_gen.prepare_html_table(html_content, header_list, table_styling="class='green-table'")

    html_content = html_gen.add_data_row(html_content, row_data)

    html_content = html_gen.close_html_table(html_content)



    html_content += "</td>"

    return html_content    

def prepare_percent_yearly_table(html_content):

    header_list = [f"% Target {CURRENT_YEAR}", '']

    row_data = [["% Target YTD", '']]



    html_content += "<td colspan='2' style='border:0px;'>"



    html_content = html_gen.prepare_html_table(html_content, header_list, table_styling="class='green-table'")

    html_content = html_gen.add_data_row(html_content, row_data)

    html_content = html_gen.close_html_table(html_content)



    html_content += "</td>"

    return html_content    



def prepare_data_table(html_content, effective_from, effective_to):

    trader_data = get_trader_data(effective_from, effective_to)

    traders_row = []    

    ytd_fx_row_data = []

    ytd_mds_row_data = []

    ytd_total_row_data = []

    ytd_frequency_row_data = []

    today_fx_row_data = []

    today_mds_row_data = []

    today_total_row_data = []

    today_frequency_row_data = []



    for keys, value in trader_data.items():

        traders_row.append(keys)

        ytd_fx_row_data.append(value['FX_YTD'])

        ytd_mds_row_data.append(value['MDS_YTD'])

        ytd_total_row_data.append(value['FX_YTD'] + value['MDS_YTD'])

        ytd_frequency_row_data.append(value['frequency_YTD'])

        today_fx_row_data.append(value['FX_TOD'])

        today_mds_row_data.append(value['MDS_TOD'])

        today_total_row_data.append(value['FX_TOD'] + value['MDS_TOD'])

        today_frequency_row_data.append(value['frequency_TOD'])



    formatted_from = datetime.datetime.strptime(effective_from, '%Y-%m-%d').strftime('%d-%b-%y')

    formatted_to = datetime.datetime.strptime(effective_to, '%Y-%m-%d').strftime('%d-%b-%y')



    header_list = [""]

    header_list.extend(traders_row)

    html_content = html_gen.prepare_html_table(html_content, header_list, header_style="colspan='2' style='text-align:left'", table_styling="class='data-table'")



    date_from = ["Effective Date From"]

    date_from.extend(formatted_from for _ in range(len(traders_row)))

    date_to = ["Effective Date To"]

    date_to.extend(formatted_to for _ in range(len(traders_row)))

    row_data = [date_from, date_to]

    html_content = html_gen.add_data_row(html_content, row_data, "style='text-align:right'", "colspan='2'")


    row_data = [locale.format_string("%.2f", x) if str(x) != "nan" else 0 for x in ytd_fx_row_data]
    row_data = [["YTD", "FX"] + row_data]



    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>YTD</td>", "<td rowspan='7'>YTD</td>")

    html_content = html_content.replace("<td colspan='2'>FX</td>", "<td>FX</td>")

    row_data = [locale.format_string("%.2f", x) if str(x) != "nan" else 0 for x in ytd_mds_row_data]
    row_data = [["MDS"] + row_data]
    
    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>MDS</td>", "<td>MDS</td>")
    row_data = ["Total"]


    row_data = [locale.format_string("%.2f", x) if str(x) != "nan" else 0 for x in ytd_total_row_data]
    row_data = [["Total"] + row_data]
    
    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Total</td>", "<td>Total</td>")
    row_data = ["Target"]

    row_data.extend("" for _ in range(len(traders_row)))

    row_data = [[x if str(x) != "nan" else 0 for x in row_data]]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Target</td>", "<td>Target</td>")
    row_data = ["Realisasi (%)"]

    row_data.extend("" for _ in range(len(traders_row)))

    row_data = [[x if str(x) != "nan" else 0 for x in row_data]]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Realisasi (%)</td>", "<td>Realisasi (%)</td>")

    row_data = [locale.format_string("%.0f", x) if str(x) != "nan" else 0 for x in ytd_frequency_row_data]
    row_data = [["Frequency"] + row_data]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Frequency</td>", "<td>Frequency</td>")



    row_data = ["FBI"]

    row_data.extend("" for _ in range(len(traders_row)))

    row_data = [[x if str(x) != "nan" else 0 for x in row_data]]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>FBI</td>", "<td>FBI</td>")
    """ Today section of data table """
    row_data = [locale.format_string("%.2f", x) if str(x) != "nan" else 0 for x in today_fx_row_data]
    row_data = [["Today", "FX"] + row_data]
    
    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Today</td>", "<td rowspan='7'>Today</td>")

    html_content = html_content.replace("<td colspan='2'>FX</td>", "<td>FX</td>")

    row_data = [locale.format_string("%.2f", x) if str(x) != "nan" else 0 for x in today_mds_row_data]
    row_data = [["MDS"] + row_data]


    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>MDS</td>", "<td>MDS</td>")
    
    
    row_data = [x if str(x) != "nan" else 0 for x in today_total_row_data]
    row_data = [["Total"] + row_data]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Total</td>", "<td>Total</td>")
    row_data = ["Target"]

    row_data.extend("" for _ in range(len(traders_row)))

    row_data = [[x if str(x) != "nan" else 0 for x in row_data]]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Target</td>", "<td>Target</td>")
    row_data = ["Realisasi (%)"]

    row_data.extend("" for _ in range(len(traders_row)))

    row_data = [[x if str(x) != "nan" else 0 for x in row_data]]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Realisasi (%)</td>", "<td>Realisasi (%)</td>")

    row_data = [locale.format_string("%.0f", x) if str(x) != "nan" else 0 for x in today_frequency_row_data]
    row_data = [["Frequency"] + row_data]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>Frequency</td>", "<td>Frequency</td>")



    row_data = ["FBI"]

    row_data.extend("" for _ in range(len(traders_row)))

    row_data = [[x if str(x) != "nan" else 0 for x in row_data]]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_content.replace("<td colspan='2'>FBI</td>", "<td>FBI</td>")
    row_data = [f"Target {CURRENT_YEAR} (USD)"]

    row_data = [[x if str(x) != "nan" else 0 for x in row_data]]

    html_content = html_gen.add_data_row(html_content, row_data, '', "colspan='2'")

    html_content = html_gen.close_html_table(html_content)



    html_content = html_content.replace("<td >FREQ_TOD</td>", f"<td>{locale.format_string('%.0f', sum(today_frequency_row_data))}</td>")  # Replace header top table values

    html_content = html_content.replace("<th >VOLUME_TOD</th>", f"<td>{locale.format_string('%.0f', sum(today_fx_row_data) + sum(today_mds_row_data))}</td>")  # Replace header top table values

    html_content = html_content.replace("<td >VOLUME_YTD</td>", f"<td>{locale.format_string('%.0f', sum(ytd_fx_row_data) + sum(ytd_mds_row_data))}</td>")  # Replace header top table values
    
    return html_content

ael_gui_parameters={'runButtonLabel':'&&Run',   

                    'hideExtraControls': True,

                    'windowCaption':'FO16 - TAS Report - Dashboard Performance Client'}
ael_variables=[

    ['report_name','Report Name','string', None, 'FO16 - TAS Report - Dashboard Performance Client', 1,0],

    ['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

    ['output_file','Secondary Output Files','string', ['.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],

    ['effective_from', 'Effective Date From', 'string', None, acm.Time.DateToday(), 1, 0],

    ['effective_to', 'Effective Date To', 'string', None, acm.Time.DateToday(), 1, 0],



]

def ael_main(parameter):

    report_name = parameter['report_name']

    file_path = str(parameter['file_path'])

    output_file = parameter['output_file']

    effective_from = parameter['effective_from']

    effective_to = parameter['effective_to']

    output_file = parameter['output_file']



    title_style = """

        .title {

            color: #800000;

            text-align: left;   

        }

            

        .subtitle-1 {

            color: #0000FF;

            font-size: 20px;

            text-align: left;   

        }

        

        .subtitle-2 {

            color: #000080;

            font-size: 16px;

            text-align: left;   

        }

    """    

    titles = ["Trade Number", "Trader/Dealer", "New CTPTY Reff", "New CTPTY CIF", "Registration Status"]



    html_content = html_gen.create_base_html_content("", additional_styles=additional_style)

    html_content += "<table>"

    html_content += "<tr></tr>"

    html_content += div_side_by_side

    html_content = prepare_title(html_content)

    html_content += "<td colspan='20' style='border:0px;'></td>"

    html_content += end_div_side_by_side
    html_content += div_side_by_side

    html_content = prepare_workdays_table(html_content)

    html_content += "<td style='border:0px;' colspan='2'></td>"

    html_content = prepare_vol_today_table(html_content)

    html_content += "<td style='border:0px;' colspan='2'></td>"

    html_content = prepare_vol_yearly_table(html_content)

    html_content += "<td style='border:0px;' colspan='2'></td>"

    html_content = prepare_percent_yearly_table(html_content)

    html_content += end_div_side_by_side

    html_content += "<tr><td colspan='20' style='border:0px;'></td></tr>"

    html_content = prepare_data_table(html_content, effective_from, effective_to)

    html_content += "</table>"

    html_content = html_content.replace("nan", "0")    
    
    html_content = html_gen.close_html_table(html_content)

    current_date = get_current_date("-")

    file_url = html_gen.create_html_file(html_content, file_path, report_name, current_date, open_html=True, folder_with_file_name=True)

    if ".xls" in output_file:

        generate_file_for_other_extension(file_url , ".xls")
