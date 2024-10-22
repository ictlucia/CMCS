import string
import os
from datetime import date
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from Report_Python_P2 import usd_price_mtm

def getFilePathSelection():

    """ Directory selector dialog """

    selection = acm.FFileSelection()

    selection.PickDirectory(True)

    selection.SelectedDirectory = r"C:\\"

    return selection

##################################################################################################
# GENERATE QUERY VALUE
##################################################################################################

def get_trdnbr(curr_code, prfid): 
    """
    All field using the same product Type & product code.
    The Different of the field is on the Porfolio that used.
    """
    query_string = f"""
        SELECT 
            t.trdnbr
        FROM
            Trade t, Instrument i
        WHERE 
            t.insaddr = i.insaddr AND 
            DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND' AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'INDOIS', 'NCD', 'SBBI') AND
            i.instype = 'Bond' AND
            DISPLAY_ID(t, 'prfnbr') IN {prfid}
    """
    
    query_results = ael.asql(query_string)[1][0]
    trdnbr_list = []
    for query_result in query_results:
        trdnbr = query_result[0]
        try :
            if acm.FTrade[trdnbr].Currency().Name() == curr_code:
                trdnbr_list.append(trdnbr)
        except :
            continue
    
    return trdnbr_list

def get_trdnbr_except(curr_list, prfid):    
    query_string = f"""
        SELECT 
            t.trdnbr
        FROM
            Trade t, Instrument i
        WHERE 
            t.insaddr = i.insaddr AND 
            DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND' AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'INDOIS', 'NCD', 'SBBI') AND
            i.instype = 'Bond' AND
            DISPLAY_ID(t, 'prfnbr') IN {prfid}
    """
            
    query_results = ael.asql(query_string)[1][0]
    trdnbr_list = []
    for query_result in query_results:
        trdnbr = query_result[0]
        try :
            if acm.FTrade[trdnbr].Currency().Name() not in curr_list:
                trdnbr_list.append(trdnbr)
        except :
            continue
    
    return trdnbr_list

def get_value(trdinfo_list, use_bookval, long_pos): 
    row_val = [0] if use_bookval == False else [0, 0]
    
    for trdnbr in trdinfo_list:
        trade = acm.FTrade[trdnbr]
                    
        context = acm.GetDefaultContext()
        columnId_bookVal = 'Portfolio Book Cash Value'
        columnId_marketVal = 'Portfolio PL Market Value'
            
        calcSpace = acm.Calculations().CreateCalculationSpace(context, 'FTradeSheet')
        calculation_mv = calcSpace.CreateCalculation(trade, columnId_marketVal).FormattedValue().replace(".", "").replace(",", ".")
            
        amt = calculation_mv if calculation_mv != "" else 0
        if use_bookval != False:
            calculation_bv = calcSpace.CreateCalculation(trade, columnId_bookVal).FormattedValue().replace(".", "").replace(",", ".")
            bookval = calculation_bv if calculation_bv != "" else 0
                
        # "Long positions only" will be calculated if AMT value of trade is Positive (>0)
        if long_pos == True:
            amt = "".join([x for x in str(amt) if x.isdigit() or x == "." or x == "-"])
            amt = amt if amt != "" else 0
            if float(amt) >= 0 :
                result_trade = [amt] if use_bookval == False else [amt, bookval]
            else :
                result_trade = [0] if use_bookval == False else [0, 0]
        else :
            result_trade = [amt] if use_bookval == False else [amt, bookval]
        
        if trade.Instrument().Currency().Name() != "USD" :
            usd_rate = usd_price_mtm(trade, curr_target='USD') if usd_price_mtm(trade, curr_target='USD') != None else 1
        else :
            usd_rate = 1
        
        for i, _ in enumerate(result_trade):
            add_val = "".join([x for x in str(result_trade[i]) if x.isdigit() or x == "." or x == "-"])
            add_val = add_val if add_val != "" else 0
            row_val[i] += float(add_val) * usd_rate
    
    return row_val

def get_val_dict(currency_list, list_code):
     """
        1. ('BB BOND OCI BMHK', 'BB BOND PL BMHK') is Porfolio for field : "Fair value through other comprehensive income/Fair value through profit or loss"
        2. "('BB BOND AC BMHK')" is Porfolio for field : "Amortised cost"
        3. Last 2 portfolio is Portfolio for field : "Trading book" ("Long positions only" and "Both long and short positions)
            > The Different for "Long positions only" and "Both long and short positions on a net basis" field is by the value of AMT.
            > "Long positions only" will be calculated if AMT value of trade is Positive (>0)
    """
    port_list_2d = [
        "('BB BOND OCI BMHK', 'BB BOND PL BMHK')",
        "('BB BOND AC BMHK')",
        "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')",
        "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"
    ]
    
    use_bookval_list = [False, True, False, False]
    long_pos_list = [False, False, True, False]
    
    new_data_dict = {}
    add_val_list = [0] * 5
    for currency, code in zip(currency_list, list_code):
        row_values = []
        for port_list, use_bookval, long_pos in zip(port_list_2d, use_bookval_list, long_pos_list):
            trdnbr_list = get_trdnbr(code, port_list)
            val_per_port = get_value(trdnbr_list, use_bookval, long_pos)
            row_values.extend(val_per_port)
        
        print([currency, code] + [x if x != 0 else "" for x in row_values])
        new_data_dict[currency] = [code] + [x if x != 0 else "" for x in row_values]
        
        for i, _ in enumerate(row_values):
            add_val_list[i] += float(row_values[i])
    
    row_values = []
    for port_list, use_bookval, long_pos in zip(port_list_2d, use_bookval_list, long_pos_list):
        trdnbr_list = get_trdnbr_except(currency_list, port_list)
        val_per_port = get_value(trdnbr_list, use_bookval, long_pos)
        row_values.extend(val_per_port)
    
    for i, _ in enumerate(row_values):
        add_val_list[i] += float(row_values[i])
    
    new_data_dict["Currencies not specified above"] = ["OTH"] + [x if x != 0 else "" for x in row_values]
    
    new_data_dict["Total"] = ['TOT'] + [x if x != 0 else "" for x in add_val_list]
    
    return new_data_dict

### TABLE HEADER, TITLE, SUBTITLE, AND VALUE CONTENT
## HEADER CONTENT AND SPAN FORMATING
row_header_1 = ["Currency", "Banking book", "Trading book"]
row_header_2 = ["Fair value through other comprehensive income/Fair value through profit or loss", "Amortised cost", "Long positions only", "Both long and short positions on a net basis"]
row_header_3 = (["AMT"] + ["AMT", "Book value"]) + (["AMT"] * 2)

header_cell_span_1 = [["2", "3"], ["3", "1"], ["2", "1"]]
header_cell_span_2 = [["1", "1"], ["2", "1"], ["1", "1"], ["1", "1"]]
header_cell_span_3 = [["1", "1"]] + [["1", "1"]] * 4

row_header = [row_header_1, row_header_2, row_header_3]
header_cell_span = [header_cell_span_1, header_cell_span_2, header_cell_span_3]

# ------------------------------------------------------------------------------------------------------------------------------------------
currency_list = ["Australian dollars", "Canadian dollars", "Chinese renminbi", "Euro", "Hong Kong dollars", "Japanese yen", "New Zealand dollars", "Pound sterling", "Singapore dollars", "Swiss Francs",
                 "US dollars"]

code_list = ["AUD", "CAD", "CNY", "EUR", "HKD", "JPY", "NZD", "GBP", "SGD", "CHF", "USD"]

############################################################################################
# GENERATING HTML CODE & CONVERT TO XLS 
############################################################################################
def open_table():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
<h1>Part 5 - Denomination of currency</h1>
<p>AMT (current market value unless otherwise specified) In HK$&#39;000</p>
<table style="width: fit-content">
"""

## HEADER TEMPLATE OF HTML 
def table_header(row_header, header_cell_span):
    style_1 = "text-align : center; font-weight:bold; border:1px solid black; vertical-align: middle;"
    style_2 = "text-align : center; font-weight:bold; border-left:1px solid black; border-right:1px solid black; vertical-align: middle;"
    style_3 = "text-align : center; font-weight:bold; border-left:1px solid black; border-right:1px solid black; border-bottom:1px solid black; vertical-align: middle;"
    html_code = ""

    i = 0
    for row_header_list, span_header_list in zip(row_header, header_cell_span):
        i += 1
        html_code += '<tr>\n<td style="width: 15px"></td>\n'
        for header_content, cell_span in zip(row_header_list, span_header_list):
            background_color_condition = i == 3 and header_content == ""
            style_condition = header_content not in [row_header_2[0], ""] and i != 4
            style_condition2 = header_content not in [row_header_2[0], ""]
            style = f'background-color:{"black" if background_color_condition else "white"};{style_1 if style_condition else style_3 if i == 4 else style_2}'
            html_code += f'<td style="{style}" colspan="{cell_span[0]}" rowspan="{cell_span[1]}"> {header_content} </td>\n'
        html_code += "</tr>\n"
    return html_code

def title_subtitle(list_content, style=''):
    html_code = '<tr>\n<td style="width: 15px"></td>\n'
    for content in list_content:
        cond = 'colspan="2"' if content == "" else 'colspan="2"'
        html_code += f'<td style="{style}" {cond}>{content}</td>' + "\n"
    html_code += "</tr>\n"
    
    return html_code
    
## BODY TEMPLATE OF HTML
def table_body(content_dict, style='', space=2):
    html_code = ""
        
        #elif any(x in key_content for x in ["(i)", "(ii)", "(iii)", "(iv)", "(v)", "(vi)", "(vii)", "(viii)"]):
            #html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;">{"&emsp;&emsp;- of which:<br>" if "(i)" in key_content and space == 2 else  ""}{"&emsp;" * space}{key_content}</td>\n'

    for key_content, list_val_content in content_dict.items():
        html_code += '<tr>\n<td style="width: 15px"></td>\n'
        html_code += f'<td style="border-bottom: 1px solid black; border-left: 1px solid black; width:225px;">{key_content}</td>\n'

        for i, val_content in enumerate(list_val_content):
            border_sty = "1px solid black"
            background_total = "background-color: #cffcd7;" if key_content == "Total" and i != 0 else ""
            content_style = f'{background_total} text-align:{"center" if i == 0 else "right"}; border-bottom: {border_sty}; border-right: {border_sty}; border-left {border_sty if i == 0 else ""}; width: 200px'
            
            html_code += f'<td style="text-align: right; {content_style}">{val_content}</td>\n'
        
        html_code += "</tr>\n" 
    
    return html_code

def template_order_table(code,list_template_order, title_style='', subtitle_style='', skip_row=''):
    for template_order in list_template_order:
        code += table_body(template_order)
    return code

def html_to_xls(data_dict, report_folder, report_name):
    skip_row = '<tr><td>&nbsp;</td><td colspan="3" style="border-bottom: 1px solid">&nbsp;</td></tr>'
    skip_row2 = '<tr><td>&nbsp;</td><td colspan="4" style="border-bottom: 1px solid">&nbsp;</td></tr>'
    code = open_table()
    code += table_header(row_header, header_cell_span)

    title_style = "font-weight: bold; border-left: 1px solid black; border-right: 1px solid black;"
    subtitle_style = "font-weight: bold; background-color:#999897; border-left: 1px solid black; border-right: 1px solid black;"
    list_template_order = [
                      data_dict
                      ]

    code = template_order_table(code,list_template_order, title_style, subtitle_style, skip_row)
    
    
    
    file_path = os.path.join(report_folder, report_name)
    f = open(file_path, "w")
    f.write(code + "</table></body></html>")
    f.close()

##################################################################################

# CREATING A GUI PARAMETER

##################################################################################
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'HKCO01e - ICC - HKMAs Survey on Debt Securities Held'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'HKCO01e - ICC - HKMAs Survey on Debt Securities Held', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Output Files','string', ['.pdf', '.xls'], '.xls', 0 , 0, 'Select Output Extension Type']
]

def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = parameter['report_name'] + ".xls"
    file_path = str(parameter['file_path'])
    output_file = "".join(parameter['output_file'])
    
    folder_name = "report"+date.today().strftime("%Y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    
    data_dict = get_val_dict(currency_list, code_list)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    if ".xls" in output_file:
        html_to_xls(data_dict, report_folder, report_name)
