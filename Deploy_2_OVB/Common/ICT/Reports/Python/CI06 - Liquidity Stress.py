import acm, ael, datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import HTMLGenerator
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import generate_file_for_other_extension
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import (
    getFilePathSelection,
    get_current_date,
)


def time_bucket_list():
    time_bucket = [datetime.datetime.now().strftime("%d/%m/%Y")]
    daydelta_list = [7, 30, 90, 180, 270, 365, 730, 1095, 1460, 1825]
    for day in daydelta_list:
        day_delta = datetime.timedelta(days=day)
        today_date = datetime.datetime.now() - day_delta
        time_bucket.append(today_date.strftime("%d/%m/%Y"))
    valueday_filter_list = [f"AND value_day = '{time_bucket[0]}'"]
    for i, j in zip(time_bucket[:-1], time_bucket[1:]):
        valueday_filter_list.append(f"AND value_day <= '{i}' AND value_day >= '{j}'")
    valueday_filter_list.append(f"AND value_day <= '{time_bucket[-1]}'")
    return valueday_filter_list


def prepare_query_data(optkey3="", optkey4="", portfolio=""):
    time_bucket = time_bucket_list()
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
    portfolio_query = (
        " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio + "\n" if portfolio != "" else ""
    )
    result_list = []
    for date_day in time_bucket:
        query_string = (
            """
            SELECT t.trdnbr, nominal_amount(t) 'Nominal', t.value_day, t.maturity_date, t.curr
            FROM Trade t   
        """
            + optkey3_query
            + optkey4_query
            + portfolio_query
            + date_day
        )
        query_results = (
            sum([x[1] for x in ael.asql(query_string)[1][0]])
            if len(ael.asql(query_string)[1][0]) != 0
            else 0
        )
        result_list.append(f"{float(query_results):,}")
    return result_list


FILE_NAME = "CI06 - Liquidity Stress"
TITLE = ""
TODAY = datetime.datetime.now().strftime("%d-%b-%Y")
html_gen = HTMLGenerator()
ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": FILE_NAME,
}
ael_variables = [
    ["report_name", "Report Name", "string", None, FILE_NAME, 1, 0],
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
        "Secondary Output Files",
        "string",
        [".xls", ".pdf"],
        ".xls",
        0,
        1,
        "Select Secondary Extensions Output",
    ],
]
product_type = [
    "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'INDOIS', 'PBS', 'NCD', 'SVBLCY', 'SVBUSD')",
    "('IWFSBI', 'IWFGOV', 'IWFDIS', 'IWFNON', 'IWFOTH', 'CWFSBI', 'CWFGOV', 'CWFDIS', 'CWFNON', 'CWFOTH', 'IBSBI', 'IBGOV', 'IBDIS', 'IBNON', 'IBOTH', 'CCSBI', 'CCGV', 'CCDC', 'CCND', 'CCOH', 'OVBSBI', 'OVBGOV', 'OVBDIS', 'OVBNON', 'OVBOTH')",
]
asset_dict = {
    "1. Cash": [0 for _ in range(16)],
    "2. Nostro": [0 for _ in range(16)],
    "3. MM Placement": [0 for _ in range(16)],
    "a. Interbank Placement": prepare_query_data("('DL')", "('CMP')")
    + [0 for _ in range(4)],
    "b. Interoffice": prepare_query_data("('DL')", "('OVP')") + [0 for _ in range(4)],
    "4. Loan To Customers": [0 for _ in range(16)],
    "a. Govt Loan": [0 for _ in range(16)],
    "b. Corp Loan": [0 for _ in range(16)],
    "5. Securities": [0 for _ in range(16)],
    "Bonds": [0 for _ in range(16)],
    "a. HTM": prepare_query_data(
        "('BOND')", product_type[0], "('BB BOND AC BMCI', 'BB BOND SHARIA AC BMCI')"
    )
    + [0 for _ in range(4)],
    "b. AFS": prepare_query_data(
        "('BOND')",
        product_type[0],
        "('BB BOND OCI BMCI', 'BB BOND SHARIA OCI BMCI', 'CB 1 BMCI', 'GVI 1 BMCI', 'Commercial 1 BMCI')",
    )
    + [0 for _ in range(4)],
    "c. Trading": prepare_query_data(
        "('BOND')",
        product_type[0],
        "('IRT DCM 1 BMCI', 'IRT DCM 2 BMCI','BB BOND PL BMCI', 'BB BOND SHARIA PL BMCI')",
    )
    + [0 for _ in range(4)],
    "Trade Finance": [0 for _ in range(16)],
    "a. Interoffice TF (UPAS/TR/EUBD HO/Nego)": [0 for _ in range(16)],
    "6. Other Assets": [0 for _ in range(16)],
    "": ["" for _ in range(16)],
    "Total Aset": [0 for _ in range(16)],
}
liabilities_dict = {
    "1. Current Account": [0 for _ in range(16)],
    "a. Head Office": [0 for _ in range(16)],
    "b. Customers": [0 for _ in range(16)],
    "2. Deposit Taken": [0 for _ in range(16)],
    "a. Intra-Office": prepare_query_data("('DL')", "('OVT')") + [0 for _ in range(4)],
    "b. Interbank": prepare_query_data("('DL')", "('CMT')") + [0 for _ in range(4)],
    "3. Customer Deposit": [0 for _ in range(16)],
    "4. Borrowing": [0 for _ in range(16)],
    "a. Securities Issued": prepare_query_data("('DEBT')") + [0 for _ in range(4)],
    "b. Short Term/Long Term Borr": prepare_query_data("('DL')", "('MD')")
    + [0 for _ in range(4)],
    "c. Repo": prepare_query_data("('REPO')", product_type[1]) + [0 for _ in range(4)],
    "5. Other Liabilites": [0 for _ in range(16)],
    "6. HO Funds (Initial Dep + RE)": [0 for _ in range(16)],
    "7. MTM": [0 for _ in range(16)],
    "8. Current P/L": [0 for _ in range(16)],
    "": [0 for _ in range(16)],
    "Total Liabillites & Capital": [0 for _ in range(16)],
}
cash_inflow = {
    "Renew customer current account R/O": [0 for _ in range(6)],
    "Renew customer Fixed Deposit R/O": [0 for _ in range(6)],
    "New or R/O interbank Borrowing & Banker Acceptance": prepare_query_data(
        "('DL')", "('CMT', 'BA')"
    )[:6],
    "Strategic Bonds transaction sell / matured": [0 for _ in range(6)],
    "New or R/O MM Borrowing Other Overseas Branches": [0 for _ in range(6)],
    "New or R/O MM Borrowing from Interoffice": prepare_query_data("('DL')", "('OVT')")[
        :6
    ],
    "New or R/O MM Borrowing from interbank": prepare_query_data("('DL')", "('CMT')")[
        :6
    ],
    "New or R/O Repo Transaction": prepare_query_data("('REPO')", product_type[1])[:6],
    "Matured MM Placement to interbank": prepare_query_data("('DL')", "('CMP')")[:6],
    "Loan Principal Repayment": [0 for _ in range(6)],
    "TF Repayment": [0 for _ in range(6)],
    "Total Cash Inflow": [0 for _ in range(6)],
}
cash_outflow = {
    "Trade Finance R/O": [0 for _ in range(6)],
    "New Loan Facility Disbursement": [0 for _ in range(6)],
    "Strategic Bonds Transaction buy": [0 for _ in range(6)],
    "New or RO MM Placement to Other Overseas Branches": [0 for _ in range(6)],
    "New or RO MM Placement to interbank": prepare_query_data("('DL')", "('CMP')")[:6],
    "Matured MM Borrowing from Other Overseas Branches": prepare_query_data(
        "('DL')", "('OVT')"
    )[:6],
    "Matured MM Borrowing from interoffice": prepare_query_data("('DL')", "('CMT')")[
        :6
    ],
    "Matured Repo": prepare_query_data("('REPO')", product_type[1])[:6],
    "Loan drawdown new & existing customer": [0 for _ in range(6)],
    "Total Cash Outflow": [0 for _ in range(6)],
}


def prepare_header1(html_content, table_type):
    headers = [
        table_type,
        TODAY,
        "&#8804; 7 days",
        "7 days-1 Mo",
        "> 1 Mo-3 Mo",
        "> 3Mo - 6Mo",
        ">6Mo - 9Mo",
        "> 9 Mo - 12 Mo",
        "> 12 Mo - 24 Mo",
        "> 24 Mo - 36 Mo",
        "> 36 Mo - 48 Mo",
        "> 48 Mo - 60 Mo",
        "> 60 Mo",
        "Non Rate Senst Asset",
        "Current Rate %",
        "Interest",
        "Nominal",
    ]
    html_content = html_gen.open_table_row(html_content, row_attribute="")
    for i, header in enumerate(headers):
        if i <= 7:
            html_content = html_gen.add_cell_data(
                html_content, header, "style='background-color:#aec5eb'"
            )
        elif i >= 13:
            html_content = html_gen.add_cell_data(
                html_content, header, "style='background-color:magenta'"
            )
        else:
            html_content = html_gen.add_cell_data(html_content, header)
    html_content = html_gen.close_table_row(html_content)
    return html_content


def prepare_header2(html_content):
    headers = [
        "Time Bucket",
        "&#8804; 7 days",
        "7 days-1 Mo",
        "> 1 Mo-3 Mo",
        "> 3Mo - 6Mo",
        ">6Mo - 9Mo",
        "> 9 Mo - 12 Mo",
        "> 12 Mo - 24 Mo",
        "> 24 Mo - 36 Mo",
        "> 36 Mo - 48 Mo",
        "> 48 Mo - 60 Mo",
        "> 60 Mo",
        "Non Rate Senst Asset",
        "Current Rate %",
        "Interest",
        "Nominal",
    ]
    html_content = html_gen.open_table_row(html_content, row_attribute="")
    for i, header in enumerate(headers):
        if i == 0:
            html_content = html_gen.add_cell_data(html_content, header, "colspan='2'")
        elif i >= 1 and i <= 6:
            html_content = html_gen.add_cell_data(
                html_content, header, "style='background-color:grey'"
            )
        else:
            html_content = html_gen.add_cell_data(html_content, header)
    html_content = html_gen.close_table_row(html_content)
    return html_content


def prepare_header3(html_content):
    headers = [
        "Static Liquidity Gap",
        "&#8804; 7 days",
        "7 days-1 Mo",
        "> 1 Mo-3 Mo",
        "> 3Mo - 6Mo",
        ">6Mo - 9Mo",
        "> 9 Mo - 12 Mo",
        "1 - 5 Yr",
        "> 5 Yr",
    ]
    html_content = html_gen.open_table_row(html_content, row_attribute="")
    for i, header in enumerate(headers):
        if i == 0:
            html_content = html_gen.add_cell_data(html_content, header, "colspan='2'")
        else:
            html_content = html_gen.add_cell_data(
                html_content, header, "style = 'background-color : purple'"
            )
    html_content = html_gen.close_table_row(html_content)
    return html_content


def prepare_header4(html_content, table_type):
    headers = [
        table_type,
        "&#8804; 7 days",
        "7 days - 1 Mo",
        ">1 Mo - 3 Mo",
        "> 3 Mo - 6 Mo",
        "> 6 Mo - 9 Mo",
        "> 9 Mo - 12 Mo",
    ]
    html_content = html_gen.open_table_row(html_content, row_attribute="")
    for i, header in enumerate(headers):
        if i == 0:
            html_content = html_gen.add_cell_data(
                html_content, header, "colspan='2' style = 'background-color : #aec5eb'"
            )
        else:
            html_content = html_gen.add_cell_data(
                html_content, header, "style = 'background-color : #aec5eb'"
            )
    html_content = html_gen.close_table_row(html_content)
    return html_content


def prepare_table(
    html_content, data_dict, table_type, full_header_time=True, spankey=False
):
    if full_header_time == True:
        html_content = prepare_header1(html_content, table_type)
    elif full_header_time == False:
        html_content = prepare_header4(html_content, table_type)
    for i_dict, (key, val_list) in enumerate(data_dict.items()):
        if i_dict == len(data_dict.keys()) - 1:
            html_content = html_gen.open_table_row(html_content, row_attribute="")
            html_content = html_gen.add_cell_data(
                html_content,
                key,
                f"""{"colspan='2'" if spankey == True else ""} style='background-color : #aec5eb; text-align: left'""",
            )
            for i, val in enumerate(val_list):
                html_content = html_gen.add_cell_data(
                    html_content,
                    val,
                    'style="background-color : #aec5eb; text-align: right"',
                )
            continue
        html_content = html_gen.open_table_row(html_content, row_attribute="")
        if spankey == True:
            html_content = html_gen.add_cell_data(
                html_content, key, "colspan='2' style='text-align: left'"
            )
        else:
            html_content = html_gen.add_cell_data(
                html_content,
                key if any(x.isdigit() for x in key) else f"&emsp;{key}",
                "style='text-align: left'",
            )
        for i, val in enumerate(val_list):
            if i >= 1 and i <= 12:
                html_content = html_gen.add_cell_data(
                    html_content,
                    val,
                    "style='background-color:khaki', 'text-align: right'",
                )
            else:
                html_content = html_gen.add_cell_data(
                    html_content, val, "style='text-align: right'"
                )
        html_content = html_gen.close_table_row(html_content)
    return html_content


def prepare_total_assets_table(html_content):
    return html_content


def ael_main(parameter):
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = parameter["output_file"]
    current_date = get_current_date("")
    html_content = html_gen.create_base_html_content(TITLE, "")
    # Assets
    html_content = html_gen.prepare_html_table(
        html_content, [], row_style="", header_style="", table_styling=""
    )
    html_content = prepare_table(html_content, asset_dict, "ASSETS")
    # Total Assets Table
    total_assets_data = [
        ["", 0, ""],
        ["Total Assets", "", 0],
        ["Total Assets per BS", "", 0],
    ]
    html_content = html_gen.add_data_row(
        html_content,
        total_assets_data,
        row_class="",
        cell_class="style='text-align: left'",
    )
    html_content = html_gen.prepare_html_table(
        html_content,
        [],
        row_style="",
        header_style="",
        table_styling="style='border:0px'",
    )
    html_content = prepare_table(html_content, liabilities_dict, "Liabillities")
    aset_minus = [["Aset minus Kewajiban & Modal"] + [0] * 14]
    static_liquidity_gap = [
        ["Periodic Static Gap", ""] + [0] * 8,
        ["Cummulative Static Gap", ""] + [0] * 8,
    ]
    html_content = html_gen.prepare_html_table(
        html_content,
        [],
        row_style='style="text-align : left"',
        header_style="",
        table_styling="style='border:0px'",
    )
    html_content = prepare_header2(html_content)
    html_content = html_gen.prepare_html_table(
        html_content,
        [],
        row_style="",
        header_style="",
        table_styling="style='border:0px'",
    )
    html_content = html_gen.add_data_row(
        html_content,
        aset_minus,
        row_class="",
        cell_class="style='background-color : #aec5eb; text-align: left'",
    )
    total_liabilities_data = [
        ["Total Liabilities & Capital", "", 0],
        ["Total Liabilities & Capital per BS", "", 0],
    ]
    html_content += "<tr><td>&nbsp;</td></tr>"
    html_content = html_gen.add_data_row(
        html_content,
        total_liabilities_data,
        row_class="",
        cell_class="style='text-align: left'",
    )
    html_content = html_gen.prepare_html_table(
        html_content,
        [],
        row_style="",
        header_style="",
        table_styling="style='border:0px'",
    )
    html_content = prepare_header3(html_content)
    html_content = html_gen.add_data_row(
        html_content,
        static_liquidity_gap,
        row_class="style='background-color : #aec5eb'",
        cell_class="style='text-align: left'",
    )
    html_content = html_gen.prepare_html_table(
        html_content,
        [],
        row_style="",
        header_style="",
        table_styling="style='border:0px'",
    )
    html_content = prepare_table(html_content, cash_inflow, "Cash Inflow", False, True)
    html_content = html_gen.prepare_html_table(
        html_content,
        [],
        row_style="",
        header_style="",
        table_styling="style='border:0px'",
    )
    html_content = prepare_table(
        html_content, cash_outflow, "Cash Outflow", False, True
    )
    dynamic_liquidity_gap = [
        ["Periodic Dynamic Gap", ""] + [0] * 8,
        ["Cummulative Dynamic Gap", ""] + [0] * 8,
    ]
    html_content = html_gen.prepare_html_table(
        html_content,
        [],
        row_style="",
        header_style="",
        table_styling="style='border:0px'",
    )
    html_content = prepare_header3(html_content)
    html_content = html_gen.add_data_row(
        html_content,
        dynamic_liquidity_gap,
        row_class="style='background-color : #aec5eb'",
        cell_class="style='text-align: left'",
    )
    html_content = html_gen.close_html_table(html_content)
    html_url = html_gen.create_html_file(
        html_content,
        file_path,
        report_name,
        current_date,
        open_html=True,
        folder_with_file_name=False,
    )
    for extension in output_file:
        if extension == ".xls":
            generate_file_for_other_extension(html_url, extension)
