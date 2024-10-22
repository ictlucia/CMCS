import acm, ael
from datetime import date, datetime
import locale
import calendar
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

locale.setlocale(locale.LC_ALL, 'en_US')
xsl_gen = XSLFOGenerator()
#############################################################################################################################
def choose_header(name_header, isHeader1):
    list_header_2d = [
                ["Jenis Transaksi", "Lokasi Transaksi", name_header, "Total Transaksi"],
                ["SBN", "Obligasi Korporasi", "SBSN", "Sukuk", "EBUS lain", "Value (IDR T)", "Freq"],
                ["Value (IDR T)", "Freq"] * 5
    ] if isHeader1 == True else [
            ["Laporan Kegiatan Keagenan", "Jumlah Penjualan (IDR T)", "Jumlah Penjualan"],
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
    'Transaksi Jual Beli Efek' : [["OTC Murni"], ["Bursa"], ["PPA"]],
    'Transaksi Repurchase Agreement' : [["OTC Murni"], ["Bursa"], ["PPA"]],
    'Transaksi Pinjam Meminjam Efek' : [["OTC Murni"], ["Bursa"], ["PPA"]],
    'Transaksi EBUS lainnya' : [["OTC Murni"], ["Bursa"], ["PPA"]]
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

def get_val_query(date_bucket, category, type="'BOND'", partyType="Counterparty"):
    query = f"""
    SELECT 
        trdnbr
    FROM 
        Trade t
    WHERE 
        status = 'BO-BO Confirmed' AND
        Display_id(t, 'optkey3_chlnbr') = {type} AND
        Display_id(t, 'optkey4_chlnbr') IN {category}
        AND value_day IN {date_bucket}
    """
    
    try :
        result = [trdnbr[0] for trdnbr in ael.asql(query)[1][0]]
    except :
        print(query)
    
    nominal, freq = 0, 0
    for trdnbr in result:
        print(trdnbr)
        trade = acm.FTrade[trdnbr]
        Tradeinstype = trade.Instrument().InsType()
        TradepartyType = trade.Counterparty().Type()
        
        if TradepartyType == partyType:
            idr_rate = price_mtm(trade, curr_target='IDR') if price_mtm(trade, curr_target='IDR') != None else 15000
            
            val_cal = trade.Nominal() if type == "'BOND'" else trade.Nominal() * trade.Instrument().ContractSize()
            
            nominal += (abs(float(val_cal)) * idr_rate) / 1000000000000 if trade.Instrument().Currency().Name() != "IDR" else val_cal / 10 ** 12
            print(val_cal, nominal)
            freq += 1
    
    return [f"{float(abs(nominal))}", freq]

sbn = get_val_query(weekdays_date(), "('FR', 'ORI', 'SPN', 'INDON')")
obkor = get_val_query(weekdays_date(), "('KONVEN')")
sbsn = get_val_query(weekdays_date(), "('PBS', 'SR', 'SPNS', 'INDOIS')")
sukuk = get_val_query(weekdays_date(), "('SYARIAH')")
other = get_val_query(weekdays_date(), "('SBKMTN')")
all_data = [sbn, obkor, sbsn, sukuk, other]
total = [sum([float(x[0]) for x in all_data]), sum([x[1] for x in all_data])]

sbn_repo = get_val_query(weekdays_date(), "('BI')", "'REPO'", "Client")
pedagang_ebus = [sbn + obkor + sbsn + sukuk + other + total] + [[0] * 12 for _ in range(2)] + [sbn_repo + [0] * 8 + sbn_repo] + [[0] * 12 for _ in range(8)]

sbn = get_val_query(weekdays_date(), "('FR', 'ORI', 'SPN', 'INDON')", "'BOND'", "Client")
obkor = get_val_query(weekdays_date(), "('KONVEN')", "'BOND'", "Client")
sbsn = get_val_query(weekdays_date(), "('PBS', 'SR', 'SPNS', 'INDOIS')", "'BOND'", "Client")
sukuk = get_val_query(weekdays_date(), "('SYARIAH')", "'BOND'", "Client")
other = get_val_query(weekdays_date(), "('SBKMTN')", "'BOND'", "Client")

all_data = [sbn, obkor, sbsn, sukuk, other]
total = [sum([float(x[0]) for x in all_data]), sum([x[1] for x in all_data])]

perantara_ebus = [sbn + obkor + sbsn + sukuk + other + total] + [[0] * 12 for _ in range(11)]

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

def html_header(html_code, isHeader1=True, name_header=None):
    list_header_2d, list_span_2d = choose_header(name_header, isHeader1)
    color_bg = "#facdaf" if list_header_2d[0][0] == "Jenis Transaksi" else "yellow"

    for list_header, list_span in zip(list_header_2d, list_span_2d):
        html_code += "<tr>\n"
        for header, span in zip(list_header, list_span):
            html_code += f'<td rowspan="{span[0]}" colspan="{span[1]}" style="font-weight : bold; border : 1px black solid; background-color : {color_bg}; vertical-align: middle; text-align: center">{header}</td>\n'
        html_code += "</tr>\n"
    
    return html_code

def html_content_table(data_dict, html_code, data_list_2d, name_header, isHeader1=True):
    html_code = html_header(html_code, isHeader1, name_header)
    
    if type(data_dict) is not list :
        i = 0
        for key, val_list_2d in data_dict.items():
            html_code += f'<tr><td rowspan="3" style="vertical-align : middle; border : 1px black solid;">{key}</td>'
            for val_list in val_list_2d:
                val_list = val_list + [f"{float(x):.2f}" if i%2 == 0 else x for i, x in enumerate(data_list_2d[i])]
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

def generate_excel(report_folder, report_name):
    html_code = open_code_html()
    
    today_date = date.today().strftime("%d %B %Y")
    title_1 = "1. Laporan Kegiatan PPE-EBUS Bulanan"
    html_code = open_header(html_code, today_date, title_1)
    
    html_code = html_content_table(data_dict_1, html_code, pedagang_ebus, "Sebagai Pedagang EBUS")
    
    html_code += "<tr><td>&nbsp;</td></tr>" * 3
    html_code = html_content_table(data_dict_1, html_code, perantara_ebus, "Sebagai Perantara EBUS")
    
    
    html_code += "<tr><td>&nbsp;</td></tr>" * 3
    title_2 = "2. Laporan Kegagalan Transaksi"
    html_code = open_header(html_code, today_date, title_2)
    html_code += "<tr><td>&nbsp;</td><td style='font-weight : bold'>NIHIL</td></tr>"
    
    html_code += "<tr><td>&nbsp;</td></tr>" * 3
    title_3 = "3. Laporan Kegiatan Keagenan"
    html_code = open_header(html_code, today_date, title_3)
    html_code = html_content_table(data_dict_2, html_code, pedagang_ebus, None, False)
    
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
                    'windowCaption':'BO82 - PPE EBUS Sebagai Perantara (Overseas Branch)'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'BO82 - PPE EBUS Sebagai Perantara (Overseas Branch)', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Output Files','string', ['.pdf', '.xls'], '.pdf', 0 , 0, 'Select Output Extension Type']
]

def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = "".join(parameter['output_file'])
    
    folder_name = "report"+date.today().strftime("%Y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    if ".xls" in output_file:
        generate_excel(report_folder, report_name + ".xls")
    elif ".pdf" :
        generate_pdf(report_name, file_path, date.today().strftime("%Y%m%d"))
