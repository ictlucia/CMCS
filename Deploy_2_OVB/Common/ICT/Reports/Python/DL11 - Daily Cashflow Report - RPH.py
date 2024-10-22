from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael
from datetime import date
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer

ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "DL11 - Daily Cashflow Report - RPH",
}
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "DL11 - Daily Cashflow Report - RPH",
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


def query_nominal(optkey3, optkey4, portfolio):
    optkey3_query = (
        " AND DISPLAY_ID(t, 'optkey3_chlnbr') in " + optkey3 if optkey3 else ""
    )
    optkey4_query = (
        " AND DISPLAY_ID(t, 'optkey4_chlnbr') in " + optkey4 if optkey4 else ""
    )
    port_query = " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio if portfolio else ""
    query = (
        f"""
            SELECT SUM(t.price*t.quantity) FROM trade t, instrument i, party p 
            where t.insaddr=i.insaddr and t.counterparty_ptynbr = p.ptynbr
            """
        + optkey3_query
        + optkey4_query
        + port_query
    )
    result = ael.asql(query)
    value = result[1][0][0][0] if result[1][0] else 0
    return value


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
            color: black;
            font-size:20px;
        }
        .subtitle-1 {
            color: #0000FF;
            font-size: 16px;
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
        table {
            border: 0;
            text-align: left;
            width:60%;
        }
        tr, td, th {
            border: none;
            text-align: left;
        }
        .yel, .number {
            background-color:#f1f511;
        }
        .number, .number_total, .number-white {
            text-align: right;
        }
        .orange, .number_total {
            background-color:#f5a43b;
            font-weight: bold;
        }
    """
    current_date = date.today().strftime("%y%m%d")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content(
        "RASIO PELAKSANAAN HEDGING (RPH) KREDIT DAN OBLIGASI BUNGA TETAP KLN",
        title_style,
    )
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content(
        "RASIO PELAKSANAAN HEDGING (RPH) KREDIT DAN OBLIGASI BUNGA TETAP KLN"
    )
    title = "RPH", "", "", ""
    html_content = html_gen.prepare_html_table(html_content, title)
    xsl_fo_content = xsl_gen.add_xsl_fo_table_header(xsl_fo_content, title)
    html_content = html_gen.add_data_row(
        html_content, [["", current_date, "", "Valas"]], "", "class=bold"
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content, [["", current_date, "", "Valas"]], "", 'font-weight="bold"'
    )
    html_content = html_gen.add_data_row(
        html_content,
        [
            [
                "(a)",
                "Posisi baki debet kredit bunga tetap per",
                current_date,
                "(Eq Juta USD)",
            ]
        ],
        "",
        "class=bold",
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [
            [
                "(a)",
                "Posisi baki debet kredit bunga tetap per",
                current_date,
                "(Eq Juta USD)",
            ]
        ],
        "",
        'font-weight="bold"',
    )
    list_data_a = {
        "Large Corporate": "-",
        "Hubungan Kelembagaan": "-",
        "Middle Corporate (Auto Sector)": "-",
        "SME Banking": "2",
        "Consumer Loan (KTA)": "1",
        "Auto Loan (MTF+MUF)": "-",
        "Total (a)": "3",
    }
    for key, value in list_data_a.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        html_content = html_gen.add_cell_data(
            html_content, "", "" if "Total (" not in key else "class=orange"
        )
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "")
        html_content = html_gen.add_cell_data(
            html_content, key, "" if "Total (" not in key else "class=orange"
        )
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, key)
        html_content = html_gen.add_cell_data(
            html_content, "", "" if "Total (" not in key else "class=orange"
        )
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, key)
        html_content = html_gen.add_cell_data(
            html_content,
            value,
            "class=number" if "Total (" not in key else "class=number_total",
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, value, 'background-color="yellow"'
        )
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    html_content = html_gen.add_data_row(
        html_content,
        [
            [
                "(b)",
                f'Posisi obligasi bunga tetap per {date.today().strftime("%d %B %Y")}',
            ]
        ],
        "",
        "class=bold",
    )
    xsl_fo_content = xsl_gen.add_xsl_data_row(
        xsl_fo_content,
        [["(b)", "Posisi obligasi bunga tetap per 18 Juli 2022"]],
        "",
        'font-weight="bold"',
    )
    b_query = {
        "b1": [
            "('BOND', 'SBI')",
            "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'INDOIS', 'PBS', 'NCD', 'SVBLCY', 'SVBUSD', 'IDSV')",
            "('BB BOND OCI BMDL')",
        ],
        "b2": [
            "('BOND', 'SBI')",
            "('CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'INDOIS', 'PBS', 'NCD', 'SVBLCY', 'SVBUSD', 'IDSV')",
            "('BB BOND AC BMDL')",
        ],
    }
    list_data_b = {
        "Posisi Obligasi Fixed Rate Portoflio AFS per": query_nominal(
            b_query["b1"][0], b_query["b1"][1], b_query["b1"][2]
        ),
        "Posisi Obligasi Fixed Rate Portoflio HTM per": query_nominal(
            b_query["b2"][0], b_query["b2"][1], b_query["b2"][2]
        ),
        "Total (b)": query_nominal(b_query["b1"][0], b_query["b1"][1], b_query["b1"][2])
        + query_nominal(b_query["b2"][0], b_query["b2"][1], b_query["b2"][2]),
    }
    for key, value in list_data_b.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        html_content = html_gen.add_cell_data(
            html_content, "", "" if "Total (" not in key else "class=orange"
        )
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "")
        html_content = html_gen.add_cell_data(
            html_content, key, "" if "Total (" not in key else "class=orange"
        )
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, key)
        html_content = html_gen.add_cell_data(
            html_content,
            current_date if "Total (" not in key else "",
            "" if "Total (" not in key else "class=orange",
        )
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, current_date)
        html_content = html_gen.add_cell_data(
            html_content,
            value,
            "class=number" if "Total (" not in key else "class=number_total",
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, value, 'background-color="yellow"'
        )
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    # html_content = html_gen.add_data_row(html_content,[['','Total (b)','','0']],'class=orange','class=bold')
    # xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[['','Total (b)','','0']],'background-color="orange"','font-weight="bold"')
    gabungan_query = {
        "d": [
            "('DL')",
            "('CMT', 'BA', 'BLT')",
            "('IRT MM Depo Loan Repo RR 1 BMDL', 'IRT MM Depo Loan Repo RR 2 BMDL', 'LIQ IB BMDL, LIQ MM BMDL', 'ALM Bilateral Loans BMDL')",
        ],
        "e": [
            "('REPO')",
            "('IWFSBI', 'IWFGOV', 'IWFDIS', 'IWFNON', 'IWFOTH', 'IBSBI', 'IBGOV', 'IBDIS', 'IBNON', 'IBOTH')",
            "('IRT MM Depo Loan Repo RR 1 BMDL', 'IRT MM Depo Loan Repo RR 2 BMDL', 'LIQ MM BMDL')",
        ],
        "k": ["('SWAP')", "('IRS')", "('BB Derivative BMDL')"],
    }
    list_data_gabungan = {
        "(c)": ["Deposito tenor > 6 mo", "", "-"],
        "(d)": [
            "Pinjaman Interbank (MM/BA/BL) tenor > 6 mo",
            "",
            query_nominal(
                gabungan_query["d"][0], gabungan_query["d"][1], gabungan_query["d"][2]
            ),
        ],
        "(e)": [
            "Repo tenor > 6 mo",
            "",
            query_nominal(
                gabungan_query["e"][0], gabungan_query["e"][1], gabungan_query["e"][2]
            ),
        ],
        "(f)": ["Senior debt (per 2024-01-22 )", "", "-"],
        "(g)": ["Global Bonds (per 2024-01-22 )", "", "-"],
        "(h)": ["Sustainability Bonds (per 2024-01-22 )", "", "-"],
    }
    for key, value in list_data_gabungan.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        html_content = html_gen.add_cell_data(html_content, key, "")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, key)
        html_content = html_gen.add_cell_data(html_content, value[0], "")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, value[0])
        html_content = html_gen.add_cell_data(html_content, value[1], "")
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, value[1])
        html_content = html_gen.add_cell_data(
            html_content,
            value[2],
            "class=number-white" if "(per " in value[0] else "class=number",
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, value[2], 'background-color="yellow"'
        )
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    list_data_gabungan_terakhir = {
        "(i)": ["Natural Hedge (i) = (c)+(d)+(e)+(f)+(g)+(h)", "", "-"],
        "(j)": ["Net baki debet (Total (a)+(b)-(i))", "", "-"],
        "(k)": [
            "Outstanding IRS<sup>(3)</sup>",
            "",
            query_nominal(
                gabungan_query["k"][0], gabungan_query["k"][1], gabungan_query["k"][2]
            ),
        ],
        "(l)": ["Rasio Pelaksanaan Hedging<sup>(2)</sup>(i)/(k)", "", "-"],
        "(m)": ["Realisasi biaya bunga hedging(4)", "", "-"],
        "(n)": ["Revaluasi(4)", "", "-"],
    }
    for key, value in list_data_gabungan_terakhir.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        html_content = html_gen.add_cell_data(
            html_content,
            key if key not in ["(m)", "(n)"] else value[0],
            'colspan="2" style="font-weight: bold"' if key in ["(m)", "(n)"] else "",
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, key if key not in ["(m)", "(n)"] else ""
        )
        html_content = html_gen.add_cell_data(
            html_content,
            value[0] if key not in ["(m)", "(n)"] else "",
            "class=orange" if key not in ["(m)", "(n)"] else "",
        )
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, value[0])
        html_content = html_gen.add_cell_data(
            html_content,
            value[1] if key not in ["(m)", "(n)"] else "-",
            "class=orange" if key not in ["(m)", "(n)"] else 'style="text-align:right"',
        )
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, value[1])
        html_content = html_gen.add_cell_data(
            html_content,
            value[2] if key not in ["(m)", "(n)"] else "",
            "class=number-white" if key in ["(m)", "(n)"] else "class=number_total",
        )
        xsl_fo_content = xsl_gen.add_xsl_column(
            xsl_fo_content, value[2], 'background-color="yellow"'
        )
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
