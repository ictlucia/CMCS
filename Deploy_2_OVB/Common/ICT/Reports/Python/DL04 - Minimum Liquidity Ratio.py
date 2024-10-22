from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael
import FParameterUtils
import datetime
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer

def query_val():
    
#    if optkey3 != "" or optkey4 != "" or port != "" or add_filter != "":
        
    port_list = ["FX Spot 1 BMDL", "FX Spot 2 BMDL", "FX Derivatives 1 BMDL", "FX Derivatives 2 BMDL", "IRT DCM 1 BMDL", "IRT DCM 2 BMDL", 
                     "IRT MM Depo Loan Repo RR 1 BMDL", "IRT MM Depo Loan Repo RR 2 BMDL", "BB BOND PL BMDL", "BB BOND AC BMDL", "BB BOND OCI BMDL",
                     "BB BOND SHARIA PL BMDL", "BB BOND SHARIA AC BMDL", "BB BOND SHARIA OCI BMDL", "IBFI 1 BMDL", "CB 1 BMDL", "CB 2 BMDL", "CB 3 BMDL",
                     "CB 4 BMDL", "CB 5 BMDL", "CB 6 BMDL", "GVI 1 BMDL", "GVI 2 BMDL", "Commercial 1 BMDL", "Commercial 2 BMDL", "Commercial 3 BMDL",
                     "Commercial 4 BMDL", "Commercial 5 BMDL", "Commercial 6 BMDL", "LIQ IB BMDL", "LIQ MM BMDL", "SAM 1 BMDL", "SAM 2 BMDL", "SAM 3 BMDL"]
        
    port_null = "(" + ", ".join([f"'{x}'" for x in port_list]) + ")"

    where = "WHERE"

    optkey3_query = " DISPLAY_ID(t, 'optkey3_chlnbr') in ('FX', 'BOND', 'DL', 'SBI')"
            
    optkey4_query = " AND DISPLAY_ID(t, 'optkey4_chlnbr') in ('TOD', 'TOM', 'SPOT', 'FWD', 'NDF', 'NS', 'SWAP', 'OPT', 'CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'INDOIS', 'PBS', 'NCD', 'SVBLCY', 'SVBUSD', 'IDSV', 'CMP', 'CMT', 'OVP', 'OVT')"
            
    portfolio_query = " AND DISPLAY_ID(t, 'prfnbr') in " + port_null
    
    query_string = f"""
    SELECT 
        t.price*t.quantity
    FROM
        Trade t
    """ + where + optkey3_query + optkey4_query + portfolio_query
    
    query_results = sum([x[0] for x in ael.asql(query_string)[1][0]]) if len(ael.asql(query_string)[1][0])!=0 else 0
    
    return f"{float(query_results):,}"
    
 #   else : return 0

def convertUSD(curr,amount):
    if curr=="USD":
        return abs(amount)
    else:
        price = acm.FPrice.Select(f"instrument = {curr} and market='EOD'")
        price_value = 0
        for all_price in price:
            if all_price.Currency().Name()=="USD":
                price_value = all_price.Settle()
        return abs(price_value * amount)

def process_text(ael_params, raw_text):
    processed_string = raw_text.replace("<Date>", acm.Time.DateToday())
    processed_string = processed_string.replace("<Report Name>", ael_params['report_name'])
    return processed_string

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'DL04 - Minimum Liquidity Ratio'}

ael_variables=[
['report_name','Report Name','string', None, 'DL04 - Minimum Liquidity Ratio', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['email_params','Email Params','string', None, 'ribka.siahaan@bankmandiri.co.id, tqatestingbo@gmail.com\\ <Report Name> - <Date>\\ Enclosed <Report Name> report document as of <Date>\\ ', 0,0],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.xls',0,1, 'Select Secondary Extensions Output']
]

def ael_main(parameter):
    html_gen = HTMLGenerator()
    xsl_gen = XSLFOGenerator()
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = str(parameter['output_file'][0])
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
    """

    current_date = datetime.date.today().strftime('%y%m%d')

    date_today = acm.Time.DateToday()

    html_content = html_gen.create_base_html_content("Minimum Liquidity Ratio as per. "+current_date, title_style)
    xsl_fo_content = xsl_gen.prepare_xsl_fo_content("Minimum Liquidity Ratio as per. "+current_date)
    
    html_content = html_gen.prepare_html_table(html_content,['','',''])
    xsl_fo_content = xsl_gen.add_xsl_fo_table_header(xsl_fo_content,['','',''])    
    
    title = 'Central Bank Requirement : Liquidity Ratio'
    
    
    html_content = html_gen.open_table_row(html_content)
    xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)

    html_content = html_gen.add_cell_data(html_content, title,'colspan=3 style=background-color:#324175;color:white;')
    xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,title,'number-columns-spanned="3" background-color="#324175" color="white"')

    
    html_content = html_gen.close_table_row(html_content)
    xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)


    subtitle = ['No','Items','Amount']

    html_content = html_gen.add_data_row(html_content,[subtitle],'style=background-color:#a0c5de;')
    xsl_fo_content = xsl_gen.add_xsl_data_row(xsl_fo_content,[subtitle],'background-color="#a0c5de"')

    list_value = {
                'Vault Cash' : ["('FX')", "('TOD', 'TOM', 'SPOT')", "", ""],
                'Precious Metals (Gold)' : ["", "", "", ""],
                'Deposits with BCTL' : ["", "", "", ""],
                'Deposits in Other Financial Institution' : ["", "", "", ""],
                'Readily Marketable Securities' : ["('BOND')", "('ROI', 'INDOIS')", "", ""],
                'Net Interbank Lending &#38; Borrowing w/remaining mat up to 1 mo' : ["('DL')", "('CMP', 'CMT')", "", ""]
                }
                
                

    
    count = 0
    for key, val in list_value.items():
        #optkey3_val, optkey4_val, port, ops_filter = val
        count += 1
        
        html_content = html_gen.open_table_row(html_content)
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content)
        
        html_content = html_gen.add_cell_data(html_content,count,'style="text-align:right;"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,count,'text-align="right"')
        
        html_content = html_gen.add_cell_data(html_content, key,'style="text-align:left;"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, key,'text-align="left"')
        
        html_content = html_gen.add_cell_data(html_content, query_val(),'style="text-align:right;"')
        
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content, query_val(),'text-align="right"')
        
        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)

    list_total = [
                'Total Highly Liquid Asset',
                'Total Liabilities (DPK)',
                'LIQUIDITY RATIO (Min. 15%)'
                ]

                

    for items in list_total:
        html_content = html_gen.open_table_row(html_content,'style="background-color:#7bdb91;border:0;"')
        xsl_fo_content = xsl_gen.prepare_xsl_row(xsl_fo_content,'background-color="#7bdb91" border="None"')
        
        html_content = html_gen.add_cell_data(html_content,'')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,'')
        
        html_content = html_gen.add_cell_data(html_content,items)
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,items)
        
        html_content = html_gen.add_cell_data(html_content,0,'style="text-align:right;"')
        xsl_fo_content = xsl_gen.add_xsl_column(xsl_fo_content,0,'text-align="right"')

        html_content = html_gen.close_table_row(html_content)
        xsl_fo_content = xsl_gen.close_xsl_row(xsl_fo_content)
    
    xsl_fo_content = xsl_fo_content.replace('page-width="25in"','page-width="15in"')
    
    html_content = html_gen.close_html_table(html_content)
    xsl_fo_content = xsl_gen.close_xsl_table(xsl_fo_content)
    

    html_file = html_gen.create_html_file(html_content, file_path, report_name, current_date, True)
    xsl_fo_file = xsl_gen.create_xsl_fo_file(report_name,file_path,xsl_fo_content,current_date)


    generated_reports = []
    
    if output_file == ".xls" :
        generate_file_for_other_extension(html_file, '.xls')
        
        xls_file = html_file.split('.')
        xls_file[-1] = 'xls'
        xls_file = ".".join(xls_file)
        
        generated_reports.append(xls_file)
        
    elif output_file == ".pdf" :            
        pdf_file = xsl_fo_file.split('.')
        pdf_file[-1] = 'pdf'
        pdf_file = ".".join(pdf_file)
        
        generated_reports.append(pdf_file)
        
        generate_pdf_from_fo_file(xslfo_file)

    SMTPParameters = FParameterUtils.GetFParameters(acm.GetDefaultContext(), 'CustomReportSMTPParameters')
    hostname = str(SMTPParameters.At('SMTPServer'))
    port = int(SMTPParameters.At('SMTPPort').Text())
    username = SMTPParameters.At('EmailUserName').Text()
    password = SMTPParameters.At('SMTPPassword').Text()
    tls_mode = bool(SMTPParameters.At('SecureSMTPConnection').Text())

    # Setup SMTPServer Object
    SMTPServer = ICTCustomFEmailTransfer.SMTPServer(hostname=hostname, port=port, username=username, password=password, tls_mode=tls_mode)
            
    # Setup Message Object
    split_params = email_params.split("\ ")
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






