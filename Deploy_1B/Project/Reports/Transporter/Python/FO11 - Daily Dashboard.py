from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import ael
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
    font-weight: bold;
}
"""
def prepare_sum_vol_1_table(html_content):
    non_idr_query = ael.asql("SELECT sum(quantity) FROM trade WHERE creat_time=TODAY AND curr~=230 AND insaddr~= 230")[1]
    mds_query = ael.asql("SELECT sum(quantity) FROM trade WHERE creat_time=TODAY AND optkey3_chlnbr=391 AND optkey4_chlnbr=337")[1]
    valas_beli_query = ael.asql("SELECT sum(quantity) FROM trade WHERE creat_time=TODAY AND curr~=230 AND insaddr~= 230 AND quantity > 0")[1]
    valas_jual_query = ael.asql("SELECT sum(quantity) FROM trade WHERE creat_time=TODAY AND curr~=230 AND insaddr~= 230 AND quantity < 0")[1]
    swap_query = ael.asql("SELECT sum(abs(quantity/2)) FROM trade where creat_time=TODAY and optkey3_chlnbr = 386 and optkey4_chlnbr = 377")[1]
    
    non_idr_result = non_idr_query[0][0][0] if len(non_idr_query[0]) > 0 else 0
    mds_result = mds_query[0][0][0] if len(mds_query[0]) > 0 else 0
    valas_beli_result = valas_beli_query[0][0][0] if len(valas_beli_query[0]) > 0 else 0
    valas_jual_result = valas_jual_query[0][0][0] if len(valas_jual_query[0]) > 0 else 0
    swap_result = swap_query[0][0][0] if len(swap_query[0]) > 0 else 0

    row_name = [["Jual-Beli Non IDR", non_idr_result], ["MDS", mds_result], ["Nasabah Beli Valas", valas_beli_result], ["Nasabah Jual Valas", valas_jual_result], ["Swap", swap_result], ["Grand Total", 0]]
    sum_of_row = sum(value for name, value in row_name)
    row_name[-1][1] = sum_of_row
    
        
    col_name = ["", "Sum of VOL(USD)"]
    
    html_content += "<td style='border:0px;' colspan='2'>"
    
    html_content = html_gen.prepare_html_table(html_content, col_name)
    html_content = html_gen.add_data_row(html_content, row_name)
    html_content = html_gen.close_html_table(html_content)
    html_content += "</td>"
    html_content += "<td style='border:0px;'></td>"
    
    return html_content
    
def prepare_sum_vol_2_table(html_content):
    query = """
    SELECT sum(abs(quantity)) 
    FROM trade t, portfolio p 
    WHERE t.prfnbr = p.prfnbr 
    AND t.creat_time=TODAY
    AND (p.prfid = 'Banknotes Branch Settlement' OR p.prfid = 'Banknotes Export Import' OR p.prfid='Banknotes Interbank' OR p.prfid='Banknotes Trader')
    """
    query_result = ael.asql(query)[1]
    bank_notes = query_result[0][0][0] if len(query_result[0]) > 0 else 0
    
    query = """
    SELECT sum(abs(quantity))
    FROM trade t, portfolio p
    WHERE t.prfnbr = p.prfnbr 
    AND t.creat_time=TODAY
    AND (p.prfid = 'Retail FX BO' OR p.prfid = 'Retail FX Branch' OR p.prfid='Retail SP')
    
    """
    query_result = ael.asql(query)[1]
    retail = query_result[0][0][0] if len(query_result[0]) > 0 else 0
    
    query = """
    SELECT sum(abs(quantity))
    FROM trade t, portfolio p 
    WHERE t.prfnbr = p.prfnbr
    AND t.creat_time=TODAY
    AND (p.prfid = 'Wholesale FX Branch' OR p.prfid = 'Wholesale FX & Derivative BO')
    """
    
    query_result = ael.asql(query)[1]
    wholesale = query_result[0][0][0] if len(query_result[0]) > 0 else 0
    
    row_name = [["Banknotes", bank_notes], ["Retail", retail], ["Wholesale", wholesale], ["Grand Total", 0]]
    sum_of_row = sum(value for name, value in row_name)
    row_name[-1][1] = sum_of_row
    
    col_name = ["", "Sum of VOL(USD)"]
    html_content += "<td style='border:0px;' colspan='2'>"
    html_content = html_gen.prepare_html_table(html_content, col_name)
    html_content = html_gen.add_data_row(html_content, row_name)
    html_content = html_gen.close_html_table(html_content)
    html_content += "</td>"
    html_content += "<td style='border:0px;'></td>"
    return html_content
def prepare_nasabah_jual_table(html_content):
    sell_query = ael.asql("SELECT p.ptyid, sum(abs(t.quantity)) 'Volume' FROM trade t, party p WHERE p.ptynbr = t.counterparty_ptynbr AND t.quantity < 0 AND t.creat_time = TODAY GROUP BY p.ptyid ORDER BY 2 desc")[:10]
    sell_query = sell_query[1][0][:10]
    
    row_name = []
    
    for i in range(len(sell_query)):
        row_name.append([i + 1, sell_query[i][0], sell_query[i][1]]) 
    
    col_name = ["No", "Nasabah Jual", "Volume Amount"]
    html_content += "<td style='border:0px;' colspan='3'>"
    html_content = html_gen.prepare_html_table(html_content, col_name)
    html_content = html_gen.add_data_row(html_content, row_name)
    html_content = html_gen.close_html_table(html_content)
    html_content += "</td>"
    html_content += "<td style='border:0px;'></td>"
    return html_content
def prepare_nasabah_beli_table(html_content):
    buy_query = ael.asql("SELECT p.ptyid, sum(t.quantity) 'Volume' FROM trade t, party p WHERE p.ptynbr = t.counterparty_ptynbr AND t.quantity > 0 AND t.creat_time = TODAY GROUP BY p.ptyid ORDER BY 2 desc")[:10]
    buy_query = buy_query[1][0][:10]
    
    row_name = []
    
    for i in range(len(buy_query)):
        row_name.append([i + 1, buy_query[i][0], buy_query[i][1]]) 
    
    col_name = ["No", "Nasabah Beli", "Volume Amount"]
    html_content += "<td style='border:0px;' colspan='3'>"
    html_content = html_gen.prepare_html_table(html_content, col_name)
    html_content = html_gen.add_data_row(html_content, row_name)
    html_content = html_gen.close_html_table(html_content)
    html_content += "</td>"
    
    return html_content
    
def prepare_average_rate(html_content):
    
    buy_query = ael.asql("SELECT avg(quantity) FROM trade where creat_time=TODAY and optkey3_chlnbr = 386 and optkey4_chlnbr = 377 and quantity > 0")
    sell_query = ael.asql("SELECT avg(quantity) FROM trade where creat_time=TODAY and optkey3_chlnbr = 386 and optkey4_chlnbr = 377 and quantity < 0")
    
    avg_buy_value = buy_query[1][0][0][0] if len(buy_query[1][0]) else 0
    avg_sell_value = sell_query[1][0][0][0] if len(sell_query[1][0]) else 0
    
    row_name = [["P", avg_buy_value], ["S", avg_sell_value]]
    col_name = ["P/S", "Average Rate"]
    
    html_content += "<td style='border:0px;' colspan='2'>"
    html_content = html_gen.prepare_html_table(html_content, col_name)
    html_content = html_gen.add_data_row(html_content, row_name)
    
    spread_row = [["Spread", abs(avg_buy_value - avg_sell_value)]]
    html_content = html_gen.add_data_row(html_content, spread_row, "class='bold-with-border'")
    html_content = html_gen.close_html_table(html_content)
    html_content += "</td>"
    html_content += "<td style='border:0px;'>"
    html_content += "</td>"
    return html_content
    
def prepare_sum_open_table(html_content):
    query = """
    SELECT sum(abs(nominal_amount(t))) 
    FROM Trade t
    WHERE t.optkey4_chlnbr=378
    AND t.creat_time=TODAY
    """
    query_result = ael.asql(query)[1]
    tod_result = query_result[0][0][0] if len(query_result[0]) > 0 else 0
    
    query_2 = """SELECT sum(abs(nominal_amount(t))) 
    FROM Trade t
    WHERE t.optkey4_chlnbr=379
    AND t.creat_time=TODAY
    """
    query_result = ael.asql(query_2)[1]
    tom_result = query_result[0][0][0] if len(query_result[0]) > 0 else 0
    
    query_3 = """SELECT sum(abs(nominal_amount(t))) 
    FROM Trade t
    WHERE t.optkey4_chlnbr=374
    AND t.creat_time=TODAY
    """
    query_result = ael.asql(query_3)[1]
    spot_result = query_result[0][0][0] if len(query_result[0]) > 0 else 0
        
    row_name = [["1. Today", tod_result], ["2. Tom", tom_result], ["3. Spot++", spot_result]]
    col_name = ["", "Sum of OPEN"]
    
    html_content += "<td style='border:0px;' colspan='2'>"
    html_content = html_gen.prepare_html_table(html_content, col_name)
    html_content += "<br>"
    html_content = html_gen.add_data_row(html_content, row_name)
    
    open_position = [["Open Position", 10.0]]
    html_content = html_gen.add_data_row(html_content, open_position, "class='bold-with-border'")
    
    non_today_gapping = [["Non Today Gapping", 10.0]]
    html_content = html_gen.add_data_row(html_content, non_today_gapping, "class='bold-with-border'")
    html_content = html_gen.close_html_table(html_content)
    html_content += "</td>"
    html_content += "<td style='border:0px;'>"
    html_content += "</td>"
    return html_content
    
def prepare_outstanding_table(html_content):
    query_1 = """
    SELECT sum(abs(nominal_amount(t)))
    FROM Trade t
    WHERE t.optkey3_chlnbr=386
    AND t.optkey4_chlnbr=311
    AND t.value_day between TODAY AND date_add_banking_day(TODAY, , 6)
    """
    query1_result = ael.asql(query_1)[1]
    query1_result = query1_result [0][0][0] if len(query1_result [0]) > 0 else 0
    
    query_2 = """
    SELECT sum(abs(nominal_amount(t)))
    FROM Trade t
    WHERE t.optkey3_chlnbr=386
    AND t.optkey4_chlnbr=311
    AND t.value_day between date_add_banking_day(TODAY, , 7) AND date_add_banking_day(TODAY, , 13)
    """
    query_2_result = ael.asql(query_2)[1]
    query_2_result = query_2_result [0][0][0] if len(query_2_result [0]) > 0 else 0
    query_3 = """
    SELECT sum(abs(nominal_amount(t)))
    FROM Trade t
    WHERE t.optkey3_chlnbr=386
    AND t.optkey4_chlnbr=311
    AND t.value_day between date_add_banking_day(TODAY, , 14) AND date_add_banking_day(TODAY, , 29)
    """
    query_3_result = ael.asql(query_3)[1]
    query_3_result = query_3_result [0][0][0] if len(query_3_result [0]) > 0 else 0
    query_4 = """
    SELECT sum(abs(nominal_amount(t)))
    FROM Trade t
    WHERE t.optkey3_chlnbr=386
    AND t.optkey4_chlnbr=311
    AND t.value_day between date_add_banking_day(TODAY, , 30) AND date_add_banking_day(TODAY, , 89)
    """
    query_4_result = ael.asql(query_4)[1]
    query_4_result = query_4_result [0][0][0] if len(query_4_result [0]) > 0 else 0
    
    query_5 = """
    SELECT sum(abs(nominal_amount(t)))
    FROM Trade t
    WHERE t.optkey3_chlnbr=386
    AND t.optkey4_chlnbr=311
    AND t.value_day >= date_add_banking_day(TODAY, , 90)
    """
    query_5_result = ael.asql(query_5)[1]
    query_5_result = query_5_result [0][0][0] if len(query_5_result [0]) > 0 else 0
    row_name = [["1. < 7 days", query1_result], ["2. 7 days - < 14 days", query_2_result], ["3. 14 days - < 30 days", query_3_result], ["4. 30 days - < 90 days", query_4_result], ["4. >= 90 days", query_5_result], ["Grand Total", 0]]
    sum_of_row = sum(int(value) for name, value in row_name)
    row_name[-1][1] = sum_of_row
    
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
    
def prepare_open_position1_table(html_content):
    
    query = """
    SELECT t.insaddr, t.curr, sum(abs(nominal_amount(t)))
    FROM trade t
    WHERE t.quantity > 0 
    AND optkey3_chlnbr = 386
    AND t.creat_time = TODAY
    GROUP BY 1, 2
    ORDER BY 3 DESC
    """
    
    result_query = ael.asql(query, 1)[1][0][10:17]
    row_name = []
    for i in range(len(result_query)):
        curr1 = result_query[i][0].und_insaddr.insid if result_query[i][0].und_insaddr != None else result_query[i][0].insid
        row_name.append([i + 1, curr1 + "/" + result_query[i][1].insid, result_query[i][2]])
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
def prepare_open_position2_table(html_content):
    query = """
        SELECT t.insaddr, t.curr, sum(abs(nominal_amount(t)))
        FROM trade t
        WHERE t.quantity > 0 
        AND optkey3_chlnbr = 386
        AND t.creat_time = TODAY
        GROUP BY 1, 2
        ORDER BY 3 DESC
        """
        
    result_query = ael.asql(query, 1)[1][0][:10]
    
    row_name = []
    for i in range(len(result_query)):
        curr1 = result_query[i][0].und_insaddr.insid if result_query[i][0].und_insaddr != None else result_query[i][0].insid
        row_name.append([i + 1, curr1 + "/" + result_query[i][1].insid, result_query[i][2]])
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
    html_content += "<td id='marktra' colspan='10' rowspan='2' style='text-align:center'>Marktra Generator</td>"
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
] 
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
      
    html_content = html_gen.create_base_html_content("", additional_styles=additional_style)
    html_content += "<table>"
    html_content += prepare_marktra_html_title(html_content)
    html_content += "<tr></tr><tr></tr>"
    html_content += div_side_by_side
    html_content = prepare_sum_vol_1_table(html_content)
    html_content = prepare_sum_vol_2_table(html_content)
    html_content = prepare_nasabah_jual_table(html_content)
    html_content = prepare_nasabah_beli_table(html_content)
    html_content += end_div_side_by_side

    html_content += "<tr></tr>"

    html_content += "<tr>"
    html_content = prepare_average_rate(html_content)
    html_content += "</tr>"

    html_content += "<tr></tr>"

    html_content += div_side_by_side
    html_content = prepare_sum_open_table(html_content)
    html_content = prepare_outstanding_table(html_content)
    html_content = prepare_open_position1_table(html_content)
    html_content = prepare_open_position2_table(html_content)
    html_content += end_div_side_by_side
    html_content += "</table>"

    current_date = get_current_date("-")
    folder_with_file_name = True
    if report_name == "":
        folder_with_file_name = False
    
    if '.html' in output_file:
        open_html = True
    else:
        open_html = False
    file_url = html_gen.create_html_file(html_content, file_path, report_name, current_date, open_html=open_html, folder_with_file_name=folder_with_file_name)
    
    if '.xls' in output_file:
        generate_file_for_other_extension(file_url , ".xls")
    else:
        pass
