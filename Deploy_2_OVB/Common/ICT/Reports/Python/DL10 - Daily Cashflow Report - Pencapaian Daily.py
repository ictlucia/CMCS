from datetime import date
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer

def query_result(optkey3="", optkey4="", portfolio=""):    
    
    optkey3_query = "WHERE DISPLAY_ID(t, 'optkey3_chlnbr') in " + optkey3 + "\n" if optkey3 != "" else ""
            
    optkey4_query = " AND DISPLAY_ID(t, 'optkey4_chlnbr') in " + optkey4 + "\n" if optkey4 != "" else ""
            
    portfolio_query = " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio + "\n" if portfolio != "" else ""
            
    query_string = """

            SELECT t.trdnbr, nominal_amount(t) 'Nominal', t.value_day, t.maturity_date, t.curr

            FROM Trade t   
 
        """ + optkey3_query + optkey4_query + portfolio_query
    
    query_results = float(sum([x[1] for x in ael.asql(query_string)[1][0]]) if len(ael.asql(query_string)[1][0]) != 0 else 0)
            
    return f"{query_results:,}"

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

def row_content(list_content, list_style):
     row_content = ""

     for list_content_1d, list_style_1d in zip(list_content, list_style):
          row_content += "<tr>"
          for content, style in zip(list_content_1d, list_style_1d):
               row_content += f'<td style="{style}">{content}</td>\n'
          
          row_content += "</tr>"
     return row_content

def close_html():
     return """
    </table>
</body>
</html>
"""

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'DL10 - Daily Cashflow Report - Pencapaian Daily'}

#settings.FILE_EXTENSIONS

ael_variables=[

['report_name','Report Name','string', None, 'DL10 - Daily Cashflow Report - Pencapaian Daily', 1,0],

['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

['output_file','Output Files','string', ['.xls', '.pdf'], '.xls', 0 , 0, 'Select Output Extension Type'],

['email_params','Email Params','string', None, 'ribka.siahaan@bankmandiri.co.id, tqatestingbo@gmail.com\\ <Report Name> - <Date>\\ Enclosed <Report Name> report document as of <Date>\\ ', 0,0],

]

def process_text(ael_params, raw_text):
    processed_string = raw_text.replace("<Date>", acm.Time.DateToday())
    processed_string = processed_string.replace("<Report Name>", ael_params['report_name'])
    return processed_string

def ael_main(parameter):
     report_name = parameter['report_name']
     file_path = str(parameter['file_path'])
     output_file = "".join(parameter['output_file'])
     date_today = date.today().strftime('%y%m%d')
     email_params = str(parameter['email_params'])
     
     
     
     port_list = "('BB BOND PL BMDL', 'BB BOND AC BMDL', 'BB BOND OCI BMDL', 'BB BOND SHARIA PL BMDL', 'BB BOND SHARIA AC BMDL', 'BB BOND SHARIA OCI BMDL', 'IBFI 1 BMDL', 'CB 1 BMDL', 'CB 2 BMDL', 'CB 3 BMDL', 'CB 4 BMDL', 'CB 5 BMDL', 'CB 6 BMDL', 'GVI 1 BMDL', 'GVI 2 BMDL', 'Commercial 1 BMDL', 'Commercial 2 BMDL', 'Commercial 3 BMDL', 'Commercial 4 BMDL', 'Commercial 5 BMDL', 'Commercial 6 BMDL', 'SAM 1 BMDL', 'SAM 2 BMDL', 'SAM 3 BMDL', 'FX with Customer BMDL')"
     optkey3_list = "('BOND', 'FX', 'SBI')"
     optkey4_list = "('TOD', 'TOM', 'SPOT', 'FWD', 'NDF', 'NS', 'SWAP', 'OPT', 'CBUSD', 'CBVALAS', 'UST', 'BILLS', 'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 'SPN', 'SPNS', 'FR', 'INDOIS', 'PBS', 'NCD', 'SVBLCY', 'SVBUSD', 'IDSV')"
     
     list_content_head = [["Daily Performance as of", "10/6/2022", "", ""]]
     list_style_head = [["font-weight: bold;", "font-weight: bold; text-align: right;", "", ""]]

     nil_content = [["", "", "", ""]]
     first_content = [
          ["", "in USD", "", ""],
          ["Int Income Bonds", query_result(optkey3_list, optkey4_list, port_list), "", ""],
          ["FBI FX Remittance", query_result(optkey3_list, optkey4_list, port_list), "", ""],
          ["", "", "", "1 Jan - today"]
          ]

     unNil_style = [["border : 1px black solid", "border : 1px black solid; text-align: right;", "", ""]]

     list_content = first_content + nil_content * 3 + [["RE APR 2022", query_result(optkey3_list, optkey4_list, port_list), "", ""]]
     list_style_content =  nil_content + unNil_style * 2 + nil_content * 4 + unNil_style
     
     generated_reports = []
     if output_file == ".xls" :
        html_code = open_code_html()
        html_code += row_content(list_content_head, list_style_head)
        html_code += row_content(list_content, list_style_content)
    
        folder_path = os.path.join(file_path, "report"+date_today)
        create_folder_if_not_exists(folder_path)
        file_name = os.path.join(folder_path, report_name+output_file)
        f = open(file_name, "w")
        f.write(html_code)
        f.close()
        
        xls_file = file_name.split('.')
        xls_file[-1] = 'xls'
        xls_file = ".".join(xls_file)

        generated_reports.append(xls_file)
     else :
        pdf_gen = XSLFOGenerator()
        title = "Daily Performance as of 10/6/2022"
        xsl_fo_content = pdf_gen.prepare_xsl_fo_content(title)
        xsl_fo_content = pdf_gen.add_xsl_fo_table_header(xsl_fo_content, ['', '', '', ''], 'background-color="white" border="0px"')
        for content in list_content:
            if content[0] == "":
                xsl_fo_content = pdf_gen.add_xsl_data_row(xsl_fo_content, [content], 'border="2px solid white"')
            else:
                xsl_fo_content = pdf_gen.add_xsl_data_row(xsl_fo_content, [content], 'border-top="2px solid black" border-bottom="2px solid black"')
        xsl_fo_content = pdf_gen.close_xsl_table(xsl_fo_content)
        xslfo_file = pdf_gen.create_xsl_fo_file(report_name, file_path, xsl_fo_content, "10/6/2022")
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
