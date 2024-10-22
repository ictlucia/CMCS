import ael, acm
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from datetime import date, datetime

######################################################################################################################################################
# GET DATA
######################################################################################################################################################
def getDataQuery():
    query = acm.FSQL["HKBOa05 Query"].Value().Text()
    resultQuery = ael.asql(query)[1][0]
    data_dict = {}

    for result in resultQuery:
        result = list(result)
        result[-1] = result[-1].split("_")[1].replace("D", "-").replace("C", "") if result[-1] else 0
        try :
            data_dict[result[0]][str(result[1])].append(result[2:])
        except :
            try :
                data_dict[result[0]][str(result[1])] = [result[2:]]
            except :
                data_dict[result[0]] = {str(result[1]) : [result[2:]]}
    
    return data_dict
        
######################################################################################################################################################
# TABLE FORMATING (XLS)
######################################################################################################################################################
def openHtmlCode():
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
                <td colspan="3" style="border-top: dashed; width: 15cm; text-align: left">Branch : 04 Report : R04RN0SB</td>
                <td colspan="3" style="border-top: dashed; width: 15cm; text-align: left">Nostro Balance Report</td>
            </tr>
            <tr>
                <td colspan="3" style="width: 15cm; text-align: left">System date : {dateNow} Create time {timeNow}</td>
            </tr>
            <tr>
                <td colspan="3" style="border-bottom: dashed; width: 15cm; text-align: left">Branch Processing date : {dateNow}</td>
            </tr>
    """
    
    return html_code

def headerCurrHtml(curr):
    html_code = f"""
        <tr><td></td></tr>
        <tr><td></td></tr>
        <tr><td colspan="3">Currency Code: {curr}</td></tr>
    """
    return html_code

def headerGlHtml(glNum):
    html_code = f"""
        <tr><td colspan="3">General Ledger Account: {glNum}</td></tr>
    """
    return html_code

def headerField():
    html_code = f"""
        <tr>
            <td>Nostro Account Number</td>
            <td>Account Name</td>
            <td>Account Balance</td>
        </tr>
    """
    return html_code

def dataBodyHtml(data_list):
    html_code = f"""
        <tr>
            <td style="text-align: left;">{data_list[0]}</td>
            <td style="text-align: left;">{data_list[1]}</td>
            <td style="text-align: right;">{float(data_list[2]):,}</td>
        </tr>
    """
    return html_code

def totalAmountHtml(unit, value):
    htmlCode = f"""
        <tr><td colspan="3">Total General Ledger Account: {unit}</td></tr>
        <tr><td></td><td></td><td  style="text-align: right; border-top: solid;">{float(value):,}</td></tr>
    """
    return htmlCode

def generateXlsFile(file_path):
    htmlCode = openHtmlCode()
    
    for i, (curr, data_gl) in enumerate(getDataQuery().items()):
        valCurr = 0
        htmlCode += headerCurrHtml(curr)
        for glNum, list_2d in data_gl.items():
            htmlCode += headerGlHtml(glNum)
            valGl = 0
            for j, data_list in enumerate(list_2d):
                htmlCode += headerField() if i == 0 and j == 0 else ""
                htmlCode += dataBodyHtml(data_list)
                valGl += float(data_list[-1])
                
            valCurr += valGl
            htmlCode += totalAmountHtml(glNum, valGl)
        htmlCode += totalAmountHtml(curr, valCurr)
    
    htmlCode += "</table></body></html>"
    f = open(file_path + ".xls", "w")
    f.write(htmlCode)
    f.close()

######################################################################################################################################################
# TABLE FORMATING (PDF)
######################################################################################################################################################
def openPdfCode(title, title_styling=""):
    style = f'number-columns-spanned="3" column-width="15cm" text-align="left" vertical-align="middle"'
    
    xsl_fo_content = f"""<?xml version="1.1" encoding="utf-8"?>
    <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format">
        <fo:layout-master-set>
        <fo:simple-page-master master-name="my_page" margin="0.5in" page-width="25in">
        <fo:region-body/>
        </fo:simple-page-master>
        </fo:layout-master-set>
        <fo:page-sequence master-reference="my_page">
        <fo:flow flow-name="xsl-region-body">
    <fo:block {title_styling}> {title} </fo:block>
    <fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
    <fo:table-body>
        <fo:table-row>
            <fo:table-cell {style} border-top-style="dashed"><fo:block>Branch : 04 Report : R04RN0SB</fo:block></fo:table-cell>
            <fo:table-cell {style} border-top-style="dashed"><fo:block>Nostro Balance Report</fo:block></fo:table-cell>
        </fo:table-row>
        <fo:table-row>
            <fo:table-cell {style}><fo:block>System date : 22 Sep 2022 Create time 9:25 PM</fo:block></fo:table-cell>
        </fo:table-row>
        <fo:table-row>
            <fo:table-cell {style} border-bottom-style="dashed"><fo:block>ranch Processing date : 22 Sep 2022</fo:block></fo:table-cell>
        </fo:table-row>
    """
    
    return xsl_fo_content


def generatePdfFile(file_path):
    xslfoCode = openPdfCode("test")

    xslfoCode += """</fo:table-body></fo:table></fo:flow></fo:page-sequence></fo:root>"""
    f = open(file_path + ".fo", "w")
    f.write(xslfoCode)
    f.close()
    generate_pdf_from_fo_file(file_path)

    
######################################################################################################################################################
# REPORT GENERATING
######################################################################################################################################################

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'HKBOa05 - Nostro Balance'}
ael_variables=[
['report_name','Report Name','string', None, 'HKBOa05 - Nostro Balance', 1,0],
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
    
    for ext in output_file:
        file_path = os.path.join(report_folder, report_name)
        if ext == ".xls":
            generateXlsFile(file_path)
        elif ext == ".pdf":
            generatePdfFile(file_path)
