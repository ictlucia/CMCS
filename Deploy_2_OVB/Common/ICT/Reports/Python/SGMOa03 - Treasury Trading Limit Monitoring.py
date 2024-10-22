from datetime import date, timedelta, datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael

ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "SGMOa03 - Treasury Trading Limit Monitoring",
}
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "SGMOa03 - Treasury Trading Limit Monitoring",
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


def time_bucket_list():
    time_bucket = []
    for day in range(30):
        day_delta = timedelta(days=day)
        delta_date = datetime.now() + day_delta
        str_date = delta_date.strftime("%m/%d/%Y")
        query_time = f"AND value_day = '{str_date}'"
        time_bucket.append(query_time)
    return time_bucket


def prepare_query_data(optkey3="", optkey4="", portfolio="", date_val=""):
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
    query_string = (
        """
        SELECT t.trdnbr, nominal_amount(t) 'Nominal', t.value_day, t.maturity_date, t.curr
        FROM Trade t   
    """
        + optkey3_query
        + optkey4_query
        + portfolio_query
        + date_val
    )
    query_results = (
        sum([x[1] for x in ael.asql(query_string)[1][0]])
        if len(ael.asql(query_string)[1][0]) != 0
        else 0
    )
    print(date_val, query_results)
    return query_results


def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    start_date = parameter["start_date"][0]
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
        .yellow {
            background-color:yellow;
            font-weight:bold;
        }
        .blue {
            background-color:#4497eb;
            color:white;
            font-weight:bold;
        }
    """
    current_date = datetime.now().strftime("%y%m%d")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content(
        "SGMOa03 - Treasury Trading Limit Monitoring as per. " + date_today, title_style
    )
    html_content = html_gen.prepare_html_table(html_content, "")
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content(
        "SGMOa03 - Treasury Trading Limit Monitoring as per. " + date_today, ""
    )
    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""
    list_title = {
        "Intraday NOP": "4",
        "Overnight NOP": "2",
        "Monthly Loss Limit": "2",
        "Yearly Loss Limit": "2",
    }
    list_subtitle = [
        "FX Trading (1st)",
        "FX Trading (2nd)",
        "FI Trading (1st)",
        "FI Trading (2nd)",
        "FX Trading",
        "FI Trading",
        "FX Trading",
        "FI Trading",
        "FX Trading",
        "FI Trading",
    ]
    # Adding Title Row
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    html_content = html_gen.add_cell_data(html_content, "", "rowspan=2")
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content, "", 'number-rows-spanned="2"'
    )
    for key, value in list_title.items():
        html_content = html_gen.add_cell_data(
            html_content, key, "colspan=" + value + " class=bold"
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, key, 'number-columns-spanned="' + value + '"'
        )
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    # Adding Subtitle Row
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    for subtitle in list_subtitle:
        html_content = html_gen.add_cell_data(html_content, subtitle, "class=yellow")
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, subtitle, 'background-color="yellow"'
        )
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    list_limit = [
        "56,000,000",
        "56,000,000",
        "56,000,000",
        "56,000,000",
        "56,000,000",
        "56,000,000",
        "56,000,000",
        "56,000,000",
        "56,000,000",
        "56,000,000",
    ]
    # Adding Limit Row
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    html_content = html_gen.add_cell_data(html_content, "The Limits", "class=bold")
    xsl_fo_content = xsl_gen.add_xsl_column(
        xsl_fo_content, "The Limits", 'font-weight="bold"'
    )
    for limits in list_limit:
        html_content = html_gen.add_cell_data(html_content, limits, "class=blue")
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, limits, 'background-color="#4497eb"'
        )
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    port_list = [
        "FX Spot 1 BMSG - ACU",
        "FX Spot 2 BMSG - ACU",
        "FX Derivatives 1 BMSG - ACU",
        "FX Derivatives 2 BMSG - ACU",
        "FX Spot 1 BMSG - DBU",
        "FX Spot 2 BMSG - DBU",
        "FX Derivatives 1 BMSG - DBU",
        "FX Derivatives 2 BMSG - DBU",
        "IRT DCM 1 BMSG - ACU",
        "IRT DCM 2 BMSG - ACU",
        "IRT DCM 1 BMSG - DBU",
        "IRT DCM 2 BMSG - DBU",
        "IRT Derivative 1 BMSG - ACU",
        "IRT Derivative 2 BMSG - ACU",
        "IRT DCM 1 BMSG - DBU",
        "IRT DCM 2 BMSG - DBU",
    ]
    optkey3_list = ["FX", "BOND", "SWAP"]
    optkey4_list = [
        "TOD",
        "TOM",
        "SPOT",
        "FWD",
        "SWAP",
        "OPT",
        "NDF",
        "CBUSD",
        "CBVALAS",
        "UST",
        "BILLS",
        "ROI",
        "ORI",
        "SR",
        "SBBI",
        "SBK",
        "SPN",
        "SPNS",
        "FR",
        "VR",
        "INDOIS",
        "PBS",
        "NCD",
        "IRS",
    ]
    portfolio = "(" + ", ".join([f"'{x}'" for x in port_list]) + ")"
    optkey3 = "(" + ", ".join([f"'{x}'" for x in optkey3_list]) + ")"
    optkey4 = "(" + ", ".join([f"'{x}'" for x in optkey4_list]) + ")"
    # Adding List of 30 Date
    for count, val_date in enumerate(time_bucket_list()):
        query_result = prepare_query_data(optkey3, optkey4, portfolio, val_date)
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        add_date = acm.Time.DateAddDelta(start_date, 0, 0, count)
        # Converting date to Desired type
        year, month, day = add_date.split("-")
        new_date = date(int(year), int(month), int(day)).strftime("%d-%b-%y")
        html_content = html_gen.add_cell_data(html_content, new_date)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, new_date)
        for data in range(len(list_limit)):
            html_content = html_gen.add_cell_data(html_content, query_result)
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, query_result)
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
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
