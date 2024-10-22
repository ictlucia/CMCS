import string
import os
from datetime import date
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

def getFilePathSelection():

    """ Directory selector dialog """

    selection = acm.FFileSelection()

    selection.PickDirectory(True)

    selection.SelectedDirectory = r"C:\\"

    return selection

def get_trdnbr(optkey3_list, optkey4_list, portfolio):  
    use_where = " WHERE " if optkey3_list and optkey4_list else ""
    optkey3 = f" DISPLAY_ID(t, 'optkey3_chlnbr') IN {optkey3_list} AND" if optkey3_list else ""
    optkey4 = f" DISPLAY_ID(t, 'optkey4_chlnbr') IN {optkey3_list}" if optkey3_list else ""
    
    query_string = f"""
        SELECT 
            t.trdnbr
        FROM
            Trade t
        {use_where} 
    """ + optkey3 + optkey4
    
    return [x[0] for x in ael.asql(query_string)[1][0]]

def get_value_row(trdnbr_list, bussiness_status=""):
    principal_amount = 0
    
    for trdnbr in trdnbr_list:
        trade = acm.FTrade[trdnbr]
        try :
            business_status_trade = trade.Counterparty().AdditionalInfo().Business_Status()
        except :
            business_status_trade = None
        
        if business_status_trade == bussiness_status:
            try :
                principal_amount += trade.Price() * trade.Nominal()
            except :
                continue
    
    return principal_amount

### TABLE HEADER, TITLE, SUBTITLE, AND VALUE CONTENT
## HEADER CONTENT AND SPAN FORMATING
row_header_1 = ["I. Analysis of products reported in Section II of Part 1A, 1B &amp; 1C", "Principal amount"]
row_header_2 = ["Traditional", "Synthetic"]
row_header_3 = ["II. Securitization exposures incurred as originating institution not reported in Section II item (J) of Part 1A, 1B &amp; 1C", "Principal amount"]
row_header_4 = ["III. Use of credit derivatives (e.g. CDS, total return swaps) to hedge the debt securities reported in Part 1A, 1B &amp; 1C", "Notional amount", "Current market value"]

header_cell_span_1 = [["2", "2"], ["2", "1"]]
header_cell_span_2 = [["1", "1"], ["1", "1"]]
header_cell_span_3 = [["2", "1"], ["1", "1"]]
header_cell_span_4 = [["2", "1"], ["1", "1"], ["1","1"]]

row_header = [row_header_1, row_header_2, row_header_3, row_header_4]
header_cell_span = [header_cell_span_1, header_cell_span_2, header_cell_span_3, header_cell_span_4]

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 3A
title_A = ["Part 1A - Holdings in debt securities (banking book - Fair value through other comprehensive income/Fair value through profit or loss)", ""]

traditional_1 = get_trdnbr("('BOND')", "('ORI', 'INDOIS', 'SVBLCY', 'SVBUSD', 'UST')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')")
traditional_2 = get_trdnbr("('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')")

# BAB 1
subtitle_A1 = ["(A) By type of underlying assets", ""]
contents_dict_A1 = {
    "(a) Claims on sovereigns" : [get_value_row(traditional_1, "Sovereign"), 0],
    "(b) Claims on public sector entities" : [get_value_row(traditional_2, "Public sector entities"), 0],
    "(c) Claims on banks" : [get_value_row(traditional_2, "Banks"), 0],
    "(d) Claims on non-bank financial institutions" : [get_value_row(traditional_2, "Non-bank financial institution"), 0],
    "(e) Claims on corporates" : [get_value_row(traditional_2, "Corporate"), 0],
    "(f) Commercial mortgage loans" : [0, 0],
    "(g) Residential mortgage loans" : [0, 0],
    "&ensp;(i) of which non-prime 1" : [0, 0],
    "(h) Credit card receivables" : [0, 0],
    "&ensp;(i) of which non-prime 2" : [0, 0],
    "(i) Other personal lending (e.g. auto, student, etc.)" : [0, 0],
    "&ensp;(i) of which non-prime 3" : [0, 0],
    "(j) Leveraged loans / SME loans" : [0, 0],
    "(k) Other" : [0, 0],
    "(l) Total": [0] * 2
}

for key, items in contents_dict_A1.items():
    if key == "(l) Total" :
        contents_dict_A1["(l) Total"] = [round(x, 2) for x in contents_dict_A1["(l) Total"]]
        break
    for i, val in enumerate(items):
        contents_dict_A1["(l) Total"][i] += round(float(val), 1)

# BAB 2
subtitle_A2 = ["(B) By type of products", ""]
contents_dict_A2 = {
    "(a) Sukuk" : [0, 0],
    "(b) CDOs" : [0, 0],
    "(c) SIV notes" : [0, 0],
    "(d) ABCPs" : [0, 0],
    "(e) MBSs" : [0, 0],
    "(f) ABSs" : [0, 0],
    "(g) Other" : [0, 0],
    "(h) Resecuritization transactions" : [0, 0],
    "(i) Total" : [0] * 2
}

for key, items in contents_dict_A1.items():
    if key == "(l) Total" :
        contents_dict_A1["(l) Total"] = [round(x, 2) for x in contents_dict_A1["(l) Total"]]
        break
    for i, val in enumerate(items):
        contents_dict_A1["(l) Total"][i] += round(float(val), 1)

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 3B
title_B= ["Part 1B - Holdings in debt securities (banking book)", ""]

# BAB 1
subtitle_B1 = ["I. Debt securities other than those reported in section II below", ""]
contents_dict_B1 = {
    "(A) Securitization exposures (except drawn amount reported in Survey on Off-balance Sheet Exposures in Derivatives and Securitization Transactions)" : ["0"] * 1
}

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 3C
title_C = ["Part 1C - Holdings in debt securities (Trading book)", ""]

# BAB 1
subtitle_C1 = ["I. Debt securities other than those reported in section II below", ""]
contents_dict_C1 = {
    "(A) Total protection bought" : [0, 0],
    "&emsp; of which: reference entity / reference obligation is" : [""] * 1,
    "&emsp;&ensp;(a) a single name (individual entity)" : [0, 0],
    "&emsp;&ensp;(b) multiple names (more than one entity)" : [0, 0],
    "&emsp;&ensp;(c) an index" : [0, 0],
    "&emsp;&ensp;(d) others" : [0, 0]
}


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
<h1>Part 3 - Supplementary information to Part 1</h1>
<p>In HK$&#39;000</p>
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
        if any(key in key_content for key in [f"({alphabeth})" for alphabeth in list(string.ascii_uppercase)]):
            html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;">&emsp;{key_content}</td>\n'
            

        else:
            if any(x in key_content for x in ["(l) Total", "(i) Total"]):
                if "(i) Total" in key_content:
                    html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;"><b>&emsp;{key_content}</b>&nbsp;(Amount should be same as (A)(l))</td>\n'
                else:
                    html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px; font-weight: bold;">&emsp;{key_content}</td>\n'
            else :
                if any(x in key_content for x in ["&ensp;(i) of which non-prime 1", "&ensp;(i) of which non-prime 2", "&ensp;(i) of which non-prime 3"]):
                    html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;">&emsp;{"&ensp;(i) of which non-prime"}</td>\n'
                else:
                    html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;">&emsp;{key_content}</td>\n'

        for i, val_content in enumerate(list_val_content):
            border_sty = "1px solid black"
            if "Total" in key_content:
                content_style = f'background-color:{"#87e8a1" if i <= 1 else ""};border-bottom: {border_sty}; border-left: {border_sty}; border-right: {border_sty if i == len(list_val_content) - 1 else ""}; width: 180px'
            else:
                if "&emsp; of which: reference entity / reference obligation is" in key_content:
                    content_style = f'background-color:{"#999897" if i <= 1 else ""};border-bottom: {border_sty}; border-left: {border_sty}; border-right: {border_sty if i == len(list_val_content) - 1 else ""}; width: 180px' 
                else:
                    content_style = f'background-color:{"" if i <= 1 else "#87e8a1"};border-bottom: {border_sty}; border-left: {border_sty}; border-right: {border_sty if i == len(list_val_content) - 1 else ""}; width: 180px'
            
            val_content = val_content if val_content else 0
            if "&emsp; of which: reference entity / reference obligation is" in key_content:
                html_code += f'<td style="text-align: right; {content_style}" colspan="2">{f"{float(val_content):,}"}</td>\n'
            else:
                html_code += f'<td style="text-align: right; {content_style}">{f"{float(val_content):,}"}</td>\n'
            
        html_code += "</tr>\n" 
    
    return html_code

def template_order_table(code,list_template_order, title_style='', subtitle_style='', skip_row=''):
    for template_order in list_template_order:
        if template_order in [title_A, title_B, title_C] :
            code += title_subtitle(template_order, style=title_style)
        elif template_order == skip_row:
            code += template_order
        elif template_order in [subtitle_A1, subtitle_A2, subtitle_B1, subtitle_C1]:
            code += title_subtitle(template_order, style=subtitle_style)
        else :
            code += table_body(template_order)
    return code

def html_to_xls(report_folder, report_name):
    skip_row = '<tr><td>&nbsp;</td><td colspan="3" style="border-bottom: 1px solid">&nbsp;</td></tr>'
    skip_row2 = '<tr><td>&nbsp;</td><td colspan="4" style="border-bottom: 1px solid">&nbsp;</td></tr>'
    code = open_table()
    code += table_header(row_header[:2], header_cell_span[:2])

    title_style = "font-weight: bold; border-left: 1px solid black; border-right: 1px solid black;"
    subtitle_style = "font-weight: bold; background-color:#999897; border-left: 1px solid black; border-right: 1px solid black;"
    list_template_order = [
                      subtitle_A1, contents_dict_A1, subtitle_A2, contents_dict_A2, skip_row,
                      contents_dict_B1, skip_row,
                      contents_dict_C1,
                      ]

    code = template_order_table(code,list_template_order[:5], title_style, subtitle_style, skip_row)
    
    code += table_header(row_header[2:-1], header_cell_span[2:-1])
    
    code = template_order_table(code,list_template_order[5:7], title_style, subtitle_style, skip_row)
    
    code += table_header(row_header[-1:], header_cell_span[-1:])
    
    code = template_order_table(code,list_template_order[7:], title_style, subtitle_style, skip_row)
    
    
    file_path = os.path.join(report_folder, report_name)
    f = open(file_path, "w")
    f.write(code + "</table></body></html>")
    f.close()

##################################################################################

# CREATING A GUI PARAMETER

##################################################################################
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'HKCO01c - ICC - HKMAs Survey on Debt Securities Held'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'HKCO01c - ICC - HKMAs Survey on Debt Securities Held', 1,0],
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
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    if ".xls" in output_file:
        html_to_xls(report_folder, report_name)
