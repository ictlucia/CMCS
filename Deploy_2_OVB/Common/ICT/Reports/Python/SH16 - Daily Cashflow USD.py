from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from datetime import date
import acm, ael
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer
import datetime
import re
from Report_Python_P2 import usd_price_mtm


def adding_data_row(html_content, row_data, row_class="", cell_class=""):
    for row in row_data:
        html_content += f"<tr {row_class}>"
        for cell in row:
            if "isNum" in str(cell):
                html_content += (
                    f'<td style="text-align : right">'
                    + str(cell).replace("isNum", "")
                    + "</td>"
                )
            elif str(cell) in ["NET CASH FLOW (B - C)", "SALDO KUMULATIF"]:
                html_content += f"<td>" + str(cell) + "</td>"
            else:
                html_content += f"<td {cell_class}>" + str(cell) + "</td>"
        html_content += "</tr>"
    return html_content


def get_optkey3_oid(optkey_string):
    optkey = acm.FChoiceList.Select("list=Product Type")
    for name in optkey:
        if name.Name() == optkey_string:
            return name.Oid()


def get_optkey4_oid(optkey_string):
    optkey = acm.FChoiceList.Select("list=Category")
    for name in optkey:
        if name.Name() == optkey_string:
            return name.Oid()


def get_data(
    optkey3="", optkey4="", portfolio="", bank="", type="", port_type="", time_bucket=""
):
    # Setting the Blank Value
    if (
        optkey3 == ""
        and optkey4 == ""
        and portfolio == ""
        and bank == ""
        and type == ""
        and port_type == ""
    ):
        return 0
    else:
        optkey3_query = ""
        optkey4_query = ""
        portfolio_query = ""
        bank_query = ""
        type_query = ""
        time_query = ""
        end_date = "i.exp_day"
        date_today = acm.Time.DateToday()
        if "FX" in optkey3:
            end_date = "t.value_day"
        # Setting up Date Mapping
        if time_bucket == date_today:
            time_query = (
                " and "
                + end_date
                + " >'"
                + acm.Time.DateAddDelta(date_today, 0, 0, -1)
                + "' and "
                + end_date
                + " <= '"
                + date_today
                + "'"
            )
        elif time_bucket == "Next Day":
            time_query = (
                " and "
                + end_date
                + " >'"
                + acm.Time.DateAddDelta(date_today, 0, 0, 1)
                + "' and "
                + end_date
                + " <= '"
                + acm.Time.DateAddDelta(date_today, 0, 0, 2)
                + "'"
            )
        elif time_bucket == "2 - 7 Days":
            time_query = (
                " and "
                + end_date
                + " >'"
                + acm.Time.DateAddDelta(date_today, 0, 0, 2)
                + "' and "
                + end_date
                + " <= '"
                + acm.Time.DateAddDelta(date_today, 0, 0, 8)
                + "'"
            )
        elif time_bucket == "7 days - I Month":
            time_query = (
                " and "
                + end_date
                + " >'"
                + acm.Time.DateAddDelta(date_today, 0, 0, 7)
                + "' and "
                + end_date
                + " <= '"
                + acm.Time.DateAddDelta(date_today, 0, 1, 0)
                + "'"
            )
        elif time_bucket == "1-3 Months":
            time_query = (
                " and "
                + end_date
                + " >'"
                + acm.Time.DateAddDelta(date_today, 0, 1, 0)
                + "' and "
                + end_date
                + " <= '"
                + acm.Time.DateAddDelta(date_today, 0, 3, 0)
                + "'"
            )
        elif time_bucket == "3-6 Months":
            time_query = (
                " and "
                + end_date
                + " >'"
                + acm.Time.DateAddDelta(date_today, 0, 3, 0)
                + "' and "
                + end_date
                + " <= '"
                + acm.Time.DateAddDelta(date_today, 0, 6, 0)
                + "'"
            )
        # Setting up Additional Query for Specific Banks
        if bank == "Correspondent Bank":
            bank_query = " and p.correspondent_bank='Yes'"
        elif bank == "Interbank":
            bank_query = " and p.ptyid LIKE '%Mandiri%'"
        # Setting up Additional Query for Specific Types
        if type == "Loan" or type == "Sell":
            type_query = " and t.quantity > 0"
        elif type == "Deposit" or type == "Buy":
            type_query = " and t.quantity < 0"
        if optkey3:
            optkey3_query = " AND DISPLAY_ID(t, 'optkey3_chlnbr') in " + optkey3
        if optkey4:
            optkey4_query = " AND DISPLAY_ID(t, 'optkey4_chlnbr') in " + optkey4
        if portfolio:
            portfolio_query = " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio
        # Setting up the Query
        query = (
            f"""
                SELECT t.price, t.quantity, t.trdnbr FROM trade t, instrument i, party p 
                where t.insaddr=i.insaddr and t.counterparty_ptynbr = p.ptynbr
                """
            + optkey3_query
            + optkey4_query
            + portfolio_query
            + time_query
            + bank_query
            + type_query
        )
        result = ael.asql(query)
        total_nominal = 0
        for row in result[1][0]:
            tradeCurr = acm.FTrade[row[2]].Currency().Name()
            if any(col != None for col in row):
                if tradeCurr == "USD":
                    nominal = row[0] * row[1]
                else:
                    usd_price = usd_price_mtm(acm.FTrade[row[2]], "USD")
                    nominal = (
                        ((usd_price * row[0]) * row[1])
                        if usd_price != None
                        else ((15000 * row[0]) * row[1])
                    )
            total_nominal += nominal
        return total_nominal


def process_text(ael_params, raw_text):
    processed_string = raw_text.replace("<Date>", acm.Time.DateToday())
    processed_string = processed_string.replace(
        "<Report Name>", ael_params["report_name"]
    )
    return processed_string


ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "SH16 - Daily Cashflow USD",
}
ael_variables = [
    ["report_name", "Report Name", "string", None, "SH16 - Daily Cashflow USD", 1, 0],
    [
        "file_path",
        "Folder Path",
        getFilePathSelection(),
        None,
        getFilePathSelection(),
        1,
        1,
    ],
    ["currency", "Currency Of Choice", "string", ["USD"], "USD", 0, 0],
    [
        "output_file",
        "Secondary Output Files",
        "string",
        [".pdf", ".xls"],
        ".xls",
        0,
        1,
        "Select Secondary Extensions Output",
    ],
    [
        "email_params",
        "Email Params",
        "string",
        None,
        "ribka.siahaan@bankmandiri.co.id, tqatestingbo@gmail.com\\ <Report Name> - <Date>\\ Dear Sir / Madam, <br><br><Report Name> as of <Date>\\ ",
        0,
        0,
    ],
]


def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = parameter["output_file"]
    email_params = str(parameter["email_params"])
    currency = str(parameter["currency"])
    title_style = """
        .title {
            color: #800000;
            text-align: left;   
        }
        .subtitle-1 {
            color: #0000FF;
            font-size: 20px;
            text-align: left;
            font-weight: bold;
        }
        .subtitle-2 {
            color: #000080;
            font-size: 16px;
            text-align: left;
        }
        .amount {
            font-weight: bold;
        }
        .currency {
            background-color:blue;
            color:white;
            text-align:center;
        }
        .bold {
        }
        td {
            text-align:left;
        }
        .deskripsi {
            text-align:center;
        }
        .subtitle-3 {
            text-align:left;
            color: blue;
            border: hidden;
        }
        .subtitle-4 {
            text-align:right;
            font-size:15px;
            color: white;
            background-color: orange;
            border: hidden;
        }
    """
    current_date = datetime.date.today().strftime("%y%m%d")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content(
        "Daily Cashflow Report - Cashflow as per. " + current_date, title_style
    )
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content(
        "Daily Cashflow Report - Cashflow as per. " + current_date
    )
    title = [" ", " "]
    # TITLE
    html_content += "<div><table>"
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(
        html_content, "LAPORAN DAILY CASHFLOW", 'colspan="3" style=" border: hidden;"'
    )
    html_content = html_gen.close_table_row(html_content)
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(
        html_content, "&nbsp;", 'style=" border: hidden;"'
    )
    html_content = html_gen.close_table_row(html_content)
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(
        html_content,
        "POSISI LIKUIDITAS PER",
        'colspan="3" class="subtitle-3" style="margin-botton:-20px"',
    )
    html_content = html_gen.add_cell_data(
        html_content,
        date.today().strftime("%d-%b-%y"),
        'class="subtitle-3" style="border:hidden; text-align: right"',
    )
    html_content = html_gen.close_table_row(html_content)
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(
        html_content, "Dlm USD (Million)", 'colspan="3" class="subtitle-3"'
    )
    html_content = html_gen.close_table_row(html_content)
    # html_content = html_gen.add_cell_data(html_content,' '+current_date,'class="subtitle-4"')
    # Preparing Title
    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>
    """
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    html_content = html_gen.add_cell_data(
        html_content, title[0], 'rowspan=2 colspan="3" class="deskripsi"'
    )
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content, title[0], 'number-rows-spanned="2"'
    )
    html_content = html_gen.add_cell_data(
        html_content, title[1], 'colspan=6 class="currency"'
    )
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content,
        title[1],
        'number-columns-spanned="6" background-color="blue" color="white" font-weight="bold"',
    )
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    time_bucket = [
        [
            date.today().strftime("%d-%b-%y"),
            "Next day",
            "2 - 7 days",
            "7 days - I Month",
            "1-3 Months",
            "3-6 Months",
        ]
    ]
    # Adding Time Bucket
    html_content = html_gen.add_data_row(
        html_content, time_bucket, "", 'style="text-align:center"'
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content, time_bucket)
    # Adding row [A.Saldo Nostro]
    saldo_nostro = [f"{x:,}" for x in [0, 0, 0, 0, 0, 0]]
    # QUERY FILTER OPTKEY3
    # DL, BOND, FX
    # QUERY FILTER OPTKEY4
    # TOD, TOM, SPOT, FWD, SWAP, OPT, NDF, CBIDR, CBUSD, CBVALAS, UST, BILLS, ROI, ORI, INDOIS, NCD, SVBUSD, SVBLCY, OVT, CMP, OVP, BA, CMT, BLT, BA
    optkey4_list = [
        "('BA', 'BLT')",
        "('CBIDR', 'CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'INDOIS', 'NCD', 'SVBUSD', 'SVBLCY')",
        "('TOD', 'TOM', 'SPOT', 'FWD', 'NDF', 'SWAP', 'OPT')",
    ]
    html_content = html_gen.add_data_row(
        html_content, [["A", "SALDO NOSTRO &#38; KAS"] + saldo_nostro], "", "class=bold"
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [["A", "SALDO NOSTRO &#38; KAS"] + saldo_nostro],
        "",
        'font-weight="bold"',
    )
    html_content = html_content.replace(
        "<td class=bold>SALDO NOSTRO &#38; KAS</td>",
        '<td colspan="2" class=bold>SALDO NOSTRO &#38; KAS</td>',
    )
    html_content = html_content.replace(
        "<td class=bold>null-a1</td>",
        '<td class=bold style="background-color:yellow">1</td>',
    )
    html_content = html_content.replace(
        "<td class=bold>testwidth</td>", '<td class=bold style="width : 500px">1</td>'
    )
    port_list = [
        "('IRT DCM 1 BMSH - ACU', 'IRT DCM 2 BMSH - ACU', 'IRT DCM 1 BMSH - DBU', 'IRT DCM 2 BMSH - DBU')",
        "('BB BOND OCI BMSH - ACU', 'BB BOND OCI BMSH - DBU')",
        "('BB BOND AC BMSH - ACU', 'BB BOND AC BMSH - DBU')",
    ]
    # Adding row [B.Inflow]
    list_value_b = []
    sub_row_b = {
        "INFLOW": ["", "", "", "", "", ""],
        "Penempatan Interbank Jatuh Tempo": [
            "('DL')",
            "('CMP')",
            "",
            "Correspondent Bank",
            "Loan",
            "",
        ],
        "Pinjaman Interbank": [
            "('DL')",
            "('CMT')",
            "",
            "Correspondent Bank",
            "Deposit",
            "",
        ],
        "Penempatan Interoffice Jatuh Tempo": [
            "('DL')",
            "('OVP')",
            "",
            "Interbank",
            "Loan",
            "",
        ],
        "Pinjaman Interoffice": ["('DL')", "('OVT')", "", "Interbank", "Deposit", ""],
        "Borrowing (BA Financing/Term Loan)": [
            "('DL')",
            optkey4_list[0],
            "",
            "",
            "Deposit",
            "",
        ],
        "Trade Finance Jatuh Tempo": ["", "", "", "", "", ""],
        "Usance": ["", "", "", "", "", ""],
        "Sight": ["", "", "", "", "", ""],
        "TR": ["", "", "", "", "", ""],
        "Others": ["", "", "", "", "", ""],
        "Penerimaan Trade Services": ["", "", "", "", "", ""],
        "Securities Jatuh Tempo &#38; Penerimaan Coupon": ["", "", "", "", "", ""],
        "HFT": ["('BOND')", optkey4_list[1], port_list[0], "", "", "", "FVTPL"],
        "AFS": ["('BOND')", optkey4_list[1], port_list[1], "", "", "", "FVOCI"],
        "HTM": [
            "('BOND')",
            optkey4_list[1],
            port_list[2],
            "",
            "",
            "",
            "Amortised Cost",
        ],
        "Pelunasan Pinjaman Nasabah (Pokok &#38; Bunga)": ["", "", "", "", "", ""],
        "Lainnya": ["", "", "", "", "", ""],
        "": ["", "", "", "", "", ""],
        "ADDITIONAL VARIABLES FOR NON BANK INSTITUTION": ["", "", "", "", "", ""],
        "Deposito / DOC Jatuh Tempo": ["", "", "", "", "", ""],
        "Penjualan Obligasi (proprietary trading)": ["", "", "", "", "", ""],
        "Pembelian USD": ["('FX')", optkey4_list[2], "", "", "Buy", ""],
        "Pelunasan Funding Bonds &#38; IPO": ["", "", "", "", "", ""],
    }
    total_sub_row_b = [float(x.replace(",", "")) for x in saldo_nostro]
    for key, value in sub_row_b.items():
        temp_row = ["B" if key == "INFLOW" else ""]
        temp_row.extend(
            [key]
            if key in ["INFLOW", "ADDITIONAL VARIABLES FOR NON BANK INSTITUTION"]
            else ["-", key]
            if key
            not in [
                "UPAS&emsp;*5)",
                "TR&emsp;*8)",
                "Others&emsp;*5)",
                "HFT",
                "AFS",
                "HTM",
            ]
            else ["", f"- {key}"]
        )
        for i in range(len(time_bucket[0])):
            val = get_data(
                value[0],
                value[1],
                value[2],
                value[3],
                value[4],
                value[5],
                time_bucket[0][i],
            )
            temp_row.append(val)
        for i in range(3, len(temp_row)):
            total_sub_row_b[i - 3] += temp_row[i]
            temp_row[i] = f"{temp_row[i]:,}isNum"
        list_value_b.append(temp_row)
    html_content = adding_data_row(
        html_content, list_value_b, "", 'style="text-align: left;"'
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content, list_value_b, "", 'text-align="left"'
    )
    html_content = html_content.replace(
        '<td style="text-align: left;">B</td>', '<td style="text-align: center;">B</td>'
    )
    html_content = html_content.replace(
        '<td style="text-align: left;">-</td>', '<td style="text-align: center;">-</td>'
    )
    html_content = html_content.replace(
        '<td style="text-align: left;">INFLOW</td>',
        '<td colspan="2" style="text-align: left;">INFLOW</td>',
    )
    html_content = html_content.replace(
        '<td style="text-align: left;">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>',
        '<td colspan="2" style="text-align: left">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>',
    )
    sub_total_b = [["Sub Total Inflow"] + [f"{x:,}" for x in total_sub_row_b]]
    old_att = 'style="text-align: left;  border-top: 1px black solid; border-bottom: 1px black solid;"'
    new_att = 'colspan="3" style="border-top: 1px black solid; border-bottom: 1px black solid; text-align: left; "; "'
    html_content = adding_data_row(
        html_content,
        [[sub_total_b[0][0]] + [str(x) + "isNum" for x in sub_total_b[0][1:]]],
        "",
        old_att,
    )
    html_content = html_content.replace(
        f"<td {old_att}>Sub Total Inflow</td>", f"<td {new_att}>Sub Total Inflow</td>"
    )
    # Adding row [C. Outflow]
    sub_row_c = {
        "OUTFLOW": ["", "", "", "", "", ""],
        "Penempatan Interbank (Interbank Placement)": [
            "('DL')",
            "('CMP')",
            "",
            "Correspondent Bank",
            "Deposit",
            "",
        ],
        "Pinjaman Interbank Jatuh Tempo": [
            "('DL')",
            "('CMT')",
            "",
            "Correspondent Bank",
            "Loan",
            "",
        ],
        "Penempatan Interoffice": ["('DL')", "('OVP')", "", "Interbank", "Deposit", ""],
        "Pinjaman Interoffice Jatuh Tempo": [
            "('DL')",
            "('OVT')",
            "",
            "Interbank",
            "Loan",
            "",
        ],
        "Borrowing (BA Financing/Term Loan) Jatuh Tempo": [
            "('DL')",
            optkey4_list[0],
            "",
            "",
            "",
            "",
        ],
        "Penarikan Trade Finance": ["", "", "", "", "", ""],
        "Usance": ["", "", "", "", "", ""],
        "Sight": ["", "", "", "", "", ""],
        "TR": ["", "", "", "", "", ""],
        "Others": ["", "", "", "", "", ""],
        "Deposit Nasabah Jatuh Tempo": ["", "", "", "", "", ""],
        "Pembelian Securities": ["", "", "", "", "", ""],
        "HFT": ["('BOND')", optkey4_list[1], port_list[0], "", "", "Amortised Cost"],
        "AFS": ["('BOND')", optkey4_list[1], port_list[1], "", "", "FVOCI"],
        "HTM": ["('BOND')", optkey4_list[1], port_list[2], "", "", "FVTPL"],
        "Penarikan Pinjaman Nasabah": ["", "", "", "", "", ""],
        "Saldo Vostro": ["", "", "", "", "", ""],
        "Lainnya": ["", "", "", "", "", ""],
        "": ["", "", "", "", "", ""],
        "ADDITIONAL VARIABLES FOR NON BANK INSTITUTION": ["", "", "", "", "", ""],
        "Penempatan Deposito / DOC": ["", "", "", "", "", ""],
        "Pembelian Obligasi (proprietary trading)": ["", "", "", "", "", ""],
        "Penjualan USD": ["('FX')", optkey4_list[2], "", "", "Sell", ""],
        "Funding Bonds &#38; IPO": ["", "", "", "", "", ""],
        "Biaya Operasional": ["", "", "", "", "", ""],
    }
    # List for the values
    list_value_c = []
    total_sub_row_c = [0] * 6
    # Function for Populating Values
    for key, value in sub_row_c.items():
        temp_row = ["C" if key == "OUTFLOW" else ""]
        temp_row.extend(
            [key]
            if key in ["OUTFLOW", "ADDITIONAL VARIABLES FOR NON BANK INSTITUTION"]
            else ["-", key]
            if key
            not in [
                "Sight&emsp;*5)",
                "TR&emsp;*8)",
                "Others&emsp;*5)",
                "HFT",
                "AFS",
                "HTM",
            ]
            else ["", f"- {key}"]
        )
        for i in range(len(time_bucket[0])):
            val = get_data(
                value[0],
                value[1],
                value[2],
                value[3],
                value[4],
                value[5],
                time_bucket[0][i],
            )
            temp_row.append(val)
        for i in range(3, len(temp_row)):
            total_sub_row_c[i - 3] += float(temp_row[i])
            temp_row[i] = f"{temp_row[i]:,}isNum"
        list_value_c.append(temp_row)
    html_content = adding_data_row(
        html_content, list_value_c, "", 'style="text-align: left;"'
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content, list_value_c, "", 'text-align="left"'
    )
    html_content = html_content.replace(
        '<td style="text-align: left;">C</td>', '<td style="text-align: center;">C</td>'
    )
    html_content = html_content.replace(
        '<td style="text-align: left;">-</td>', '<td style="text-align: center;">-</td>'
    )
    html_content = html_content.replace(
        '<td style="text-align: left;">OUTFLOW</td>',
        '<td colspan="2" style="text-align: left;">OUTFLOW</td>',
    )
    html_content = html_content.replace(
        '<td style="text-align: left;">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>',
        '<td colspan="2" style="text-align: left">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>',
    )
    sub_total_c = [["Sub Total Outflow"] + [f"{x:,}" for x in total_sub_row_c]]
    old_att = 'style="text-align: left;  border-top: 1px black solid; border-bottom: 1px black solid;"'
    new_att = 'colspan="3" style="border-top: 1px black solid; border-bottom: 1px black solid; text-align: left; "; "'
    html_content = adding_data_row(
        html_content,
        [[sub_total_c[0][0]] + [str(x) + "isNum" for x in sub_total_c[0][1:]]],
        "",
        old_att,
    )
    html_content = html_content.replace(
        f"<td {old_att}>Sub Total Outflow</td>", f"<td {new_att}>Sub Total Outflow</td>"
    )
    # Adding row [D. Net Cash Flow (B - C)]
    net_cashflow_val = []
    for total_b, total_c in zip(sub_total_b[0][1:], sub_total_c[0][1:]):
        net_cashflow_val.append(
            float(total_b.replace(",", "")) - float(total_c.replace(",", ""))
        )
    net_cashflow = [
        ["D", "NET CASH FLOW (B - C)"] + [f"{x:,}" for x in net_cashflow_val]
    ]
    html_content = adding_data_row(
        html_content,
        [net_cashflow[0][0:2] + [str(x) + "isNum" for x in net_cashflow[0][2:]]],
        "",
        'class=bold colspan="2"',
    )
    # Adding row [E. Saldo Kumulatif]
    saldo_kumulatif_val = [net_cashflow_val[0]]
    for i, net_cashflow in enumerate(net_cashflow_val[1:]):
        saldo_kumulatif_val.append(net_cashflow + saldo_kumulatif_val[i])
    saldo_kumulatif = [
        ["E", "SALDO KUMULATIF"] + [f"{x:,}" for x in saldo_kumulatif_val]
    ]
    print(
        [[saldo_kumulatif[0][0]] + [str(x) + "isNum" for x in saldo_kumulatif[0][1:]]]
    )
    html_content = adding_data_row(
        html_content,
        [saldo_kumulatif[0][0:2] + [str(x) + "isNum" for x in saldo_kumulatif[0][2:]]],
        "",
        'class=bold colspan="2"',
    )
    report_name_list = [
        "SALDO NOSTRO &#38; KAS&emsp;*3)",
        "MANDATORY DEPOSIT LRA &#38; CRA BCTL",
        "SALDO TERSEDIA&emsp;*3)",
        "NET CASH FLOW (B - C)",
        "SALDO KUMULATIF",
        "LIMIT INTERNAL CUMULATIVE MISMATCH PER BUCKET&emsp;*9)",
        "EXCESS (GAP) TO LIMIT",
    ]
    for reports_name in report_name_list:
        html_content = html_content.replace(
            f"<td class=bold>{reports_name}</td>",
            f'<td class="bold" colspan="2">{reports_name}</td>',
        )
    color_val_col = ["#7AB5DE", "#9DACB6", "#73E563"]
    for val_col, color_col in zip(["val-e", "val-f", "val-g"], color_val_col):
        html_content = html_content.replace(
            f"<td class=bold>{val_col}</td>",
            f'<td style="background-color:{color_col};"></td>',
        )
    xsl_fo_content = xsl_fo_content.replace("emsp", "#160")
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    html_content = html_content.replace(">0<", "><")
    html_file = html_gen.create_html_file(
        html_content, file_path, report_name, current_date, True
    )
    xsl_fo_file = xsl_gen.create_xsl_fo_file(
        report_name, file_path, xsl_fo_content, current_date
    )
    generated_reports = []
    for i in output_file:
        if i != ".pdf":
            generate_file_for_other_extension(html_file, i)
            xls_file = html_file.split(".")
            xls_file[-1] = "xls"
            xls_file = ".".join(xls_file)
            generated_reports.append(xls_file)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
            pdf_file = xsl_fo_file.split(".")
            pdf_file[-1] = "pdf"
            pdf_file = ".".join(pdf_file)
            generated_reports.append(pdf_file)
    SMTPParameters = FParameterUtils.GetFParameters(
        acm.GetDefaultContext(), "CustomReportSMTPParameters"
    )
    hostname = str(SMTPParameters.At("SMTPServer"))
    port = int(SMTPParameters.At("SMTPPort").Text())
    username = SMTPParameters.At("EmailUserName").Text()
    password = SMTPParameters.At("SMTPPassword").Text()
    tls_mode = bool(SMTPParameters.At("SecureSMTPConnection").Text())
    # Setup SMTPServer Object
    SMTPServer = ICTCustomFEmailTransfer.SMTPServer(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        tls_mode=tls_mode,
    )
    # Setup Message Object
    split_params = email_params.split("\\ ")
    recipients = split_params[0].split(", ")
    subject = process_text(parameter, split_params[1])
    sender = SMTPParameters.At("EmailSender").Text()
    body = process_text(parameter, split_params[2])
    cc = None if len(parameter) <= 3 else split_params[3].split(", ")
    MessageObject = ICTCustomFEmailTransfer.Message(
        recipients, subject, sender, body, cc, generated_reports
    )
    # Send email
    EmailTransfer = ICTCustomFEmailTransfer(SMTPServer, MessageObject)
    try:
        EmailTransfer.Send()
        print("Email transfer successful for", report_name)
    except Exception as e:
        print("Email Transfer failed:", e)
