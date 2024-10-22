import re
import ael, acm
import datetime
from datetime import date, timedelta, datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

##################################################################################################
# RUNNING QUERY FUNCTION
##################################################################################################
# Creating Base Query Format
def run_query_asql(date):
    optkey3_list = "('DL', 'BOND', 'REPO', 'FX')"
    optkey4_list = "('ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'VR', 'PBS', 'NCD', 'CL', 'MD', 'CMT', 'BLT', 'BA', 'TOD', 'TOM', 'FWD', 'NDF', 'NS', 'OPT', 'CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'INDOIS', 'CMP', 'OVT', 'OVP', 'SPOT', 'SWAP', 'IWFSBI', 'IWFGOV', 'IWFDIS', 'IWFNON', 'IWFOTH', 'IBSBI', 'IBGOV', 'IBDIS', 'IBNON', 'IBOTH', 'BOB', 'IBOH', 'CWFSBI', 'CWFGOV', 'CWFDIS', 'CWFNON', 'CWFOTH', 'CCSBI', 'CCGV', 'CCDC', 'CCND', 'CCOH', 'CCSBI', 'CCGOV', 'CCOTH')"
    query = f"""
        SELECT
            trdnbr 
        FROM 
            trade tr
        WHERE
            {date} AND
            DISPLAY_ID(tr, 'optkey3_chlnbr') IN {optkey3_list} AND
            DISPLAY_ID(tr, 'optkey4_chlnbr') IN {optkey4_list} AND
            DISPLAY_ID(tr, 'prfnbr') in ('BB BOND PL BMCI', 'BB BOND AC BMCI', 'BB BOND OCI BMCI', 'BB BOND SHARIA PL BMCI', 'BB BOND SHARIA AC BMCI', 'BB BOND SHARIA OCI BMCI', 'CB 1 BMCI', 'GVI 1 BMCI', 'Commercial 1 BMCI', 'IRT DCM 1 BMCI', 'IRT DCM 2 BMCI', 'LIQ IB BMCI', 'FXT Spot Major 1 BMCI', 'FXT Spot Major 2 BMCI', 'FXT Derivatives 1 BMCI', 'FXT Derivatives 2 BMCI')
    """
    ## Running query using AEL ASQL
    val_list = ael.asql(query)[1][0]
    ## Saving Trade Number to list
    trdnbr_list = []
    for i in val_list:
        trdnbr_list.append(i[0])
    return trdnbr_list


# Creating Query Filter Base On optkey3_chlnbr & optkey4_chlnbr
"""
Filter Format
1) ((DISPLAY_ID(tr, 'optkey3_chlnbr') = '{optkey3 value}' AND DISPLAY_ID(tr, 'optkey4_chlnbr') = '{optkey4 value})' OR ....)
2) ((DISPLAY_ID(tr, 'optkey3_chlnbr') = '{optkey3 value}' AND DISPLAY_ID(tr, 'optkey4_chlnbr') IN ('{optkey4 list}')) OR ....)
"""


def filter_query(d_info):
    d_filter = {}
    for key, list_vals in d_info.items():
        list_filter = []
        for list_val in list_vals:
            filter_1 = f"DISPLAY_ID({list_val[0][0][:2]}, '{list_val[0][1]}') = '{list_val[0][2]}'"  ## Filtering for optkey3_chlnbr
            if not isinstance(
                list_val[1][2], list
            ):  ## Check optkey4_chlnbr Value type (List / String)
                if list_val[1][2] != None:
                    filter_2 = f"DISPLAY_ID({list_val[1][0][:2]}, '{list_val[1][1]}') = '{list_val[1][2]}'"  ## Filtering for optkey4_chlnbr (String)
                else:
                    filter_2 = ""
            else:
                join_val = "('" + "', '".join(list_val[1][2]) + "')"
                filter_2 = f"DISPLAY_ID({list_val[1][0][:2]}, '{list_val[1][1]}') IN {join_val}"  ## Filtering for optkey4_chlnbr (List)
            list_filter.append(" AND ".join([filter_1, filter_2]))
        d_filter[key] = "(" + ") OR (".join(list_filter) + ")"
    return d_filter


# Creating Time range for filtering and List Month-Year
def get_time_range(date):
    today_date = datetime.strptime(date, "%Y-%m-%d")
    list_date = [today_date + timedelta(days=31 * i) for i in range(12)] + [
        today_date.replace(year=today_date.year + i) for i in range(1, 6)
    ]  # Get date range from <= 1 Month until >60 Month
    list_date_new = [
        date.replace(day=1).strftime("%d/%m/%Y") for date in list_date
    ]  # Change date format to dd/mm/yyyy to fit with 'value_day' format in ASQL
    list_month_year = [date.replace(day=1).strftime("%b-%y") for date in list_date][
        1:
    ] + [
        "",
        "Dalam Juta USD",
        "",
    ]  # Creating List for column month-year
    filter_months = [
        f"(value_day >= '{list_date_new[i]}' AND value_day < '{list_date_new[i+1]}')"
        if i + 1 < len(list_date_new)
        else f"(value_day >= '{list_date_new[i]}')"
        for i in range(len(list_date_new))
    ]  # Create a filtering format for value_day
    return filter_months, list_month_year, list_date[0].replace(day=1).strftime("%b-%y")


##################################################################################################
# HTML TABLE FUNCTION
##################################################################################################
# Table Info that contains Repricing Gap & Neraca
def info_table(curr, date):
    html_code = f"""
    <tr class="info">
            <td>Repricing Gap</td>
            <td>{curr}</td>
        </tr>
        <tr class="info">
            <td>Neraca</td>
            <td>{date}</td>
        </tr>
    """
    return html_code


# Header info about month range start from neraca date until >60 Month
def month_html_func(list_month):
    open_tr_month = '<tr class="month">\n'  # Generate row
    close_tr_month = "</tr>"  # Close row
    null_col = "<td></td>\n"  # Null column
    list_month_td = []  # List month
    for month in list_month:
        list_month_td.append(f"<td>{month}</td>")
    str_month_td = "\n".join(list_month_td)  # Join list to string
    return open_tr_month + null_col + str_month_td + close_tr_month


def header_html_func(list_header):
    open_tr_head = '<tr class="header">\n'  # Generate Row
    close_tr_head = "</tr>"  # Close Row
    list_head_td = []  # List header
    for header in list_header:
        list_head_td.append(f'<td class="header-val">{header}</td>')
    str_head_td = "\n".join(list_head_td)  # Join list header to string
    return open_tr_head + str_head_td + close_tr_head


def content_html_func(caption, list_content, list_agg):
    caption_html = f'<tr>\n<td class="caption">{caption}</td>\n</tr>\n'  # Generate Caption (Aset / kewajiban)
    list_content_tr = []  # List row of content
    for content in list_content:
        list_content_td = []  # List Column Value per row
        key = f'<td class="content-val">&emsp;{content[0]}</td>'  # Key value per row
        list_content_td.append(key)
        for val_content in content[1]:
            val_html = (
                f'<td class="number-cell">{int(val_content):,}</td>'  # Value column
            )
            list_content_td.append(val_html)
        str_content_td = (
            "<tr>" + "\n".join(list_content_td) + "</tr>"
        )  # Join list content per row to string
        list_content_tr.append(str_content_td)
    str_content = "\n".join(list_content_tr)  # Join list content to string
    # Get aggregate value per table
    list_agg_td = []
    key_agg = f'<td class="agg">{list_agg[0]}</td>'
    list_agg_td.append(key_agg)
    for agg_val in list_agg[1]:
        list_agg_td.append(f'<td class="number-cell-agg">{int(agg_val):,}</td>')
    str_agg = "\n".join(list_agg_td)
    str_agg_tr = "<tr>" + str_agg + "</tr>"
    return caption_html + str_content + str_agg_tr


# Getting balance info
def balance_info_func(list_balance):
    open_tr_bal = "<tr>\n"
    close_tr_bal = "</tr>"
    list_bal_td = []
    list_bal_td.append(f'<td class="balance-title">{list_balance[0]}</td>')
    for bal in list_balance[1]:
        list_bal_td.append(f'<td class="number-cell-balance">{int(bal):,}</td>')
    str_bal_td = "\n".join(list_bal_td)
    return open_tr_bal + str_bal_td + close_tr_bal


# Get value for Periodic Gap & Cummulative Gap
def footer_info_func(list_footer):
    footer = []
    for footers in list_footer:
        open_tr_foot = '<tr class="footer">\n'
        close_tr_foot = "</tr>"
        list_foot_td = []
        list_foot_td.append(f'<td class="caption">{footers[0]}</td>')
        for val_footers in footers[1]:
            list_foot_td.append(
                f'<td class="number-cell-footer">{int(val_footers):,}</td>'
            )
        str_foot_td = open_tr_foot + "\n".join(list_foot_td) + close_tr_foot
        footer.append(str_foot_td)
    str_footer = "\n".join(footer)
    return str_footer


# Generate css style for html table & Merge all HTML Code
def html_generate(table):
    open_code_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <style>
            table{
                border-collapse: collapse;
            }
            .info{
                font-weight: bold;
                text-align: left;
            }
            .month{
                font-weight: bold;
                text-align: center;
            }
            .header-val{
                font-weight: bold;
                border: 2px solid black;
                text-align: center;
            }
            .caption{
                font-weight: bold;
            }
            .agg{
                font-weight: bold;
                text-align: center;
            }
            .number-cell, .content-val{
                border-bottom: 2px solid black;
            }
            .number-cell-balance, .balance-title {
                border-bottom: 2px solid black;
            }
            .balance-title {
                border-left: 2px solid black;
            }
            .number-cell, .number-cell-agg, .number-cell-balance, .number-cell-footer {
                text-align: right;
            }
            .balance-title{
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <table>
    """
    close_code_html = """
        </table>
        </body>
        </html>
    """
    return open_code_html + table + close_code_html


##################################################################################################
# PDF FORMATING
##################################################################################################
# Creating Header table style for XSL-FO
def add_xsl_fo_table_header(
    xsl_fo_content, header_list, header_styling="font-weight='bold' font-size='8px'"
):
    # Open table for XSL-FO Table
    xsl_fo_table = """<fo:table margin-bottom="20px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
    """
    # Generate table column for header
    for i in range(len(header_list)):
        xsl_fo_table += f""" <fo:table-column column-width='{'9%' if i == 0 else '7%' if i == 18 else 'auto'}'/>
        """
    xsl_fo_table += """<fo:table-header font-weight="bold">\n<fo:table-row>
    """
    for i_header in range(len(header_list)):
        xsl_fo_table += (
            f"""<fo:table-cell {header_styling}><fo:block>"""
            + str(header_list[i_header])
            + """</fo:block></fo:table-cell>
        """
        )
    xsl_fo_table += """</fo:table-row></fo:table-header>\n<fo:table-body>
    """
    return xsl_fo_content + xsl_fo_table


## Adding Table row body in XSL-FO
def add_xsl_data_row(
    xsl_content,
    row_data,
    text_align="start",
    cell_styling="border-width='1px' border-style='solid' padding='8pt'",
    block_styling='padding="5pt"',
    xsl_fo_table=False,
):
    xsl_content += (
        """<fo:table margin-bottom="20px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
    """
        if xsl_fo_table == True
        else ""
    )
    xsl_content += (
        """<fo:table-body>
    """
        if xsl_fo_table == True
        else ""
    )
    for row in row_data:
        xsl_content += """<fo:table-row>
        """
        for i_cell in range(len(row)):
            xsl_content += (
                f"""<fo:table-cell text-align='{text_align if text_align == "center" or i_cell == 0 else "right"}'
                            {cell_styling[0]}><fo:block column-width='{'9%' if i_cell == 0 else 'auto'}' {block_styling}>"""
                + str(row[i_cell])
                + """</fo:block></fo:table-cell>
            """
            )
        xsl_content += """</fo:table-row>
        """
    return xsl_content


# Generate XSL-FO & PDF
def xslfo_gen(
    neraca_date,
    list_month_year,
    header,
    data,
    list_agg,
    file_name,
    file_path,
    date,
    aset_caption,
    kewajiban_caption,
):
    text_align1, cell_styling1 = "center", [
        'font-weight="bold" font-size="8px"',
        'font-weight="bold" font-size="8px"',
    ]
    text_align2, cell_styling2 = "start", ['font-size="8px"']
    gen = XSLFOGenerator()
    title = f"Repricing Gap&#160;: USD<fo:block/>Neraca{'&#160;' * 13}: {neraca_date}<fo:block/>"
    xsl_fo_content = gen.prepare_xsl_fo_content(
        title, 'padding="8pt" font-weight="bold" font-size="8px"'
    )
    xsl_fo_content = add_xsl_fo_table_header(xsl_fo_content, list_month_year)
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content,
        [header],
        text_align1,
        cell_styling1,
        'border-width="1px" border-style="solid"',
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content, [aset_caption], text_align2, cell_styling1
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content,
        data[0],
        text_align2,
        cell_styling2,
        'border-bottom="1pt solid black"',
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content, [list_agg[0]], text_align2, cell_styling1
    )
    xsl_fo_content = gen.close_xsl_table(xsl_fo_content)
    xsl_fo_content = add_xsl_fo_table_header(
        xsl_fo_content, [""] * len(list_month_year)
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content,
        [header],
        text_align1,
        cell_styling1,
        'border-width="1px" border-style="solid"',
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content, [kewajiban_caption], text_align2, cell_styling1
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content,
        data[1],
        text_align2,
        cell_styling2,
        'border-bottom="1pt solid black"',
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content, [list_agg[1]], text_align2, cell_styling1
    )
    xsl_fo_content = gen.close_xsl_table(xsl_fo_content)
    xsl_fo_content = add_xsl_fo_table_header(
        xsl_fo_content, [""] * len(list_month_year)
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content,
        [header],
        text_align1,
        cell_styling1,
        'border-width="1px" border-style="solid"',
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content,
        data[2],
        text_align2,
        cell_styling2,
        'border-bottom="1pt solid black"',
    )
    xsl_fo_content = gen.close_xsl_table(xsl_fo_content)
    xsl_fo_content = add_xsl_fo_table_header(
        xsl_fo_content, [""] * len(list_month_year)
    )
    xsl_fo_content = add_xsl_data_row(
        xsl_fo_content, data[3], text_align2, cell_styling2
    )
    xsl_fo_content = gen.close_xsl_table(xsl_fo_content)
    xsl_fo_file = gen.create_xsl_fo_file(file_name, file_path, xsl_fo_content, date)
    return xsl_fo_file


##################################################################################################
# FILTER QUERY (OPTKEY3 & OPTKEY4) - DICTIONARY
##################################################################################################
asset_keys = [
    "1.1 Kas",
    "1.2 Penempatan pada Bank Indonesia",
    "1.3 Penempatan pada Bank Lain",
    "1.4 Tagihan Sport dan Derivative",
    "1.5 Surat berharga yang dimiliki",
    "1.6 S/B Reverse Repo",
    "1.7 Kredit yang diberikan",
    "1.8 OKPN",
    "1.9 Tagihan Akseptasi",
    "1.10 Aktiva Tetap dan Inventaris",
    "1.11 Rupa Rupa Aktiva",
]
kewajiban_keys = [
    "2.1. Giro",
    "2.2. Tabungan",
    "2.3. Depo Berjangka",
    "2.4. Kewajiban Kepada BI",
    "2.5. Kewajiban Kepada Bank Lain",
    "2.6. Kewajiban Spot dan Derivative",
    "2.7. Kewajiban Surat Berharga (Repo)",
    "2.8. Kewajiban Akseptasi",
    "2.9. Pinjaman Diterima",
    "2.10. Kewajiban Lain-Lain",
]
##################################################################################################
# TABLE CONTENT
##################################################################################################
# Header list for table
list_header = [
    "Skala Waktu",
    "&#8804;1 Mo",
    ">1 Mo - 2 Mo",
    ">2 Mo - 3 Mo",
    ">3 Mo - 4 Mo",
    ">4 Mo - 5 Mo",
    ">5 Mo - 6 Mo",
    ">6 Mo - 7 Mo",
    ">7 Mo - 8 Mo",
    "> 8 Mo - 9 Mo",
    "> 9 Mo - 10 Mo",
    "> 10 Mo - 11 Mo",
    "> 11 Mo - 12 Mo",
    "> 12 Mo - 24 Mo",
    "> 24 Mo - 36 Mo",
    "> 36 Mo - 48 Mo",
    "> 48 Mo - 60 Mo",
    "> 60",
    "Non Rate Sensitive Items",
    "TOTAL",
]
##################################################################################################
# GENERATE TABLE
##################################################################################################
# Define GUI Parameter
ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "CI02 - Repricing GAP",
}
# settings.FILE_EXTENSIONS
ael_variables = [
    ["report_name", "Report Name", "string", None, "CI02 - Repricing GAP", 1, 0],
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
        [".xls", ".pdf"],
        ".xls",
        0,
        0,
        "Select Output Extension Type",
    ],
]
input_date = date.today()
# Running GUI System
def ael_main(parameter):
    # Define Varible that needed
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = "".join(parameter["output_file"])
    # Getting Time range on a month start from currently month
    filter_months, list_month_year, neraca_date = get_time_range(
        str(input_date.replace(day=1))
    )
    # Get parameter for ACM Calculation
    context = acm.GetDefaultContext()
    sheetType = "FTradeSheet"
    columnId = "Portfolio Position"
    ## TABLE CONTENT FOR ASET
    caption_aset = "1. Aset"  # Caption
    list_content_aset = []
    for key in asset_keys:
        # sql_filter = filter_query(d_filter_aset) # Generate Query Filter
        list_total_per_date = []
        for date in filter_months:
            trdnbr_query_result = run_query_asql(date)  # Run SQL Query
            calcSpace = acm.Calculations().CreateCalculationSpace(
                context, sheetType
            )  # Running Calculation
            port_value = []
            for trade_num in trdnbr_query_result:
                dataTrade = acm.FTrade[trade_num]
                calculation = calcSpace.CreateCalculation(dataTrade, columnId)
                result = calculation.FormattedValue()
                if result == "":
                    result = "0"
                num_result = float("".join(re.findall(r"\d+", result)))
                if num_result >= 0:
                    port_value.append(num_result)
            list_total_per_date.append(sum(port_value))
        for x in [0, sum(list_total_per_date)]:
            list_total_per_date.append(x)
        list_content_aset.append([key, list_total_per_date])
    list_agg_asset = ["TOTAL ASSET"]
    agg_val_aset = []
    for i in range(len(list_content_aset[0][1])):
        agg_val_aset.append(
            sum([list_content_aset[x][1][i] for x in range(len(list_content_aset))])
        )
    list_agg_asset.append(agg_val_aset)
    ## TABLE CONTENT FOR KEWAJIBAN
    caption_kewajiban = "2. Kewajiban"
    list_content_kewajiban = []
    for key in kewajiban_keys:
        # sql_filter = filter_query(d_filter_aset) # Generate Query Filter
        list_total_per_date = []
        for date in filter_months:
            trdnbr_query_result = run_query_asql(date)  # Run SQL Query
            calcSpace = acm.Calculations().CreateCalculationSpace(
                context, sheetType
            )  # Running Calculation
            port_value = []
            for trade_num in trdnbr_query_result:
                dataTrade = acm.FTrade[trade_num]
                calculation = calcSpace.CreateCalculation(dataTrade, columnId)
                result = calculation.FormattedValue()
                if result == "":
                    result = "0"
                num_result = float("".join(re.findall(r"\d+", result)))
                if num_result >= 0:
                    port_value.append(num_result)
            list_total_per_date.append(sum(port_value))
        for x in [0, sum(list_total_per_date)]:
            list_total_per_date.append(x)
        list_content_kewajiban.append([key, list_total_per_date])
    list_agg_kewajiban = ["TOTAL LIABILITIES"]
    agg_val_kewajiban = []
    for i in range(len(list_content_kewajiban[0][1])):
        agg_val_kewajiban.append(
            sum(
                [
                    list_content_kewajiban[x][1][i]
                    for x in range(len(list_content_kewajiban))
                ]
            )
        )
    list_agg_kewajiban.append(agg_val_kewajiban)
    list_balance = [
        "4. Off Balance Sheet",
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    periodic_gap = [
        agg_val_aset[0] - agg_val_kewajiban[0]
        if agg_val_aset[0] - agg_val_kewajiban[0] >= 0
        else f"({agg_val_aset[0] - agg_val_kewajiban[0]})"
    ]
    cummulative_gap = [
        agg_val_aset[0] - agg_val_kewajiban[0]
        if agg_val_aset[0] - agg_val_kewajiban[0] >= 0
        else f"({agg_val_aset[0] - agg_val_kewajiban[0]})"
    ]
    for i in range(len(agg_val_aset) - 1):
        periodic_gap_temp = (
            agg_val_aset[i + 1] - agg_val_kewajiban[i + 1]
            if agg_val_aset[i + 1] - agg_val_kewajiban[i + 1] >= 0
            else f"({agg_val_aset[i+1] - agg_val_kewajiban[i+1]})"
        )
        periodic_gap.append(periodic_gap_temp)
        cummulative_gap_temp = (
            cummulative_gap[i] + agg_val_aset[i + 1]
            if cummulative_gap[i] + agg_val_aset[i + 1] >= 0
            else f"({cummulative_gap[i] + agg_val_aset[i+1]})"
        )
        cummulative_gap.append(cummulative_gap_temp)
    list_footer = [["PERIODIC GAP", periodic_gap], ["CUMMULATIVE GAP", cummulative_gap]]
    skip_row = "<tr><td>&nbsp;</td></tr>"
    table_info = info_table("USD", neraca_date) + skip_row
    Asset = (
        month_html_func(list_month_year)
        + header_html_func(list_header)
        + content_html_func(caption_aset, list_content_aset, list_agg_asset)
    )
    kewajiban = (
        skip_row
        + header_html_func(list_header)
        + content_html_func(
            caption_kewajiban, list_content_kewajiban, list_agg_kewajiban
        )
    )
    balance = skip_row + header_html_func(list_header) + balance_info_func(list_balance)
    footer = skip_row + footer_info_func(list_footer)
    table_html_full = (
        table_info + "\n" + Asset + "\n" + kewajiban + "\n" + balance + "\n" + footer
    )
    full_code_html = html_generate(table_html_full)
    date_name = datetime.today().strftime('%y%m%d')
    if output_file == ".pdf":
        aset_caption = [caption_aset] + [""] * len(list_header[1:])
        kewajiban_caption = [caption_kewajiban] + [""] * len(list_header[1:])
        data_asets = [["&#160;" * 5 + x[0]] + x[1] for x in list_content_aset]
        data_kewajibans = [["&#160;" * 5 + x[0]] + x[1] for x in list_content_kewajiban]
        list_footers = [[x[0]] + x[1] for x in list_footer]
        list_agg_assets = [list_agg_asset[0]] + list_agg_asset[1]
        list_agg_kewajibans = [list_agg_kewajiban[0]] + list_agg_kewajiban[1]
        data_balance = [list_balance[0]] + list_balance[1]
        xslfo_file = xslfo_gen(
            neraca_date,
            [""] + list_month_year,
            list_header,
            [data_asets, data_kewajibans, [data_balance], list_footers],
            [list_agg_assets, list_agg_kewajibans],
            report_name,
            file_path,
            date_name,
            aset_caption,
            kewajiban_caption,
        )
        generate_pdf_from_fo_file(xslfo_file)
    elif output_file == ".xls":
        generate_html = HTMLGenerator().create_html_file(
            full_code_html, file_path, report_name, date_name, False
        )
        generate_file_for_other_extension(generate_html, ".xls")
