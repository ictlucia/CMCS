import acm, ael, random

from datetime import datetime

from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

from BookRateInquiry import getBookRate

today = acm.Time.DateToday()
today_dt = datetime.strptime(today, "%Y-%m-%d")
formatted_today = today_dt.strftime("%d/%m/%Y")
    

ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'BO39 - Laporan Penginputan NTR Akhir Hari'}

                    

ael_variables=[

['report_name','Report Name','string', None, 'BO39 - Laporan Penginputan NTR Akhir Hari', 1,0],

['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

['output_file','Secondary Output Files','string', ['.xls', '.pdf'], '.xls', 0, 1, 'Select Secondary Extensions Output'],

]



def ael_main(parameter):

    report_name = parameter['report_name']

    file_path = str(parameter['file_path'])

    output_file = parameter['output_file']
    
    current_date = get_current_date("")
    
    html_gen = HTMLGenerator()
    
    xsl_gen = XSLFOGenerator()
    
    title_style = """
        .title {
            color: black;
            text-align: left;   
        }
        
    """
    curr = acm.FCurrency.Select('')
    
    html_content = html_gen.create_base_html_content("BO39 - Laporan Penginputan NTR Akhir Hari", title_style)
    
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("BO39 - Laporan Penginputan NTR Akhir Hari")
    
    title_list = ['Market Data Source', 'FA', 'eMAS', 'RECONCILIATION RESULT']
    
    subtitle = ['KODE', 'MATA UANG', 'KURS BELI', 'KURS JUAL', 'KURS TENGAH','CCY', 'NTR', 'DELTA', 'UPDATE', 'CCY', 'RATE', 'COLUMN1', 'CCY', 'FA', 'DIFF', 'EMAS', 'DIFF']
    
    html_content +="<div><table>"
    xsl_fo_content +="""<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto"><fo:table-body>"""
    
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content) 
    
    span = [5,4,3,5]
    
    html_content = html_gen.open_table_row(html_content)
    for i, title in enumerate(title_list):
        html_content = html_gen.add_cell_data(html_content, title, f'colspan={span[i]}')
        xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[title[i]],"number-columns-spanned='"+str(span[i])+"'")
    html_content = html_gen.close_table_row(html_content)
        
        
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    html_content = html_gen.add_data_row(html_content,[subtitle])
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[subtitle])
    

    ccys = [i.Name() for i in acm.FCurrency.Select('')]
    
    ccys.sort()

    columns = ['Market Data Source', 'FA', 'eMAS', 'RECONCILIATION RESULT']

    

    sub_columns = ['KODE', 'MATA UANG', 'KURS BELI', 'KURS JUAL', 'KURS TENGAH','CCY', 'NTR', 'DELTA', 'UPDATE', 'CCY', 'RATE', 'COLUMN1', 'CCY', 'FA', 'DIFF', 'EMAS', 'DIFF']

    

    market_col = sub_columns[:5]

    fa_col = sub_columns[5:9]

    emas_col = sub_columns[9:12]

    recon_col = sub_columns[12:]

    rows = [sub_columns]

    for ccy in ccys:

        kode = acm.FCurrency[ccy].Oid()

        temp_row = [kode, ccy]
        
        """
        price_list_source = acm.FPrice.Select(f"instrument='{ccy}' and currency='IDR' and market='REFINITIV_SPOT' and day = YESTERDAY")
        
        if len(price_list_source) > 0 :
            price_source = price_list_source.Last()
            
            bid_source = price_source.Bid() if str(price_source.Bid()) != "nan" else 0

            ask_source = price_source.Ask() if str(price_source.Ask()) != "nan" else 0
        
            ntr_source = price_source.Settle() if str(price_source.Settle()) != "nan" else 0

            #ntr_source = round( (bid + ask) / 2, 5)
            
        else :
            
            bid_source, ask_source, ntr_source = [0, 0, 0]
        """
        
        
        
        price_list_fa = acm.FPrice.Select(f"instrument='{ccy}' and currency='IDR' and market='EOD_MtM' and day = TODAY")
        
        if len(price_list_fa) > 0 :
        
            price_fa = price_list_fa.Last()
            
            bid_fa = price_fa.Bid() if price_fa.Bid() else 0

            ask_fa = price_fa.Ask() if price_fa.Ask() else 0
        
            ntr_fa = price_fa.Settle() if price_fa.Settle() else 0
            
            price_list_fa_yesterday = acm.FPrice.Select(f"instrument='{ccy}' and currency='IDR' and market='EOD_MtM' and day = YESTERDAY")
            
            if len(price_list_fa_yesterday) > 0 :
                
                price_fa_ytd = price_list_fa_yesterday.Last()
                
                ntr_fa_yesterday = price_fa_ytd.Settle() if price_fa_ytd.Settle() else 0
            
                delta_fa = ntr_fa - ntr_fa_yesterday

            update_fa = price_fa.Day()
            
        else :
            
            ntr_fa, delta_fa, update_fa = [0, 0, "-"]
        
        try :
        
            bid_emas = float(getBookRate(ccy)[-1]['minimumRate'])
        
            ask_emas = float(getBookRate(ccy)[-1]['maximumRate'])
        
            ntr_emas = (bid_emas + ask_emas)/2
        
        except :
            
            ntr_emas = 0

                
        diff_fa_emas = abs( ntr_fa - ntr_emas )
        

        temp_row.extend(["", "", "", ccy, ntr_fa, delta_fa, update_fa, ccy, ntr_emas, "", ccy, "", "", "", diff_fa_emas])

        rows.append(temp_row)

        

    current_hour = get_current_hour("")
    current_date = get_current_date("")
    #print(rows)
    
    table_html = create_html_table(columns, rows)
    table_xsl_fo = create_xsl_fo_table(columns, rows)
    
    for col in columns:
        if col.lower() == 'market data source':
            table_html = table_html.replace('<th>{}</th>'.format(col), '<th colspan={} style="background-color:#FFFFFF;font-weight:bold">{}</th>'.format(len(market_col), col))
            table_xsl_fo = table_xsl_fo.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{col}</fo:block></fo:table-cell>',
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-columns-spanned="{len(market_col)}"><fo:block>{col}</fo:block></fo:table-cell>')
        elif col.lower() == 'fa':
            table_html = table_html.replace('<th>{}</th>'.format(col), '<th colspan={} style="background-color:#FFFFFF;font-weight:bold">{}</th>'.format(len(fa_col), col))
            table_xsl_fo = table_xsl_fo.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{col}</fo:block></fo:table-cell>',
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-columns-spanned="{len(fa_col)}"><fo:block>{col}</fo:block></fo:table-cell>')
        elif col.lower() == 'emas':
            table_html = table_html.replace('<th>{}</th>'.format(col), '<th colspan={} style="background-color:#FFFFFF;font-weight:bold">{}</th>'.format(len(emas_col), col))
            table_xsl_fo = table_xsl_fo.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{col}</fo:block></fo:table-cell>',
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-columns-spanned="{len(emas_col)}"><fo:block>{col}</fo:block></fo:table-cell>')
        else:
            table_html = table_html.replace('<th>{}</th>'.format(col), '<th colspan={} style="background-color:#FFFFFF;font-weight:bold">{}</th>'.format(len(recon_col), col))
            table_xsl_fo = table_xsl_fo.replace(f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>{col}</fo:block></fo:table-cell>',
            f'<fo:table-cell padding="8pt" border-width="1px" border-style="solid" text-align="center" number-columns-spanned="{len(recon_col)}"><fo:block>{col}</fo:block></fo:table-cell>')
            
    for ccy in ccys:
        table_html = table_html.replace('<td>{}</td>'.format(ccy), '<td style="background-color:#FFFFFF;font-weight:bold">{}</td>'.format(ccy))
    for k in set(rows[0]):
        table_html = table_html.replace('<td>{}</td>'.format(k), '<td style="background-color:#FFFFFF;font-weight:bold">{}</td>'.format(k))

    table_html = table_html.replace('&', '&amp;')
    table_html = table_html.replace('%', '&#37;')
    
    table_xsl_fo = table_xsl_fo.replace('&', '&amp;')
    table_xsl_fo = table_xsl_fo.replace('%', '&#37;')
        
    html_file = create_html_file(report_name + " " + current_date + current_hour, file_path, [table_html], report_name, current_date)
    
    xsl_fo_file = create_xsl_fo_file(report_name + " " +current_date+current_hour, file_path, [table_xsl_fo], report_name, current_date)

    xsl_f = open(xsl_fo_file, "r")

    xsl_contents = xsl_f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">')
    xsl_contents = xsl_contents.replace('<fo:block font-weight="bold" font-size="30px" margin-bottom="30px">'+report_name+'</fo:block>',
    '<fo:block font-weight="bold" font-size="30px" margin-bottom="30px" text-align="center">'+report_name+'</fo:block>')
    xsl_contents = xsl_contents.replace('</fo:table-header>', '</fo:table-row>')
    xsl_contents = xsl_contents.replace('<fo:table-body>', '')
    xsl_contents = xsl_contents.replace('<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">', 
    '<fo:table-body>\n\t<fo:table-row font-weight="bold">')
    xsl_f = open(xsl_fo_file, "w")
    xsl_f.write(xsl_contents)
    xsl_f.close()

    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
    '''
    '''
    try:
        os.remove(xsl_fo_file)
    except:
        pass
    

