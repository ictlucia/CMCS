import os
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from datetime import date

#############################################################################
# QUERY FUNCTION
#############################################################################
def usd_price_mtm(curr_first, curr_target="USD"):
    prices = acm.FPrice.Select(f"instrument = '{curr_first}' and market = 'EOD_MtM'")
    for p in prices:
        if p.Instrument():
            if p.Currency().Name() == curr_target:
                return p.Settle()
    return 10000


def checking_currency(trade_nominal_list, curr):
    nominal_list = []
    for trade, nominal in trade_nominal_list:
        trade_curr = acm.FTrade[trade].Currency().Name()
        if trade_curr == curr:
            nominal_list.append(nominal)
    total_nominal = sum(nominal_list)
    return float(total_nominal)


def query_process(optkey3="", optkey4="", portfolio=""):
    optkey3_query = (
        "WHERE DISPLAY_ID(t, 'optkey3_chlnbr') in " + optkey3 + "\n"
        if optkey3 != ""
        else ""
    )
    optkey4_query = (
        " AND DISPLAY_ID(t, 'optkey4_chlnbr') in " + optkey4 + "\n"
        if optkey4 != ""
        else ""
    )
    portfolio_query = f" AND (DISPLAY_ID(t, 'prfnbr') = '{portfolio[0]}'\n"
    for port in portfolio[1:-1]:
        portfolio_query += f" OR DISPLAY_ID(t, 'prfnbr') = '{port}'\n"
    portfolio_query += f" OR DISPLAY_ID(t, 'prfnbr') = '{portfolio[-1]}')\n"
    query_string = (
        """
            SELECT t.trdnbr, nominal_amount(t)
            FROM Trade t   
        """
        + optkey3_query
        + optkey4_query
        + portfolio_query
    )
    print(query_string)
    query_results = ael.asql(query_string)[1][0]
    list_curr = ["RMB", "USD"]
    usd_book = 0
    for i, curr in enumerate(list_curr):
        Nominal_per_curr = checking_currency(query_results, curr)
        usd_price = usd_price_mtm(curr)
        usd_book += Nominal_per_curr * usd_price
        list_curr[i] = f"{Nominal_per_curr:,}"
    return [f"{usd_book:,}"] + list_curr


#############################################################################
# FILTER LIST
#############################################################################
#############################################################################
# TOP HEADER
#############################################################################
def curr_price_func(curr_pair):
    today_date = date.today().strftime("%Y-%m-%d")
    curr1, curr2 = curr_pair.split("/")
    ins_curr1, ins_curr2 = acm.FInstrument[curr1], acm.FInstrument[curr2]
    curr_val_list = []
    for ins_curr in [ins_curr1, ins_curr2]:
        for price_info in ins_curr.Prices().AsArray():
            price, market, day = (
                price_info.Settle(),
                price_info.Market().Name(),
                price_info.Day(),
            )
            if day == today_date and market == "EOD_MtM":
                curr_val_list.append(price)
    if len(curr_val_list) > 0:
        return curr_val_list[0] * curr_val_list[1]
    else:
        return 0


curr_pair_list = ["USD/CNY", "USD/SGD", "EUR/USD", "USD/IDR", "GBP/USD", "USD/JPY"]
curr_price = {}
for curr_pair in curr_pair_list:
    curr_price[curr_pair] = curr_price_func(curr_pair)
#############################################################################
# VALUE FIRST TABLE
#############################################################################
port_list = [
    "FX Spot 1 BMSH - DBU",
    "FX Spot 2 BMSH - DBU",
    "FX Derivatives 1 BMSH - DBU",
    "FX Derivatives 2 BMSH - DBU",
    "IRT DCM 1 BMSH - DBU",
    "IRT DCM 2 BMSH - DBU",
    "IRT MM Depo Loan Repo RR 1 BMSH - DBU",
    "IRT MM Depo Loan Repo RR 2 BMSH - DBU",
    "IRT MM Bond RDPU 1 BMSH - DBU",
    "IRT MM Bond RDPU 2 BMSH - DBU",
    "IRT Derivative 1 BMSH - DBU",
    "IRT Derivative 2 BMSH - DBU",
    "BB Derivative BMSH - DBU",
    "BB FX BMSH - DBU",
    "BB BOND PL BMSH - DBU",
    "BB BOND AC BMSH - DBU",
    "BB BOND OCI BMSH - DBU",
    "BB BOND SHARIA PL BMSH - DBU",
    "BB BOND SHARIA AC BMSH - DBU",
    "BB BOND SHARIA OCI BMSH - DBU",
    "IBFI 1 BMSH - DBU",
    "CB 1 BMSH - DBU",
    "CB 2 BMSH - DBU",
    "CB 3 BMSH - DBU",
    "CB 4 BMSH - DBU",
    "CB 5 BMSH - DBU",
    "CB 6 BMSH - DBU",
    "GVI 1 BMSH - DBU",
    "GVI 2 BMSH - DBU",
    "Commercial 1 BMSH - DBU",
    "Commercial 2 BMSH - DBU",
    "Commercial 3 BMSH - DBU",
    "Commercial 4 BMSH - DBU",
    "Commercial 5 BMSH - DBU",
    "Commercial 6 BMSH - DBU",
    "SAM 1 BMSH - DBU",
    "SAM 2 BMSH - DBU",
    "SAM 3 BMSH - DBU",
    "LIQ IB BMSH - DBU",
    "LIQ MM BMSH - DBU",
    "ALM Bilateral Loans BMSH - DBU",
    "ALM Bonds Issued BMSH - DBU",
    "LIQ NOS BMSH - DBU",
    "FX with Customer BMSH - DBU",
    "Bonds with Customer BMSH - DBU",
    "Derivative with Customer BMSH - DBU",
]
# port_list = "(" + ",".join([f"'{x}'" for x in port_list[:39]]) + ")"
query_result = [
    query_process("('DL')", "('CL', 'MD', 'CMP', 'CMT', 'OVP', 'BA')", port_list)
] * 5
query_result_total_1 = [0, 0, 0]
for i in range(len(query_result[0])):
    list_row = [
        str(query_result[j][i]).replace(",", "") for j in range(len(query_result))
    ]
    query_result_total_1[i] += sum([float(i) for i in list_row])
header_a1 = ["BMSH PLACEMENT TO INTEROFFICE", "", "RMB BOOK", "RMB", "USD"]
content_a1 = {
    "INTER OFFICE ASSET-TRUST RECEIPT": ["GL19611214/204 =< 1 MONTHS"]
    + query_result[0],
    "INTER OFFICE ASSET-UPAS": ["GL 19611205 =< 1 MONTHS"] + query_result[1],
    "BMSH Nostro at INTEROFFICE": [""] + query_result[2],
    "BMSH INTEROFFICE PLACEMENT": [""] + query_result[3],
    "OTHERS": [""] + query_result[4],
    "SUB TOTAL": [""] + query_result_total_1,
}
query_result = [
    query_process("('DL')", "('CL', 'MD', 'CMP', 'CMT', 'OVP', 'BA')", port_list)
] * 3
query_result_total_2 = [0, 0, 0]
for i in range(len(query_result[0])):
    list_row = [
        str(query_result[j][i]).replace(",", "") for j in range(len(query_result))
    ]
    query_result_total_2[i] += sum([float(i) for i in list_row])
header_a2 = ["INTEROFFICE PLACEMENT TO BMSH", "", "TOTAL (RMB)", "RMB", "USD"]
content_a2 = {
    "BMSH INTEROFFICE BORROWING =< 1 MONTHS": [""] + query_result[0],
    "HO VOSTRO AT BMSH": [""] + query_result[1],
    "OTHERS": [""] + query_result[2],
    "SUB TOTAL": [""] + query_result_total_2,
}
total_a = [
    "NETT INTEROFFICE",
    "",
    query_result_total_1[0] + query_result_total_2[0],
] + [""] * 2
#############################################################################
# VALUE SECOND TABLE (ASSETS)
#############################################################################
query_result = [
    query_process("('DL')", "('CL', 'MD', 'CMP', 'CMT', 'OVP', 'BA')", port_list)
] * 14
query_result_total_1 = [0, 0, 0]
for i in range(len(query_result[0])):
    list_row = [
        str(query_result[j][i]).replace(",", "") for j in range(len(query_result))
    ]
    query_result_total_1[i] += sum([float(i) for i in list_row])
header_b = ["1. CURRENT ASSETS", "", "TOTAL (RMB)", "RMB", "USD"]
sub_header_b = ["NETT INTEROFFICE POSSITIVE", ""] + [""] * 3
content_b = {
    "-1.1 CASH": [""] + query_result[0],
    "-1.2 GOLDEN": [""] + query_result[1],
    "-1.3 DEPOSIT WITH PBOC": [""] + query_result[2],
    "-1.4 DEPOSIT WITH INTERBANK": ["+ Over Amount of RD"] + query_result[3],
    "-1.4 INTERBANK PLCMT  =< 1 MONTHS": ["IP/FT + Time Deposit"] + query_result[4],
    "-1.4 INTERBANK LENDING =< 1 MONTHS": ["IP/CM"] + query_result[5],
    "-1.5 A/R INTEREST =< 1 MONTHS": [""] + query_result[6],
    "-1.5 A/R OTHER =< 1 MONTHS": [""] + query_result[7],
    "-1.6 NEGOTIATION =< 1 MONTHS": [""] + query_result[8],
    "-1.9 DEPOSIT WITH INTERBRANCH": [""] + query_result[9],
    "-1.6 TRADE =< 1 MONTHS": [""] + query_result[10],
    "-1.6 LOANS =< 1 MONTHS": [""] + query_result[11],
    "-1.7 INVESTMENT =< 1 MONTHS": [""] + query_result[12],
    "-1.9 OTHERS =< 1 MONTHS": [""] + query_result[13],
}
total_b = ["TOTAL CURRENT ASSETS", "", query_result_total_1[0]]
#############################################################################
# VALUE SECOND TABLE (LIABILITIES)
#############################################################################
query_result = [
    query_process("('DL')", "('CL', 'MD', 'CMP', 'CMT', 'OVP', 'BA')", port_list)
] * 12
query_result_total_2 = [0, 0, 0]
for i in range(len(query_result[0])):
    list_row = [
        str(query_result[j][i]).replace(",", "") for j in range(len(query_result))
    ]
    query_result_total_2[i] += sum([float(i) for i in list_row])
header_c = ["2. CURRENT LIABILITIES", "", "TOTAL (RMB)", "RMB", "USD"]
sub_header_c = ["NETT INTEROFFICE NEGATIVE", ""] + [""] * 3
content_c = {
    "-2.1 CHECKING ACCOUNT": [""] + query_result[0],
    "-2.2 DEPOSIT <= 1M": [""] + query_result[1],
    "-2.3 INTERBANK DEPO": ["IT-FT"] + query_result[2],
    "-2.3 INTERBANK TAKEN =< 1 MONTH": ["IT-CM"] + query_result[3],
    "-2.3 INTERBANK BOROWG =< 1 MONTH": [""] + query_result[4],
    "-2.5 A/P =< 1 MONTHS": [""] + query_result[5],
    "-2.6 BOROWG FM CENTEAL BK =< 1 MTH": [""] + query_result[6],
    "-BILLS FINANCE =< 1 MTH": [""] + query_result[7],
    "-2.5 A/P INT =< 1 MONTHS": [""] + query_result[8],
    "-2.7 OTHER BOROWG =< 1 MONTHS": [""] + query_result[9],
    "-2.7 INTERBRANCH TAKEN": [""] + query_result[10],
    "-2.7 OTHERS =< 1 MONTHS": [""] + query_result[11],
}
total_c = ["TOTAL CURRENT LIABILITIES", "", query_result_total_2[0]]
total_summary = {
    "TOTAL CURRENT ASSETS": ["", query_result_total_1[0]],
    "TOTAL CURRENT LIABILITIES": ["", query_result_total_2[0]],
}
#############################################################################
# GENERATE XLS TABLE
#############################################################################
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
<table style="width: fit-content">
"""


def currency_price(html_code, curr_price):
    date_today_ddByy = date.today().strftime("%d-%b-%y")
    html_code += f'<tr><td style=" font-weight: bold; text-align:center; width:400px">EXCHANGE RATE</td></tr>'
    html_code += f'<tr><td rowspan="6" style="border-right: 1px black solid; font-weight: bold; text-align:center; vertical-align:top">{date_today_ddByy}</td>'
    html_code += f'<td style="border-top: 1px black solid; font-weight: bold; background-color:#F8B4FF">{list(curr_price.keys())[0]}</td><td style="border-top: 1px black solid; border-right: 1px black solid; font-weight: bold; background-color:#F8B4FF">{list(curr_price.values())[0]}</td></tr>'
    for key, val in curr_price.items():
        if key != "USD/CNY":
            html_code += f'<tr><td style="font-weight: bold; background-color:#F8B4FF">{key}</td><td style="border-right: 1px black solid; font-weight: bold; background-color:#F8B4FF">{val}</td></tr>'
    return html_code


def header_a(html_code, header_list):
    border = "border-top: 1px solid black; border-bottom: 1px solid black; text-align: center;"
    border_add = "border-left: 1px solid black; border-right: 1px solid black"
    style_1 = f'background-color : #3F95B8; font-weight:bold; {border}; text-align:{"left" if header_list[0] != "NETT INTEROFFICE" else "center"}'
    style_2 = f'background-color :  {"#ADD1DF" if header_list[0] != "NETT INTEROFFICE" else "#B3FDB4"}; font-weight:bold; {border} {border_add}; color: {"red" if header_list[2] == header_a1[2] else "black"}'
    style_basic = f"font-weight:bold; {border}"
    html_code += "<tr>\n"
    for i_head, val_header in enumerate(header_list):
        html_code += f'<td style="{style_1 if i_head == 0 else style_2 if i_head == 2 else style_basic}">{val_header}</td>\n'
    return html_code + "</tr>\n"


def sub_header(html_code, subheader_list):
    border = "border-top: 1px solid black; border-bottom: 1px solid black;"
    border_full = "border: 1px solid black;"
    html_code += "<tr>\n"
    if "TOTAL CURRENT" in subheader_list[0]:
        for i_head, val_header in enumerate(subheader_list):
            html_code += f'<td style="text-align:center; background-color:#B3FDB4; font-weight: bold; {border if i_head != 2 else border_full}">{val_header}</td>\n'
        html_code += (
            f'<td style="background-color:white; font-weight: bold; {border}">&nbsp;</td>'
            * 7
        )
    else:
        for i_head, val_header in enumerate(subheader_list):
            html_code += f'<td style="background-color:#B3FDB4; font-weight: bold; {border if i_head != 2 else border_full}">{val_header}</td>\n'
    return html_code + "</tr>\n"


def content_a(html_code, content_dict):
    border = "border-left: 1px solid black; border-right: 1px solid black"
    style = f"background-color : #ADD1DF; {border}"
    style_2 = f"background-color : #AAAAAA; {border}"
    for key, val in content_dict.items():
        html_code += "<tr>\n"
        row = ["&emsp;" + key if key != "SUB TOTAL" else key] + val
        for i, col in enumerate(row):
            if key != "SUB TOTAL":
                html_code += f'<td style="{style if i == 2 else ""}">{col}</td>\n'
            else:
                html_code += f'<td style="{style_2 if i == 2 else "text-align:center" if i == 0 else ""}">{col}</td>\n'
        html_code += "</tr>\n"
    return html_code


def summary(html_code, total_summary):
    html_code += '<tr><td colspan="3" style="background-color: #3F95B8; color:white; font-weight:bold; text-align:center">SUMMARY RMB BOOK</td></tr>'
    for key, val_list in total_summary.items():
        html_code += f'<tr><td style="background-color: #ADD1DF">{key}</td>'
        for val in val_list:
            html_code += f"<td>{val}</td>"
        html_code += "</tr>"
    val_summary_list_2d = [
        ["LIQUIDITY RATIO", "", "95%"],
        ["LIQUIDITY RATIO TRESHOLD", "", "above 25%"],
    ]
    for i, val_list in enumerate(val_summary_list_2d):
        html_code += "<tr>"
        for val in val_list:
            if i == 0:
                html_code += f'<td style="background-color:#194454; color:white; text-align: center">{val}</td>'
            else:
                html_code += f'<td style="background-color: {"red" if val != "" else ""}; color:white; text-align: center">{val}</td>'
        html_code += "</tr>"
    return html_code


def generate_excel(report_folder, report_name):
    date_today_ddmmyyyy = date.today().strftime("%d-%m-%Y")
    html_code = open_table()
    # html_code += f'<tr><td style="text-align: center; font-weight:bold" colspan="5">{date_today_ddmmyyyy}</td></tr>'
    # html_code += '<tr><td></td></tr>'
    html_code = currency_price(html_code, curr_price)
    html_code += "<tr><td></td></tr>"
    html_code += '<tr><td style="text-align:left; font-weight:bold" colspan="10">INTEROFFICE EXPOSURES</td></tr>'
    html_code = header_a(html_code, header_a1)
    html_code = content_a(html_code, content_a1)
    html_code = header_a(html_code, header_a2)
    html_code = content_a(html_code, content_a2)
    html_code = header_a(html_code, total_a)
    html_code += "<tr><td></td></tr>"
    html_code += '<tr><td style="text-align:left; font-weight:bold" colspan="10">LIQUIDITY RATIO - FCCY</td></tr>'
    html_code = header_a(html_code, header_b)
    html_code = sub_header(html_code, sub_header_b)
    html_code = content_a(html_code, content_b)
    html_code = sub_header(html_code, total_b)
    html_code += "<tr><td></td></tr>"
    html_code = header_a(html_code, header_c)
    html_code = sub_header(html_code, sub_header_c)
    html_code = content_a(html_code, content_c)
    html_code = sub_header(html_code, total_c)
    html_code += "<tr><td></td></tr>"
    html_code = summary(html_code, total_summary)
    red_text = [
        "=< 1 MONTHS",
        "=< 1 MONTH",
        "=< 1 MTH",
        "<= 1 M",
        "+ Over Amount of RD",
        "+ Time Deposit",
    ]
    for change_text in red_text:
        html_code = html_code.replace(
            change_text, f'<span style="color: red">{change_text}</span>'
        )
    file_path = os.path.join(report_folder, report_name)
    f = open(file_path, "w")
    f.write(html_code + "</table></body></html>")
    f.close()


##################################################################################
# CREATING A GUI PARAMETER
##################################################################################
ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "SH17b - Liquidity Ratio - RMB Book",
}
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "SH17b - Liquidity Ratio - RMB Book",
        1,
        0,
    ],
    [
        "file_path",
        "Folder Path",
        getFilePathSelection(),
        None,
        getFilePathSelection(),
        1,
        1,
    ],
    [
        "output_file",
        "Output Files",
        "string",
        [".pdf", ".xls"],
        ".xls",
        0,
        0,
        "Select Output Extension Type",
    ],
]


def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = parameter["report_name"] + ".xls"
    file_path = str(parameter["file_path"])
    output_file = "".join(parameter["output_file"])
    folder_name = "report" + date.today().strftime("%y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    if ".xls" in output_file:
        generate_excel(report_folder, report_name)
