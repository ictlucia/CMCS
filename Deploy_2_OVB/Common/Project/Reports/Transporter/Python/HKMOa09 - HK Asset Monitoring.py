from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import test_new_html as html_gen
import acm, ael


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'HKMOa09 - HK Asset Monitoring'}



ael_variables=[
['report_name','Report Name','string', None, 'HKMOa09 - HK Asset Monitoring', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output']
]




def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    title_style = """
        .title {
            color: black;
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
    html_content = html_gen.create_base_html_content("Hong Kong Assets - "+current_date, title_style)
    title = ['Date','Nostro USD+HKD','Placement','Sec','Total','Clean Dep','%']
    html_content = html_gen.prepare_html_table(html_content,title)
    
    for data in range(15):
        temp_row=[]
        for rows in title:
            temp_row.append(0)
        html_content = html_gen.add_data_row(html_content,[temp_row])
        
    html_content = html_gen.close_html_table(html_content)
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True, True)

    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)




