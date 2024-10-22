from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import test_new_html as html_gen
import acm, ael


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'DL09 - Daily Cashflow Report - PDN'}



ael_variables=[
['report_name','Report Name','string', None, 'DL09 - Daily Cashflow Report - PDN', 1,0],
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
    html_content = html_gen.create_base_html_content("NOP Report - "+current_date, title_style)
    
    title = ['DESKRIPSI SANDI','VALUTA','TOTAL NERACA','TOTAL ADM','POSISI NETTO','P/L']
    html_content = html_gen.prepare_html_table(html_content,title)
    
    currency = {
                "Australian Dollar":"AUD",
                "Brunei Dollar":"BND",
                "Canadian Dollar":"CAD",
                "Swiss Franc": "CHF",
                "Chinese Yuan": "CNY",
                "Danish Krone": "DKK",
                "Euro Currency": "EUR",
                "UK Pound Sterling":"GBP",
                "Hongkong Dollar":"HKD",
                "Japanese Yen":"JPY",
                "Malaysian Ringgit":"MYR",
                "Norwegian Krone":"NOK",
                "New Zealand Dollar":"NZD",
                "Saudi Arabian Riyal":"SAR",
                "Swedish Krone":"SEK",
                "Singapore Dollar":"SGD",
                "Thailand Baht":"THB",
                "US Dollar":"USD"
                }
                
    for keys,value in currency.items():
        temp_row = []
        temp_row.append(keys)
        temp_row.append(value)
        temp_row.append(0)
        temp_row.append(0)
        temp_row.append(0)
        temp_row.append(0)
        html_content = html_gen.add_data_row(html_content,[temp_row])
    
    non_idr_ccy = ['Total non-IDR ccy',0,0,0,0,0]
    idr_ccy = ['Indonesian Rupiah','IDR',0,0,0]
    bmhk_nop=[0,0,0,'BMHK NOP',0]
    html_content = html_gen.add_data_row(html_content,[non_idr_ccy],"style=font-weight:bold")
    html_content = html_gen.add_data_row(html_content,[idr_ccy])
    html_content = html_gen.add_data_row(html_content,[bmhk_nop],"style=font-weight:bold")
    
    
    for title_blue in title:
        html_content = html_content.replace("<th>"+title_blue+"</th>","<th style='background-color:blue;color:white'>"+title_blue+"</th>")
    
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True, True)

    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
