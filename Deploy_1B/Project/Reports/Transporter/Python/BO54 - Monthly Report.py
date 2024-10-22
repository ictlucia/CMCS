import acm, ael, math
from datetime import datetime
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
current_year = datetime.now().year
list_month = ['JANUARI', 'FEBRUARI', 'MARET', 'APRIL', 'MEI', 'JUNI', 'JULI', 'AGUSTUS', 'SEPTEMBER', 'OKTOBER', 'NOVEMBER', 'DESEMBER']
def getFilePathSelection():
    """ Directory selector dialog """
    selection = acm.FFileSelection()
    selection.PickDirectory(True)
    selection.SelectedDirectory = r"C:"
    return selection
def int_to_dot_precision(number):
    value = '{:,}'.format(number).replace(',', '.')
    return value
    
def list_dot_precision_to_int(list):
    new_list = [int(str(x).replace('.', '')) for x in list]
    return new_list
    
def get_list_trade(year, month, column, currency):
    startmonth = str(month).zfill(2)
    endmonth = str(month + 1).zfill(2) if startmonth != '12' else '01'
    startyear = year
    endyear = (1 + year) if startmonth == '12' else year
    query = """
    select t.trdnbr, position(t) 'Position', time_to_day(t.time) 'Time', t.status, i.insid 'Currency', c3.entry 'ProductType'
    from trade t, choicelist c3, instrument i
    where (t.optkey3_chlnbr=c3.seqnbr) and (t.curr=i.insaddr)
    and (t.status = 'FO Confirmed')
    and (i.insid = '{curr}')
    and t.time between '{start_year}-{start_month}-01' and '{end_year}-{end_month}-01'
    and
    """.format(
        curr=currency,
        start_year=str(startyear),
        end_year=str(endyear),
        start_month=startmonth, 
        end_month=endmonth
    )
    if column == 'FX':
        query += "(c3.entry = 'FX')"
    elif column == 'MM':
        query += "(c3.entry = 'DL')"
    elif column == 'BONDS':
        query += "(c3.entry = 'BOND')"
    elif column == 'REPO':
        query += "((c3.entry = 'REPO') or (c3.entry = 'REVREPO'))"
    elif column == 'DERIVATIF':
        query += "(c3.entry = 'SWAP')"
        
    result = ael.asql(query)[1][0]
    list_trade = [x[0] for x in result]
    list_position = [int(round_half_up(x[1])) for x in result]
    return list_trade, list_position
    
ael_gui_parameters={'runButtonLabel':'&&Run',
                'hideExtraControls': True,
                'windowCaption':'BO54 - Monthly Report'}
ael_variables=[
['report_name','Report Name','string', None, 'Monthly Report', 1,0],
['year','Year','int', [i for i in range(1970, current_year + 1)], current_year, 1,0],
['from_month','From (Start Month)','string', [c.capitalize() for c in list_month], 'Januari', 1,0],
['to_month','To (End Month)','string', [c.capitalize() for c in list_month], 'Desember', 1,0],
['filter_currency','Currency','string', acm.FCurrency.Select(''), 'IDR', 1, 0, "Select to Filter the Currency", None, 0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf', 0, 1, 'Select Secondary Extensions Output'],
]
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    year = parameter['year']
    from_month = parameter['from_month']
    to_month = parameter['to_month']
    filter_currency = parameter['filter_currency']
    output_file = parameter['output_file']
    month_dict = {}
    for i, item in enumerate([c.capitalize() for c in list_month]):
        month_dict[item] = i + 1
        
    if month_dict[from_month] > month_dict[to_month]:
        raise ValueError("End Month must be later than Start Month")
    else:
        columns = ['YEAR', 'MONTH', 'FREQUENCY', 'VOLUME']
        sub_columns = ['REPLENISHMENT', 'FX', 'MM', 'BONDS', 'REPO', 'DERIVATIF']
        mod_subcols = sub_columns[1:]; mod_subcols.append(sub_columns[0])
        
        rows = [[x+'-F' if i < len(sub_columns) else x+'-V' for i, x in enumerate(sub_columns*2)]]
        list_freq, list_volume, reple_freq, reple_volume = [], [], [], []
        # MONTH ITERATION
        for i in range(month_dict[from_month], month_dict[to_month] + 2):
            temp_freq, temp_volume = [], []
            if i < month_dict[to_month] + 1: #Monthly Part
                month = list_month[i-1]
                if i == month_dict[from_month]:
                    rows.append([' '+str(year), month])
                else:
                    rows.append([month])
                
                # FREQUENCY AND VOLUME PART
                for type in ('FREQUENCY', 'VOLUME'):
                    if type == 'FREQUENCY':
                        # Replenishment and Each Column
                        for subcol in mod_subcols:
                            if subcol != 'REPLENISHMENT':
                                value = len(get_list_trade(year, i, subcol, filter_currency)[0])
                                temp_freq.append(int_to_dot_precision(value))
                            else:
                                value = sum(list_dot_precision_to_int(temp_freq))
                                reple_freq.append(int_to_dot_precision(value))
                        list_freq.append(temp_freq)
                    else:
                        for subcol in mod_subcols:
                            if subcol != 'REPLENISHMENT':
                                value = sum(get_list_trade(year, i, subcol, filter_currency)[1])
                                temp_volume.append(int_to_dot_precision(value))
                            else:
                                value = sum(list_dot_precision_to_int(temp_volume))
                                reple_volume.append(int_to_dot_precision(value))
                        list_volume.append(temp_volume)
                        
            else: # Yearly Total Part
                month = '{} Total'.format(str(year))
                rows.append([month])
                
                # FREQUENCY AND VOLUME PART
                for type in ('FREQUENCY', 'VOLUME'):
                    if type == 'FREQUENCY':
                        for i, subcol in enumerate(mod_subcols):
                            if subcol != 'REPLENISHMENT':
                                value_col = [x[i] for x in list_freq]
                                value = sum(list_dot_precision_to_int(value_col))
                                temp_freq.append(int_to_dot_precision(value))
                            else:
                                total_reple = sum(list_dot_precision_to_int(reple_freq))
                                reple_freq.append(int_to_dot_precision(total_reple))
                        list_freq.append(temp_freq)
                    else:
                        for i, subcol in enumerate(mod_subcols):
                            if subcol != 'REPLENISHMENT':
                                value_col = [x[i] for x in list_volume]
                                value = sum(list_dot_precision_to_int(value_col))
                                temp_volume.append(int_to_dot_precision(value))
                            else:
                                total_reple = sum(list_dot_precision_to_int(reple_volume))
                                reple_volume.append(int_to_dot_precision(total_reple))
                        list_volume.append(temp_volume)
        data = [reple_freq, list_freq, reple_volume, list_volume]
        i = 1        
        for k in range(month_dict[from_month], month_dict[to_month] + 2):
            rows[i].append(data[0][i-1]) #reple_freq
            rows[i].extend(data[1][i-1]) #list_freq
            rows[i].append(data[2][i-1]) #reple_volume
            rows[i].extend(data[3][i-1]) #list_volume
            i += 1
            
        current_hour = get_current_hour("")
        current_date = get_current_date("")
        report_name = report_name + " - " + filter_currency
        
        table_html = create_html_table(columns, rows)
        table_xsl_fo = create_xsl_fo_table(columns, rows)
        
        len_month = 1 + month_dict[to_month] - month_dict[from_month]
        table_html = table_html.replace('<th>YEAR</th>', '<th rowspan="'+'2'+'" style="background-color:#5A9BD5;font-weight:bold">YEAR</th>')
        table_html = table_html.replace('<th>MONTH</th>', '<th rowspan="'+'2'+'" style="background-color:#5A9BD5;font-weight:bold">MONTH</th>')
        table_html = table_html.replace('<th>FREQUENCY</th>', '<th colspan="'+str(len(sub_columns))+'" style="background-color:#5A9BD5;font-weight:bold">FREQUENCY</th>')
        table_html = table_html.replace('<th>VOLUME</th>', '<th colspan="'+str(len(sub_columns))+'" style="background-color:#F895D5;font-weight:bold">VOLUME</th>')
        table_html = table_html.replace('<td> {}</td>'.format(str(year)), '<td rowspan="{}" style="background-color:#DDEBF6;font-weight:bold"> {}</td>'.format(str(len_month), str(year)))
        
        # Replace HTML Text
        for subcol in sub_columns:
            table_html = table_html.replace('<td>{}</td>'.format(subcol+'-F'), '<td style="background-color:#5A9BD5;font-weight:bold">{}</td>'.format(subcol))
            table_html = table_html.replace('<td>{}</td>'.format(subcol+'-V'), '<td style="background-color:#F895D5;font-weight:bold">{}</td>'.format(subcol))
        for row in rows:
            row_data = [str(r) for r in row[1:]] if row[1] == from_month.upper() else row
            text = '<td>'+'</td><td>'.join(row_data)
            split_text = text.split('<td>')
            if 'Total' not in row[0]:
                final_text = '<td style="background-color:#FFFFFF;font-weight:bold">' + '<td style="background-color:#FFFFFF;font-weight:normal">'.join(split_text[1:])
                table_html = table_html.replace(text, final_text)
            else:
                final_text = '<td colspan="2" style="background-color:#BDD7EE;font-weight:bold">' + '<td style="background-color:#BDD7EE;font-weight:bold">'.join(split_text[1:])
                table_html = table_html.replace(text, final_text)
        
        # Replace fo-table Text
        table_xsl_fo = table_xsl_fo.replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" page-height="420mm" page-width="594mm" margin="0.5in">')
        table_xsl_fo = table_xsl_fo.replace(
        '''
    <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>YEAR</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>MONTH</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>FREQUENCY</fo:block></fo:table-cell>
        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>VOLUME</fo:block></fo:table-cell>
        </fo:table-header>
    <fo:table-body>
    <fo:table-row>
        <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>REPLENISHMENT-F</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>FX-F</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>MM-F</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>BONDS-F</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>REPO-F</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>DERIVATIF-F</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>REPLENISHMENT-V</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>FX-V</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>MM-V</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>BONDS-V</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>REPO-V</fo:block></fo:table-cell>
            <fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>DERIVATIF-V</fo:block></fo:table-cell>
            </fo:table-row>
        ''',
        '''
            <fo:table-row>
                <fo:table-cell padding="8pt" border-width="1px" border-style="solid" font-weight="bold" background-color="#5A9BD5" number-columns-spanned="1" number-rows-spanned="2"><fo:block>YEAR</fo:block></fo:table-cell>
                <fo:table-cell padding="8pt" border-width="1px" border-style="solid" font-weight="bold" background-color="#5A9BD5" number-columns-spanned="1" number-rows-spanned="2"><fo:block>MONTH</fo:block></fo:table-cell>
                <fo:table-cell padding="8pt" border-width="1px" border-style="solid" font-weight="bold" background-color="#5A9BD5" number-columns-spanned="6"><fo:block>FREQUENCY</fo:block></fo:table-cell>
                <fo:table-cell padding="8pt" border-width="1px" border-style="solid" font-weight="bold" background-color="#F895D5" number-columns-spanned="6"><fo:block>VOLUME</fo:block></fo:table-cell>
            </fo:table-row>
            <fo:table-row>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#5A9BD5"><fo:block>REPLENISHMENT</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#5A9BD5"><fo:block>FX</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#5A9BD5"><fo:block>MM</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#5A9BD5"><fo:block>BONDS</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#5A9BD5"><fo:block>REPO</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#5A9BD5"><fo:block>DERIVATIF</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#F895D5"><fo:block>REPLENISHMENT</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#F895D5"><fo:block>FX</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#F895D5"><fo:block>MM</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#F895D5"><fo:block>BONDS</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#F895D5"><fo:block>REPO</fo:block></fo:table-cell>
                <fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#F895D5"><fo:block>DERIVATIF</fo:block></fo:table-cell>
            </fo:table-row>
        </fo:table-header>
        <fo:table-body>
        '''
        )
        
        # Generate HTML and FO file
        html_file = create_html_file(report_name + " " + current_date + current_hour, file_path, [table_html], report_name, current_date)
        xsl_fo_file = create_xsl_fo_file(report_name + " " + current_date + current_hour, file_path, [table_xsl_fo], report_name, current_date)
        
        f = open(xsl_fo_file, "r")
        contents = f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="420mm" page-width="594mm">')
        contents = contents.replace(
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block> {}</fo:block></fo:table-cell>'.format(str(year)),
        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" background-color="#DDEBF6" number-columns-spanned="1" number-rows-spanned="{}"><fo:block> {}</fo:block></fo:table-cell>'.format(str(len_month), str(year))
        )
        for row in rows:
            row_data = [str(r) for r in row[1:]] if row[1] == list_month[0] else row
            conn_str = '<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'
            new_conn_str = '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="normal" background-color="#FFFFFF"><fo:block>'
            if 'Total' not in row[0]:
                old_string = conn_str+('</fo:block></fo:table-cell>\n            '+conn_str).join(row_data)
                new_string = new_conn_str.replace('font-weight="normal"', 'font-weight="bold"')+('</fo:block></fo:table-cell>\n            '+new_conn_str).join(row_data)
                contents = contents.replace(old_string, new_string)
            else:
                new_conn_str = new_conn_str.replace('font-weight="normal" background-color="#FFFFFF"', 'font-weight="bold" background-color="#BDD7EE"')
                old_string = conn_str+('</fo:block></fo:table-cell>\n            '+conn_str).join(row_data)
                new_string = new_conn_str.replace('><fo:block>', ' number-columns-spanned="2" number-rows-spanned="1"><fo:block>')+('</fo:block></fo:table-cell>\n            '+new_conn_str).join(row_data)
                contents = contents.replace(old_string, new_string)
                
        f = open(xsl_fo_file, "w")
        f.write(contents)
        f.close()
        
        for i in output_file:
            if i != '.pdf' :
                generate_file_for_other_extension(html_file, i)
            else:
                generate_pdf_from_fo_file(xsl_fo_file)
        
        try:
            os.remove(xsl_fo_file)
        except:
            pass
