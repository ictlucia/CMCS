from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael
import datetime
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer
import datetime

def getPNLTrade(tradenumber):
    context = acm.GetDefaultContext()
    sheetType = 'FTradeSheet'
    ins = acm.FTrade[tradenumber]
    columnId = "Portfolio Total Profit and Loss"
    calcSpace = acm.Calculations().CreateCalculationSpace(context, sheetType)
    result1 = calcSpace.CreateCalculation(ins, columnId).FormattedValue()
    result2 = result1.replace("#","")
    result3 = result2.replace(",","")
    result4 = result3.replace(".","")
    return int(result4)
    
def getinsnum(insid):
    insnum = acm.FInstrument[insid].Oid()
    return insnum
    
def process_text(ael_params, raw_text):
    processed_string = raw_text.replace("<Date>", acm.Time.DateToday())
    processed_string = processed_string.replace("<Report Name>", ael_params['report_name'])
    return processed_string
    
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'DL09 - Daily Cashflow Report - PDN'}



ael_variables=[
['report_name','Report Name','string', None, 'DL09 - Daily Cashflow Report - PDN', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output'],
['email_params','Email Params','string', None, 'ribka.siahaan@bankmandiri.co.id, tqatestingbo@gmail.com\\ <Report Name> - <Date>\\ Enclosed <Report Name> report document as of <Date>\\ ', 0,0],

]




def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    email_params = str(parameter['email_params'])
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
        
        th {
            background-color:white;
            font-weight : Normal;
            border : None
        }
        
        .left {
            text-align:left;
        }
        .right {
            text-align:right;
        }
        .center {
            text-align:center;
        }
        
        .bold {
            font-weight:bold;
        }
        
        .header_table {
            font-weight:bold;
            background-color : blue;
            color : white
        }
        
    """
    current_date = datetime.date.today().strftime('%y%m%d')
    utc_time = datetime.datetime.now()
    date_today = acm.Time.DateToday()
    html_content = html_gen.create_base_html_content("LAPORAN POSISI DEVISA NETTO", title_style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("LAPORAN POSISI DEVISA NETTO")
    
    html_content += "<br><div>UNIT KERJA &#8195;&#8195;&#8195;&#8195;&#8195;&#8195; MANDIRI DILI-TIMOR LESTE</div>"
    xsl_fo_content +="<fo:block>UNIT KERJA &#8195;&#8195;&#8195;&#8195;&#8195;&#8195; BANK MANDIRI DILI</fo:block>"
    
    
    html_content += "<div>TANGGAL PELAPORAN &#8195;"+str(utc_time)+"</div><br>"
    xsl_fo_content +="<fo:block>TANGGAL PELAPORAN &#8195;"+str(utc_time)+"</fo:block>"
    
    
    in_usd = ['','','','','(In USD)']
    title = ['DESKRIPSI SANDI','VALUTA','TOTAL NERACA','TOTAL ADM','POSISI NETTO']
    html_content = html_gen.prepare_html_table(html_content,in_usd)
    html_content = html_gen.add_data_row(html_content,[title], 'class=header_table')
    
    html_content = html_gen.open_table_row(html_content)
    html_content = html_gen.add_cell_data(html_content,'a', 'class=header_table')
    html_content = html_gen.add_cell_data(html_content,'b', 'class=header_table')
    html_content = html_gen.add_cell_data(html_content,'c', 'class=header_table')
    html_content = html_gen.add_cell_data(html_content,'d', 'class=header_table')
    html_content = html_gen.add_cell_data(html_content,'ABS (c+d)', 'class=header_table')
    html_content = html_gen.close_table_row(html_content)
    
    xsl_fo_content = xsl_gen.add_xsl_fo_table_header(xsl_fo_content,title,'background-color="blue" color="white"')
    
    
    currency = {
                "Australian Dollar":['AUD','28,438','-','28,438'],
                "Brunei Dollar":['BND','-','-','-'],
                "Canadian Dollar":['CAD','-','-','-'],
                "Swiss Franc": ['CHF','-','-','-'],
                "Chinese Yuan": ['CNY','(24,606)','-','(24,606)'],
                "Danish Kroner": ['DKK','-','-','-'],
                "Euro Currency": ['EUR','49,604,975','(49,629,213)','975,762'],
                "UK Pound Sterling":['GBP','(20,909)','-','(20,909)'],
                "Hongkong Dollar":['HKD','(489,973)','-','(489,973)'],
                "Indonesian Rupiah": ['IDR','-','-','-'],
                "Japanese Yen":['JPY','8,095','-','8,095'],
                "Malaysian Ringgit":['MYR','-','-','-'],
                "Norwegian Kroner":['NOK','-','-','-'],
                "New Zealand Dollar":['NZD','684','-','684'],
                "Saudi Arabian Riyal":['SAR','-','-','-'],
                "Swedish Kroner":['SEK','-','-','-'],
                "Singapore Dollar":['SGD','62,547','-','62,547'],
                "Thailand Baht":['THB','-','-','-'],
                "US Dollar":['USD','-','-','-']
                }
                
    for keys,value in currency.items():
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        
        html_content = html_gen.add_cell_data(html_content,keys,'class="left"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,keys,'text-align="left"')
        
        html_content = html_gen.add_cell_data(html_content,value[0],'class="center"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,value[0],'text-align="center"')
        
        html_content = html_gen.add_cell_data(html_content,value[1],'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,value[1],'text-align="right"')
        
        
        html_content = html_gen.add_cell_data(html_content,value[2],'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,value[2],'text-align="right"')
        
        
        html_content = html_gen.add_cell_data(html_content,value[3],'class="right"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,value[3],'text-align="right"')
        
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
        
    
    non_idr_ccy = ['Total non-IDR ccy',0,0,0,0]
    idr_ccy = ['Indonesian Rupiah','IDR',0,0,0]
    bmhk_nop=['','','','BMDL NOP',0]
    
    html_content = html_gen.add_data_row(html_content,[non_idr_ccy],"class='bold'")
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[non_idr_ccy],'font-weight="bold"')
    
    html_content = html_gen.add_data_row(html_content,[idr_ccy])
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[idr_ccy])
    
    
    html_content = html_gen.add_data_row(html_content,[bmhk_nop],"class='bold'")
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[bmhk_nop],'font-weight="bold"')
    
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    
    
    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True)
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
            pdf_file = xsl_fo_file.split('.')
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
