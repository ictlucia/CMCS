import ael, acm
import os
from math import ceil
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from FReportUtils import *
from datetime import date
import datetime
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer

## IMPORT XSL FILE FROM FXSLTEMPLATE
context = acm.GetDefaultContext()
xslExtension = context.GetExtension("FXSLTemplate", "FObject", "DL01")
xsl = xslExtension.Value()
## GETTING IDR RATE
def idr_rate(trade):
    instrument = trade.Instrument()
    ins_name = instrument.Name()
    for i in range(len(instrument.Prices())):
        market = instrument.Prices()[i].Market().Name()
        curr = instrument.Prices()[i].Currency().Name()
        if market == "REFINITIV_SPOT" and curr == "IDR" and ins_name != "IDR":
            return (
                instrument.Prices()[i].Settle()
                if instrument.Prices()[i].Settle() != None
                else 0
            )
        else:
            0


def xsl_generate(data):
    open_code = '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type = "text/xsl" href = "main.xsl"?>\n<data1>'
    val_params = ""
    for val in data:
        val_params += f"""
        <cust>
            <pengirim>{val[0]}</pengirim>
            <lamp>{val[1]}</lamp>
            <kode>{val[2]}</kode>
            <curr>{val[3]}</curr>
            <usdAmount>{val[4]}</usdAmount>
            <bankPos>{val[5]}</bankPos>
            <rate>{val[6]}</rate>
            <idrAmount>{val[7]}</idrAmount>
            <usd>{val[8]}</usd>
            <idr>{val[9]}</idr>
            <cost>{val[10]}</cost>
            <profit>{val[11]}</profit>
            <remittanceFee>{val[12]}</remittanceFee>
            <rek>{val[13]}</rek>
            <namaPenerima>{val[14]}</namaPenerima>
            <bankPenerima>{val[15]}</bankPenerima>
            <sumberDana>{val[16]}</sumberDana>
            <telp>{val[17]}</telp>
            <alamat>{val[18]}</alamat>
            <idPengirim>{val[19]}</idPengirim>
            <kewarganegaraan>{val[20]}</kewarganegaraan>
            <localId>{val[21]}</localId>
            <trx>{val[22]}</trx>
            <status>{val[23]}</status>
            <gender>{val[24]}</gender>
            <tahunLahir>{val[25]}</tahunLahir>
            <kodeWn>{val[26]}</kodeWn>
            <no>{val[27]}</no>
        </cust>
    """
    return open_code + val_params + "</data1>"


ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "DL01 - Add Fill-in Boxes Option in Remittance Activities",
}
# settings.FILE_EXTENSIONS
ael_variables = [
    [
        "report_name",
        "Report Name",
        "string",
        None,
        "DL01 - Add Fill-in Boxes Option in Remittance Activities",
        1,
        0,
    ],
    [
        "email_params",
        "Email Params",
        "string",
        None,
        "ribka.siahaan@bankmandiri.co.id, tqatestingbo@gmail.com\\ <Report Name> - <Date>\\ Enclosed <Report Name> report document as of <Date>\\ ",
        0,
        0,
    ],
    [
        "file_path",
        "Folder Path",
        getFilePathSelection(),
        None,
        getFilePathSelection(),
        1,
        1,
    ],
    [
        "output_file",
        "Output Files",
        "string",
        [".xls", ".pdf"],
        ".pdf",
        0,
        0,
        "Select Output Extension Type",
    ],
]


def add_xsl_fo_table_header(
    xsl_fo_content,
    header_list,
    header_styling="padding='8pt' border-width='1px' border-style='solid'",
):
    xsl_fo_table = """<fo:table margin-bottom="50px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto">
    """
    for header in header_list:
        xsl_fo_table += """ <fo:table-column border-width="1px" border-style="solid" column-width="auto"/>
        """
    xsl_fo_table += """ <fo:table-column border-width="1px" border-style="solid" column-width="auto"/>"""
    xsl_fo_table += """<fo:table-header background-color="#16ab11" color="#ffffff" font-weight="bold" font-size="12px">\n<fo:table-row>
    """
    for header in header_list:
        span = (
            'number-columns-spanned="2"'
            if header == "Accumulated Position"
            else 'number-rows-spanned="2"'
        )
        xsl_fo_table += (
            f"""<fo:table-cell {span} {header_styling}><fo:block>"""
            + str(header)
            + """</fo:block></fo:table-cell>
        """
        )
    xsl_fo_table += """</fo:table-row>"""
    xsl_fo_table += """<fo:table-row>"""
    subheader_list = ["USD", "IDR"]
    for subheader in subheader_list:
        xsl_fo_table += (
            f"""<fo:table-cell {header_styling}><fo:block>"""
            + str(subheader)
            + """</fo:block></fo:table-cell>"""
        )
    xsl_fo_table += """</fo:table-row></fo:table-header>\n<fo:table-body>"""
    return xsl_fo_content + xsl_fo_table


def add_xsl_data_row(
    xsl_content,
    row_data,
    cell_styling="border-width='1px' border-style='solid' padding='8pt'",
    block_styling="font-size='8px'",
):
    xsl_content += """
        """
    mod_last_row = len(row_data) % 3
    for i_row in range(len(row_data)):
        row = row_data[i_row]
        xsl_content += """<fo:table-row>
            """
        span = f'number-rows-spanned="{3 if i_row != (len(row_data) - mod_last_row) else mod_last_row}"'
        for i in range(len(row) - 1):
            cell = row[i]
            if i == 1 and int(row[-1]) % 3 == 1:
                xsl_content += (
                    f"""<fo:table-cell {cell_styling} {span}><fo:block {block_styling}>"""
                    + str(cell)
                    + """</fo:block></fo:table-cell>"""
                )
            if i != 1:
                xsl_content += (
                    f"""<fo:table-cell {cell_styling}><fo:block {block_styling}>"""
                    + str(cell)
                    + """</fo:block></fo:table-cell>"""
                )
        xsl_content += """</fo:table-row>
            """
    return xsl_content


def xslfo_gen(header, data, file_name, file_path, date):
    cell_styling = (
        "border-width='1px' border-style='solid' padding='8pt' column-width='auto'"
    )
    gen = XSLFOGenerator()
    title = "Sample Blotter"
    title_styling = 'margin-bottom="30px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto" font-weight = "bold" font-size = "24px"'
    xsl_fo_content = gen.prepare_xsl_fo_content(title, title_styling)
    xsl_fo_content = add_xsl_fo_table_header(xsl_fo_content, header)
    xsl_fo_content = add_xsl_data_row(xsl_fo_content, data, cell_styling)
    xsl_fo_content = gen.close_xsl_table(xsl_fo_content)
    xsl_fo_file = gen.create_xsl_fo_file(file_name, file_path, xsl_fo_content, date)
    return xsl_fo_file


def process_text(ael_params, raw_text):
    processed_string = raw_text.replace("<Date>", acm.Time.DateToday())
    processed_string = processed_string.replace(
        "<Report Name>", ael_params["report_name"]
    )
    return processed_string


def ael_main(parameter):
    report_name = parameter["report_name"]
    file_path = str(parameter["file_path"])
    output_file = "".join(parameter["output_file"])
    email_params = str(parameter["email_params"])
    date_today = datetime.date.today().strftime("%y%m%d")
    query = """
        SELECT trdnbr FROM Trade t 
        WHERE
            DISPLAY_ID(t, 'prfnbr') = 'FX with Customer BMDL' AND
            DISPLAY_ID(t, 'optkey3_chlnbr') = 'FX' AND
            DISPLAY_ID(t, 'optkey4_chlnbr') in ('TOD', 'TOM', 'SPOT', 'FWD', 'NDF', 'NS', 'SWAP', 'OPT')
        """
    query_result = ael.asql(query)
    trades = []
    for row in query_result[1][0]:
        trades.append(row[0])
    no = 1
    header = [
        "PENGIRIM",
        "LAMP",
        "DEALCODE/TRX",
        "CURRENCY",
        "USD AMOUNT",
        "BANK POSITION",
        "RATE",
        "IDR AMOUNT",
        "Accumulated Position",
        "Cost",
        "Profit (Dari Spread)",
        "Remittance Fee",
        "NO REKENING TUJUAN",
        "NAMA PENERIMA",
        "BANK PENERIMA",
        "SUMBER DANA",
        "NO TLP PENGIRIM",
        "ALAMAT PENGIRIM",
        "NO ID PENGIRIM",
        "KEWARGANEGARAAN",
        "LOCAL ID",
        "TUJUAN TRX",
        "STATUS",
        "JENIS KELAMIN",
        "TAHUN LAHIR",
        "KODE WN",
    ]
    data = []
    codeWn = {"Indonesia": "ID", "Timor Leste": "TL", "Bangladesh": "BD", "China": "CN"}
    for trade_nbr in trades:
        trade = acm.FTrade[trade_nbr]
        if (
            trade.Type() == "Account Transfer"
            and trade.ValueDay() == str(datetime.date.today())
            and trade.Trade().TradeConnections().At(1).FromTrade().Oid()
            == trade.Trade().Oid()
        ):
            date = trade.ValueDay()
            name = trade.Trade().Acquirer().Accounts().First().Name()
            usdAmount = abs(trade.Trade().Payments().First().Amount())
            bankPos = "BUY" if usdAmount >= 0 else "SELL"
            idrRate = idr_rate(trade)
            idrAmount = idrRate * usdAmount if idrRate != None else 0
            remittanceFee = (
                o
                if trade.Trade().Payments().First().Amount() == 0
                else 1
                if trade.Trade().Payments().First().Amount() < 100
                else 2
                if trade.Trade().Payments().First().Amount() < 1000
                else 3
            )
            receiver = (
                trade.Trade()
                .TradeConnections()
                .At(1)
                .ToTrade()
                .Acquirer()
                .Accounts()
                .First()
                .Name()
                if trade.Trade().TradeConnections().At(1).FromTrade().Oid()
                == trade.Trade().Oid()
                else None
            )
            senderTelp = trade.Trade().Acquirer().Telephone()
            senderAddress = trade.Trade().Acquirer().Address()
            senderId = trade.Name()
            senderCountry = trade.Trade().Acquirer().Country()
            lamp = ceil(no / 12)
            codeWN = codeWn[senderCountry]
            data.append(
                [
                    name,
                    lamp,
                    "-",
                    "-",
                    usdAmount,
                    bankPos,
                    idrRate,
                    idrAmount,
                    usdAmount,
                    idrAmount,
                    idrRate,
                    "-",
                    remittanceFee,
                    "-",
                    "-",
                    receiver,
                    "-",
                    senderTelp,
                    senderAddress,
                    senderCountry,
                    senderId,
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    codeWN,
                    no,
                ]
            )
            data.append(
                [
                    name,
                    lamp,
                    "-",
                    "-",
                    usdAmount,
                    bankPos,
                    idrRate,
                    idrAmount,
                    usdAmount,
                    idrAmount,
                    idrRate,
                    "-",
                    remittanceFee,
                    "-",
                    "-",
                    receiver,
                    "-",
                    senderTelp,
                    senderAddress,
                    senderCountry,
                    senderId,
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    codeWN,
                    2,
                ]
            )
            data.append(
                [
                    name,
                    lamp,
                    "-",
                    "-",
                    usdAmount,
                    bankPos,
                    idrRate,
                    idrAmount,
                    usdAmount,
                    idrAmount,
                    idrRate,
                    "-",
                    remittanceFee,
                    "-",
                    "-",
                    receiver,
                    "-",
                    senderTelp,
                    senderAddress,
                    senderCountry,
                    senderId,
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    codeWN,
                    3,
                ]
            )
            data.append(
                [
                    name,
                    lamp,
                    "-",
                    "-",
                    usdAmount,
                    bankPos,
                    idrRate,
                    idrAmount,
                    usdAmount,
                    idrAmount,
                    idrRate,
                    "-",
                    remittanceFee,
                    "-",
                    "-",
                    receiver,
                    "-",
                    senderTelp,
                    senderAddress,
                    senderCountry,
                    senderId,
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    codeWN,
                    4,
                ]
            )
            data.append(
                [
                    name,
                    lamp,
                    "-",
                    "-",
                    usdAmount,
                    bankPos,
                    idrRate,
                    idrAmount,
                    usdAmount,
                    idrAmount,
                    idrRate,
                    "-",
                    remittanceFee,
                    "-",
                    "-",
                    receiver,
                    "-",
                    senderTelp,
                    senderAddress,
                    senderCountry,
                    senderId,
                    "-",
                    "-",
                    "-",
                    "-",
                    "-",
                    codeWN,
                    5,
                ]
            )
            no += 1
    xml_file = xsl_generate(data)
    html_file = transformXML(xml_file, "DL01")
    generated_reports = []
    if output_file == ".html":
        generate_html = HTMLGenerator().create_html_file(
            html_file, file_path, report_name, date_today, False
        )
        generated_reports.append(generate_html)
    elif output_file == ".xls":
        generate_html = HTMLGenerator().create_html_file(
            html_file, file_path, report_name, date_today, False
        )
        generate_file_for_other_extension(generate_html, ".xls")
        xls_file = generate_html.split(".")
        xls_file[-1] = "xls"
        xls_file = ".".join(xls_file)
        generated_reports.append(xls_file)
        os.remove(os.path.join(file_path, f"report{date_today}", f"{report_name}.html"))
    elif output_file == ".pdf":
        xslfo_file = xslfo_gen(header, data, report_name, file_path, date_today)
        pdf_file = xslfo_file.split(".")
        pdf_file[-1] = "pdf"
        pdf_file = ".".join(pdf_file)
        generated_reports.append(pdf_file)
        generate_pdf_from_fo_file(xslfo_file)
    SMTPParameters = FParameterUtils.GetFParameters(
        acm.GetDefaultContext(), "CustomReportSMTPParameters"
    )
    hostname = str(SMTPParameters.At("SMTPServer"))
    port = int(SMTPParameters.At("SMTPPort").Text())
    username = SMTPParameters.At("EmailUserName").Text()
    password = SMTPParameters.At("SMTPPassword").Text()
    tls_mode = bool(SMTPParameters.At("SecureSMTPConnection").Text())
    # Setup SMTPServer Object
    SMTPServer = ICTCustomFEmailTransfer.SMTPServer(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        tls_mode=tls_mode,
    )
    # Setup Message Object
    split_params = email_params.split("\\ ")
    recipients = split_params[0].split(", ")
    subject = process_text(parameter, split_params[1])
    sender = SMTPParameters.At("EmailSender").Text()
    body = process_text(parameter, split_params[2])
    cc = None if len(parameter) <= 3 else split_params[3].split(", ")
    MessageObject = ICTCustomFEmailTransfer.Message(
        recipients, subject, sender, body, cc, generated_reports
    )
    # Send email
    EmailTransfer = ICTCustomFEmailTransfer(SMTPServer, MessageObject)
    try:
        EmailTransfer.Send()
        print("Email transfer successful for", report_name)
    except Exception as e:
        print("Email Transfer failed:", e)
