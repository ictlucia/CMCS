from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer
import datetime

ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "DL06 - Placement & Borrowing Outstanding - Compiles",
}
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "DL06 - Placement & Borrowing Outstanding - Compiles",
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
        [".xls"],
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
        "ribka.siahaan@bankmandiri.co.id, tqatestingbo@gmail.com\\ <Report Name> - <Date>\\ Enclosed <Report Name> report document as of <Date>\\ ",
        0,
        0,
    ],
]


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


def process_text(ael_params, raw_text):
    processed_string = raw_text.replace("<Date>", acm.Time.DateToday())
    processed_string = processed_string.replace(
        "<Report Name>", ael_params["report_name"]
    )
    return processed_string


def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = parameter["output_file"]
    email_params = str(parameter["email_params"])
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
    """
    current_date = datetime.date.today().strftime("%y%m%d")
    date_today = acm.Time.DateToday()
    portfolio_list = "('IRT MM Depo Loan Repo RR 1 BMDL', 'IRT MM Depo Loan Repo RR 2 BMDL', 'LIQ IB BMDL', 'LIQ MM BMDL')"
    optkey3_list = "('DL')"
    optkey4_list = "('CMP', 'CMT', 'OVP', 'OVT')"
    html_content = html_gen.create_base_html_content(
        "DL06 - Placement & Borrowing Outstanding - Compiles as per. " + date_today, ""
    )
    html_content = html_gen.prepare_html_table(html_content, "")
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content(
        "DL06 - Placement &amp; Borrowing Outstanding - Compiles as per. " + date_today,
        "",
    )
    xsl_fo_content += """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""
    list_data = {
        "Placement": [
            query_result(optkey3_list, optkey4_list, portfolio_list),
            "#3c8f52",
        ],
        "BMSG": [query_result(optkey3_list, optkey4_list, portfolio_list), "#479ec9"],
        "BMHK": [query_result(optkey3_list, optkey4_list, portfolio_list), "#479ec9"],
        "BMCIB": [query_result(optkey3_list, optkey4_list, portfolio_list), "#479ec9"],
        "BMSH": [query_result(optkey3_list, optkey4_list, portfolio_list), "#479ec9"],
        "Bunga Acrual": [
            query_result(optkey3_list, optkey4_list, portfolio_list),
            "#f28dbe",
        ],
        "Jurnal Balik": [
            query_result(optkey3_list, optkey4_list, portfolio_list),
            "#eb444a",
        ],
    }
    for key, val in list_data.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        html_content = html_gen.add_cell_data(html_content, key)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, key)
        html_content = html_gen.add_cell_data(
            html_content, val[0], "width=160px; style=background-color:" + val[1]
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, val[0], "width='160px' background-color='" + val[1] + "'"
        )
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_fo_content.replace('page-width="25in"', 'page-width="5in"')
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
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
            pdf_file = xslfo_file.split(".")
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
    split_params = email_params.split("\ ")
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
