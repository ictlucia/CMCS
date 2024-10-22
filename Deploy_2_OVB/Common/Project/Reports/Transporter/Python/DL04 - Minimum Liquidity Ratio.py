from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import test_new_html as html_gen
import acm, ael


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'DL04 - Minimum Liquidity Ratio'}



ael_variables=[
['report_name','Report Name','string', None, 'DL04 - Minimum Liquidity Ratio', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output']
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

    current_date = get_current_date("/")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content("Minimum Liquidity Ratio - "+current_date, title_style)
    title = 'Central Bank Requirement : Liquidity Ratio'
    html_content = html_gen.prepare_html_table(html_content,[title])
    html_content = html_content.replace('<th>'+title+"</th>","<th colspan=3 style='background-color:#324175;color:white;'>"+title+"</th>")
    subtitle = ['No','Items','Amount']
    
    html_content = html_gen.add_data_row(html_content,[subtitle],'style=background-color:#a0c5de;')
    
    list_value = [
                'Vault Cash',
                'Precious Metals (Gold)',
                'Deposits with BCTL',
                'Deposits in Other Financial Institution',
                'Readily Marketable Securities',
                'Net Interbank Lending & Borrowing w/remaining mat up to 1 mo'
                ]
    
    for count in range(len(list_value)):
        temp_row =[]
        temp_row.append(count+1)
        temp_row.append(list_value[count])
        temp_row.append(0)
        html_content = html_gen.add_data_row(html_content,[temp_row],'','style=text-align:left;')

    for new_value in list_value:
       html_content = html_content.replace("<td>"+new_value+"</td>","<td style=text-align:left>"+new_value+"</td>")
    
    list_total = [
                'Total Highly Liquid Asset',
                'Total Liabilities (DPK)',
                'LIQUIDITY RATIO (Min. 15%)'
                ]
                
    for items in list_total:
        temp_row = []
        temp_row.append('')
        temp_row.append(items)
        temp_row.append(0)
        html_content = html_gen.add_data_row(html_content,[temp_row],'style = "background-color:#7bdb91;border-color:#7bdb91;"')
    
    
    html_content = html_gen.close_html_table(html_content)
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True, True)

    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)



