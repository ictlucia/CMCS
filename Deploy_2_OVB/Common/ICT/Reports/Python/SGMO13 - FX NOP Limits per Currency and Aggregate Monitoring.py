import acm, ael
from datetime import date, datetime, timedelta
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *


def timebucket():
    date_bucket = [date.today()]
    for i in range(1, 25):
        next = date_bucket[i - 1] + timedelta(days=1)
        date_bucket.append(next)
    date_bucket = [x.strftime("%d-%b") for x in date_bucket]
    return date_bucket


def open_code_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
    <table>
    """


def html_header(html_code):
    list_header_2d = [
        [
            "Date",
            "Highest Utilization per Currency",
            "Limit",
            "Conclusion",
            "Aggregate",
            "Limit",
            "Conclusion",
        ],
        ["In eq. USD", "Currency", "(in eqv. USD)", "Utilization", "(in eqv. USD)"],
    ]
    list_span_2d = [
        [[2, 1], [1, 2], [1, 1], [2, 1], [1, 1], [1, 1], [2, 1]],
        [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1]],
    ]
    i = 0
    for list_header, list_span in zip(list_header_2d, list_span_2d):
        html_code += "<tr>\n"
        for header, span in zip(list_header, list_span):
            color = (
                "#66afe3"
                if header
                in ["Highest Utilization per Currency", "Aggregate", "Utilization"]
                else "#bcbfc2"
                if header in ["Limit", "(in eqv. USD)"]
                else "white"
            )
            if i == 0 and header not in ["Date", "Conclusion"]:
                html_code += f'<td rowspan="{span[0]}" colspan="{span[1]}" style="background-color : {color}; vertical-align: middle; text-align: center">{header}</td>\n'
            else:
                html_code += f'<td rowspan="{span[0]}" colspan="{span[1]}" style="border-bottom : 1px black solid; background-color : {color}; vertical-align: middle; text-align: center">{header}</td>\n'
        html_code += "</tr>\n"
        i += 1
    return html_code


def html_content(html_code, date_bucket):
    data_row_2d = []
    for date in date_bucket:
        data_val_list = [date, 100, "SGD", 200, "Comply", 12342, 3124, "Comply"]
        html_code += "<tr>"
        for col_val in data_val_list:
            html_code += f"<td>{col_val}</td>"
        html_code += "</tr>"
    return html_code


def generate_excel(report_folder, report_name):
    html_code = open_code_html()
    html_code = html_header(html_code)
    html_code = html_content(html_code, timebucket())
    file_path = os.path.join(report_folder, report_name)
    f = open(file_path, "w")
    f.write(html_code + "</table></body></html>")
    f.close()


ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "testing",
}
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "SGMO13 - FX NOP Limits per Currency and Aggregate Monitoring",
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
        "Output Files",
        "string",
        [".pdf", ".xls"],
        ".xls",
        0,
        0,
        "Select Output Extension Type",
    ],
]


def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = parameter["report_name"] + ".xls"
    file_path = str(parameter["file_path"])
    output_file = "".join(parameter["output_file"])
    folder_name = "report" + date.today().strftime("%y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    if ".xls" in output_file:
        generate_excel(report_folder, report_name)
