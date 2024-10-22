import ael, acm
import datetime
from datetime import date, timedelta, datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import re

##################################################################################################
# HTML TABLE FUNCTION
##################################################################################################
def open_html():
    html_code = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <table style="width: 1000px;">
    """
    return html_code


def header_html(header1, header2):
    row_code = "<tr>\n"
    for col1 in header1:
        row_code += (
            f'<th rowspan="2" style="background-color: gray;">{col1}</th>'
            if col1 == "Port"
            else f'<th colspan="2" style="background-color: gray;">{col1}</th>\n'
        )
    row_code += "</tr>\n<tr>\n"
    for col2 in header2:
        row_code += f'<th style="background-color: gray;">{col2}</th>\n'
    row_code += "</tr>"
    return row_code


def content_html(list_content, list_footer):
    row_code = ""
    for row_value in list_content:
        row_code += "<tr>\n"
        for i_col in range(len(row_value)):
            row_code += (
                f'<td style="text-align: center;">{row_value[i_col]}</td>\n'
                if i_col % 2 == 0
                else f'<td style="text-align: right;">{row_value[i_col]}</td>\n'
            )
        row_code += "</tr>\n"
    row_code += "<tr>\n"
    for i_foot in range(len(list_footer)):
        row_code += (
            f'<td style="text-align: center; background-color: gainsboro;">{list_footer[i_foot]}</td>\n'
            if i_foot % 2 == 0
            else f'<td style="text-align: right; background-color: gainsboro;">{list_footer[i_foot]}</td>\n'
        )
    row_code += "</tr>\n"
    return row_code + "</table></body></html>"


##################################################################################################
# PDF FORMATING
##################################################################################################
def add_xsl_fo_table_header(
    xsl_fo_content,
    header_list1,
    header_list2,
    header_styling="padding='8pt' border-width='1px' border-style='solid'",
):
    xsl_fo_table = """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
    """
    for header in header_list2:
        xsl_fo_table += """ <fo:table-column border-width="1px" border-style="solid" column-width="auto"/>
        """
    xsl_fo_table += """ <fo:table-column border-width="1px" border-style="solid" column-width="auto"/>"""
    xsl_fo_table += """<fo:table-header background-color="#808080" color="#ffffff" font-weight="bold" font-size="12px">\n<fo:table-row>
    """
    for header in header_list1:
        span = (
            'number-rows-spanned="2"'
            if header == "Port"
            else 'number-columns-spanned="2"'
        )
        xsl_fo_table += (
            f"""<fo:table-cell {span} {header_styling}><fo:block>"""
            + str(header)
            + """</fo:block></fo:table-cell>
        """
        )
    xsl_fo_table += """</fo:table-row>"""
    xsl_fo_table += """<fo:table-row>"""
    for subheader in header_list2:
        xsl_fo_table += (
            f"""<fo:table-cell {header_styling}><fo:block>"""
            + str(subheader)
            + """</fo:block></fo:table-cell>"""
        )
    xsl_fo_table += """</fo:table-row></fo:table-header>\n<fo:table-body>"""
    return xsl_fo_content + xsl_fo_table


def xslfo_gen(header, data_content, footer, file_name, file_path, date):
    header1, header2 = header
    gen = XSLFOGenerator()
    xsl_fo_content = gen.prepare_xsl_fo_content(
        "asdasd", 'padding="8pt" font-weight="bold" font-size="8px"'
    )
    xsl_fo_content = add_xsl_fo_table_header(xsl_fo_content, header1, header2)
    xsl_fo_content = gen.add_xsl_data_row(xsl_fo_content, data_content)
    xsl_fo_content = gen.add_xsl_data_row(
        xsl_fo_content,
        footer,
        cell_styling="border-width='1px' border-style='solid' padding='8pt' background-color='#666666'",
    )
    xsl_fo_content = gen.close_xsl_table(xsl_fo_content)
    xsl_fo_file = gen.create_xsl_fo_file(file_name, file_path, xsl_fo_content, date)
    return xsl_fo_file


##################################################################################################
# FILTER LIST
##################################################################################################
port_list = [
    "IR BMSG",
    "BB BOND PL BMSG - ACU",
    "BB BOND AC BMSG - ACU",
    "BB BOND OCI BMSG - ACU",
    "BB BOND SHARIA PL BMSG -  ACU",
    "BB BOND SHARIA AC BMSG - ACU",
    "BB BOND SHARIA OCI BMSG - ACU",
    "IBFI 1 BMSG - ACU",
    "CB 1 BMSG - ACU",
    "CB 2 BMSG - ACU",
    "CB 3 BMSG - ACU",
    "CB 4 BMSG - ACU",
    "CB 5 BMSG - ACU",
    "CB 6 BMSG - ACU",
    "GVI 1 BMSG - ACU",
    "GVI 2 BMSG - ACU",
    "Commercial 1 BMSG - ACU",
    "Commercial 2 BMSG - ACU",
    "Commercial 3 BMSG - ACU",
    "Commercial 4 BMSG - ACU",
    "Commercial 5 BMSG - ACU",
    "Commercial 6 BMSG - ACU",
    "BB BOND PL BMSG - DBU",
    "BB BOND AC BMSG - DBU",
    "BB BOND OCI BMSG - DBU",
    "BB BOND SHARIA PL BMSG - DBU",
    "BB BOND SHARIA AC BMSG - DBU",
    "BB BOND SHARIA OCI BMSG - DBU",
    "IBFI 1 BMSG - DBU",
    "CB 1 BMSG - DBU",
    "CB 2 BMSG - DBU",
    "CB 3 BMSG - DBU",
    "CB 4 BMSG - DBU",
    "CB 5 BMSG - DBU",
    "CB 6 BMSG - DBU",
    "GVI 1 BMSG - DBU",
    "GVI 2 BMSG - DBU",
    "Commercial 1 BMSG - DBU",
    "Commercial 2 BMSG - DBU",
    "Commercial 3 BMSG - DBU",
    "Commercial 4 BMSG - DBU",
    "Commercial 5 BMSG - DBU",
    "Commercial 6 BMSG - DBU",
]
portfolio_1 = "(" + ", ".join([f"'{x}'" for x in port_list[:41]]) + ")"
portfolio_2 = "(" + ", ".join([f"'{x}'" for x in port_list[41:]]) + ")"
optkey3 = "('BOND')"
optkey4 = "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'VR', 'INDOIS', 'PBS', 'NCD')"
##################################################################################################
# GENERATE CONTENT
##################################################################################################
def get_trdnbr(optkey3="", optkey4="", portfolio=""):
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
    portfolio_query1 = (
        " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio[0] + "\n"
        if portfolio != ""
        else ""
    )
    portfolio_query2 = (
        " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio[1] + "\n"
        if portfolio != ""
        else ""
    )
    query_string = (
        """
        SELECT t.trdnbr
        FROM Trade t   
    """
        + optkey3_query
        + optkey4_query
        + portfolio_query1
        + portfolio_query2
    )
    if optkey3 != "" and optkey4 != "" and portfolio != "":
        freq_vol = len([x[0] for x in ael.asql(query_string)[1][0]])
        total_nominal = sum(
            [acm.FTrade[x[0]].Nominal() for x in ael.asql(query_string)[1][0]]
        )
    else:
        query_results = 0
    return total_nominal, freq_vol


def Fvol_port(port):
    context = acm.GetDefaultContext()
    sheetType = "FPortfolioSheet"
    columnId = "Portfolio Position"
    calcSpace = acm.Calculations().CreateCalculationSpace(context, sheetType)
    ComPort = acm.FCompoundPortfolio[port]
    calculation = calcSpace.CreateCalculation(ComPort, columnId)
    result = calculation.FormattedValue()
    if result == "" or result == "NaN":
        result = "0"
    num_result = abs(float("".join(re.findall(r"\d+", result))))
    return num_result


list_header1 = ["Port", "Volume (USD)", "Limit Given (USD)", "Limit Available (USD)"]
list_header2 = ["Volume", "Freq"] * 3
port_list = ["AFS"]
vol_port, freq_vol = get_trdnbr(optkey3, optkey4, [portfolio_1, portfolio_2])
vol_LimitGiven = 900000000
freq_LimitGiven = 25
afs_value = [
    vol_port,
    freq_vol,
    vol_LimitGiven,
    freq_LimitGiven,
    vol_LimitGiven - vol_port,
    freq_LimitGiven - freq_vol,
]
port_list.extend(afs_value)
port_list = [port_list]
total_list = ["Total"] + afs_value
##################################################################################################
# GENERATE TABLE
##################################################################################################
# Define GUI Parameter
ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "SGMO15 - Total Available for Sale Securities AFS (Volume Limit Summary)",
}
# settings.FILE_EXTENSIONS
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "SGMO15 - Total Available for Sale Securities AFS (Volume Limit Summary)",
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
    # Define Varible that needed
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = "".join(parameter["output_file"])
    input_date = datetime.today()
    date_name = input_date.strftime('%y%m%d')
    full_html_code = (
        open_html()
        + header_html(list_header1, list_header2)
        + content_html(port_list, total_list)
    )
    if output_file == ".xls":
        generate_html = HTMLGenerator().create_html_file(
            full_html_code, file_path, report_name, date_name, False
        )
        generate_file_for_other_extension(generate_html, ".xls")
    elif output_file == ".pdf":
        xslfo_file = xslfo_gen(
            [list_header1, list_header2],
            port_list,
            [total_list],
            report_name,
            file_path,
            str(input_date),
        )
        generate_pdf_from_fo_file(xslfo_file)
