import string
import os
import acm, ael, calendar
from datetime import date
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from Report_Python_P2 import usd_price_mtm
##################################################################################################
# GENERATE QUERY VALUE
##################################################################################################
def get_trdnbr(nation, prfid):        
    query_string = f"""
        SELECT 
            t.trdnbr, t.insaddr
        FROM
            Trade t, Instrument i
        WHERE 
            t.insaddr = i.insaddr AND 
            ((DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND' AND DISPLAY_ID(t, 'optkey4_chlnbr') IN ('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'INDOIS', 'NCD', 'SBBI', 'SVBUSD', 'SVBLCY')) OR 
            (DISPLAY_ID(t, 'optkey3_chlnbr') = 'SBI' AND DISPLAY_ID(t, 'optkey4_chlnbr') IN ('IDSV')))
            AND i.instype = 'Bond' AND
            DISPLAY_ID(t, 'prfnbr') IN {prfid}
    """
            
    query_results = ael.asql(query_string)[1][0]
    
    trdinfo_list = []
    for query_result in query_results:
        trdnbr, insaddr = query_result
        try :
            if acm.FTrade[trdnbr].Counterparty().Country() == nation:
                trdinfo_list.append(query_result)
        except :
            continue
    
    return trdinfo_list
    
def get_trdnbr_except(nation_list, prfid):
    query_string = f"""
        SELECT 
            t.trdnbr, t.insaddr
        FROM
            Trade t, Instrument i
        WHERE 
            t.insaddr = i.insaddr AND 
            ((DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND' AND DISPLAY_ID(t, 'optkey4_chlnbr') IN ('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'INDOIS', 'NCD', 'SBBI', 'SVBUSD', 'SVBLCY')) OR 
            (DISPLAY_ID(t, 'optkey3_chlnbr') = 'SBI' AND DISPLAY_ID(t, 'optkey4_chlnbr') IN ('IDSV')))
            AND i.instype = 'Bond' AND
            DISPLAY_ID(t, 'prfnbr') IN {prfid}
    """
            
    query_results = ael.asql(query_string)[1][0]
    
    trdinfo_list = []
    for query_result in query_results:
        trdnbr, insaddr = query_result
        try :
            if acm.FTrade[trdnbr].Counterparty().Country() not in nation_list:
                trdinfo_list.append([trdnbr, insaddr])
        except :
            continue
    
    return trdinfo_list
    
def get_days_range(trade):
    value_day = datetime.strptime(trade.ValueDay(), "%Y-%m-%d")
    end_date = datetime.strptime(trade.Instrument().EndDate(), "%Y-%m-%d")
    
    try :
    
        val_on_year = float(str(end_date - value_day).split(" ")[0]) / 365
    
    except :
        
        val_on_year = 0
    return val_on_year
    
def get_arm(trdinfo_list):
    unique_ins = list(set([x[1] for x in trdinfo_list]))
    unique_ins.sort()
    
    arm = 0
    for ins in unique_ins:
        total_principal_amount = 0
        day_range_and_principal = []
        trade_used = [trdnbr for trdnbr, insaddr in trdinfo_list if insaddr == ins]
        for trdnbr in trade_used:
            trade = acm.FTrade[trdnbr]
            principal_amount = abs(trade.Nominal()) * abs(trade.Price())
            total_days = get_days_range(trade)
            day_range_and_principal.append([principal_amount, total_days])
            total_principal_amount += principal_amount
        
        for list_val in day_range_and_principal:
            try :
                arm += list_val[0] * (list_val[1] / total_principal_amount)
            except :
                arm += 0
            
    return arm
    
def get_value(trdinfo_list, use_bookval, long_pos): 
    row_val = [0, 0, 0] if use_bookval == False else [0, 0, 0, 0]
    use_trade = []
    
    for trdnbr, insaddr in trdinfo_list:
        trade = acm.FTrade[trdnbr]
                    
        context = acm.GetDefaultContext()
        columnId_IC = 'Instrument Convexity'
        columnId_bookVal = 'Portfolio Book Cash Value'
        columnId_marketVal = 'Portfolio PL Market Value'
            
        calcSpace = acm.Calculations().CreateCalculationSpace(context, 'FTradeSheet')
        calculation_mv = calcSpace.CreateCalculation(trade, columnId_marketVal).FormattedValue().replace(".", "").replace(",", ".")
        try :
            calculation_cv = calcSpace.CreateCalculation(trade, columnId_IC).FormattedValue().replace(".", "").replace(",", ".")
        except :
            calculation_cv = 0
        
        amt = calculation_mv if calculation_mv != "" else 0
        cv01 = calculation_cv if calculation_cv != "" else 0
        
        if use_bookval != False:
            calculation_bv = calcSpace.CreateCalculation(trade, columnId_bookVal).FormattedValue().replace(".", "").replace(",", ".")
            bookval = calculation_bv if calculation_bv != "" else 0
                
        if long_pos == True:
        
            try :
                amt = "".join([x for x in str(amt) if x.isdigit() or x == "." or x == "-"])
                amt = float(amt) if amt != "" else 0
            
            except :
                
                amt = "".join([x for x in str(amt) if x.isdigit() or x == "," or x == "-"])
                amt = float(amt) if amt != "" else 0
                
            if amt >= 0 :
                use_trade.append([trdnbr, insaddr])
                result_trade = [amt, cv01, 0] if use_bookval == False else [amt, bookval, cv01, 0]
            else :
                result_trade = [0, 0, 0] if use_bookval == False else [0, 0, 0, 0]
        else :
            use_trade.append([trdnbr, insaddr])
            result_trade = [amt, cv01, 0] if use_bookval == False else [amt, bookval, cv01, 0]
        
        if trade.Instrument().Currency().Name() != "USD" :
            usd_rate = usd_price_mtm(trade, curr_target='USD') if usd_price_mtm(trade, curr_target='USD') != None else 1
        else :
            usd_rate = 1
        
        for i, _ in enumerate(result_trade):
        
            try :
                add_val = "".join([x for x in str(result_trade[i]) if x.isdigit() or x == "." or x == "-"])
                add_val = float(add_val) if add_val != "" else 0
            
            except :
                
                add_val = "".join([x for x in str(result_trade[i]) if x.isdigit() or x == "," or x == "-"])
                add_val = float(add_val) if add_val != "" else 0
                
            row_val[i] += float(add_val) * usd_rate
    
    arm = get_arm(use_trade)
    row_val[-1] = f"{arm:.2f}" if arm != 0 else 0
    
    return row_val
    
def get_val_dict(nation_list_2d, list_code):
    region_list = ["Developed countries", "Offshore centres", "Developing Europe" , "Developing Latin America and Caribbean", "Developing Africa and Middle East", "Developing Asia and Pacific"]
    code_list_region = ['5R', '1N', '3C', '4U', '4W', '4Y']
    port_list_2d = [
        "('BB BOND OCI BMHK', 'BB BOND PL BMHK')",
        "('BB BOND AC BMHK')",
        "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')",
        "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"
    ]
    
    use_bookval_list = [False, True, False, False]
    long_pos_list = [False, False, True, False]
    
    new_data_dict = {
            "1. International organisations" : ["1C"] + [0] * 13,
            "2. Analysis by jurisdiction" : ["&nbsp;"]
    }
    
    add_val_list = [0] * 13
    
    code_i = 0
    for region_i, nation_list in enumerate(nation_list_2d) :
        new_data_dict[region_list[region_i]] = [code_list_region[region_i]]
        add_val_list_region = [0] * 13
        for nation in nation_list:
            row_values = []
            for port_list, use_bookval, long_pos in zip(port_list_2d, use_bookval_list, long_pos_list):
                trdnbr_list = get_trdnbr(nation, port_list)
                val_per_port = get_value(trdnbr_list, use_bookval, long_pos)
                row_values.extend(val_per_port)
            
            new_data_dict[nation] = [list_code[code_i]] + [x if x != 0 else "" for x in row_values]
            code_i += 1
            
            for i, _ in enumerate(row_values):
                add_val_list[i] += float(row_values[i])
                add_val_list_region[i] += float(row_values[i])
        
        new_data_dict[region_list[region_i]].extend(add_val_list_region)
                        
    new_data_dict["Total of Section 1 and 2"] = ['5Z'] + [x if x != 0 else "" for x in add_val_list]
    new_data_dict["2. Analysis by jurisdiction"].extend([x if x != 0 else "" for x in add_val_list])
        
    row_values = []
    for port_list, use_bookval, long_pos in zip(port_list_2d, use_bookval_list, long_pos_list):
        trdnbr_list = get_trdnbr_except(nation_list, port_list)
        val_per_port = get_value(trdnbr_list, use_bookval, long_pos)
        row_values.extend(val_per_port)
    
    new_data_dict["3. Unallocated"] = ["5M"] + [x if x != 0 else "" for x in row_values]
    
    for i, _ in enumerate(add_val_list):
            add_val_list[i] += float(row_values[i])
        
    new_data_dict["Total of Section 1, 2 and 3"] = ['5J'] + [x if x != 0 else "" for x in add_val_list]
    
    return new_data_dict
    
def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"C:\\"
    return selection
### TABLE HEADER, TITLE, SUBTITLE, AND VALUE CONTENT
## HEADER CONTENT AND SPAN FORMATING

row_header_1 = ["Country / Jurisdiction", "Banking book", "Trading book"]
row_header_2 = ["Fair value through other comprehensive income/Fair value through profit or loss", "Amortised cost", "Long positions only", "Both long and short positions on a net basis"]
row_header_3 = (["Name", "CODE", "Amt", "CV01", "Average remaining maturity"] + ["Amt", "Book value", "CV01", "Average remaining maturity"]) + (["Amt", "CV01", "Average remaining maturity"] * 2)
header_cell_span_1 = [["3", "2"], ["7", "1"], ["6", "1"]]
header_cell_span_2 = [["3", "1"], ["4", "1"], ["3", "1"], ["3", "1"]]
header_cell_span_3 = [["2", "1"]] + [["1", "1"]] * 14
row_header = [row_header_1, row_header_2, row_header_3]
header_cell_span = [header_cell_span_1, header_cell_span_2, header_cell_span_3]

# ------------------------------------------------------------------------------------------------------------------------------------------
nation_list_2d = [
    ["Andorra" , "Austria" , "Belgium" , "Cyprus" , "Denmark" , "Estonia" , "Faeroe Islands" , "Finland" , "France" , 
    "Germany" , "Greece" , "Greenland" , "Iceland" , "Ireland" , "Italy" , "Liechtenstein" , "Luxembourg" , "Malta" , "Netherlands" , "Norway" , "Portugal" , "San Marino" , "Slovakia" , "Slovenia" , "Spain" , 
    "Sweden" , "Switzerland" , "United Kingdom" , "Vatican City State" , "Australia" , "Canada" , "Japan" , "New Zealand" , "United States" , "Residual developed countries"] , 
    ["Aruba" , "Bahamas" , "Bahrain" , "Barbados" , "Bermuda" , "Cayman Islands" , "Curacao" , "Gibraltar" , "Guernsey" , "Hong Kong, China" , "Isle of Man" , "Jersey" , "Lebanon" , 
    "Macao, China" , "Mauritius" , "Panama" , "Samoa" , "Singapore" , "Sint Maarten" , "Vanuatu" , "West Indies UK" , "Former Netherlands Antilles" , "Residual offshore centres"] , 
    ["Albania" , "Belarus" , "Bosnia and Herzegovina" , "Bulgaria" , "Croatia" , "Czech Republic" , "Hungary" , "Latvia" , "Lithuania" , "Macedonia" , "Moldova" , "Montenegro" , 
    "Poland" , "Romania" , "Russia" , "Serbia" , "Turkey" , "Ukraine" , "Former Serbia and Montenegro" , "Residual developing Europe"] , 
    ["Argentina" , "Belize" , "Bolivia" , 
    "Bonaire, Saint Eustatius and Saba" , "Brazil" , "Chile" , "Colombia" , "Costa Rica" , "Cuba" , "Dominica" , "Dominican Republic" , "Ecuador" , "El Salvador" , "Falkland Islands" , "Grenada" , "Guatemala" , 
    "Guyana" , "Haiti" , "Honduras" , "Jamaica" , "Mexico" , "Nicaragua" , "Paraguay" , "Peru" , "St. Lucia" , "St. Vincent and Grenadines" , "Suriname" , "Trinidad and Tobago" , "Turks and Caicos Islands" , 
    "Uruguay" , "Venezuela" ,  "Residual developing Latin America and Caribbean"] , 
    ["Algeria" , "Angola" , "Benin" , "Botswana" , "Burkina Faso" , "Burundi" , "Cameroon" , "Cape Verde" , "Central African Republic" , "Chad" , "Comoros" , "Congo" , 
    "Congo Democratic Republic" , "C&#244;te d&#39;Ivoire" , "Djibouti" , "Egypt" , "Equatorial Guinea" , "Eritrea" , "Ethiopia" , "Gabon" , "Gambia" , "Ghana" , "Guinea" , "Guinea-Bissau" , "Iran" , "Iraq" , 
    "Israel" , "Jordan" , "Kenya" , "Kuwait" , "Lesotho" , "Liberia" , "Libya" , "Madagascar" , "Malawi" , "Mali" , "Mauritania" , 
    "Morocco" , "Mozambique" , "Namibia" , "Niger" , "Nigeria" , "Oman" , "Palestinian Territory" , "Qatar" , "Rwanda" , "Sao Tome and Principe" , "Saudi Arabia" , "Senegal" , "Seychelles" , "Sierra Leone" , 
    "Somalia" , "South Africa" , "South Sudan" , "St. Helena" , "Sudan" , "Swaziland" , "Syria" , "Tanzania" , "Togo" , "Tunisia" , "Uganda" , "United Arab Emirates" , "Yemen" , "Zambia" , "Zimbabwe" , 
    "Residual developing Africa and Middle East"] , 
    ["Afghanistan" , "Armenia" , "Azerbaijan" , "Bangladesh" , "Bhutan" , "British Overseas Territories" , "Brunei" , "Cambodia" , 
    "Mainland China" , "Fiji" , "French Polynesia" , "Georgia" , "India" , "Indonesia", "Kazakhstan" , "Kiribati" , "Kyrgyz Republic" , "Laos" , "Malaysia" , "Maldives" , "Marshall Islands" , "Micronesia" , 
    "Mongolia" , "Myanmar" , "Nauru" , "Nepal" , "New Caledonia" , "North Korea" , "Pakistan" , "Palau" , "Papua New Guinea" , "Philippines" , "Solomon Islands" , "South Korea", "Sri Lanka" , "Taiwan, China" ,
    "Tajikistan" , "Thailand" , "Timor Leste" , "Tonga" , "Turkmenistan" , "Tuvalu" , "US Pacific Islands" , "Uzbekistan" , "Vietnam" , "Wallis and Futuna", "Residual developing Asia and Pacific"]]

list_code =[
    'AD', 'AT', 'BE', 'CY', 'DK', 'EE', 'FO', 'FI', 'FR', 'DE', 'GR', 'GL', 'IS', 'IE', 'IT', 'LI', 'LU', 'MT', 'NL', 'NO', 'PT', 'SM', 'SK', 'SI', 'ES', 'SE', 'CH', 'UK', 'VA', 'AU', 'CA', 
    'JP', 'NZ', 'US', '2R', 'AW', 'BS', 'BH', 'BB', 'BM', 'KY', 'CW', 'GI', 'GG', 'HK', 'IM', 'JE', 'LB', 'MO', 'MU', 'PA', 'WS', 'SG', 'SX', 'VU', '1Z', '2D', '2N', 'AL', 'BY', 'BA', 'BG', 'HR', 
    'CZ', 'HU', 'LV', 'LT', 'MK', 'MD', 'ME', 'PL', 'RO', 'RU', 'RS', 'TR', 'UA', '2B', '2B', 'AR', 'BZ', 'BO', 'BQ', 'BR', 'CL', 'CO', 'CR', 'CU', 'DM', 'DO', 'EC', 'SV', 'FK', 'GD', 'GT', 'GY', 'HT', 
    'HN', 'JM', 'MX', 'NI', 'PY', 'PE', 'LC', 'VC', 'SR', 'TT', 'TC', 'UY', 'VE', '2H', 'DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 'CI', 'DJ', 'EG', 'GQ', 'ER', 'ET', 
    'GA', 'GM', 'GH', 'GN', 'GW', 'IR', 'IQ', 'IL', 'JO', 'KE', 'KW', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MA', 'MZ', 'NA', 'NE', 'NG', 'OM', 'PS', 'QA', 'RW', 'ST', 'SA', 'SN', 'SC', 'SL', 'SO', 'ZA', 
    'SS', 'SH', 'SD', 'SZ', 'SY', 'TZ', 'TG', 'TN', 'UG', 'AE', 'YE', 'ZM', 'ZW', '2W', 'AF', 'AM', 'AZ', 'BD', 'BT', '1W', 'BN', 'KH', 'CN', 'FJ', 'PF', 'GE', 'IN', 'ID', 'KZ', 'KI', 'KG', 'LA', 'MY', 'MV', 'MH', 
    'FM', 'MN', 'MM', 'NR', 'NP', 'NC', 'KP', 'PK', 'PW', 'PG', 'PH', 'SB', 'KR', 'LK', 'TW', 'TJ', 'TH', 'TL', 'TO', 'TM', 'TV', 'PU', 'UZ', 'VN', 'WF', '2O']

bold_row_list = [
                "1. International organisations", "2. Analysis by jurisdiction", "Developed countries", "Offshore centres", 
                "Developing Europe", "Developing Latin America and Caribbean", "Developing Africa and Middle East", "Developing Asia and Pacific", 
                "Total of Section 1 and 2", "3. Unallocated", "Total of Section 1, 2 and 3"
                ]
                

green_row_list = [
                "2. Analysis by country", "Developed countries", "Offshore centres", 
                "Developing Europe", "Developing Latin America and Caribbean", "Developing Africa and Middle East", "Developing Asia and Pacific", 
                "Total of Section 1 and 2", "Total of Section 1, 2 and 3"
                 ]
green_row_indices = [1, 4, 5, 6, 8, 9, 11, 12]
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
<h1>Part 4 - Country of ultimate risk</h1>
<p>AMT (current market value unless otherwise specified) and CV01 In HK$&#39;000&#59;&nbsp;Average remaining maturity in number of years (2 decimal places)</p>
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
            if any(x in key_content for x in bold_row_list):
                html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px; font-weight: bold;">&emsp;{key_content}</td>\n'
            else :
                html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;">&emsp;{key_content}</td>\n'
        for i, val_content in enumerate(list_val_content):
            border_sty = "1px solid black"
            if any(x in key_content for x in green_row_list):
                if val_content == "&nbsp;":
                    content_style = f'background-color:black ; border-bottom: {border_sty}; border-left: {border_sty}; border-right: {border_sty if i == len(list_val_content) - 1 else ""}; width: 200px'
                else:
                    content_style = f'background-color:{"#87e8a1" if i in green_row_indices else ""};border-bottom: {border_sty}; border-left: {border_sty}; border-right: {border_sty if i == len(list_val_content) - 1 else ""}; width: 100px'
            else:
                content_style = f'background-color:{""};border-bottom: {border_sty}; border-left: {border_sty}; border-right: {border_sty if i == len(list_val_content) - 1 else ""}; width: 200px'
            
            html_code += f'<td style="{content_style}">{val_content}</td>\n'
        
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
                    'windowCaption':'HKCO01d - ICC - HKMAs Survey on Debt Securities Held'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'HKCO01d - ICC - HKMAs Survey on Debt Securities Held', 1,0],
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
    
    data_dict = get_val_dict(nation_list_2d, list_code)
    
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    if ".xls" in output_file:
        html_to_xls(data_dict, report_folder, report_name)
