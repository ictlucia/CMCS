import acm, ael, os
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BO67 - Rekap Bulan Systematic Internalizer'}

ael_variables=[
['report_name','Report Name','string', None, 'BO67 - Rekap Bulan Systematic Internalizer', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
]

def runReport():
    context = acm.GetDefaultContext()
    template  = str(context.GetExtension("FXSLTemplate", "FObject", "XlsTemplateBO67"))

    query = acm.FSQL.Select("name = BO67 - Rekap Bulan Systematic Internalizer - Query")[0].Text()
    queryResults = ael.asql(query)[1]

    for i, queryResult in enumerate(queryResults):
        dictWeek = {"Minggu I" : [0] * 7, "Minggu II" : [0] * 7, "Minggu III" : [0] * 7, "Minggu IV" : [0] * 7, "Minggu V" : [0] * 7, }
        for row in queryResult:
            dictWeek[row[0]] = [x if x != "" else 0 for x in row[1:]]
            
        for j, [key, row] in enumerate(dictWeek.items()):
            for k, col in enumerate(row):
                code = "{{" + f"{i+1}{j+1}{k+1}" "}}"
                colVal = f"{round(float(col), 2):,}"
                template = template.replace(code, str(colVal))
    
    return template

def ael_main(parameter):
    year, month, day = [str(x) if len(str(x)) > 1 else "0" + str(x) for x in acm.Time().DateToYMD(acm.Time().DateToday())]

    report_name = parameter['report_name']
    file_path_base = str(parameter['file_path'])
    folder_path = os.path.join(file_path_base, report_name, f"{year}{month}{day}")
    file_path = os.path.join(folder_path, report_name + ".xls")
    
    reportCode = runReport()
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    with open(file_path, "w") as file:
        file.write(reportCode)
    
