from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael
import datetime

ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "HKMOa09 - RISK - HK Asset Monitoring",
}
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "HKMOa09 - RISK - HK Asset Monitoring",
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


def prepare_html_table(
    html_content,
    header_list,
    date_str,
    row_style="",
    header_style="font-weight: bold",
    table_styling="",
    date_style="text-align: left;",
):
    html_table = f"""
        <div> 
            <table {table_styling}>
        """
    html_table += f"<tr {row_style}>"
    html_table += (
        f"<td colspan='{len(header_list)}' style='{date_style}'>" + date_str + "</th>"
    )
    html_table += "</tr>"
    html_table += f"<tr {row_style}>"
    for i in header_list:
        html_table += f"<td style='{header_style}'>" + str(i) + "</th>"
    html_table += "</tr>"
    return html_content + html_table


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
    today_date = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    str_date = f"{str(today_date)} (UTC+07:00)"
    html_content = html_gen.create_base_html_content(
        "Hong Kong Assets - " + current_date, title_style
    )
    title = ["Date", "Nostro USD+HKD", "Placement", "Sec.", "Total", "Clean Dep.", "%"]
    html_content = prepare_html_table(html_content, title, str_date)
    for data in range(15):
        temp_row = []
        for rows in title:
            temp_row.append(0)
        html_content = html_gen.add_data_row(html_content, [temp_row])
    html_content = html_gen.close_html_table(html_content)
    html_file = html_gen.create_html_file(
        html_content, file_path, report_name, current_date, True, False
    )
    for i in output_file:
        if i != ".pdf":
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
