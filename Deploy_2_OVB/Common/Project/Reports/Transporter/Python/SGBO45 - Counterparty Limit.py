from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

file_name = 'SGBO45 - Counterparty Limit'

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':file_name}

ael_variables=[
['report_name','Report Name','string', None, file_name, 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
]

def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']

    titles = ['CAT', 'CUSTNAME', 'CFCOUN', 'CFCITZ', 'BR', 'SOURCE', 'CUSTLMT', 'SUBLMT', 'SUB LIMIT NAME', 'FACILITY NAME', 'ACCOUNT NO', 'R', 'DUE DATE', 'ORI', 'CCY', 'CFLCAS', 'PRODUCT', 'CUSTLMT (TOTAL)', 'TOTAL']
    compliance_rule = acm.FComplianceRule.Select('')

    row = []
    rows = []
    country_list = []
    countryid_list = []
    i = 0

    for cr in compliance_rule:
        for ar in cr.AppliedRules():
            if ar.TargetType() == 'Party':
                country = ar.Target().Country()
                countryid = ar.Target().Free1()
                if country.upper() not in country_list and country != "":
                    if countryid.upper() not in countryid_list and countryid != "":
                        country_list.append(country.upper())
                        countryid_list.append(countryid.upper())
                        row = ['CUST', '', country.upper(), country.upper(), '', '', acm.Time.DateFromTime(cr.UpdateTime()), cr.Thresholds()[0].DefaultValue(), cr.Thresholds()[-1].DefaultValue()]
                        rows.append(row)

    #rows = ['','','','','','','','','','','','','','','','','','','']
    
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)

    current_date = get_current_date('')

    html_file = create_html_file(report_name, file_path, [table_html], report_name, current_date)
    xsl_fo_file = create_xsl_fo_file(report_name, file_path, [table_xsl_fo], report_name, current_date)
    
    xsl_f = open(xsl_fo_file, "r")

    xsl_contents = xsl_f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" reference-orientation="90">')

    xsl_f = open(xsl_fo_file, "w")
    xsl_f.write(xsl_contents)
    xsl_f.close()
    
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
