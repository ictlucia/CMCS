import acm
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

##################################################################################
# CREATE HTML TEMPLATE TABLE
##################################################################################
def open_html_table():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        table {
            width: 1000px;
        }

        /* Text Align - Left */
        .left-text {
            text-align: left;
        }
        .right-text {
            text-align: right;
        }

        .mid-text {
            text-align: center;
        }
    </style>
</head>
<body>
    <table>
    """

def html_table(title, header_list, content_align, content_list=None):
    title_table = f'<tr> <th colspan="{len(header_list)}">{title}</th></tr>\n'
    skip_row = "<tr> <td>&nbsp;</td></tr>\n"
    
    str_header = "<tr>\n"
    for header in header_list:
        str_header += f"<th>{header}</th>\n"
    str_header += "</tr>\n"
    
    str_content = "<tr>\n"
    for row_content in content_list:
        for i in range(len(row_content)):
            str_content += f'<td class = "{content_align[i]}-text">{row_content[i]}</td>\n'
        str_content += "<tr>\n"
    
    return title_table + skip_row + str_header + str_content + "</table>\n" + "</body>\n" + "</html>"

##################################################################################
# PULL DATA USING ACM
##################################################################################
def get_content_list(compliance_rule_name):
    compliance_rules = acm.FComplianceRule.Select('')
    usd_ins = acm.FInstrument['USD']

    for i in range(len(usd_ins.Prices())):
        market = usd_ins.Prices()[i].Market().Name()
        curr = usd_ins.Prices()[i].Currency().Name()
        if market == "EOD" and curr == "IDR":
            eodVal = usd_ins.Prices()[i].Settle()
    
    content_list = []
    for compliance_rule in compliance_rules :
        if compliance_rule.Name() == compliance_rule_name:
            for target in compliance_rule.AppliedRules():
                hostId = target.Target().HostId() if target.Target().HostId() != "" else "-"
                sn = target.Target().Name() if target.Target().Name() != "" else "-"
                ccy = "IDR"
                limit =  target.ThresholdValues().First().ValueAdjusted() if target.ThresholdValues().First().ValueAdjusted() != "" else "-"
                expDate = target.ThresholdValues().First().AppliedRule().EndDate() if target.ThresholdValues().First().AppliedRule().EndDate() != "" else "-"
                limUsd = round(limit / eodVal, 2)
                content_list.append([hostId, sn, ccy, limit, expDate, "-", "-", limUsd, "-"])
    return content_list

title = "LIMIT NON-BANK - EXPIRED"
header_list = ["CIF", "SN", "CCY", "LIMIT", "EXPDATE", "PRODCODE", "LIMUSD", "EXPUSD", "TERM"]
content_align = ["left", "left", "mid", "right", "mid", "left", "mid", "right", "right"]
content_list = get_content_list("Limit NonBank - NBK EF")
date_today = acm.Time.DateToday()

##################################################################################
# GENERATE HTML TO XSL
##################################################################################
html_code = open_html_table() + html_table(title, header_list, content_align, content_list)
html_file = HTMLGenerator().create_html_file(html_code, "C:", "HKMOa04", date_today, False)
generate_file_for_other_extension(html_file, '.xls')

