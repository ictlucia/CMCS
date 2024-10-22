from datetime import date, timedelta, datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael

html_gen = HTMLGenerator()
xsl_gen = XSLFOGenerator()


def getFilePathSelection(status=True):
    """Directory selector dialog"""
    selection = acm.FFileSelection()
    selection.PickDirectory(status)
    selection.SelectedDirectory = "D:\\HTML-Folder\\"
    return selection


def create_total_table(html_content, list_data):
    count = 0
    html_content = html_gen.open_table_row(html_content)
    for each_total in list_data:
        if count == 1:
            html_content = html_gen.add_cell_data(
                html_content, each_total, 'class="right"'
            )
        elif count == 3:
            html_content = html_gen.add_cell_data(
                html_content, each_total, 'style="background-color:#b3b5b4"'
            )
        else:
            html_content = html_gen.add_cell_data(html_content, each_total)
        count += 1
    html_content = html_gen.close_table_row(html_content)
    return html_content


def create_total_table_xsl(xsl_fo_content, list_data):
    count = 0
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    for each_total in list_data:
        if count == 1:
            xsl_fo_content = xsl_gen.add_xsl_column(
                xsl_fo_content, each_total, 'text-align="right"'
            )
        elif count == 3:
            xsl_fo_content = xsl_gen.add_xsl_column(
                xsl_fo_content, each_total, 'background-color="#b3b5b4"'
            )
        else:
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, each_total)
        count += 1
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    return xsl_fo_content


ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "HKO09 - Liquidity Maintenance Ratio",
}
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "HKO09 - Liquidity Maintenance Ratio",
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
    ["start_date", "Start Date", "string", None, acm.Time.DateToday(), 0, 1],
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
]


def ael_main(parameter):
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = parameter["output_file"]
    title_style = """
        .title {
            color: black;
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
        .bold {
            font-weight: bold;
        }
        .left {
            text-align: left;
        }
        .right {
            text-align: right;
        }
        .subtitle-3 {
            text-align:left;
            font-weight:bold;
            font-size:15px;
            text-decoration: underline;
            border: hidden;
        }
    """
    current_date = get_current_date("")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content(
        "HKO09 - Liquidity Maintenance Ratio as per. " + date_today, title_style
    )
    html_content = html_gen.prepare_html_table(html_content, "")
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content(
        "HKO09 - Liquidity Maintenance Ratio as per. " + date_today
    )
    # Preparing Title
    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>
    """
    todays = date.today().strftime("%d-%b-%y")
    html_content += "<tr>"
    html_content += "<td style='text-align: left; border:None; font-weight:bold' colspan=4>PT. Bank Mandiri (persero) Tbk, Hong Kong Branch</td>"
    html_content += "<td style='text-align: left; border:None'>Date :</td>"
    html_content += f"<td style='text-align: left; border:None'>{todays}</td></tr>"
    html_content += "<tr><td style='text-align: left; border:None; font-weight:bold' colspan=4><u>Data Liquidity Maintenance Ratio Report (in USD)</u></td></tr>"
    title = ["", "", "", "PRINCIPAL", "LCF", "WEIGHTED"]
    # Manually Adding Title
    html_content += "<tr>"
    xsl_fo_content += "<fo:table-row>"
    for each_title in title:
        html_content += "<td style='border:None'><u>" + each_title + "</u></td>"
        xsl_fo_content += (
            "<fo:table-cell><fo:block>" + each_title + "</fo:block></fo:table-cell>"
        )
    html_content += "</tr>"
    xsl_fo_content += "</fo:table-row>"
    # Row A
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    html_content = html_gen.add_cell_data(
        html_content,
        "A. LIQUERIABLE ASSETS",
        'colspan=6 class="left" style="font-weight:bold; background-color:#fab07f;"',
    )
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content,
        "A. LIQUERIABLE ASSETS",
        'number-columns-spanned="6" text-align="left" font-weight="bold" background-color="#fab07f"',
    )
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    list_data_a = {
        "A1 &nbsp; Currency notes and coins": [
            "MABS1E.partA1",
            "15,181",
            "100%",
            "15,181",
        ],
        "A2 &nbsp; Gold bullion": ["", "-", "90%", "-"],
        "A3 &nbsp; Claims on or, reserves maintained with, the Exhange Fund and overseas central banks that can be withdrawn overnight or repayable on demand": [
            "",
            "-",
            "100%",
            "-",
        ],
    }
    # Subrow A
    for key, value in list_data_a.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        html_content = html_gen.add_cell_data(
            html_content, key, 'colspan=2 class="left"'
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            key,
            'border-width="1px" border-style="solid" padding="8pt" number-columns-spanned="2" text-align="left"',
        )
        html_content = html_gen.add_cell_data(html_content, value[0], 'class="left"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[0],
            'border-width="1px" border-style="solid" padding="8pt" text-align="left"',
        )
        html_content = html_gen.add_cell_data(
            html_content, value[1], 'class="right" style="color:blue"'
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[1],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right" color="blue"',
        )
        html_content = html_gen.add_cell_data(html_content, value[2], 'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[2],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right"',
        )
        html_content = html_gen.add_cell_data(html_content, value[3], 'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[3],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right"',
        )
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    list_data_a4 = [
        "A4",
        "(a) Total one-month assets of relevant banks to the reporting institution",
        "",
        "",
        "",
        "",
    ]
    html_content = html_gen.add_data_row(
        html_content, [list_data_a4], "", 'class="left"'
    )
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content,
        list_data_a4[0],
        'border-width="1px" border-style="solid" padding="8pt" width="10px"',
        'text-align="left"',
    )
    for data in list_data_a4[1:]:
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            data,
            'border-width="1px" border-style="solid" padding="8pt" width="10px"',
            'text-align="left"',
        )
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    # xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[list_data_a4],'border-width="1px" border-style="solid" padding="8pt"','text-align="left"')
    list_subdata_a4 = {
        "(1) - BANK NOSTRO": ["MABS1E.partA4a-1", "196,532,496", "", "157,225,997"],
        "(2) - BK PLACEMENT WITHIN 1 MTH": [
            "MABS1E.partA4a-2",
            "92,000,000",
            "",
            "73,600,000",
        ],
        "(3) - INT REC BK PLACEMENT WITHIN 1 MTH": [
            "MABS1E.partA4a-2",
            "161,001",
            "",
            "128,801",
        ],
        "(4) - UPAS BILL DUE WITHIN 1 MTH": [
            "MABS1E.partA4a-4",
            "1,402,475",
            "",
            "1,121,980",
        ],
        "(5) - INT REC ON UPAS BILL DUE WITHIN 1 MTH": [
            "MABS1E.partA4a-4",
            "11,708",
            "",
            "9,366",
        ],
        "(6) - FUNDING REC'B FM NEW BORROWING DUE WITHIN 1MTH": [
            "MABS1E.partA4a-5",
            "190,000,000",
            "",
            "152,000,000",
        ],
        "(7) - FX SETTLEMENT WITHIN 1 MTH": [
            "MABS1E.partA4a-7",
            "66,829,507",
            "",
            "53,463,606",
        ],
        "(8) - UNMATURED SALES OF QUALIFIED SECURITIES DUE WITHIN 1MTH": [
            "MABS1E.partA4a-8",
            "-",
            "",
            "-",
        ],
        "(9) - RISK PARTICIPATION DUE WITH 1MTH": [
            "MABS1E.partA4a-9",
            "10,000,000",
            "",
            "8,000,000",
        ],
        "(10) - INT ON RISK PARTICIPATION DUE WITN 1MTH": [
            "MABS1E.partA4a-9",
            "83,810",
            "",
            "67,048",
        ],
        "(11) - REVERSE REPO": ["MABS1E.partA4a-10", "-", "", "-"],
        "(12) - INT ON REVERSE REPO": ["MABS1E.partA4a-10", "-", "", "-"],
        "(13) - OTHERS DUE FROM BANKS": ["MABS1E.partA4a-10", "-", "", "-"],
    }
    for key, value in list_subdata_a4.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        html_content = html_gen.add_cell_data(html_content, "")
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            "",
            'border-width="1px" border-style="solid" padding="8pt" width="10px"',
        )
        html_content = html_gen.add_cell_data(
            html_content, key, 'class="left" style="color:blue"'
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            key,
            'border-width="1px" border-style="solid" padding="8pt" text-align="left" color="blue"',
        )
        html_content = html_gen.add_cell_data(html_content, value[0], 'class="left"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[0],
            'border-width="1px" border-style="solid" padding="8pt" text-align="left"',
        )
        html_content = html_gen.add_cell_data(
            html_content, value[1], 'class="right" style="color:blue"'
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[1],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right" color="blue"',
        )
        html_content = html_gen.add_cell_data(html_content, value[2], 'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[2],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right"',
        )
        html_content = html_gen.add_cell_data(html_content, value[3], 'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[3],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right"',
        )
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    list_total_a4 = ["", "Total A4(a)", "", "557,020,997", "", "445,616,798"]
    html_content = create_total_table(html_content, list_total_a4)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content,
        list_total_a4[0],
        'border-width="1px" border-style="solid" padding="8pt" width="10px"',
        'text-align="left"',
    )
    for data in list_total_a4[1:]:
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            data,
            'border-width="1px" border-style="solid" padding="8pt"',
            'text-align="left"',
        )
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    # xsl_fo_content = create_total_table_xsl(xsl_fo_content,list_total_a4)
    list_data_b4 = [
        "",
        "(b) Total one-month liabilities of the reporting institutions to the relevant banks",
        "",
        "",
        "",
        "",
    ]
    html_content = html_gen.add_data_row(
        html_content, [list_data_b4], "", 'class="left"'
    )
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content,
        list_data_b4[0],
        'border-width="1px" border-style="solid" padding="8pt" width="10px"',
        'text-align="left"',
    )
    for data in list_data_b4[1:]:
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            data,
            'border-width="1px" border-style="solid" padding="8pt"',
            'text-align="left"',
        )
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    # xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[list_data_b4],'border-width="1px" border-style="solid" padding="8pt"','text-align="left"')
    list_subdata_b4 = {
        "(1) - BANK VOSTRO": ["MABS1E.partA4b-1", "9,776,017", "", "7,820,814"],
        "(2) - BK DEPOSITS WITHIN 1 MTH": [
            "MABS1E.partA4b-2",
            "92,000,000",
            "",
            "73,600,000",
        ],
        "(3) - INT PAY'B BK DEPOSITS WITHIN 1 MTH": [
            "MABS1E.partA4b-2",
            "161,001",
            "",
            "128,801",
        ],
        "(4) - UPAS COMMITMENT/OTHER TRADE BILL WITHIN 30 DAYS": [
            "MABS1E.partA4b-3",
            "1,402,475",
            "",
            "1,121,980",
        ],
        "(5) - ACCEPTANCE WITHIN 1 MTH": ["MABS1E.partA4b-5", "11,708", "", "9,366"],
        "(6) - SLC/LC SIGHT/CONFIRM CONF WITHIN 1MTH": [
            "MABS1E.partA4b-6",
            "190,000,000",
            "",
            "152,000,000",
        ],
        "(7) - FX SETTLEMENT WITHIN 1 MTH": [
            "MABS1E.partA4b-7",
            "66,829,507",
            "",
            "53,463,606",
        ],
        "(8) - UNMATURED PURCHASE OF SECURITIES": ["MABS1E.partA4b-8", "-", "", "-"],
        "(9) - TRADE LOAN": ["MABS1E.partA4b-9", "10,000,000", "", "8,000,000"],
        "(10) - INT PAY'B TRADE LOAN": ["MABS1E.partA4b-9", "83,810", "", "67,048"],
        "(11) - REPO": ["MABS1E.partA4b-10", "-", "", "-"],
        "(12) - REPO INT": ["MABS1E.partA4b-10", "-", "", "-"],
        "(13) - AUTO 1MTH BANK BORROWING (IF NOSTRO BAL &#60; 0 )": [
            "MABS1E.partA4a-1",
            "-",
            "",
            "-",
        ],
    }
    for key, value in list_subdata_b4.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        html_content = html_gen.add_cell_data(html_content, "")
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            "",
            'border-width="1px" border-style="solid" padding="8pt" width="10px"',
        )
        html_content = html_gen.add_cell_data(
            html_content, key, 'class="left" style="color:blue"'
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            key,
            'border-width="1px" border-style="solid" padding="8pt" text-align="left" color="blue"',
        )
        html_content = html_gen.add_cell_data(html_content, value[0], 'class="left"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[0],
            'border-width="1px" border-style="solid" padding="8pt" text-align="left"',
        )
        html_content = html_gen.add_cell_data(
            html_content, value[1], 'class="right" style="color:blue"'
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[1],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right" color="blue"',
        )
        html_content = html_gen.add_cell_data(html_content, value[2], 'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[2],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right"',
        )
        html_content = html_gen.add_cell_data(html_content, value[3], 'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            value[3],
            'border-width="1px" border-style="solid" padding="8pt" text-align="right"',
        )
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    list_total_b4 = ["", "Total A4(b)", "", "476,250,125", "", "381,000,100"]
    html_content = create_total_table(html_content, list_total_b4)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content,
        list_total_b4[0],
        'border-width="1px" border-style="solid" padding="8pt" width="10px"',
        'text-align="left"',
    )
    for data in list_total_b4[1:]:
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            data,
            'border-width="1px" border-style="solid" padding="8pt"',
            'text-align="left"',
        )
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    # xsl_fo_content = create_total_table_xsl(xsl_fo_content,list_total_b4)
    list_minus_total = [
        "",
        "A4(a)-A4(b) (for use of calculate A4C only)",
        "",
        "80,770,872",
        "80%",
        "64,616,698",
    ]
    html_content = html_gen.add_data_row(
        html_content,
        [list_minus_total],
        "",
        'class="left" style=background-color:#fab07f',
    )
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content,
        list_minus_total[0],
        'border-width="1px" border-style="solid" padding="8pt" width="10px"',
        'text-align="left"',
    )
    for data in list_minus_total[1:]:
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content,
            data,
            'border-width="1px" border-style="solid" padding="8pt"',
            'text-align="left"',
        )
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    # xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[list_minus_total],'border-width="1px" border-style="solid" padding="8pt"','text-align="left" background-color="#fab07f"')
    total_amount_c4 = "53,782,250"
    list_total_c4 = [
        "",
        "(C) Net due from relevant banks >=0 (max. 40% on item(B4))",
        "",
        "",
        "",
        total_amount_c4,
        "*max",
    ]
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    for c4 in list_total_c4:
        if c4 == "*max":
            html_content = html_gen.add_cell_data(
                html_content, c4, 'style="background-color:yellow;" class="bold"'
            )
            xsl_fo_content = xsl_gen.add_xsl_column(
                xsl_fo_content,
                c4,
                'border-width="1px" border-style="solid" padding="8pt" background-color="yellow" font-weight="bold"',
            )
        elif c4 == total_amount_c4:
            html_content = html_gen.add_cell_data(html_content, c4, 'class="bold"')
            xsl_fo_content = xsl_gen.add_xsl_column(
                xsl_fo_content,
                c4,
                'border-width="1px" border-style="solid" padding="8pt" font-weight="bold"',
            )
        elif c4 == "":
            html_content = html_gen.add_cell_data(html_content, c4, 'class="left"')
            xsl_fo_content = xsl_gen.add_xsl_column(
                xsl_fo_content,
                c4,
                'border-width="1px" border-style="solid" padding="8pt" width="10px" text-align="left"',
            )
        else:
            html_content = html_gen.add_cell_data(html_content, c4, 'class="left"')
            xsl_fo_content = xsl_gen.add_xsl_column(
                xsl_fo_content,
                c4,
                'border-width="1px" border-style="solid" padding="8pt" text-align="left"',
            )
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_fo_content.replace("&nbsp;", "&#160;")
    xsl_fo_content = xsl_fo_content.replace('page-width="25in"', 'page-width="12in"')
    # Close Table
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    xsl_fo_content = xsl_fo_content.replace('page-width="12in"', 'page-width="20in"')
    # Create File
    html_file = html_gen.create_html_file(
        html_content, file_path, report_name, current_date, True
    )
    xsl_fo_file = xsl_gen.create_xsl_fo_file(
        report_name, file_path, xsl_fo_content, current_date
    )
    for i in output_file:
        if i != ".pdf":
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
