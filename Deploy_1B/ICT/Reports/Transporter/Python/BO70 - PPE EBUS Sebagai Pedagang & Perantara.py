import acm, ael
from datetime import date, datetime
import locale
import calendar
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

locale.setlocale(locale.LC_ALL, 'en_US')
xsl_gen = XSLFOGenerator()
#############################################################################################################################
def choose_header(name_header, isHeader1, inOriginalAmount):
    list_header_2d = [  
                ["Jenis Transaksi", "Lokasi Transaksi", name_header, "Total Transaksi"],
                ["SBN", "Obligasi Korporasi", "SBSN", "Sukuk", "EBUS lain", "Value (IDR)" if inOriginalAmount else "Value (IDR T)", "Freq"],
                ["Value (IDR)" if inOriginalAmount else "Value (IDR T)", "Freq"] * 5
    ] if isHeader1 == True else [
            ["Laporan Kegiatan Keagenan", "Jumlah Penjualan (IDR T)" if inOriginalAmount else "Jumlah Penjualan (IDR T)", "Jumlah Penjualan"],
            ["Individu", "Institusi", "Individu", "Institusi"]
    ]

    list_span_2d = [
                [[3, 1], [3, 1], [1, 10], [1, 2]],
                [[1, 2], [1, 2], [1, 2], [1, 2], [1, 2], [2, 1], [2, 1]],
                [[1, 1] for _ in range(12)],
    ] if isHeader1 == True else [
            [[2, 1], [1, 2], [1, 2]],
            [[1, 1] for _ in range(4)],
    ]
    
    return list_header_2d, list_span_2d

data_dict_1 = {
    'Transaksi Jual Beli Efek' : ["OTC Murni", "Bursa", "PPA"],
    'Transaksi Repurchase Agreement' : ["OTC Murni", "Bursa", "PPA"],
    'Transaksi Pinjam Meminjam Efek' : ["OTC Murni", "Bursa", "PPA"],
    'Transaksi EBUS lainnya' : ["OTC Murni", "Bursa", "PPA"]
}

data_dict_2 = [
    ['Sebagai Agen Penjual Obligasi Korporasi'],
    ['Sebagai Agen Penjual Sukuk'],
    ['Sebagai Agen Penjual EBUS Lain'],
]

#############################################################################################################################
def price_mtm(trade, curr_target='IDR'):

    prices = acm.FPrice.Select(f"instrument = '{trade.Instrument().Currency().Name()}' and market = 'EOD_MtM' and day= '{trade.TradeTimeDateOnly()}'")
    for p in prices:
        if p.Instrument():
            if p.Currency().Name() == curr_target:
                return p.Settle()

def weekdays_date():
    last_month = int(date.today().strftime("%m")) - 1
    
    date_bucket = []
    for i in range(1, 32):
        try :
            day = calendar.weekday(2024, last_month, i)
        except :
            break
        
        if day not in [5, 6]:
            date_full = datetime(2024, last_month, i)
            date_bucket.append(date_full.strftime("%d/%m/"))
    
    return "(" + ", ".join([f"'{x}'" for x in date_bucket]) + ")"

def get_val_query(inOriginalAmount, month_use):
    query = acm.FSQL['BO70 - PPE EBUS Sebagai Pedagang & Perantara'].Text().replace("{{monthUsed}}", month_use)
    pedagangList, perantaraList = ael.asql(query)[1]
    
    pedagangDict = {pedagangVal[1] : {} for pedagangVal in pedagangList}
    for pedagangVal in pedagangList:
        pedagangDict[pedagangVal[1]][pedagangVal[2]] = pedagangVal[3:] if inOriginalAmount else [x / 1000000000000 if i % 2 == 0 else x for i, x in enumerate(pedagangVal[3:])] 
    
    perantaraDict = {perantaraVal[1] : {} for perantaraVal in perantaraList}
    for perantaraVal in perantaraList:
        perantaraDict[perantaraVal[1]][perantaraVal[2]] = perantaraVal[3:] if inOriginalAmount else [x / 1000000000000 if i % 2 == 0 else x for i, x in enumerate(perantaraVal[3:])] 
    
    return pedagangDict, perantaraDict

#############################################################################################################################
## GENERATE EXCEL TEMPLATE
#############################################################################################################################

def open_code_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
    <table>
    """
    
def open_header(html_code, date, title, company = "PT Bank Mandiri (Persero) Tbk"):
    html_code += f"<tr><td style='font-weight : bold'>Nama Perusahaan</td><td style='font-weight : bold'>: {company}</td></tr>"
    html_code += "<tr><td>&nbsp;</td></tr>"
    html_code += f"<tr><td style='font-weight : bold'>Tanggal Pelaporan</td><td style='font-weight : bold'>: {date}</td></tr>"
    html_code += "<tr><td>&nbsp;</td></tr>"
    html_code += f"<tr><td style='font-weight : bold'>{title}</td></tr>"
    html_code += "<tr><td>&nbsp;</td></tr>"
    
    return html_code

def html_header(html_code, inOriginalAmount, isHeader1=True, name_header=None):
    list_header_2d, list_span_2d = choose_header(name_header, isHeader1, inOriginalAmount)
    color_bg = "#facdaf" if list_header_2d[0][0] == "Jenis Transaksi" else "yellow"

    for list_header, list_span in zip(list_header_2d, list_span_2d):
        html_code += "<tr>\n"
        for header, span in zip(list_header, list_span):
            html_code += f'<td rowspan="{span[0]}" colspan="{span[1]}" style="font-weight : bold; border : 1px black solid; background-color : {color_bg}; vertical-align: middle; text-align: center">{header}</td>\n'
        html_code += "</tr>\n"
    
    return html_code

def html_content_table(data_dict, html_code, data_list_2d, name_header, inOriginalAmount, isHeader1=True):
    html_code = html_header(html_code, inOriginalAmount, isHeader1, name_header)
    
    if type(data_dict) is not list :
        i = 0
        for key, val_list_2d in data_dict.items():
            html_code += f'<tr><td rowspan="3" style="vertical-align : middle; border : 1px black solid;">{key}</td>'
            for typeUse in val_list_2d: 
                try :
                    val_list = [typeUse] + [f"{float(x):,}" if i%2 == 0 else x for i, x in enumerate(data_list_2d[key][typeUse])]
                except :
                    val_list = [typeUse] + [0] * 12
                    
                i += 1
                
                html_code += "<tr>" if val_list[0] != "OTC Murni" else ""
                for ind, val in enumerate(val_list):
                    text_align = f"text-align: {'right' if ind != 0 else 'left'}"
                    html_code += f'<td style="border : 1px black solid; {text_align}">{f"{val}"}</td>'
                html_code += "</tr>"
    else :
        for val_list in data_dict:
            val_list.extend([0] * 4)
            html_code += "<tr>"
            for ind, val in enumerate(val_list):
                text_align = f"text-align: {'right' if ind != 0 else 'left'}"
                html_code += f'<td style="border : 1px black solid; {text_align}">{f"{val}"}</td>'
            html_code += "</tr>"
            
    return html_code 

def generate_excel(report_folder, report_name, amount_form, month_use):
    inOriginalAmount = True if amount_form == "Original Amount" else False
    
    pedagang_ebus, perantara_ebus = get_val_query(inOriginalAmount, month_use)
    
    html_code = open_code_html()
    
    today_date = date.today().strftime("%d %B %Y")
    title_1 = "1. Laporan Kegiatan PPE-EBUS Bulanan"
    html_code = open_header(html_code, today_date, title_1)
    
    html_code = html_content_table(data_dict_1, html_code, pedagang_ebus, "Sebagai Pedagang EBUS", inOriginalAmount)
    
    html_code += "<tr><td>&nbsp;</td></tr>" * 3
    html_code = html_content_table(data_dict_1, html_code, perantara_ebus, "Sebagai Perantara EBUS", inOriginalAmount)
    
    
    html_code += "<tr><td>&nbsp;</td></tr>" * 3
    title_2 = "2. Laporan Kegagalan Transaksi"
    html_code = open_header(html_code, today_date, title_2)
    html_code += "<tr><td>&nbsp;</td><td style='font-weight : bold'>NIHIL</td></tr>"
    
    html_code += "<tr><td>&nbsp;</td></tr>" * 3
    title_3 = "3. Laporan Kegiatan Keagenan"
    html_code = open_header(html_code, today_date, title_3)
    html_code = html_content_table(data_dict_2, html_code, pedagang_ebus, None, inOriginalAmount, False)
    
    file_path = os.path.join(report_folder, report_name)
    f = open(file_path, "w")
    f.write(html_code + "</table></body></html>")
    f.close()
    
#############################################################################################################################
## GENERATE PDF TEMPLATE
#############################################################################################################################

def open_header_xsl(xsl_fo_content, title):    
    open_header_dict = {
        "Nama Perusahaan" : ": PT Bank Mandiri (Persero) Tbk",
        "Tanggal Pelaporan" : ": " + date.today().strftime("%d %B %Y"),
    }
    
    for key, val in open_header_dict.items():
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "&#xa0;","", 'text-align="left"')
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
        
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, key,"", 'text-align="left"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, val,'number-columns-spanned="4"', 'text-align="left"')
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "&#xa0;","", 'text-align="left"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, title, 'number-columns-spanned="2"', 'text-align="left"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    return xsl_fo_content

def fo_header(xsl_fo_content, isHeader1=True, name_header=None):
    list_header_2d, list_span_2d = choose_header(name_header, isHeader1)
    color_bg = "#facdaf" if list_header_2d[0][0] == "Jenis Transaksi" else "yellow"
    border_style = 'border-bottom-style="solid" border-bottom-width="1px" border-start-style="solid" border-start-width="1px" border-before-style="solid" border-before-width="1px"'
    border_style_left = ' border-left-style="solid" border-left-width="1px"'

    for list_header, list_span in zip(list_header_2d, list_span_2d):
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content, border_style+border_style_left + f' background-color="{color_bg}"')
        
        for header, span in zip(list_header, list_span):
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, header, f'number-rows-spanned="{span[0]}" number-columns-spanned="{span[1]}"', border_style_left)
        
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    return xsl_fo_content

def fo_content_table(data_dict, xsl_fo_content, data_list_2d): 
    border_style = 'border-bottom-style="solid" border-bottom-width="1px" border-start-style="solid" border-start-width="1px" border-before-style="solid" border-before-width="1px"'
    border_style_left = ' border-left-style="solid" border-left-width="1px"'
    
    if type(data_dict) is not list :
        i = 0
        for key, val_list_2d in data_dict.items():
            xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content, border_style) + "\n"
            xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, key, f'number-rows-spanned="3"', f'{border_style_left}') + "\n"
            
            for val_list in val_list_2d:
                val_list = val_list + [f"{float(x):.2f}" if i%2 == 0 else x for i, x in enumerate(data_list_2d[i])]
                i += 1
                
                xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content, border_style_left) if val_list[0] != "OTC Murni" else xsl_fo_content + "\n"
                
                for ind, val in enumerate(val_list):
                    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, val, '', border_style + border_style_left) + "\n"
                    
                xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content) + "\n"
    else :
        for val_list in data_dict:
            val_list.extend(["0"] * 4)
            xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content) + "\n"
            
            for ind, val in enumerate(val_list):
                xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, val, '', f'{border_style}') + "\n"
                
            xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content) + "\n"
            
    return xsl_fo_content 
        
def generate_pdf(report_name, file_path, current_date):
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("")
    
    #Preparing Title
    xsl_fo_content += f"""
        <fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
            {'<fo:table-column column-width="100mm"/>' * 2}
            {'<fo:table-column column-width="25mm"/>' * 12}
        <fo:table-body>
    """
    
    xsl_fo_content = open_header_xsl(xsl_fo_content, "1. Laporan Kegiatan PPE-EBUS Bulanan")
    
    xsl_fo_content = fo_header(xsl_fo_content, isHeader1=True, name_header="Sebagai Pedagang EBUS")
    xsl_fo_content = fo_content_table(data_dict_1, xsl_fo_content, pedagang_ebus)
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "&#xa0;","", 'text-align="left"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    xsl_fo_content = fo_header(xsl_fo_content, isHeader1=True, name_header="Sebagai Perantara EBUS")
    xsl_fo_content = fo_content_table(data_dict_1, xsl_fo_content, perantara_ebus)
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "&#xa0;","", 'text-align="left"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    xsl_fo_content = open_header_xsl(xsl_fo_content, "2. Laporan Kegagalan Transaksi")
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "&#xa0;","", 'text-align="left"')
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "NIHIL","", 'text-align="left"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, "&#xa0;","", 'text-align="left"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    
    #Preparing Title
    xsl_fo_content += f"""
        <fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
            {'<fo:table-column column-width="100mm"/>' * 1}
            {'<fo:table-column column-width="25mm"/>' * 4}
        <fo:table-body>
    """
    
    xsl_fo_content = open_header_xsl(xsl_fo_content, "3. Laporan Kegiatan Keagenan")
    
    xsl_fo_content = fo_header(xsl_fo_content, isHeader1=False, name_header="Sebagai Pedagang EBUS")
    xsl_fo_content = fo_content_table(data_dict_2, xsl_fo_content, pedagang_ebus)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name, file_path, xsl_fo_content, current_date)
    
    generate_pdf_from_fo_file(xsl_fo_file)
    
    
#############################################################################################################################
## GENERATE REPORT
#############################################################################################################################

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BO70 - PPE EBUS Sebagai Pedagang & Perantara'}

year_list = [str(datetime.now().year - x) for x in range(25)]
list_month = list(calendar.month_name)
month_now = list_month[datetime.now().month]

ael_variables=[
['report_name','Report Name','string', None, 'BO70 - PPE EBUS Sebagai Pedagang & Perantara', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Output Files','string', ['.xls'], '.xls', 0 , 0, 'Select Output Extension Type'],
['amount_form','Amount Form','string', ['Original Amount', 'In Trilion'], 'Original Amount', 0 , 0, 'Select Amount Form'],
['report_month','Report Month','string', list_month[1:], month_now, 0 , 0, 'Select Amount Form'],
['report_year','Report Year','string', year_list, str(datetime.now().year), 0 , 0, 'Select Amount Form']
]

def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = "".join(parameter['output_file'])
    amount_form = "".join(parameter['amount_form'])
    report_month = "".join(parameter['report_month'])
    report_year = "".join(parameter['report_year'])
    
    folder_name = "report"+date.today().strftime("%Y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    if ".xls" in output_file:
        generate_excel(report_folder, report_name + ".xls", amount_form, f"{report_month} {report_year}")
    elif ".pdf" :
        generate_pdf(report_name, file_path, date.today().strftime("%Y%m%d"))
