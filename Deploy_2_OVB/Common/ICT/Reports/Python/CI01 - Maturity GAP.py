import os
import acm, ael
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import HTMLGenerator
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import generate_file_for_other_extension
from datetime import date, datetime, timedelta

html_gen = HTMLGenerator()


def time_bucket_list():
    time_bucket = [datetime.now().strftime("%d/%m/%Y")]
    daydelta_list = [8, 30, 90, 180, 365, 1825]
    for day in daydelta_list:
        day_delta = timedelta(days=day)
        today_date = datetime.now() - day_delta
        time_bucket.append(today_date.strftime("%d/%m/%Y"))
    valueday_filter_list = []
    for date_list in zip(time_bucket[:-1], time_bucket[1:]):
        valueday_filter_list.append(
            f"AND value_day <= '{date_list[0]}' AND value_day >= '{date_list[0]}'"
        )
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
        result_list.append(query_results)
    return result_list


def prepare_repricing_assets(html_content):
    optkey3_list = "('DL', 'BOND', 'REPO')"
    optkey4_list = "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'VR', 'INDOIS', 'PBS', 'NCD', 'CL', 'MD', 'CMP', 'CMT', 'OVT', 'OVP', 'BLT', 'BA', 'IWFSBI', 'IWFGOV', 'IWFDIS', 'IWFNON', 'IWFOTH', 'IBSBI', 'IBGOV', 'IBDIS', 'IBNON', 'IBOTH', 'BOB', 'IBOH', 'CWFSBI', 'CWFGOV', 'CWFDIS', 'CWFNON', 'CWFOTH', 'CCSBI', 'CCGV', 'CCDC', 'CCND', 'CCOH', 'CCSBI', 'CCGOV', 'CCOTH')"
    port_list = "('BB BOND PL BMCI', 'BB BOND AC BMCI', 'BB BOND OCI BMCI', 'BB BOND SHARIA PL BMCI', 'BB BOND SHARIA AC BMCI', 'BB BOND SHARIA OCI BMCI', 'CB 1 BMCI', 'GVI 1 BMCI', 'Commercial 1 BMCI', 'IRT DCM 1 BMCI', 'IRT DCM 2 BMCI', 'LIQ IB BMCI')"
    global HEADERS
    table_number = "39.1"
    header_list = [table_number, "ASSETS"] + HEADERS
    table_content = html_gen.prepare_html_table(
        html_content, header_list, row_style="", header_style="", table_styling=""
    )
    table_content += (
        "<caption style='text-align:left'>Interest Rate Repricing</caption>"
    )
    asset_type = [
        "<skyblue>Cash and deposits",
        "<skyblue>Loans",
        "<skyblue>Investments",
        "<skyblue>Other assets",
        "<skyblue>Total",
    ]
    query = ""
    query_data = [
        ["<lightyellow>-" for _ in range(len(HEADERS))]
        for _ in range(len(asset_type) - 1)
    ]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])
    prepare_query_data(optkey3_list, optkey4_list, port_list)
    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        result_query_list = prepare_query_data(optkey3_list, optkey4_list, port_list)
        for j in range(len(result_query_list)):
            query_data[i][j] = query_data[i][j].replace("-", str(result_query_list[j]))
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
    table_content = html_gen.add_data_row(
        table_content, row_data, row_class="", cell_class=""
    )
    table_content = html_gen.close_html_table(table_content)
    return table_content


def prepare_repricing_liabilities(html_content):
    global HEADERS
    table_number = "39.2"
    optkey3_list = "('DL', 'BOND', 'REPO')"
    optkey4_list = "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'VR', 'INDOIS', 'PBS', 'NCD', 'CL', 'MD', 'CMP', 'CMT', 'OVT', 'OVP', 'BLT', 'BA', 'IWFSBI', 'IWFGOV', 'IWFDIS', 'IWFNON', 'IWFOTH', 'IBSBI', 'IBGOV', 'IBDIS', 'IBNON', 'IBOTH', 'BOB', 'IBOH', 'CWFSBI', 'CWFGOV', 'CWFDIS', 'CWFNON', 'CWFOTH', 'CCSBI', 'CCGV', 'CCDC', 'CCND', 'CCOH', 'CCSBI', 'CCGOV', 'CCOTH')"
    port_list = "('BB BOND PL BMCI', 'BB BOND AC BMCI', 'BB BOND OCI BMCI', 'BB BOND SHARIA PL BMCI', 'BB BOND SHARIA AC BMCI', 'BB BOND SHARIA OCI BMCI', 'CB 1 BMCI', 'GVI 1 BMCI', 'Commercial 1 BMCI', 'GVI 1 BMCI', 'IRT DCM 1 BMCI', 'IRT DCM 2 BMCI', 'LIQ IB BMCI')"
    header_list = [table_number, "LIABILITES & EQUITY"] + HEADERS
    table_content = html_gen.prepare_html_table(
        html_content, header_list, row_style="", header_style="", table_styling=""
    )
    asset_type = [
        "<skyblue>Deposits from banks",
        "<skyblue>Other deposits",
        "<skyblue>Repos, Term Debt and other Borrowings",
        "<skyblue>Other liabilites",
        "<skyblue>Equity",
        "<skyblue>Total",
    ]
    query = ""
    query_data = [
        ["<lightyellow>-" for _ in range(len(HEADERS))]
        for _ in range(len(asset_type) - 1)
    ]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])
    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        result_query_list = prepare_query_data(optkey3_list, optkey4_list, port_list)
        for j in range(len(result_query_list)):
            query_data[i][j] = query_data[i][j].replace("-", str(result_query_list[j]))
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
    table_content = html_gen.add_data_row(
        table_content, row_data, row_class="", cell_class=""
    )
    table_content = html_gen.close_html_table(table_content)
    return table_content


def prepare_repricing_off_balance(html_content):
    global HEADERS
    table_number = "39.3"
    table_content = html_gen.prepare_html_table(
        html_content, "", row_style="", header_style="", table_styling=""
    )
    optkey3_list = "('DL', 'BOND', 'REPO')"
    optkey4_list = "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'VR', 'INDOIS', 'PBS', 'NCD', 'CL', 'MD', 'CMP', 'CMT', 'OVT', 'OVP', 'BLT', 'BA', 'IWFSBI', 'IWFGOV', 'IWFDIS', 'IWFNON', 'IWFOTH', 'IBSBI', 'IBGOV', 'IBDIS', 'IBNON', 'IBOTH', 'BOB', 'IBOH', 'CWFSBI', 'CWFGOV', 'CWFDIS', 'CWFNON', 'CWFOTH', 'CCSBI', 'CCGV', 'CCDC', 'CCND', 'CCOH', 'CCSBI', 'CCGOV', 'CCOTH')"
    port_list = "('BB BOND PL BMCI', 'BB BOND AC BMCI', 'BB BOND OCI BMCI', 'BB BOND SHARIA PL BMCI', 'BB BOND SHARIA AC BMCI', 'BB BOND SHARIA OCI BMCI', 'CB 1 BMCI', 'GVI 1 BMCI', 'Commercial 1 BMCI', 'GVI 1 BMCI', 'IRT DCM 1 BMCI', 'IRT DCM 2 BMCI', 'LIQ IB BMCI')"
    asset_type = ["<skyblue>Off-balance sheet items"]
    query = ""
    query_data = [
        ["<lightyellow>-" for _ in range(len(HEADERS))]
        for _ in range(len(asset_type) - 1)
    ]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])
    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        result_query_list = prepare_query_data(optkey3_list, optkey4_list, port_list)
        for j in range(len(result_query_list)):
            query_data[i][j] = query_data[i][j].replace("-", str(result_query_list[j]))
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
    table_content = html_gen.add_data_row(
        table_content, row_data, row_class="", cell_class=""
    )
    table_content = html_gen.close_html_table(table_content)
    return table_content


def prepare_maturing_assets(html_content):
    global HEADERS
    table_number = "39.4"
    optkey3_list = "('DL', 'BOND', 'REPO')"
    optkey4_list = "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'VR', 'INDOIS', 'PBS', 'NCD', 'CL', 'MD', 'CMP', 'CMT', 'OVT', 'OVP', 'BLT', 'BA', 'IWFSBI', 'IWFGOV', 'IWFDIS', 'IWFNON', 'IWFOTH', 'IBSBI', 'IBGOV', 'IBDIS', 'IBNON', 'IBOTH', 'BOB', 'IBOH', 'CWFSBI', 'CWFGOV', 'CWFDIS', 'CWFNON', 'CWFOTH', 'CCSBI', 'CCGV', 'CCDC', 'CCND', 'CCOH', 'CCSBI', 'CCGOV', 'CCOTH')"
    port_list = "('BB BOND PL BMCI', 'BB BOND AC BMCI', 'BB BOND OCI BMCI', 'BB BOND SHARIA PL BMCI', 'BB BOND SHARIA AC BMCI', 'BB BOND SHARIA OCI BMCI', 'CB 1 BMCI', 'GVI 1 BMCI', 'Commercial 1 BMCI', 'GVI 1 BMCI', 'IRT DCM 1 BMCI', 'IRT DCM 2 BMCI', 'LIQ IB BMCI')"
    header_list = [table_number, "ASSETS"] + HEADERS
    table_content = html_gen.prepare_html_table(
        html_content, header_list, row_style="", header_style="", table_styling=""
    )
    table_content += "<caption style='text-align:left'>Interest Rate Maturing</caption>"
    asset_type = [
        "<skyblue>Cash and deposits",
        "<skyblue>Loans",
        "<skyblue>Investments",
        "<skyblue>Other assets",
        "<skyblue>Total",
    ]
    query = ""
    query_data = [
        ["<lightyellow>-" for _ in range(len(HEADERS))]
        for _ in range(len(asset_type) - 1)
    ]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])
    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        result_query_list = prepare_query_data(optkey3_list, optkey4_list, port_list)
        for j in range(len(result_query_list)):
            query_data[i][j] = query_data[i][j].replace("-", str(result_query_list[j]))
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
    table_content = html_gen.add_data_row(
        table_content, row_data, row_class="", cell_class=""
    )
    table_content = html_gen.close_html_table(table_content)
    return table_content


def prepare_maturing_liabilities(html_content):
    global HEADERS
    table_number = "39.5"
    optkey3_list = "('DL', 'BOND', 'REPO')"
    optkey4_list = "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'VR', 'INDOIS', 'PBS', 'NCD', 'CL', 'MD', 'CMP', 'CMT', 'OVT', 'OVP', 'BLT', 'BA', 'IWFSBI', 'IWFGOV', 'IWFDIS', 'IWFNON', 'IWFOTH', 'IBSBI', 'IBGOV', 'IBDIS', 'IBNON', 'IBOTH', 'BOB', 'IBOH', 'CWFSBI', 'CWFGOV', 'CWFDIS', 'CWFNON', 'CWFOTH', 'CCSBI', 'CCGV', 'CCDC', 'CCND', 'CCOH', 'CCSBI', 'CCGOV', 'CCOTH')"
    port_list = "('BB BOND PL BMCI', 'BB BOND AC BMCI', 'BB BOND OCI BMCI', 'BB BOND SHARIA PL BMCI', 'BB BOND SHARIA AC BMCI', 'BB BOND SHARIA OCI BMCI', 'CB 1 BMCI', 'GVI 1 BMCI', 'Commercial 1 BMCI', 'IRT DCM 1 BMCI', 'IRT DCM 2 BMCI', 'LIQ IB BMCI')"
    header_list = [table_number, "LIABILITES & EQUITY"] + HEADERS
    table_content = html_gen.prepare_html_table(
        html_content, header_list, row_style="", header_style="", table_styling=""
    )
    asset_type = [
        "<skyblue>Deposits from banks",
        "<skyblue>Other deposits",
        "<skyblue>Repos, Term Debt and other Borrowings",
        "<skyblue>Other liabilites",
        "<skyblue>Equity",
        "<skyblue>Total",
    ]
    query = ""
    query_data = [
        ["<lightyellow>-" for _ in range(len(HEADERS))]
        for _ in range(len(asset_type) - 1)
    ]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])
    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}.{i + 1}", asset_type[i]]
        result_query_list = prepare_query_data(optkey3_list, optkey4_list, port_list)
        for j in range(len(result_query_list)):
            query_data[i][j] = query_data[i][j].replace("-", str(result_query_list[j]))
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
    table_content = html_gen.add_data_row(
        table_content, row_data, row_class="", cell_class=""
    )
    table_content = html_gen.close_html_table(table_content)
    return table_content


def prepare_maturing_off_balance(html_content):
    global HEADERS
    table_number = "39.6"
    table_content = html_gen.prepare_html_table(
        html_content, "", row_style="", header_style="", table_styling=""
    )
    asset_type = ["<skyblue>Off-balance sheet items"]
    query = ""
    query_data = [
        ["<lightyellow>-" for _ in range(len(HEADERS))]
        for _ in range(len(asset_type) - 1)
    ]
    query_data.append(["<aliceblue>" for _ in range(len(HEADERS))])
    row_data = []
    for i in range(len(asset_type)):
        temp_data = [f"{table_number}", asset_type[i]]
        temp_data.extend(query_data[i])
        row_data.append(temp_data)
    table_content = html_gen.add_data_row(
        table_content, row_data, row_class="", cell_class=""
    )
    table_content = html_gen.close_html_table(table_content)
    return table_content


ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "CI01 - Maturity GAP",
}
# settings.FILE_EXTENSIONS
ael_variables = [
    ["report_name", "Report Name", "string", None, "CI01 - Maturity GAP", 1, 0],
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
HEADERS = [
    "<skyblue>Sight - 8 days",
    "<skyblue>8 days - 1 Month",
    "<skyblue>1 - 3 Months",
    "<skyblue>3 - 6 Months",
    "<skyblue>6 - 12 Months",
    "<skyblue>1 - 5 Years",
    "<skyblue>Over 5 Years",
    "<skyblue>Non-Interest Sensitive (Assets and Liabilities)",
    "<skyblue>Total",
]


def ael_main(parameter):
    TITLE = ""
    ADDITIONAL_STYLE = """
    table {
        margin: 0px;
    }    
    """
    html_gen = HTMLGenerator()
    html_content = html_gen.create_base_html_content(TITLE, ADDITIONAL_STYLE)
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = "".join(parameter["output_file"])
    html_content = prepare_repricing_assets(html_content)
    html_content += "<br>"
    html_content = prepare_repricing_liabilities(html_content)
    html_content += "<br>"
    html_content = prepare_repricing_off_balance(html_content)
    html_content += "<br>"
    html_content = prepare_maturing_assets(html_content)
    html_content += "<br>"
    html_content = prepare_maturing_liabilities(html_content)
    html_content += "<br>"
    html_content = prepare_maturing_off_balance(html_content)
    html_content = html_content.replace("><skyblue>", "style='background:skyblue;'>")
    html_content = html_content.replace(
        "><aliceblue>", "style='background:aliceblue;'>"
    )
    html_content = html_content.replace(
        "><lightyellow>", "style='background:lightyellow;'>"
    )
    if ".xls" in output_file:
        file_url = html_gen.create_html_file(
            html_content,
            file_path,
            report_name,
            str(datetime.today().strftime('%y%m%d')),
            True,
            folder_with_file_name=False,
        )
        generate_file_for_other_extension(file_url, ".xls")
