from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael

excel_str_numbers = []

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'FO50 - TRC BONDRI Report Requirement - Data Cabang Daily SOD'}

def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"D:\HTML-Folder"
    return selection

def get_formatted_string(data):
    if data != '':
        return data
    else:
        return '-'

ael_variables=[
['report_name','Report Name','string', None, 'FO50 - TRC BONDRI Report Requirement - Data Cabang Daily SOD', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
] 
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']

    #branches = acm.FParty.Select("type='Broker'")
    all_brokers = acm.FChoiceList.Select('list=Branch')
    brokers = [broker for broker in all_brokers if broker.Description() != '']
    
    
    titles = ['No', 'BROKNO', 'BROKID', 'SN']
    
    rows = []
    count = 1
    
    for broker in brokers:
        temp_row = [str(count)]
        #print(broker)
        temp_list = broker.Name().split('-')
        brok_no = temp_list[0]
        excel_str_numbers.append(brok_no)
        
        brok_id = broker.Description()
        sn = temp_list[1]

        temp_row.extend( [brok_no, brok_id, sn] )
        
        rows.append(temp_row)
        count += 1
        
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    
    for title in titles:
        table_html = table_html.replace('<th>'+title+'</th>', '<th style="background-color: #ccccff;">'+title+'</th>')
        
    table_html = table_html.replace('&', '&amp;')
    table_html = table_html.replace('%', '&#37;')
    
    table_xsl_fo = table_xsl_fo.replace('&', '&amp;')
    table_xsl_fo = table_xsl_fo.replace('%', '&#37;')
    
    current_hour = get_current_hour("")
    current_date = get_current_date("")
    
    html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date)
    html_f = open(html_file, "r")
    html_contents = html_f.read().replace('''td, th {
      border: 1px solid #dddddd;
      text-align: center;
      padding: 8px;
    }''',
            ''' td, th {
      border: 1px solid #000000;
      text-align: center;
      padding: 8px;
    }''')
    for ex in excel_str_numbers:
        html_contents = html_contents.replace(
        '<td>'+ex+'</td>',
        f'<td>&ensp;{str(ex)}&ensp;</td>'
        )
    html_f = open(html_file, "w")
    html_f.write(html_contents)
    html_f.close()
    
    
    xsl_fo_file = create_xsl_fo_file(report_name + " " +current_date+current_hour, file_path, [table_xsl_fo], report_name, current_date)

    xsl_f = open(xsl_fo_file, "r")

    xsl_contents = xsl_f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">')
    xsl_contents = xsl_contents.replace('<fo:block font-weight="bold" font-size="30px" margin-bottom="30px">'+report_name+'</fo:block>',
    '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="center">'+report_name+'</fo:block>')
    xsl_contents = xsl_contents.replace('''<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">
    <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>No</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>BROKNO</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>BROKID</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>SN</fo:block></fo:table-cell>
        </fo:table-header>
    <fo:table-body>''',
    '''<fo:table-body>
    <fo:table-row background-color="#ccccff" font-weight="bold">
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center"><fo:block>NO</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center"><fo:block>BROKNO</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center"><fo:block>BROKID</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center"><fo:block>SN</fo:block></fo:table-cell>
    </fo:table-row>''')

    xsl_f = open(xsl_fo_file, "w")
    xsl_f.write(xsl_contents)
    xsl_f.close()

    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
            
    '''
    try:
        os.remove(xsl_fo_file)
    except:
        pass
    '''
