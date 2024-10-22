from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael


def query_result(optkey3="", optkey4="", portfolio=""):
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
    )
    query_results = float(
        sum([x[1] for x in ael.asql(query_string)[1][0]])
        if len(ael.asql(query_string)[1][0]) != 0
        else 0
    )
    return f"{query_results:,}"


ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "CI03 - Minimum Liquidity Ratio",
}
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "CI03 - Minimum Liquidity Ratio",
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
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
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
        .amount {
            font-weight: bold;
        }
    """
    current_date = get_current_date("")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content(
        "Minimum Liquidity Ratio (Monthly Report)", title_style
    )
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content(
        "Minimum Liquidity Ratio (Monthly Report)"
    )
    title_list = ["Reporting Period", current_date, ""]
    html_content = html_gen.prepare_html_table(
        html_content, title_list, header_style='style="text-align: left"'
    )
    xsl_fo_content = xsl_gen.add_xsl_fo_table_header(xsl_fo_content, title_list)
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content, [["", "", ""]], "", 'font-weight="bold" text-align="left"'
    )
    list_asset_data = {
        "Currency notes and coins": "A01",
        "Withdrawable central bank reserves": "A02",
        "Deposit balances with and Certificates of Deposit (CDs) issued by the bank's Group Bank - Parent, Branch, Subsidiary or Affiliate. (Available when a liquidity issue encountered and must have an explicit agrrement with its Group Bank that is approved by Authority.)": "A03",
        "Any Debt Securities assigned a 0% risk weight representing claims on or guaranteed by:": "",
        "Sovereigns ": "A04",
        "Central banks ": "A05",
        "Publis Sector Entities (PSEs) ": "A06",
        "Multilateral Development Banks (MDBs) ": "A07",
        "Any Debt Securities assigned a 20% risk weight representing claims on or guaranteed by:": "",
        "Sovereigns": "A08",
        "Central banks": "A09",
        "Public Sector Entities (PSEs)": "A10",
        "Multilateral Development Banks (MDBs)": "A11",
        "Any corporate debt security including commercial paper with a 20% risk rating - not issued by a financial institution or any of its affiliated entities": "A12",
        "Any covered bonds with a 20% risk rating - not issued by the bank itself or any of its affiliated entities": "A13",
    }
    for key, value in list_asset_data.items():
        temp_row = []
        temp_row.append(key)
        temp_row.append(value)
        temp_row.append(
            query_result(
                "('DL')",
                "('CL', 'MD', 'CMP', 'CMT', 'OVT', 'OVP', 'BLT', 'BA')",
                "('LIQ IB BMCI')",
            )
        )
        html_content = html_gen.add_data_row(
            html_content, [temp_row], "", 'style="text-align:left;white-space:normal"'
        )
        xsl_fo_content = xsl_gen.add_xsl_data_row(
            xsl_fo_content, [temp_row], "", 'text-align="left" white-space="normal"'
        )
    print(html_content)
    html_content = html_gen.add_data_row(
        html_content,
        [["Total Liquid Assets", "AT", ""]],
        "",
        "style=font-weight:bold;text-align:left",
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [["Total Liquid Assets", "AT", ""]],
        "",
        'font-weight="bold" text-align="left"',
    )
    html_content = html_gen.add_data_row(
        html_content,
        [["B) Qualifying Liabilities", "", ""]],
        "",
        "style=font-weight:bold;text-align:left",
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [["B) Qualifying Liabilities", "", ""]],
        "",
        'font-weight="bold" text-align="left"',
    )
    html_content = html_gen.add_data_row(
        html_content,
        [["All liabilities of the bank, excluding any contigent liabilities", "", ""]],
        "",
        "style=text-align:left",
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [["All liabilities of the bank, excluding any contigent liabilities", "", ""]],
        "",
        'text-align="left"',
    )
    list_liabilities_data = {
        "Due to non-bank customers (gross basis)": "B01",
        "Due to other banks (Net basis) maturing within one month from MLR computation day": "B02",
        "15% of all undrawn commitments": "B03",
    }
    for key, value in list_liabilities_data.items():
        temp_row = []
        temp_row.append(key)
        temp_row.append(value)
        temp_row.append(
            query_result(
                "('DL')",
                "('CL', 'MD', 'CMP', 'CMT', 'OVT', 'OVP', 'BLT', 'BA')",
                "('LIQ IB BMCI')",
            )
        )
        html_content = html_gen.add_data_row(
            html_content, [temp_row], "", 'style="text-align:left;white-space:normal"'
        )
        xsl_fo_content = xsl_gen.add_xsl_data_row(
            xsl_fo_content, [temp_row], "", 'text-align="left" white-space="normal"'
        )
    html_content = html_gen.add_data_row(
        html_content,
        [["Total Qualifying Liabilites", "BT", ""]],
        "",
        "style=font-weight:bold;text-align:left",
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [["Total Qualifying Liabilites", "BT", ""]],
        "",
        'font-weight="bold" text-align="left"',
    )
    html_content = html_gen.add_data_row(
        html_content,
        [["C) Minimum Liquidity Ratio", "", ""]],
        "",
        "style=font-weight:bold;text-align:left",
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [["C) Minimum Liquidity Ratio", "", ""]],
        "",
        'font-weight="bold" text-align="left"',
    )
    list_liquidity_data = {
        "Total Liquid Assets": "C01",
        "Total Qualifying Liabilities": "C02",
    }
    for key, value in list_liquidity_data.items():
        temp_row = []
        temp_row.append(key)
        temp_row.append(value)
        temp_row.append(
            query_result(
                "('DL')",
                "('CL', 'MD', 'CMP', 'CMT', 'OVT', 'OVP', 'BLT', 'BA')",
                "('LIQ IB BMCI')",
            )
        )
        html_content = html_gen.add_data_row(
            html_content, [temp_row], "", 'style="text-align:left;white-space:normal"'
        )
        xsl_fo_content = xsl_gen.add_xsl_data_row(
            xsl_fo_content, [temp_row], "", 'text-align="left" white-space="normal"'
        )
    html_content = html_gen.add_data_row(
        html_content,
        [["Minimum Liquidity Ratio - minimum required is 15%", "C03", ""]],
        "",
        "style=font-weight:bold;text-align:left",
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [["Minimum Liquidity Ratio - minimum required is 15%", "C03", ""]],
        "",
        'font-weight="bold" text-align="left"',
    )
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
