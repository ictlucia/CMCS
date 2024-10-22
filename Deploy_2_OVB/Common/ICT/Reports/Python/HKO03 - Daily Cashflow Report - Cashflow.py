from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from datetime import date
import acm, ael
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer
import datetime
import re
from Report_Python_P2 import usd_price_mtm
html_gen = HTMLGenerator()

def adding_data_row(html_content, row_data, row_class='', cell_class=''):
    for row in row_data:
        html_content += f"<tr {row_class}>"
        for cell in row:
            if "isNum" in str(cell):
                html_content += f'<td style="text-align : right">' + str(cell).replace("isNum", "") + "</td>"
            elif str(cell) in ["NET CASH FLOW (B - C)", "SALDO KUMULATIF"]:
                html_content += f"<td>" + str(cell) + "</td>"
            else :
                html_content += f"<td {cell_class}>" + str(cell) + "</td>"
                
        html_content += "</tr>"
    
    return html_content

def adding_data_row_xlsfo(xlsfo_content, row_data, cell_class='', block_class=''):
    for row in row_data:
        if row[2] == "" :
            for i in range(3, len(row)):
                row[i] = ""
    
    border_style = 'border-start-style="solid" border-start-width="1px" border-before-style="solid" border-before-width="1px"'
    
    for row in row_data:
        xlsfo_content += f"<fo:table-row>"
        for cell in row:
            if "isNum" in str(cell):
                xlsfo_content += f'<fo:table-cell ><fo:block {border_style} text-align="right">{str(cell).replace("isNum", "")}</fo:block></fo:table-cell>'
            elif str(cell) == "":
                xlsfo_content += f'<fo:table-cell ><fo:block></fo:block></fo:table-cell>'
            else :
                xlsfo_content += f'<fo:table-cell {cell_class}><fo:block {block_class}>{str(cell)}</fo:block></fo:table-cell>'
                 
        xlsfo_content += "</fo:table-row>"
    
    return xlsfo_content

def date_info():
    date_today = acm.Time.DateToday()
    time_list = [[0, 0, 1], [0, 0, 7], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 6, 0]]
    
    date_list = [""]
    for day, month, year in time_list:
        date = datetime.datetime.strptime(acm.Time.DateAddDelta(date_today, day, month, year), '%Y-%m-%d').strftime("%d-%b-%y")
        date_list.append(date)
    
    return date_list

def get_optkey3_oid(optkey_string):
    optkey = acm.FChoiceList.Select('list=Product Type')
    for name in optkey:
        if name.Name()== optkey_string:
            return name.Oid()

def get_optkey4_oid(optkey_string):
    optkey = acm.FChoiceList.Select('list=Category')
    for name in optkey:
        if name.Name()== optkey_string:
            return name.Oid()
            
def get_data(optkey3='',optkey4='', portfolio='', bank='',type='', port_type='', time_bucket=''):

    #Setting the Blank Value

    if optkey3 == '' and optkey4 == '' and portfolio == '' and bank == '' and type == '' and port_type=='':

        return 0

    else:

        optkey3_query = ""

        optkey4_query = ""
        
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

        

        elif time_bucket == "2 - 7 Days":

            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,0,2) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,0,7) + "'"

        

        elif time_bucket == "8 days - 1 Month":

            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,0,8) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,1,0) + "'"

        

        elif time_bucket == "1-2 Months":

            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,1,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,2,0) + "'"
            
        
        elif time_bucket == "2-3 Months":

            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,2,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,3,0) + "'"
            

        elif time_bucket == "3-6 months":

            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,3,0) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,6,0) + "'"

            

        

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



        result = ael.asql(query)
        total_nominal = 0
        for row in result[1][0]:
            tradeCurr = acm.FTrade[row[2]].Currency().Name()
            if any(col != None for col in row):
                if tradeCurr == "USD":
                    nominal = (row[0]*row[1])
                else :
                    usd_price = usd_price_mtm(acm.FTrade[row[2]], "USD")
                    nominal = ((usd_price*row[0]) * row[1]) if usd_price != None else ((15000*row[0]) * row[1])
            
            total_nominal += nominal
        
        return total_nominal
        

def process_text(ael_params, raw_text):
    processed_string = raw_text.replace("<Date>", acm.Time.DateToday())
    processed_string = processed_string.replace("<Report Name>", ael_params['report_name'])
    return processed_string


#########################################################################################################################
# GUI CODE
#########################################################################################################################

ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'HKO03 - Daily Cashflow Report'}



ael_variables=[

['report_name','Report Name','string', None, 'HKO03 - Daily Cashflow Report', 1,0],

['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

['currency','Currency Of Choice','string', ['USD','EUR','IDR','CNY','AUD','JPY','GBP','HKD'],'USD' ,0,0],

['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output']

]

def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    currency = str(parameter['currency'])

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
        
        .currency {
            background-color:blue;
            color:white;
            
            text-align:center;
        }
        
        .bold {
            
        }
        
        td {
            text-align:left;
        }
        
        .deskripsi {
            text-align:center;
            vertical-align: middle;
        }
        
        .subtitle-3 {
            text-align:left;
            
            color: blue;
            border: hidden;
        }
        
        .subtitle-4 {
            text-align:right;
            
            font-size:15px;
            color: white;
            background-color: orange;
            border: hidden;
        }
        
    """
    
    current_date = datetime.date.today().strftime('%y%m%d')
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content("Daily Cashflow Report - Cashflow as per. "+current_date, title_style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("Daily Cashflow Report - Cashflow as per. "+current_date)
    
    #Preparing Title
    xsl_fo_content += f"""
        <fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
            {'<fo:table-column column-width="15mm"/>' * 2}
            {'<fo:table-column column-width="100mm"/>' * 1}
            {'<fo:table-column column-width="55mm"/>' * 7}
        <fo:table-body>
    """
    
    title = ['DESKRIPSI', currency]
    
    time_bucket = [[date.today().strftime("%d-%b-%y"),'Next Day','2 - 7 Days','8 days - 1 Month', '1-2 Months', '2-3 Months','3-6 months']]
    
    #TITLE
    html_content +="<div><table>"
    
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content,'LAPORAN DAILY CASHFLOW (PM) - DYNAMIC','colspan="3" style=" border: hidden;"')
    html_content = html_gen.close_table_row(html_content)
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, 'LAPORAN DAILY CASHFLOW (PM) - DYNAMIC','number-columns-spanned="3"', 'text-align="left"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content,'&nbsp;','style=" border: hidden;"')
    html_content = html_gen.close_table_row(html_content)
   
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, '\n','number-columns-spanned="2"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content,'POSISI LIKUIDITAS','colspan="3" class="subtitle-3" style="margin-botton:-20px"')
    html_content = html_gen.add_cell_data(html_content, date.today().strftime("%d-%b-%y"),'class="subtitle-3" style="border:hidden; text-align: right"')
    html_content = html_gen.close_table_row(html_content)
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, 'POSISI LIKUIDITAS','number-columns-spanned="3"', 'text-align="left" color="blue"')
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, date.today().strftime("%d-%b-%y"),'', 'text-align="right" color="blue"')
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content,'Dlm USD','colspan="3" class="subtitle-3"')
    
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, 'Dlm USD','number-columns-spanned="3"', 'text-align="left" color="blue"')
    
    
    for dates in date_info():
        html_content = html_gen.add_cell_data(html_content, dates,'class="subtitle-3" style="text-align: center"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, dates,'', 'text-align="center" color="blue"')
        
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
    
    html_content = html_gen.add_cell_data(html_content,title[0],'rowspan=2 colspan="3" class="deskripsi"')
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,title[0],'number-rows-spanned="2" number-columns-spanned="3"')
    
    html_content = html_gen.add_cell_data(html_content, title[1],'colspan=7 class="currency"')
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,title[1],'number-columns-spanned="7" background-color="blue" color="white" font-weight="bold"')
    
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    
    #Adding Time Bucket
    html_content = html_gen.add_data_row(html_content, time_bucket, '', 'style="text-align:center"')
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content, time_bucket, '', 'text-align="center"')
    
    
    #Adding row [A.Saldo Nostro]
    saldo_nostro = [f"{x:,}" for x in [0, 0, 0, 0, 0, 0, 0]]
    
    #QUERY FILTER OPTKEY3
    #DL, BOND, FX
    
    #QUERY FILTER OPTKEY4
    #TOD, TOM, SPOT, FWD, SWAP, OPT, NDF, CBIDR, CBUSD, CBVALAS, UST, BILLS, ROI, ORI, INDOIS, NCD, SVBUSD, SVBLCY, OVT, CMP, OVP, BA, CMT, BLT, BA
    
    optkey4_list = [
        "('BA', 'BLT')",
        "('CBIDR', 'CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'INDOIS', 'NCD', 'SVBUSD', 'SVBLCY')",
        "('TOD', 'TOM', 'SPOT', 'FWD', 'NDF', 'SWAP', 'OPT')"
    ]
    
    border_style = 'border-bottom-style="solid" border-bottom-width="1px" border-start-style="solid" border-start-width="1px" border-before-style="solid" border-before-width="1px"'
        
    html_content = html_gen.add_data_row(html_content,[['A', 'SALDO NOSTRO'] + saldo_nostro],'','class=bold')
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content, [['A', 'SALDO NOSTRO'] + saldo_nostro],'',f'{border_style} text-align="right"')
    
    html_content = html_content.replace('<td class=bold>SALDO NOSTRO</td>','<td colspan="2" class=bold>SALDO NOSTRO</td>')
    
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="right">SALDO NOSTRO</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="2"><fo:block {border_style} text-align="left">SALDO NOSTRO</fo:block></fo:table-cell>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">A</fo:block>',f'<fo:block {border_style} text-align="center">A</fo:block>')
    
    port_list = [
        "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK', 'IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')",
        "('BB BOND OCI BMHK', 'BB BOND OCI BMHK')",
        "('BB BOND AC BMHK', 'BB BOND AC BMHK')"
    ]
    
    #Adding row [B.Inflow]
    list_value_b=[]
    sub_row_b = {

                'INFLOW':['','','','', '', ''],

                'Penempatan Interbank Jatuh Tempo':["('DL')", "('CMP')", "",'Correspondent Bank','Loan', ''],

                'Pinjaman Interbank':["('DL')","('CMT')", "",'Correspondent Bank','Deposit', ''],

                'Penempatan Interoffice Jatuh Tempo':["('DL')", "('OVP')", "",'Interbank','Loan', ''],

                'Pinjaman Interoffice':["('DL')", "('OVT')", "",'Interbank','Deposit', ''],

                'Borrowing (BA Financing/Term Loan)':["('DL')", optkey4_list[0], "", '','Deposit', ''],

                'Trade Finance Jatuh Tempo':['','','','', '', ''],

                'Usance Jatuh Tempo':['','','','', '', ''],

                'Risk Part':['','','','', '', ''],

                'TR Jatuh Tempo':['','','','', '', ''],

                'Others (Jatuh Tempo)':['','','','','', ''],

                'Penerimaan Trade Services':['','','','','', ''],

                'Securities Jatuh Tempo':['','','','','', ''],
                
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
    
    for_format_1 = ['INFLOW', 'ADDITIONAL VARIABLES FOR NON BANK INSTITUTION']
    for_format_2 = ['Usance Jatuh Tempo', 'Risk Part', 'TR Jatuh Tempo', 'Others (Jatuh Tempo)', '']
    for_format_3 = ['HFT', 'AFS', 'HTM']    
    
    total_sub_row_b = [float(x.replace(",", "")) for x in saldo_nostro]
    for key, value in sub_row_b.items():
        temp_row = ['B' if key == 'INFLOW' else '']
        
        if key in for_format_1 :
            temp_row.extend([key])
        elif key in for_format_2 :
            temp_row.extend(['', key])
        elif key in for_format_3 :
            temp_row.extend(['', "- " + key])
        else :
            temp_row.extend(['-', key])
        
        for i in range(len(time_bucket[0])):
            val = get_data(value[0],value[1],value[2],value[3], value[4], value[5],time_bucket[0][i])
            temp_row.append(val)
        for i in range(3, len(temp_row)):
            total_sub_row_b[i-3] += temp_row[i]
            temp_row[i] = f"{temp_row[i]:,}isNum"
            
        list_value_b.append(temp_row)
    
    html_content = adding_data_row(html_content,list_value_b,'','style="text-align: left;"')
    xsl_fo_content = adding_data_row_xlsfo(xsl_fo_content,list_value_b, '', f'{border_style} text-align="right"')
    
    html_content = html_content.replace('<td style="text-align: left;">Penempatan Interbank Jatuh Tempo</td>','<td style="text-align: left; width: 500px; ">Penempatan Interbank Jatuh Tempo</td>')
    html_content = html_content.replace('<td style="text-align: left;">B</td>','<td style="text-align: center;">B</td>')
    html_content = html_content.replace('<td style="text-align: left;">-</td>','<td style="text-align: center;">-</td>')
    html_content = html_content.replace('<td style="text-align: left;">INFLOW</td>','<td colspan="2" style="text-align: left;">INFLOW</td>')
    html_content = html_content.replace('<td style="text-align: left;">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>','<td colspan="2" style="text-align: left">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>')
    
    border_style_left = 'border-left-style="solid" border-left-width="1px"'
    
    xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">B</fo:block>', f'<fo:block {border_style} text-align="center">B</fo:block>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">-</fo:block>', f'<fo:block {border_style} text-align="center">-</fo:block>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="right">INFLOW</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="2"><fo:block  {border_style} text-align="left">INFLOW</fo:block></fo:table-cell>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="right">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="2"><fo:block {border_style} text-align="left">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</fo:block></fo:table-cell>')
    
    for key in sub_row_b.keys():
        if key in ['HFT', 'AFS', 'HTM'] :
            xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">- {key}</fo:block>',f'<fo:block {border_style} text-align="left">- {key}</fo:block>')
        else :
            xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">{key}</fo:block>',f'<fo:block {border_style} text-align="left">{key}</fo:block>')
    
    sub_total_b = [['Sub Total Inflow'] + [f"{x:,}" for x in total_sub_row_b]]
    
    old_att = 'style="text-align: left;  border-top: 1px black solid; border-bottom: 1px black solid;"'
    new_att = 'colspan="3" style="border-top: 1px black solid; border-bottom: 1px black solid; text-align: left; "; "'
    html_content = adding_data_row(html_content, [[sub_total_b[0][0]] + [str(x)+"isNum" for x in sub_total_b[0][1:]]],'', old_att)
    html_content = html_content.replace(f'<td {old_att}>Sub Total Inflow</td>',f'<td {new_att}>Sub Total Inflow</td>')
    
    xsl_fo_content = adding_data_row_xlsfo(xsl_fo_content,[[sub_total_b[0][0]] + [str(x)+"isNum" for x in sub_total_b[0][1:]]],'',f'{border_style} text-align="left"')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="left">Sub Total Inflow</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="3"><fo:block {border_style} text-align="left">Sub Total Inflow</fo:block></fo:table-cell>')
    
    #Adding row [C. Outflow]
    sub_row_c ={

                'OUTFLOW':['','','','','',''], 

                'Penempatan Interbank':["('DL')", "('CMP')", "",'Correspondent Bank','Deposit',''],

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
                
                'Current Account (Customer\'s Fund)':['','','','','',''],

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
    
    for_format_1 = ['OUTFLOW', 'ADDITIONAL VARIABLES FOR NON BANK INSTITUTION']
    for_format_2 = ['Usance', 'Sight', 'TR', 'Others', '']
    for_format_3 = ['HFT', 'AFS', 'HTM']   
    
    total_sub_row_c = [0] * 7
    #Function for Populating Values
    for key, value in sub_row_c.items():
        temp_row = ['C' if key == 'OUTFLOW' else '']
        
        if key in for_format_1 :
            temp_row.extend([key])
        elif key in for_format_2 :
            temp_row.extend(['', key])
        elif key in for_format_3 :
            temp_row.extend(['', "- " + key])
        else :
            temp_row.extend(['-', key])
        
        for i in range(len(time_bucket[0])):
            val = get_data(value[0],value[1],value[2],value[3], value[4], value[5],time_bucket[0][i])
            temp_row.append(val)
        for i in range(3, len(temp_row)):
            total_sub_row_c[i-3] += float(temp_row[i])
            temp_row[i] = f"{temp_row[i]:,}isNum"
         
        list_value_c.append(temp_row)
        
    html_content = adding_data_row(html_content,list_value_c,'','style="text-align: left;"')
    xsl_fo_content = adding_data_row_xlsfo(xsl_fo_content,list_value_c,'', f'{border_style} text-align="right"')
    
    html_content = html_content.replace('<td style="text-align: left;">C</td>','<td style="text-align: center;">C</td>')
    html_content = html_content.replace('<td style="text-align: left;">-</td>','<td style="text-align: center;">-</td>')
    html_content = html_content.replace('<td style="text-align: left;">OUTFLOW</td>','<td colspan="2" style="text-align: left;">OUTFLOW</td>')
    html_content = html_content.replace('<td style="text-align: left;">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>','<td colspan="2" style="text-align: left">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</td>')   
    
    xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">C</fo:block>', f'<fo:block {border_style} text-align="center">C</fo:block>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">-</fo:block>', f'<fo:block {border_style} text-align="center">-</fo:block>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:block></fo:block>', f'<fo:block {border_style_left} text-align="center">&#xa0;</fo:block>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="right">OUTFLOW</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="2"><fo:block {border_style} text-align="left">OUTFLOW</fo:block></fo:table-cell>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="right">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="2"><fo:block {border_style} text-align="left">ADDITIONAL VARIABLES FOR NON BANK INSTITUTION</fo:block></fo:table-cell>')
    
    for key in sub_row_c.keys():
        if key in ['HFT', 'AFS', 'HTM'] :
            xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">- {key}</fo:block>',f'<fo:block {border_style} text-align="left">- {key}</fo:block>')
        else :
            xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">{key}</fo:block>',f'<fo:block {border_style} text-align="left">{key}</fo:block>')
    
    sub_total_c = [['Sub Total Outflow'] + [f"{x:,}" for x in total_sub_row_c]]
    
    old_att = 'style="text-align: left;  border-top: 1px black solid; border-bottom: 1px black solid;"'
    new_att = 'colspan="3" style="border-top: 1px black solid; border-bottom: 1px black solid; text-align: left; "; "'
    html_content = adding_data_row(html_content,[[sub_total_c[0][0]] + [str(x)+"isNum" for x in sub_total_c[0][1:]]],'', old_att)
    html_content = html_content.replace(f'<td {old_att}>Sub Total Outflow</td>',f'<td {new_att}>Sub Total Outflow</td>')
    
    xsl_fo_content = adding_data_row_xlsfo(xsl_fo_content,[[sub_total_c[0][0]] + [str(x)+"isNum" for x in sub_total_c[0][1:]]],'', f'{border_style} text-align="left"')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="left">Sub Total Outflow</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="3"><fo:block {border_style} text-align="left">Sub Total Outflow</fo:block></fo:table-cell>')
    
    #Adding row [D. Net Cash Flow (B - C)]
    net_cashflow_val = []
    for total_b, total_c in zip(sub_total_b[0][1:], sub_total_c[0][1:]):
        net_cashflow_val.append(float(total_b.replace(",", "")) - float(total_c.replace(",", "")))
    
    net_cashflow = [['D', 'NET CASH FLOW (B - C)'] + [f"{x:,}" for x in net_cashflow_val]]
        
    html_content = adding_data_row(html_content,[net_cashflow[0][0:2] + [str(x)+"isNum" for x in net_cashflow[0][2:]]],'','class=bold colspan="2"')    
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content, net_cashflow,'', f'{border_style} text-align="right"')
    
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="right">NET CASH FLOW (B - C)</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="2"><fo:block {border_style} text-align="left">NET CASH FLOW (B - C)</fo:block></fo:table-cell>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">D</fo:block>', f'<fo:block {border_style} text-align="center">D</fo:block>')
    
    #Adding row [E. Saldo Kumulatif]
    saldo_kumulatif_val = [net_cashflow_val[0]]
    for i, net_cashflow in enumerate(net_cashflow_val[1:]):
        saldo_kumulatif_val.append(net_cashflow + saldo_kumulatif_val[i])
    
    saldo_kumulatif = [['E', 'SALDO KUMULATIF'] + [f"{x:,}" for x in saldo_kumulatif_val]]
    
    html_content = adding_data_row(html_content, [saldo_kumulatif[0][0:2] + [str(x)+"isNum" for x in saldo_kumulatif[0][2:]]],'','class=bold colspan="2"')
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content, saldo_kumulatif,'', f'{border_style} text-align="right"')
    
    xsl_fo_content = xsl_fo_content.replace(f'<fo:table-cell ><fo:block {border_style} text-align="right">SALDO KUMULATIF</fo:block></fo:table-cell>', f'<fo:table-cell number-columns-spanned="2"><fo:block {border_style} text-align="left">SALDO KUMULATIF</fo:block></fo:table-cell>')
    xsl_fo_content = xsl_fo_content.replace(f'<fo:block {border_style} text-align="right">E</fo:block>', f'<fo:block {border_style} text-align="center">E</fo:block>')

    report_name_list = ["SALDO NOSTRO)", "MANDATORY DEPOSIT LRA &#38; CRA BCTL", "SALDO TERSEDIA&emsp;*3)", 
                        "NET CASH FLOW (B - C)", "SALDO KUMULATIF", "LIMIT INTERNAL CUMULATIVE MISMATCH PER BUCKET&emsp;*9)", "EXCESS (GAP) TO LIMIT"]
    
    for reports_name in report_name_list :
        html_content = html_content.replace(f'<td class=bold>{reports_name}</td>', f'<td class="bold" colspan="2">{reports_name}</td>')
    
    color_val_col = ["#7AB5DE", "#9DACB6", "#73E563"]
    for val_col, color_col in zip(["val-e", "val-f", "val-g"], color_val_col) :
        html_content = html_content.replace(f'<td class=bold>{val_col}</td>', f'<td style="background-color:{color_col};"></td>')
    
    xsl_fo_content = xsl_fo_content.replace("emsp","#160")
    
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    
    html_content = html_content.replace(">0<", "><")
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, False)
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name,file_path,xsl_fo_content,current_date)
    
    
    
    generated_reports = []
    for i in output_file:

        if i != '.pdf' :

            generate_file_for_other_extension(html_file, i)
            xls_file = html_file.split('.')
            xls_file[-1] = 'xls'
            xls_file = ".".join(xls_file)
            
            generated_reports.append(xls_file)

        else:

            generate_pdf_from_fo_file(xsl_fo_file)
            pdf_file = html_file.split('.')
            pdf_file[-1] = 'pdf'
            pdf_file = ".".join(pdf_file)
            
            generated_reports.append(pdf_file)
        


    SMTPParameters = FParameterUtils.GetFParameters(acm.GetDefaultContext(), 'CustomReportSMTPParameters')
    hostname = str(SMTPParameters.At('SMTPServer'))
    port = int(SMTPParameters.At('SMTPPort').Text())
    username = SMTPParameters.At('EmailUserName').Text()
    password = SMTPParameters.At('SMTPPassword').Text()
    tls_mode = bool(SMTPParameters.At('SecureSMTPConnection').Text())

    # Setup SMTPServer Object
    SMTPServer = ICTCustomFEmailTransfer.SMTPServer(hostname=hostname, port=port, username=username, password=password, tls_mode=tls_mode)
         
    """
    # Setup Message Object
    split_params = email_params.split("\\ ")
    recipients = split_params[0].split(", ")
    subject = process_text(parameter, split_params[1])
    sender = SMTPParameters.At('EmailSender').Text()
    body = process_text(parameter, split_params[2])
    cc = None if len(parameter) <= 3 else split_params[3].split(", ")
    
    MessageObject = ICTCustomFEmailTransfer.Message(recipients, subject, sender, body, cc, generated_reports)
    
    # Send email
    EmailTransfer = ICTCustomFEmailTransfer(SMTPServer, MessageObject)
    
    try:
        EmailTransfer.Send()
        print("Email transfer successful for", report_name)
    except Exception as e:
        print("Email Transfer failed:", e)
    """
