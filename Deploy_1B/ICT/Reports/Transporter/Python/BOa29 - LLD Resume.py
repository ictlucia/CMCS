import ael, acm
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from datetime import date, datetime

######################################################################################################################################################
# GET DATA
######################################################################################################################################################
def getDataQuery():
    query_file_names = ["BOa29 Giro", "BOa29 NonGiro"]
    list_result = []
    
    for query_file_name in query_file_names:
        query = acm.FSQL[query_file_name].Value().Text()
        list_result.extend([list(x) for x in ael.asql(query)[1][0]])
    
    return list_result

######################################################################################################################################################
# TABLE FORMATING (XLS)
######################################################################################################################################################

def generateXlsFile(data_list_2d, file_path):
    headerStyle = "style='background-color: blue; text-align: center; font-weight: bold; color:white'"
    borderStyle = "border: thin solid windowtext; "
    dateNow, timeNow = datetime.now().strftime("%d %b %Y"), datetime.now().strftime("%H:%M %p")
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <table>
            <tr>
                <td {headerStyle}>CODE</td>
                <td {headerStyle}>Jenis Rekening</td>
                <td {headerStyle}>Jenis Valuta</td>
                <td {headerStyle}>Negara Debitur/Kreditur</td>
                <td {headerStyle}>Total</td>
            </tr>
    """
    
    for data_list in data_list_2d:   
        data_list[-1] = f"{data_list[-1]:,}" if data_list[-1] >= 0 else f"({data_list[-1]:,})"
        html_code += '<tr>\n' + "\n".join([f'<td style="{borderStyle} text-align: {"left" if i != 4 else "right"};">{data}</td>' for i, data in enumerate(data_list)]) + '\n</tr>'
        
    
    f = open(file_path + ".xls", "w")
    f.write(html_code + "</table></body></html>")
    f.close()

######################################################################################################################################################
# REPORT GENERATING
######################################################################################################################################################

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BOa29 - LLD Resume'}
ael_variables=[
['report_name','Report Name','string', None, 'BOa29 - LLD Resume', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls', 0, 1, 'Select Secondary Extensions Output'],
]

def ael_main(parameter):
    report_name = str(parameter['report_name'])
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    
    folder_name = "report"+date.today().strftime("%Y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    
    data_list_2d = getDataQuery()
    for ext in output_file:
        file_path = os.path.join(report_folder, report_name)
        if ext == ".xls":
            generateXlsFile(data_list_2d, file_path)
        elif ext == ".pdf":
            generatePdfFile(file_path)
