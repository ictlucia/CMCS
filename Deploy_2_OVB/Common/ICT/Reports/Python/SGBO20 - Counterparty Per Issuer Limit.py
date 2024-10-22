import acm, ael
from datetime import datetime, date
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

def getData():
    query = acm.FSQL["SGBO20 - Counterparty Per Issuer Limit"].Text()
    queryOutput = ael.asql(query)[1][0]

    dictData = {}

    for row in queryOutput:
        cptyName = row[0]
        branchName = row[1]
        #dataList = [x if i < 7 else f"{float(x):,}" for i, x in enumerate(row[2:])]
        dataList = row[2:]
        
        if cptyName in dictData.keys():
            if branchName in dictData[cptyName].keys():
                dictData[cptyName][branchName].append(dataList)
            else :
                dictData[cptyName][branchName] = [dataList]
        else :
            dictData[cptyName] = {}
            dictData[cptyName][branchName] = [dataList]
    
    return dictData


#####################################################################################################################################################################
## XLS TEMPLATE
#####################################################################################################################################################################
def xlsTemplate(RowdataList):
    htmlText = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <table style = "mso-number-format:'\@'">
                <tr><td>PT BANK MANDIRI (PERSERO) TBK</td></tr>
                <tr><td>SINGAPORE BRANCH</td></tr>
                <tr><td>Report : R02ALLYT</td></tr>
                <tr><td>Branch Processing Date:{date.today().strftime("%d %b %Y")}</td></tr>
                <tr><td>Branch Processing Date</td><td>45555</td></tr>
                <tr></tr>

                <tr style = "font-weight : bold">
                <td>BR</td> <td>DEALNO</td> <td>GRPID</td> <td>CUST</td> <td>REMARK</td> <td>REM</td> <td>EXPDATE</td> <td>CCY</td> <td>AMOUNT</td> <td>AMOUNT (USD)</td> <td>UTILIZATION</td> <td>UTILIZATION (USD)</td><td>AVAILABLE (USD)</td>
                </tr>

                <tr></tr><tr></tr><tr></tr>
                {RowdataList}
            </table>
        </body>
        </html>
    """
    return htmlText

def getRowdataList(queryResult):
    htmlText = ""
    for cptyName, branchDicts in queryResult.items():
        htmlText += f"<tr><td>{cptyName}</td></tr>\n"
        
        for branchName, dataList2d in branchDicts.items():
            for i, dataList in enumerate(dataList2d):
                htmlText += f"""<tr>\n<td style = "mso-number-format:'\@'">{branchName if i == 0 else ''}</td>\n"""
                
                for i, col in enumerate(dataList):
                    textAlign = "text-align : left;" if i < 7 else "text-align : right;"
                    htmlText += f"""<td style = "{textAlign} mso-number-format:'\@'">{col}</td>\n"""
                
                htmlText += "</tr>\n"
                
    return htmlText        

def generate_excel(report_folder, report_name):
    RowdataList = getRowdataList(getData())
    html_code = xlsTemplate(RowdataList)
    
    file_path = os.path.join(report_folder, report_name)
    f = open(file_path, "w")
    f.write(html_code)
    f.close()

#############################################################################################################################
## GENERATE REPORT
#############################################################################################################################

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'SGBO20 - Counterparty Per Issuer Limit'}

ael_variables=[
['report_name','Report Name','string', None, 'SGBO20 - Counterparty Per Issuer Limit', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Output Files','string', ['.xls'], '.xls', 0 , 0, 'Select Output Extension Type'],
]

def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = "".join(parameter['output_file'])
    
    folder_name = "report"+date.today().strftime("%Y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    if ".xls" in output_file:
        generate_excel(report_folder, report_name + ".xls")

        
        
        
        
        
        
        
        
        
        
        
        
        
    

