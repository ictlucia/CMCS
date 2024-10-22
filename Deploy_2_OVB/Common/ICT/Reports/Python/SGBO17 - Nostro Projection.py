import ael, acm
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from datetime import date, datetime

######################################################################################################################################################
# GET DATA
######################################################################################################################################################
def balanceFormat(balanceRaw):
    openingBalance, closingBalance = balanceRaw.split("//")
    
    if (openingBalance and not closingBalance):
        dateused, balanceUsed = openingBalance.split("_")
    elif (not openingBalance and closingBalance):
        dateused, balanceUsed = closingBalance.split("_")
    elif (openingBalance and closingBalance):
        dateOpeningBalance, NomOpeningbalance = openingBalance.split("_")
        dateClosingBalance, NomClosingbalance = closingBalance.split("_")
        
        balanceUsed = NomOpeningbalance if int(dateOpeningBalance) >= int(dateClosingBalance) else NomClosingbalance
    else :
        return "", 0
    
    dateused = datetime.strptime(dateused, "%Y%m%d").strftime("%d %b %Y")
    balanceUsed = float(balanceUsed.replace("D", "-").replace("C", ""))
    
    return dateused, balanceUsed

def getDataQuery():
    queryAcc = acm.FSQL["SGBO17 - Nostro Projection - Account"].Value().Text()
    querySett = acm.FSQL["SGBO17 - Nostro Projection - settlement"].Value().Text()
    accountList, settList = ael.asql(queryAcc)[1][0], ael.asql(querySett)[1][0]
    data_dict = {}
    
    for accData in accountList:
        accData = list(accData)
        dateBalance, balanceNom = balanceFormat(accData[-1])
        accData[4] = dateBalance
        accData[-1] = balanceNom
        
        data_dict[accData[0]] = {accData[4] : [accData]}
    
    for settData in settList:
        if settData[4] in data_dict[settData[0]].keys():
            data_dict[settData[0]][settData[4]].append(settData)
        else :
            data_dict[settData[0]][settData[4]] = [settData]
    
    return data_dict

print(getDataQuery())
        
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
                <td colspan="4" style="border-top: dashed; width: 15cm; text-align: left">Report : Nostro Projection</td>
                <td colspan="4" style="border-top: dashed; width: 15cm; text-align: left">NOSTRO PROJECTION</td>
            </tr>
            <tr>
                <td colspan="8" style="width: 15cm; text-align: left">System date : {dateNow} Create time {timeNow}</td>
            </tr>
            <tr>
                <td colspan="8" style="border-bottom: dashed; width: 15cm; text-align: left">Branch Processing date : {dateNow}</td>
            </tr>
    """
    
    return html_code

def headerCurrHtml(curr):
    html_code = f"""
        <tr><td></td></tr>
        <tr><td></td></tr>
        <tr><td colspan="8">NOS: {curr}</td></tr>
    """
    return html_code

def headerGlHtml(glNum):
    html_code = f"""
        <tr><td colspan="8">VDATE: {glNum}</td></tr>
    """
    return html_code

def headerField():
    html_code = f"""
        <tr>
            <td style="text-align:center; width:10cm">NOS</td>
            <td style="text-align:center">DEALNO</td>
            <td style="text-align:center">PRODUCT</td>
            <td style="text-align:center">TYPE</td>
            <td style="text-align:center">VDATE</td>
            <td style="text-align:center">POSTDATE</td>
            <td style="text-align:center">CMNE</td>
            <td style="text-align:center">AMTUPD</td>
        </tr>
    """
    return html_code

def dataBodyHtml(data_list):
    html_code = f"""
        <tr>
            <td style="text-align: left; width:10cm">{data_list[0]}</td>
            <td style="text-align: left;">{data_list[1]}</td>
            <td style="text-align: left;">{data_list[2]}</td>
            <td style="text-align: left;">{data_list[3]}</td>
            <td style="text-align: center;">{data_list[4]}</td>
            <td style="text-align: center;">{data_list[5]}</td>
            <td style="text-align: left;">{data_list[6]}</td>
            <td style="text-align: right; width:10cm">{float(data_list[7]):,}</td>
        </tr>
    """
    return html_code

def totalAmountHtml(unit, value, title):
    htmlCode = f"""
        <tr><td colspan="7">Total{title} : {unit}</td></tr>
        <tr><td colspan="7"></td><td  style="text-align: right; border-top: solid;">{float(value):,}</td></tr>
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
            htmlCode += totalAmountHtml(glNum, valGl, "VDATE")
        htmlCode += totalAmountHtml(curr, valCurr, "\t\t")
    
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
                    'windowCaption':'SGBO17 - Nostro Projection'}
ael_variables=[
['report_name','Report Name','string', None, 'SGBO17 - Nostro Projection', 1,0],
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
