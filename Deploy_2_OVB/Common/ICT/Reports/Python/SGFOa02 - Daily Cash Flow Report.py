import re
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael
from Report_Python_P2 import usd_price_mtm
from datetime import date


def get_data(optkey3='',optkey4='', portfolio='', bank='',type='', port_type='', time_bucket=''):
    #Setting the Blank Value
    if optkey3 == '' and optkey4 == '' and portfolio == '' and bank == '' and type == '' and port_type=='':
        return " "
    else:
        optkey3_query = "DL, BOND, FX, SBI"
        optkey4_query = "TOD, TOM, SPOT, FWD, SWAP, OPT, NDF, CBUSD, CBVALAS, UST, BILLS, ROI, ORI, SR, SBBI, SBK, SPN, SPNS, FR, INDOIS, PBS, NCD, SVBLCY, SVBUSD, IDSV, OVT, CMP, OVP, BA, CMT, BLT, BA"
        portfolio_query = ""
        bank_query = ""
        type_query = ""
        time_query = ""
        end_date = "i.exp_day"
        date_today = acm.Time.DateToday()
        if "FX" in optkey3:
            end_date="t.value_day"
        #Setting up Date Mapping
        if time_bucket == date_today:
            time_query = " and "+end_date+" >'"+ acm.Time.DateAddDelta(date_today,0,0,-1) +"' and "+end_date+" <= '" + date_today +"'"
        elif time_bucket == "Next Day":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,0,1) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,0,2) + "'"
        elif time_bucket == "2 - 7 days":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,0,2) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,0,8) + "'"
        elif time_bucket == "8 Days - 1 Month":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,0,7) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,1,0) + "'"
        elif time_bucket == "2 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,1,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,2,0) + "'"
        elif time_bucket == "3 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,2,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,3,0) + "'"
        elif time_bucket == "4 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,3,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,4,0) + "'"
        elif time_bucket == "5 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,4,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,5,0) + "'"
        elif time_bucket == "6 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,5,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,6,0) + "'"
        elif time_bucket == "7 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,6,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,7,0) + "'"
        elif time_bucket == "8 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,7,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,8,0) + "'"
        elif time_bucket == "9 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,8,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,9,0) + "'"
        elif time_bucket == "10 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,9,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,10,0) + "'"
        elif time_bucket == "11 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,10,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,11,0) + "'"
        elif time_bucket == "12 Months":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,11,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,12,0) + "'"
        #Setting up Additional Query for Specific Banks
        if bank == "Correspondent Bank":
            bank_query = " and p.correspondent_bank='Yes'"
        elif bank == "Interbank":
            bank_query = " and p.ptyid LIKE '%Mandiri%'"
        #Setting up Additional Query for Specific Types
        if type == "Loan" or type == "Sell" :
            type_query = " and t.quantity > 0"
        elif type == "Deposit" or type == "Buy" :
            type_query = " and t.quantity < 0"
        if optkey3:
            optkey3_query = " AND DISPLAY_ID(t, 'optkey3_chlnbr') in " + optkey3
        if optkey4:
            optkey4_query = " AND DISPLAY_ID(t, 'optkey4_chlnbr') in " + optkey4
        if portfolio :
            portfolio_query = " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio
        #Setting up the Query
        query = f"""
                SELECT t.price, t.quantity, t.trdnbr FROM trade t, instrument i, party p 
                where t.insaddr=i.insaddr and t.counterparty_ptynbr = p.ptynbr
                """ + optkey3_query + optkey4_query + portfolio_query + time_query + bank_query + type_query
        print(query)
        result = ael.asql(query)
        total_nominal = 0
        for row in result[1][0]:
            tradeCurr = acm.FTrade[row[2]].Currency().Name()
            if any(col != None for col in row):
                if tradeCurr == "USD":
                    nominal = (row[0]*row[1])
                else :
                    usd_price = usd_price_mtm(acm.FTrade[row[2]])
                    nominal = ((usd_price*row[0]) * row[1]) if usd_price != None else ((15000*row[0]) * row[1])
            total_nominal += nominal
        return f'{total_nominal:,}'
        
        
#########################################################################################################################
# GENERATE PDF
#########################################################################################################################
def prepare_xsl_fo_content(title, total_col, title_styling=''):
    xsl_fo_content = f"""<?xml version="1.1" encoding="utf-8"?>
    <fo:root xmlns:fo="http://www.w3.org/1999/XSL/Format">
        <fo:layout-master-set>
            <fo:simple-page-master master-name="my_page" margin="0.5in" page-width="25in">
                <fo:region-body/>
            </fo:simple-page-master>
        </fo:layout-master-set>
        <fo:page-sequence master-reference="my_page">
            <fo:flow flow-name="xsl-region-body">
                <fo:block {title_styling}> {title} </fo:block>
                    <fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
    """
    for _ in range(total_col):
        xsl_fo_content += '<fo:table-column border-width="1px" border-style="solid"/>\n'
    xsl_fo_content += "<fo:table-body>\n"
    return xsl_fo_content 
    
    
def add_xsl_data_row(xsl_content, row_data, cell_styling="border-width='1px' border-style='solid' padding='8pt'", block_styling=''):
    for row in row_data:        
        xsl_content += """<fo:table-row>\n"""
        for cell in row:
            xsl_content += f"""<fo:table-cell {cell_styling}><fo:block {block_styling}>""" +str(cell)+"""</fo:block>\n</fo:table-cell>\n"""
        xsl_content += """</fo:table-row>\n"""
    return xsl_content
    
    
def table_header(xsl_content):
    cell_styling = "border-width='1px' border-style='solid' padding='8pt'"
    xsl_content += """<fo:table-row>\n"""
    xsl_content += f"""<fo:table-cell {cell_styling} number-columns-spanned="3"><fo:block>""" +"Deskripsi"+"""</fo:block>\n</fo:table-cell>\n"""
    xsl_content += f"""<fo:table-cell {cell_styling} background-color='#089BCC' number-columns-spanned="6"><fo:block>""" +"BMSG"+"""</fo:block>\n</fo:table-cell>\n"""
    xsl_content += """</fo:table-row>\n"""
    return xsl_content
    
    
def date_column(xsl_content, time_bucket):
    cell_styling = "border-width='1px' border-style='solid' padding='8pt'"
    xsl_content += """<fo:table-row>\n"""
    xsl_content += f"""<fo:table-cell {cell_styling} number-columns-spanned="3"><fo:block>""" +""+"""</fo:block>\n</fo:table-cell>\n"""
    for time_val in time_bucket[0][1:]:
        xsl_content += f"""<fo:table-cell {cell_styling}><fo:block>""" +str(time_val)+"""</fo:block>\n</fo:table-cell>\n"""
    xsl_content += """</fo:table-row>\n"""
    return xsl_content
    
    
def close_xsl_table(xsl_content):
    xsl_content += """</fo:table-body></fo:table>"""
    return xsl_content
    
    
def create_xsl_fo_file(file_name, file_path, xsl_fo_content, current_datetime, folder_with_file_name=False):
    xsl_fo_content += """ </fo:flow>
        </fo:page-sequence>
        </fo:root>
    """
    if folder_with_file_name:
        folder_path = file_path+"\\"+file_name+"\\"+current_datetime
    else:
        folder_path = file_path+"\\report"+current_datetime
    try:
        os.makedirs(folder_path)
    except:
        pass
    file_url = folder_path+"\\"+file_name+".fo"
    f = open(file_url, "w")
    f.write(xsl_fo_content)
    f.close()
    return file_url
    
    
def generate_pdf_from_fo_file(foFilePath):
    foFilePath = foFilePath.replace(".fo","")
    command = Template(settings.FOP_BAT)
    command = command.substitute({'extension':'pdf', 'filename':foFilePath})
    ret = os.system(command)
    if ret == 0 :
        print('Generate PDF Succesful')
    else:
        print('Somethings wrong when generating PDF.')
        
        
def generate_pdf(list_value):
    if not os.path.exists("D:\\Project\\HKCO\\report2231"):
        os.makedirs("D:\\Project\\HKCO\\report2231")
    time_bucket = [['', date.today().strftime("%d-%b-%y"),'Next Day','2 - 7 Days','8 Days - 1 Month','2 Months','3 Months','4 Months','5 Months','6 Months','7 Months','8 Months','9 Months','10 Months','11 Months','12 Months']]
    xsl_fo_content = prepare_xsl_fo_content("teting aja", 9)
    xsl_fo_content = table_header(xsl_fo_content)
    xsl_fo_content = date_column(xsl_fo_content, time_bucket)
    xsl_fo_content = add_xsl_data_row(xsl_fo_content, list_value)
    xsl_fo_content = close_xsl_table(xsl_fo_content)
    foFilePath = create_xsl_fo_file("test", "D:\\Project\\HKCO", xsl_fo_content, "2231")
    generate_pdf_from_fo_file(foFilePath)
    
    
#########################################################################################################################
# GUI CODE
#########################################################################################################################
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'SGFOa02 - Daily Cash Flow Report'}
                    
                    
ael_variables=[
['report_name','Report Name','string', None, 'SGFOa02 - Daily Cash Flow Report', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['currency','Currency Of Choice','string',['USD','EUR','IDR','CNY','AUD','JPY','GBP','HKD'],'USD',0,0],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output']
]


def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    currency = str(parameter['currency'])
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    title_style = """
        table {
            width : 1000px;
        }
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
        .currency {
            background-color:blue;
            color:white;
        }
        .description {
            border : 1px white solid;
            text-align: left;
        }
    """
    current_date = get_current_date("")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content("Daily Cashflow Report - Cashflow as per. "+current_date, title_style)
    html_content +='<table>'
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content,'POSISI LIKUIDITAS PER','colspan=3 class="description"')
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content,'Dlm CNY (Million)','colspan=3 class="description"')
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content,'DESKRIPSI','colspan=3')
    html_content = html_gen.add_cell_data(html_content,"BMSG",'colspan=15 class="currency"')
    html_content = html_gen.close_table_row(html_content)
    time_bucket = [['', date.today().strftime("%d-%b-%y"),'Next Day','2 - 7 Days','8 Days - 1 Month','2 Months','3 Months','4 Months','5 Months','6 Months','7 Months','8 Months','9 Months','10 Months','11 Months','12 Months']]
    #Adding Time Bucket
    html_content = html_gen.add_data_row(html_content, time_bucket, '', 'class="time-bucket" style="border-bottom:1px black solid"')
    html_content = html_content.replace('<td class="time-bucket" style="border-bottom:1px black solid"></td>','<td colspan="3" class="time-bucket" style="border-bottom:1px black solid"></td>')    
    #Adding row [A.Saldo Nostro]
    saldo_nostro = ['SALDO NOSTRO &#38; KAS']
    #QUERY FILTER OPTKEY4
    #TOD, TOM, SPOT, FWD, SWAP, OPT, NDF, CBIDR, CBUSD, CBVALAS, UST, BILLS, ROI, ORI, INDOIS, NCD, SVBUSD, SVBLCY, OVT, CMP, OVP, BA, CMT, BLT, BA
    optkey4_list = [
        "('BA', 'BLT')",
        "('CBIDR', 'CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'INDOIS', 'NCD', 'SVBUSD', 'SVBLCY')",
        "('TOD', 'TOM', 'SPOT', 'FWD', 'NDF', 'SWAP', 'OPT')"
    ]
    list_value_a=[]
    #Function for Populating Saldo Nostro
    for subrow in saldo_nostro:
        temp_row =['A']
        temp_row.append(subrow)
        for items in range(len(time_bucket[0]) - 1):
            temp_row.append('')
        list_value_a.append(temp_row)
    html_content = html_gen.add_data_row(html_content,list_value_a,'','style="text-align: left; font-weight:bold; border-bottom: 1px black solid;"')
    html_content = html_content.replace('<td style="text-align: left; font-weight:bold; border-bottom: 1px black solid;">SALDO NOSTRO &#38; KAS</td>','<td colspan="2" style="border-bottom: 1px black solid; text-align: left; font-weight:bold"; font-weight:bold;">SALDO NOSTRO &#38; KAS</td>')    
    port_list = [
        "('IRT DCM 1 BMSG - ACU', 'IRT DCM 2 BMSG - ACU', 'IRT DCM 1 BMSG - DBU', 'IRT DCM 2 BMSG - DBU')",
        "('BB BOND OCI BMSG - ACU', 'BB BOND OCI BMSG - DBU')",
        "('BB BOND AC BMSG - ACU', 'BB BOND AC BMSG - DBU')"
    ]
    #Adding row [B.Inflow]
    sub_row_b = {
                'INFLOW':['','','','', '', ''],
                'Penempatan Interbank Jatuh Tempo':["('DL')", "('CMP')", "",'Correspondent Bank','Loan', ''],
                'Pinjaman Interbank':["('DL')","('CMT')", "",'Correspondent Bank','Deposit', ''],
                'Penempatan Interoffice Jatuh Tempo':["('DL')", "('OVP')", "",'Interbank','Loan', ''],
                'Pinjaman Interoffice':["('DL')", "('OVT')", "",'Interbank','Deposit', ''],
                'Borrowing (BA Financing/Term Loan)':["('DL')", optkey4_list[0], "", '','Deposit', ''],
                'Trade Finance Jatuh Tempo':['','','','', '', ''],
                'Usance':['','','','', '', ''],
                'Sight':['','','','', '', ''],
                'TR':['','','','', '', ''],
                'Others':['','','','','', ''],
                'Penerimaan Trade Services':['','','','','', ''],
                'Securities Jatuh Tempo &#38; Penerimaan Coupon':['','','','','', ''],
                'HFT':["('BOND')", optkey4_list[1], port_list[0],'','', '', 'FVTPL'],
                'AFS':["('BOND')", optkey4_list[1], port_list[1],'','', '', 'FVOCI'],
                'HTM':["('BOND')", optkey4_list[1], port_list[2],'','', '', 'Amortised Cost'],
                'Pelunasan Pinjaman Nasabah (Pokok &#38; Bunga)':['','','','','', ''],
                'Lainnya':['','','','','', ''],
                '':['','','','','', ''],
                'ADDITIONAL VARIABLES FOR NON BANK INSTITUTION':['','','','','', ''],
                'Deposito / DOC Jatuh Tempo':['','','','','', ''],
                'Penjualan Obligasi (proprietary trading)':['','','','','', ''],
                'Pembelian USD':["('FX')", optkey4_list[2], "", '','Buy', ''],
                'Pelunasan Funding Bonds &#38; IPO':['','','','','', '']
                }    
    #List for the values
    list_value_b=[]
    #Function for Populating Inflow Values
    for key, value in sub_row_b.items():
        temp_row = ['B' if key == 'INFLOW' else '']
        temp_row.extend([key] if key in ['INFLOW', "", "ADDITIONAL VARIABLES FOR NON BANK INSTITUTION"] else ['-', key] if key not in ['Usance', 'Sight', 'TR', 'HFT', 'AFS', 'HTM', 'Others'] else ['', f'- {key}'])
        for i in range(1, len(time_bucket[0])):
            val = get_data(value[0],value[1],value[2],value[3], value[4], value[5],time_bucket[0][i])
            temp_row.append(val)            
        list_value_b.append(temp_row)
    html_content = html_gen.add_data_row(html_content,list_value_b,'','style="text-align: right;"')
    html_content = html_content.replace('<td style="text-align: right;">B</td>','<td style="text-align: center;font-weight:bold">B</td>')
    html_content = html_content.replace('<td style="text-align: right;">-</td>','<td style="text-align: center;font-weight:bold">-</td>')
    html_content = html_content.replace('<td style="text-align: right;">INFLOW</td>','<td colspan="2" style="text-align: left;font-weight:bold">INFLOW</td>')
    html_content = html_content.replace('<td style="text-align: right;">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>','<td colspan="2" style="text-align: left">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>')
    for subtitle_b in [x[2] for x in list_value_b]:
        if subtitle_b not in ["INFLOW", "ADDITIONAL VARIABLES FOR NON BANK INSTITUTION"]:
            html_content = html_content.replace(f'<td style="text-align: right;">{subtitle_b}</td>',f'<td style="text-align: left;">{subtitle_b}</td>')
    sub_total_b = []
    for subrow in ['Sub Total Inflow']:
        temp_row =['', subrow]
        for items in range(len(time_bucket[0]) - 1):
            temp_row.append('')
        sub_total_b.append(temp_row)
    old_att = 'style="text-align: left; font-weight:bold; border-top: 1px black solid; border-bottom: 1px black solid;"'
    new_att = 'colspan="2" style="border-top: 1px black solid; border-bottom: 1px black solid; text-align: left; font-weight:bold"; font-weight:bold;"'
    html_content = html_gen.add_data_row(html_content,sub_total_b,'', old_att)
    html_content = html_content.replace(f'<td {old_att}>Sub Total Inflow</td>',f'<td {new_att}>Sub Total Inflow</td>')
    #Adding row [C. Outflow]
    sub_row_c ={
                'OUTFLOW':['','','','','',''], 
                'Penempatan Interbank (Interbank Placement)':["('DL')", "('CMP')", "",'Correspondent Bank','Deposit',''],
                'Pinjaman Interbank Jatuh Tempo':["('DL')","('CMT')", "",'Correspondent Bank','Loan',''],
                'Penempatan Interoffice':["('DL')", "('OVP')", "",'Interbank','Deposit',''],
                'Pinjaman Interoffice Jatuh Tempo':["('DL')","('OVT')", "",'Interbank','Loan',''],
                'Borrowing (BA Financing/Term Loan) Jatuh Tempo':["('DL')", optkey4_list[0], "", '','',''],
                'Penarikan Trade Finance':['','','','','',''],
                'Usance':['','','','','',''],
                'Sight':['','','','','',''],
                'TR':['','','','','',''],
                'Others':['','','','','',''],
                'Deposit Nasabah Jatuh Tempo':['','','','','',''],
                'Pembelian Securities':['','','','','',''],
                'HFT':["('BOND')", optkey4_list[1], port_list[0],'', '','Amortised Cost'],
                'AFS':["('BOND')", optkey4_list[1], port_list[1],'', '','FVOCI'],
                'HTM':["('BOND')", optkey4_list[1], port_list[2],'','','FVTPL'],
                'Penarikan Pinjaman Nasabah':['','','','','',''],
                'Saldo Vostro':['','','','','',''],
                'Lainnya':['','','','','',''],
                '':['','','','','',''],
                'ADDITIONAL VARIABLES FOR NON BANK INSTITUTION':['','','','','',''],
                'Penempatan Deposito / DOC':['','','','','',''],
                'Pembelian Obligasi (proprietary trading)':['','','','','',''],
                'Penjualan USD':["('FX')", optkey4_list[2], "",'','Sell',''],
                'Funding Bonds &#38; IPO':['','','','','',''],
                'Biaya Operasional':['','','','','','']
                }
    #List for the values
    list_value_c=[]
    #Function for Populating Inflow Values
    for key, value in sub_row_c.items():
        temp_row = ['C' if key == 'OUTFLOW' else '']
        temp_row.extend([key] if key in ['OUTFLOW', "", "ADDITIONAL VARIABLES FOR NON BANK INSTITUTION"] else ['-', key] if key not in ['Usance', 'Sight', 'TR', 'HFT', 'AFS', 'HTM', 'Others'] else ['', f'- {key}'])
        for i in range(1, len(time_bucket[0])):
            val = get_data(value[0],value[1],value[2],value[3], value[4], value[5], time_bucket[0][i])
            temp_row.append(val)            
        list_value_c.append(temp_row)
    html_content = html_gen.add_data_row(html_content,list_value_c,'','style="text-align:left;"')
    html_content = html_content.replace('<td style="text-align:left;">C</td>','<td style="text-align:center;font-weight:bold">C</td>')
    html_content = html_content.replace('<td style="text-align:left;">-</td>','<td style="text-align: center;font-weight:bold">-</td>')
    html_content = html_content.replace('<td style="text-align:left;">OUTFLOW</td>', '<td colspan="2" style="text-align:left; font-weight:bold;">OUTFLOW</td>')
    html_content = html_content.replace('<td style="text-align:left;">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>', '<td colspan="2" style="text-align:left;">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>')
    sub_total_c = []
    for subrow in ['Sub Total Outflow']:
        temp_row =['', subrow]
        for items in range(len(time_bucket[0]) - 1):
            temp_row.append('')
        sub_total_c.append(temp_row)
    old_att = 'style="text-align: left; font-weight:bold; border-top: 1px black solid; border-bottom: 1px black solid;"'
    new_att = 'colspan="2" style="border-top: 1px black solid; border-bottom: 1px black solid; text-align: left; font-weight:bold"; font-weight:bold;"'
    html_content = html_gen.add_data_row(html_content,sub_total_c,'', old_att)
    html_content = html_content.replace(f'<td {old_att}>Sub Total Outflow</td>',f'<td {new_att}>Sub Total Outflow</td>')
    #Adding row [D. Net Cash Flow (B - C)]
    net_cashflow = ['NET CASH FLOW (B - C)']
    list_value_d=[]
    #Function for Populating Saldo Nostro
    for subrow in net_cashflow:
        temp_row =['D']
        temp_row.append(subrow)
        for items in range(len(time_bucket[0]) - 1):
            temp_row.append('')
        list_value_d.append(temp_row)
    html_content = html_gen.add_data_row(html_content,list_value_d,'','style="text-align: left; font-weight:bold"')
    html_content = html_content.replace('<td style="text-align: left; font-weight:bold">NET CASH FLOW (B - C)</td>','<td colspan="2" style="text-align: center; font-weight:bold"; font-weight:bold">NET CASH FLOW (B - C)</td>')
    #Adding row [E. Saldo Kumulatif]
    saldo_kumulatif = ['SALDO KUMULATIF']
    list_value_e=[]
    #Function for Populating Saldo Nostro
    for subrow in saldo_kumulatif:
        temp_row =['E']
        temp_row.append(subrow)
        for items in range(len(time_bucket[0]) - 1):
            temp_row.append('')
        list_value_e.append(temp_row)
    html_content = html_gen.add_data_row(html_content,list_value_e,'','style="text-align: left;font-weight:bold"')
    html_content = html_content.replace('<td style="text-align: left;font-weight:bold">SALDO KUMULATIF</td>','<td colspan="2" style="text-align: center; font-weight:bold"; font-weight:bold">SALDO KUMULATIF</td>')
    html_content = html_gen.close_html_table(html_content)
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, False)
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            list_value_all = list_value_a + list_value_b + list_value_c + list_value_d + list_value_e
            generate_pdf(list_value_all)
