from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import test_new_html as html_gen
import acm, ael


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
            
def get_data(optkey3='',optkey4='',bank='',type='',time_bucket=''):
    
    #Setting the Blank Value
    if optkey3 == '' and optkey4 == '' and bank == '' and type == '':
        return " "
    else:
        optkey3_query = ""
        optkey4_query = ""
        bank_query = ""
        type_query = ""
        time_query = ""
        end_date = "i.exp_day"
        
        date_today = acm.Time.DateToday()
        
        if optkey3=="FX":
            end_date="t.value_day"
        
        #Setting up Date Mapping
        if time_bucket == date_today:
            time_query = " and "+end_date+" >'"+ acm.Time.DateAddDelta(date_today,0,0,-1) +"' and "+end_date+" <= '" + date_today +"'"
            
        elif time_bucket == "Next Day":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,0,1) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,0,2) + "'"
        
        elif time_bucket == "2 - 7 Days":
            time_query = " and "+end_date+" >'" + acm.Time.DateAddDelta(date_today,0,0,2) +"' and "+end_date+" <= '" + acm.Time.DateAddDelta(date_today,0,0,8) + "'"
        
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
            optkey3_query = "and optkey3_chlnbr="+str(get_optkey3_oid(optkey3))
            
        if optkey4:
            optkey4_query = "and optkey4_chlnbr="+str(get_optkey4_oid(optkey4))
            
            
        #Setting up the Query
        query = f"""
                SELECT SUM(t.price*t.quantity) FROM trade t, instrument i, party p 
                where t.insaddr=i.insaddr and t.counterparty_ptynbr = p.ptynbr 
                """ + optkey3_query + optkey4_query + time_query + bank_query + type_query


        result = ael.asql(query)
        if result[1][0]:
            return result[1][0][0][0]
        else:
            return 0
        

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'HKO03 - Daily Cashflow Report'}

ael_variables=[
['report_name','Report Name','string', None, 'HKO03 - Daily Cashflow Report', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['currency','Currency Of Choice','string',['USD','EUR','IDR','CNY','AUD','JPY','GBP','HKD'],'USD',0,0],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output']
]
def ael_main(parameter):
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
    """
    
    current_date = get_current_date("/")
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content("Daily Cashflow Report - Cashflow - "+current_date, title_style)
    
    title = ['Deskripsi',currency]
    html_content = html_gen.prepare_html_table(html_content,title)
    html_content = html_content.replace('<th>'+currency+'</th>','<th colspan=7 style=background-color:blue;color:white>'+currency+'</th>')
    html_content = html_content.replace('<th>Deskripsi</th>','<th rowspan=2>Deskripsi</th>')
    
    time_bucket = [[date_today,'Next Day','2 - 7 Days','8 days - 1 Month','1-2 Months','2-3 Months','3-6 months']]
    
    
    
    #Adding Time Bucket
    html_content = html_gen.add_data_row(html_content,time_bucket)
    
    #Adding row [A.Saldo Nostro]
    saldo_nostro = ['A.  SALDO NOSTRO']
    
    list_value_a=[]
    
    #Function for Populating Saldo Nostro
    for subrow in saldo_nostro:
        temp_row =[]
        temp_row.append(subrow)
        for items in range(len(time_bucket[0])):
            temp_row.append('')
        list_value_a.append(temp_row)
        
    html_content = html_gen.add_data_row(html_content,list_value_a,'','style="text-align: left; font-weight:bold"')
    
    
    
    #Adding row [B.Inflow]
    sub_row_b = {
                'B.  INFLOW':['','','',''],
                'Penempatan Interbank Jatuh Tempo':['DL','','Correspondent Bank','Loan'],
                'Pinjaman Interbank':['DL','','Correspondent Bank','Deposit'],
                'Penempatan Interoffice Jatuh Tempo':['DL','','Interbank','Loan'],
                'Pinjaman Interoffice':['DL','','Interbank','Deposit'],
                'Borrowing (BA Financing/Term Loan)':['DL','BA','','Deposit'],
                'Trade Finance Jatuh Tempo':['','','',''],
                'Usance Jatuh Tempo':['','','',''],
                'Risk Part':['','','',''],
                'TR Jatuh Tempo':['','','',''],
                'Others (Jatuh Tempo)':['','','',''],
                'Penerimaan Trade Services':['','','',''],
                'Securities Jatuh Tempo':['','','',''],
                'Pelunasan Pinjaman Nasabah (Pokok & Bunga)':['','','',''],
                'Lainnya':['','','',''],
                '':['','','',''],
                'ADDITIONAL VARIABLES FOR NON BANK INSTITUTION':['','','',''],
                'Deposito / DOC Jatuh Tempo':['','','',''],
                'Penjualan Obligasi (proprietary trading)':['','','',''],
                'Pembelian USD':['FX','TOD','','Buy'],
                'Pelunasan Funding Bonds & IPO':['','','',''],
                'Sub Total Inflow':['','','','']
                }
                
    
    
    #List for the values
    list_value_b=[]
    
    
    #Function for Populating Inflow Values
    for key, value in sub_row_b.items():
        temp_row = []
        temp_row.append(key)
        for time in time_bucket[0]:
            val = get_data(value[0],value[1],value[2],value[3],time)
            temp_row.append(val)            
        list_value_b.append(temp_row)
        
    html_content = html_gen.add_data_row(html_content,list_value_b,'','style="text-align: left;"')
    html_content = html_content.replace('<td style="text-align: left;">B.  INFLOW</td>','<td style="text-align: left;font-weight:bold">B.  INFLOW</td>')
    
    
    #Adding row [C. Outflow]
    sub_row_c ={
                'C.  OUTFLOW':['','','',''], 
                'Penempatan Interbank':['DL','','Correspondent Bank','Deposit'],
                'Pinjaman Interbank Jatuh Tempo':['DL','','Correspondent Bank','Loan'],
                'Penempatan Interoffice':['DL','','Interbank','Deposit'],
                'Pinjaman Interoffice Jatuh Tempo':['DL','','Interbank','Loan'],
                'Borrowing (BA Financing/Term Loan) Jatuh Tempo':['','','',''],
                'Penarikan Trade Finance':['','','',''],
                'Usance':['','','',''],
                'L/C issued':['','','',''],
                'Acceptance':['','','',''],
                'Others':['','','',''],
                'Deposit Nasabah Jatuh Tempo':['','','',''],
                'Pembelian Securities':['','','',''],
                'Penarikan Pinjaman Nasabah':['','','',''],
                'Saldo Nostro':['','','',''],
                'Current Account (Customer Fund)':['','','',''],
                'Lainnya':['','','',''],
                'ADDITIONAL VARIABLES FOR NON BANK INSTITUTION':['','','',''],
                'Penempatan Deposito / DOC':['','','',''],
                'Pembelian Obligasi (proprietary trading)':['','','',''],
                'Penjualan USD':['FX','TOD','','Sell'],
                'Funding Bonds & IPO':['','','',''],
                'Biaya Operasional':['','','',''],
                'Sub Total Outflow':['','','','']
                }
                
    #List for the values
    list_value_c=[]
    
    
    #Function for Populating Values
    for key, value in sub_row_c.items():
        temp_row = []
        temp_row.append(key)
        for time in time_bucket[0]:
            val = get_data(value[0],value[1],value[2],value[3],time)
            temp_row.append(val)            
        list_value_c.append(temp_row)
        
    html_content = html_gen.add_data_row(html_content,list_value_c,'','style="text-align:left;"')
    html_content = html_content.replace('<td style="text-align:left;">C.  OUTFLOW</td>','<td style="text-align:left;font-weight:bold">C.  OUTFLOW</td>')
    
    
    #Adding row [D. Net Cash Flow (B - C)]
    net_cashflow = ['D.  NET CASH FLOW (B - C)']
    
    list_value_d=[]
    
    #Function for Populating Saldo Nostro
    for subrow in net_cashflow:
        temp_row =[]
        temp_row.append(subrow)
        for items in range(len(time_bucket[0])):
            temp_row.append('')
        list_value_d.append(temp_row)
        
    html_content = html_gen.add_data_row(html_content,list_value_d,'','style="text-align: left;font-weight:bold"')
    
    
    #Adding row [E. Saldo Kumulatif]
    saldo_kumulatif = ['E.  SALDO KUMULATIF']
    
    list_value_e=[]
    
    #Function for Populating Saldo Nostro
    for subrow in saldo_kumulatif:
        temp_row =[]
        temp_row.append(subrow)
        for items in range(len(time_bucket[0])):
            temp_row.append('')
        list_value_e.append(temp_row)
        
    html_content = html_gen.add_data_row(html_content,list_value_e,'','style="text-align: left;font-weight:bold"')
    html_content = html_gen.close_html_table(html_content)
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True, True)

    
    
    
    
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
            
    #try:
    #    os.remove(xsl_fo_file)
    #except:
    #    pass
