import acm, ael, os, re
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

def runQuery(template, queryNameFull, totalList):
    query = acm.FSQL[queryNameFull].Text()
    resultQuery = [x[3:] for x in ael.asql(query)[1][0]]
    
    if "Counterparty" not in queryNameFull:
        subTotal = ael.asql(query)[1][1][0][3:] if ael.asql(query)[1][1] else []
    else :
        subTotal = []
    
    for row in resultQuery:
        name = row[0]
        nom1 = float(row[1])
        nom2 = float(row[2]) if "Counterparty" not in queryNameFull else float(row[2]) + float(row[1])
        
        name1, name2 = "{"+name+"1"+"}", "{"+name+"2"+"}"
        nom1, nom2 = f"{float(nom1):,}", f"{float(nom2):,}"
        
        template = template.replace(name1, nom1)
        template = template.replace(name2, nom2)
    
    if subTotal:
        indexListTotal = 0 if "Bank" in subTotal[0] else 1
        totalList[indexListTotal][0][1] += subTotal[1]
        totalList[indexListTotal][1][1] += float(subTotal[2])
        
        nameSub = subTotal[0]
        nomSub1 = float(subTotal[1])
        nomSub2 = float(subTotal[2])
        
        nameSub1, nameSub2 = "{"+nameSub+"1"+"}", "{"+nameSub+"2"+"}"
        nomSub1, nomSub2 = f"{float(nomSub1):,}", f"{float(nomSub2):,}"
        
        template = template.replace(nameSub1, nomSub1)
        template = template.replace(nameSub2, nomSub2)
    
    return template

def runReport():
    context = acm.GetDefaultContext()
    template  = str(context.GetExtension("FXSLTemplate", "FObject", "XlsTemplateHKMOa11"))  

    queryName = 'HKMOa11 - ICC - Off Balance Sheet - '
    listQueryType = ["Interest Rate", "Foreign Exchange", "Equity", "Commodity", "Other", "Counterparty"]
    
    totalList = [
        [["{TotalBank1}", 0], ["{TotalBank2}", 0]],
        [["{TotalTrd1}", 0], ["{TotalTrd2}", 0]],
    ]
    
    for queryType in listQueryType:
        queryNameFull = queryName + queryType
        
        template = runQuery(template, queryNameFull, totalList)
        
    for i in totalList:
        for j in i:
            template = template.replace(j[0], f"{float(j[1]):,}")
    template = re.sub(r'{.+}', '0', template)
    
    return template
    
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'HKMOa11 - ICC - Off Balance Sheet'}

ael_variables=[
['report_name','Report Name','string', None, 'HKMOa11 - ICC - Off Balance Sheet', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
]

def ael_main(parameter):
    year, month, day = [str(x) if len(str(x)) > 1 else "0" + str(x) for x in acm.Time().DateToYMD(acm.Time().DateToday())]
    
    report_name = parameter['report_name']
    file_path_base = str(parameter['file_path'])
    folder_path = os.path.join(file_path_base, report_name, f"{year}{month}{day}")
    file_path = os.path.join(folder_path, report_name + ".xls")
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    with open(file_path, "w") as file:
        file.write(runReport())
