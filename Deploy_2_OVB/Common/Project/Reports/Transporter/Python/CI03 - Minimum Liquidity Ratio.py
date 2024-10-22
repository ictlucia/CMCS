from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import test_new_html as html_gen
import acm, ael


ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'CI03 - Minimum Liquidity Ratio'}



ael_variables=[
['report_name','Report Name','string', None, 'CI03 - Minimum Liquidity Ratio', 1,0],
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


    current_date = get_current_date("-")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content("Minimum Liquidity Ratio (Monthly Report)", title_style)
    title = 'Reporting Period',current_date
    html_content = html_gen.prepare_html_table(html_content,title)
    html_content = html_content.replace("<table>","<table style='width:65%'>")
    
    for new_title in title:
        html_content = html_content.replace("<th>"+new_title+"</th>","<th style='text-align:left;border:0'>"+new_title+"</th>")
    
    list_asset_data = {
                'Currency notes':'A01',
                'Withdrawable central bank reserves':'A02',
                "Deposit balances with and Certificates of Deposit (CDs) issued by the bank's Group Bank - Parent, Branch, Subsidiary or Affiliate. (Available when a liquidity issue encountered and must have an explicit agrrement with its Group Bank that is approved by Authority.)":"A03",
                'Any Debt Securities assigned a 0% risk weight representing claims on or guaranteed by Sovereigns':'A04',
                'Central banks':'A05',
                'Publis Sector Entities (PSEs)':'A06',
                'Multilateral Development Banks (MDBs)':'A07',
                'Any Debt Securities assigned a 20% risk weight representing claims on or guaranteed by Sovereigns':'A08',
                'Central banks':'A09',
                'Public Sector Entities (PSEs)':'A10',
                'Multilateral Development Banks (MDBs)':'A11',
                'Any corporate debt security including commercial paper with a 20% risk rating - not issued by a financial institution or any of its affiliated entities':'A12',
                'Any covered bonds with a 20% risk rating - not issued by the bank itself or any of its affiliated entities':'A13'
                }
    html_content = html_gen.add_data_row(html_content,[['Total Liquid Assets','','']],'','style=font-weight:bold;text-align:left')

    
    for key,value in list_asset_data.items():
        temp_row=[]
        temp_row.append(key)
        temp_row.append(value)
        temp_row.append(0)
        html_content = html_gen.add_data_row(html_content,[temp_row],'','style="text-align:left;white-space:normal"')
    
    html_content = html_gen.add_data_row(html_content,[['B) Qualifying Liabilities','','']],'','style=font-weight:bold;text-align:left')
    html_content = html_gen.add_data_row(html_content,[['All liabilities of the bank, excluding any contigent liabilities','','']],'','style=text-align:left')
    
    list_liabilities_data = {
                            'Due to non-bank customers (gross basis)':'B01',
                            'Due to other banks (Net basis) maturing within one month from MLR computation day':'B02',
                            '15% of all undrawn commitments':'B03'
                            }
                            
    for key,value in list_liabilities_data.items():
        temp_row=[]
        temp_row.append(key)
        temp_row.append(value)
        temp_row.append(0)
        html_content = html_gen.add_data_row(html_content,[temp_row],'','style="text-align:left;white-space:normal"')
    
    html_content = html_gen.add_data_row(html_content,[['Total Qualifying Liabilites','','']],'','style=font-weight:bold;text-align:left')
    html_content = html_gen.add_data_row(html_content,[['C) Minimum Liquidity Ratio','','']],'','style=font-weight:bold;text-align:left')
    
    list_liquidity_data = {
                            'Total Liquid Assets':'C01',
                            'Total Qualifying Liabilities':'C02'
                            }
    
    for key,value in list_liquidity_data.items():
        temp_row = []
        temp_row.append(key)
        temp_row.append(value)
        temp_row.append(0)
        html_content = html_gen.add_data_row(html_content,[temp_row],'','style="text-align:left;white-space:normal"')
    
    html_content = html_gen.add_data_row(html_content,[['Minimum Liquidity Ratio - minimum required is 15%','','']],'','style=font-weight:bold;text-align:left')

    
    
    html_content = html_gen.close_html_table(html_content)
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True, True)

    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
