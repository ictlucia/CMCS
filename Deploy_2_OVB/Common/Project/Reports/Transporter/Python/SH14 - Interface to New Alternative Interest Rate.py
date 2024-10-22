import acm, ael, random
from datetime import datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
today = acm.Time.DateToday()
def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"C:\Users\Anugrah\Desktop"
    return selection
    
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'SH14 - Interface to New Alternative Interest Rate'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'SH14 - Interface to New Alternative Interest Rate', 1,0],
['input_date','Inputs Date', 'date', None, today, 1,0],
['market','Market Type', 'string', ['LIBOR', 'CIBOR', 'JIBOR', 'SBI1M'], 'LIBOR', 1, 0, "Select to Filter the Market", None, 1],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.xls'], '.xls', 0, 1, 'Select Secondary Extensions Output'],
]
def ael_main(parameter):
    report_name = parameter['report_name']
    input_date = '-'.join([str(i).zfill(2) for i in acm.Time.DateToYMD(parameter['input_date'])])
    market_type = parameter['market'] 
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    tenors = ['1D', '1W', '1M', '3M', '6M', '1Y', '2Y', '3Y', '4Y', '5Y']
    columns = ['TENOR', 'Market Data Source', 'NTCS Input Result', 'RESULT', 'PREVIOUS DAY RATE', 'FAIRNESS']
    rows = [['BID', 'ASK', 'MID']*5 ]
    for tenor in tenors:
        temp_row = [tenor]
        for col in columns[1:]:
            if col.lower() == 'fairness':
                b = round(temp_row[10] - temp_row[1], 4)
                a = round(temp_row[11] - temp_row[2], 4)
                m = round(temp_row[12] - temp_row[3], 4)
            elif col.lower() == 'result':
                b = 'OK' if temp_row[4] == temp_row[1] else 'NOK'
                a = 'OK' if temp_row[5] == temp_row[2] else 'NOK'
                m = 'OK' if temp_row[6] == temp_row[3] else 'NOK'
            else:
                b = round(random.uniform(-1, 1) + random.uniform(1, 2), 4)
                a = round(b + random.randint(9, 100)/10000, 4)
                m = round((b+a)/2, 4)
            for k in (b, a, m):
                temp_row.append(k)
        rows.append(temp_row)
        
    current_hour = get_current_hour("")
    current_date = get_current_date("")
    report_name = report_name + " - " + market_type + " " + input_date
    
    table_html = create_html_table(columns, rows)
    for col in columns:
        if col.lower() == 'tenor':
            table_html = table_html.replace('<th>{}</th>'.format(col), '<th rowspan=2 style="background-color:#FFFFFF;font-weight:bold">{}</th>'.format(col))
        else:
            table_html = table_html.replace('<th>{}</th>'.format(col), '<th colspan=3 style="background-color:#FFFFFF;font-weight:bold">{}</th>'.format(col))
    for tenor in tenors:
        table_html = table_html.replace('<td>{}</td>'.format(tenor), '<td style="background-color:#FFFFFF;font-weight:bold">{}</td>'.format(tenor))
    for k in set(rows[0]):
        table_html = table_html.replace('<td>{}</td>'.format(k), '<td style="background-color:#FFFFFF;font-weight:bold">{}</td>'.format(k))
    table_html = table_html.replace('<td>NOK</td>', '<td style="background-color:#F90000;font-weight:normal">NOK</td>')
    for row in rows[1:]:
        fairness = [str(i) for i in row[-3:]]
        old_text = '<td>'+'</td><td>'.join(fairness)+'</td>'
        new_text = old_text
        for value in fairness:
            if float(value) > 1 or float(value) < -1:
                new_text = new_text.replace('<td>{}</td>'.format(value), '<td style="background-color:#F90000;font-weight:normal">{}</td>'.format(value))
        table_html = table_html.replace(old_text, new_text)
        
    html_file = create_html_file(report_name + " " + current_date + current_hour, file_path, [table_html], report_name, current_date)
    
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
    
    try:
        os.remove(xsl_fo_file)
    except:
        pass
