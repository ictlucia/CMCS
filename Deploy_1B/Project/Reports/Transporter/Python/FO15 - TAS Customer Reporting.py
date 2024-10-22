from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael

        
def generate_html_file(report_name, titles, file_path, output_file):
    html_gen = HTMLGenerator()
    title_style = """
        .title {
            color: #800000;
            text-align: left;   
        }
        
        .subtitle-1 {
            color: #0000FF;
            font-size: 20px;
            text-align: left;
            font-weight: bold;
        }
        
        .subtitle-2 {
            color: #000080;
            font-size: 16px;
            text-align: left;
        }
        .amount {
            font-weight: bold;
        }
    """
    current_date = get_current_date("-")
    date_row = [["Report Date:", current_date]]
    
    html_content = html_gen.create_base_html_content(report_name, title_style)
    html_content = html_gen.prepare_html_table(html_content, [])
    html_content = html_gen.add_data_row(html_content, date_row, row_class='', cell_class='')
    html_content = html_gen.close_html_table(html_content)
    
    
    query = ael.asql("""SELECT t.trdnbr, t.trader_usrnbr, p.ptynbr, p.hostid
    FROM Party p, Trade t
    WHERE p.ptynbr *= t.counterparty_ptynbr
    /*AND p.creat_time = TODAY*/
    AND p.type = 'Counterparty'
    """, 1)
    
    data_row = query[1][0]
    for row_index in range(len(data_row)):
        print(data_row[row_index])
        data_row[row_index] = list(data_row[row_index])
        data_row[row_index][0] = data_row[row_index][0].trdnbr if data_row[row_index][0] != '' else '-' 
        data_row[row_index][1] = data_row[row_index][1].userid if (data_row[row_index][1] != '' and data_row[row_index][1] != 0) else '-' 
        data_row[row_index][2] = data_row[row_index][2].ptynbr
        data_row[row_index].append('Registered')
            
    html_content = html_gen.prepare_html_table(html_content, titles)
    html_content = html_gen.add_data_row(html_content, data_row, row_class='', cell_class='')
    html_content = html_gen.close_html_table(html_content)
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True, True)
    return html_file
    
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Tas Report - New Customer Registration'}

ael_variables=[
    ['report_name','Report Name','string', None, 'Tas Report - New Customer Registration', 1,0],
    ['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
    ['output_file','Secondary Output Files','string', ['.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
]
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    
    title_style = """
        .title {
            color: #800000;
            text-align: left;   
        }
        
        .subtitle-1 {
            color: #0000FF;
            font-size: 20px;
            text-align: left;   
        }
        
        .subtitle-2 {
            color: #000080;
            font-size: 16px;
            text-align: left;   
        }
    """    
    titles = ["Trade Number", "Trader/Dealer", "New CTPTY Reff", "New CTPTY CIF", "Registration Status"]
    for i in output_file:
        if i != '.pdf' :
            html_file = generate_html_file(report_name, titles, file_path, output_file)
            generate_file_for_other_extension(html_file , i)
        #else:
            #xsl_fo_file = generate_xls_fo_file(report_name, titles, file_path, output_file, heading_1_list, heading_2_list, optkey3_list, optkey4_list)
            #generate_pdf_from_fo_file(xsl_fo_file)
