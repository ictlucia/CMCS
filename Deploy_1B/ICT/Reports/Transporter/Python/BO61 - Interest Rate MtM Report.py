import acm, ael, random

from datetime import datetime

from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

today = acm.Time.DateToday()

def getFilePathSelection():

    """ Directory selector dialog """

    selection = acm.FFileSelection()

    selection.PickDirectory(True)

    selection.SelectedDirectory = r"C:\\"

    return selection

    

ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'BO61 - Interest Rate MtM Report'}

                    

ael_variables=[

['report_name','Report Name','string', None, 'BO61 - Interest Rate MtM Report', 1,0],

['input_date','Inputs Date', 'date', None, today, 1,0],

['market','Market Type', 'string', ['LIBOR', 'CIBOR', 'JIBOR', 'HIBOR'], 'HIBOR', 1, 0, "Select to Filter the Market", None, 1],

['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

['output_file','Secondary Output Files','string', ['.xls'], '.xls', 0, 1, 'Select Secondary Extensions Output'],

]

def get_tenor(insid):
    query = f"""
    SELECT 
        i.insid
    FROM 
        Price p, instrument i
    WHERE
        p.insaddr = i.insaddr AND
        i.insid LIKE '%{insid}%'
    GROUP BY
        i.insid
    """

    result = [x[0].split("/")[-1] for x in ael.asql(query)[1][0]]
    return result
    
def ael_main(parameter):

    report_name = parameter['report_name']

    input_date = '-'.join([str(i).zfill(2) for i in acm.Time.DateToYMD(parameter['input_date'])])

    market_type = parameter['market'] 

    file_path = str(parameter['file_path'])

    output_file = parameter['output_file']

    columns = ['TENOR', 'NTCS Input Result', 'PREVIOUS DAY RATE', 'FAIRNESS']

    rows = [['BID', 'ASK', 'MID']*3 ]
    
    curr = {'LIBOR' : 'USD', 'CIBOR' : 'CNY', 'JIBOR' : 'IDR', 'HIBOR' : 'HKD'}
    
    insName = f"{curr[market_type]}/{market_type}"
    
    tenors = get_tenor(insName)
    
    for tenor in tenors:

        temp_row = [tenor]
        
        for timestamp in ["TODAY", "YESTERDAY"]:
            
            try :
            
                price = acm.FPrice.Select(f"instrument = '{insName}/{tenor}' and market = 'REFINITIV_SPOT' and day = {timestamp}").Last()
                
                bid = price.Bid() if str(price.Bid())[0].isdigit() else 0
                ask = price.Ask() if str(price.Ask())[0].isdigit() else 0
                mid = price.Settle() if str(price.Settle())[0].isdigit() else 0
                
                temp_row.extend([float(bid), float(ask), float(mid)])
            except :                
                temp_row.extend([0, 0, 0])
                
        fairness = [temp_row[1] - temp_row[4], temp_row[2] - temp_row[5], temp_row[3] - temp_row[6]]
        temp_row.extend(fairness)
        
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

        

    html_file = create_html_file(report_name + " " + current_date + current_hour, file_path, [table_html], report_name, current_date, False)

    

    for i in output_file:

        if i != '.pdf' :

            generate_file_for_other_extension(html_file, i)

        else:

            generate_pdf_from_fo_file(xsl_fo_file)

    

    try:

        os.remove(xsl_fo_file)

    except:

        pass

