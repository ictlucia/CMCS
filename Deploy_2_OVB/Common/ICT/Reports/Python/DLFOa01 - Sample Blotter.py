import ael, acm
import os
from math import ceil
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from FReportUtils import *
from datetime import date, datetime
import FParameterUtils
from ICTCustomFEmailTransfer import ICTCustomFEmailTransfer

## IMPORT XSL FILE FROM FXSLTEMPLATE
context = acm.GetDefaultContext()
xslExtension = context.GetExtension("FXSLTemplate", "FObject", "DLFO01")
xsl = xslExtension.Value()
## GETTING CURRENCY RATE
def curr_rate(trade, curr_to):
    instrument = trade.Instrument()
    for i in range(len(instrument.Prices())):
        market = instrument.Prices()[i].Market().Name()
        curr = instrument.Prices()[i].Currency().Name()
        if market == "REFINITIV_SPOT" and curr == curr_to:
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
            <no>{val[0]}</no>
            <date>{val[1]}</date>
            <pengirim>{val[2]}</pengirim>
            <lamp>{val[3]}</lamp>
            <kode>{val[4]}</kode>
            <curr>{val[5]}</curr>
            <usdAmount>{val[6]}</usdAmount>
            <bankPos>{val[7]}</bankPos>
            <rate>{val[8]}</rate>
            <idrAmount>{val[9]}</idrAmount>
            <usd>{val[10]}</usd>
            <idr>{val[11]}</idr>
            <cost>{val[12]}</cost>
            <profit>{val[13]}</profit>
            <remittanceFee>{val[14]}</remittanceFee>
            <rek>{val[15]}</rek>
            <namaPenerima>{val[16]}</namaPenerima>
            <bankPenerima>{val[17]}</bankPenerima>
            <sumberDana>{val[18]}</sumberDana>
            <telp>{val[19]}</telp>
            <alamat>{val[20]}</alamat>
            <idPengirim>{val[21]}</idPengirim>
            <kewarganegaraan>{val[22]}</kewarganegaraan>
            <localId>{val[23]}</localId>
            <trx>{val[24]}</trx>
            <status>{val[25]}</status>
            <gender>{val[26]}</gender>
            <tahunLahir>{val[27]}</tahunLahir>
            <costRemittanceFee>{val[28]}</costRemittanceFee>
        </cust>
    """
    return open_code + val_params + "</data1>"


ael_gui_parameters = {
    "runButtonLabel": "&&Run",
    "hideExtraControls": True,
    "windowCaption": "DLFOa01 - Sample Blotter",
}
# settings.FILE_EXTENSIONS
ael_variables = [
    ["report_name", "Report Name", "string", None, "DLFOa01 - Sample Blotter", 1, 0],
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
        ".xls",
        0,
        0,
        "Select Output Extension Type",
    ],
    [
        "email_params",
        "Email Params",
        "string",
        None,
        "ribka.siahaan@bankmandiri.co.id, tqatestingbo@gmail.com\\ <Report Name> - <Date>\\ Dear Sir / Madam, <br><br><Report Name> as of <Date>\\ ",
        0,
        0,
    ],
]


def prepare_xsl_fo_content(title, total_col, title_styling=""):
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


def add_xsl_data_row(
    xsl_content,
    row_data,
    cell_styling="border-width='1px' border-style='solid' padding='8pt'",
    block_styling="",
):
    for row in row_data:
        xsl_content += """<fo:table-row>\n""" if len(row) != 0 else ""
        for cell in row:
            xsl_content += (
                f"""<fo:table-cell {cell_styling}><fo:block {block_styling}>"""
                + str(cell)
                + """</fo:block>\n</fo:table-cell>\n"""
            )
        xsl_content += """</fo:table-row>\n""" if len(row) != 0 else ""
        return xsl_content


def close_xsl_table(xsl_content):
    xsl_content += """</fo:table-body></fo:table>"""
    return xsl_content


def create_xsl_fo_file(
    file_name, file_path, xsl_fo_content, current_datetime, folder_with_file_name=False
):
    xsl_fo_content += """ </fo:flow>
        </fo:page-sequence>
        </fo:root>
    """
    if folder_with_file_name:
        folder_path = file_path + "\\" + file_name + "\\" + current_datetime
    else:
        folder_path = file_path + "\\report" + current_datetime
    try:
        os.makedirs(folder_path)
    except:
        pass
    file_url = folder_path + "\\" + file_name + ".fo"
    f = open(file_url, "w")
    f.write(xsl_fo_content)
    f.close()
    return file_url


def generate_pdf_from_fo_file(foFilePath):
    foFilePath = foFilePath.replace(".fo", "")
    command = Template(settings.FOP_BAT)
    command = command.substitute({"extension": "pdf", "filename": foFilePath})
    ret = os.system(command)
    if ret == 0:
        print("Generate PDF Succesful")
    else:
        print("Somethings wrong when generating PDF.")


def xslfo_gen(header, data, file_name, file_path, date_today):
    cell_styling = (
        "border-width='1px' border-style='solid' padding='8pt' column-width='auto'"
    )
    gen = XSLFOGenerator()
    title = "Sample Blotter"
    title_styling = 'margin-bottom="30px" text-align="center" display-align="center" inline-progression-dimension="auto" table-layout="auto" font-weight = "bold" font-size = "24px"'
    xsl_fo_content = prepare_xsl_fo_content(title, 28, title_styling)
    print(xsl_fo_content)
    xsl_fo_content = add_xsl_data_row(xsl_fo_content, [header])
    print(data)
    xsl_fo_content = add_xsl_data_row(xsl_fo_content, [data], cell_styling)
    xsl_fo_content = close_xsl_table(xsl_fo_content)
    foFilePath = create_xsl_fo_file("test", "D:\\Project\\HKCO", xsl_fo_content, date_today)
    return foFilePath


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
    date_today = datetime.today().strftime("%y%m%d")
    email_params = str(parameter["email_params"])
    trades = acm.FTrade.Select("")
    no = 1
    header = [
        "No",
        "Date",
        "Pengirim",
        "Lamp",
        "Deal/TRX",
        "Currency",
        "USD Amount",
        "bank Position",
        "Rate",
        "IDR Amount",
        "Accumulated Position",
        "Cost",
        "Profit",
        "Remittance Fee",
        "Nomor Rekening Tujuan",
        "Nama penerima",
        "Bank Penerima",
        "Sumber Dana",
        "No Telp. Pengirim",
        "Alamat pengirim",
        "No ID Pengirim",
        "Kewarganegaraan",
        "Local ID",
        "Tujuan TRX",
        "Status",
        "Jenis Kelamin",
        "Tahun lahir",
        "Cost Remittance Fee",
    ]
    data = []
    for trade in trades:
        if (
            trade.Type() == "Account Transfer"
            and trade.ValueDay() == str(datetime.today())
            and trade.Trade().TradeConnections().At(1).FromTrade().Oid()
            == trade.Trade().Oid()
        ):
            date = trade.ValueDay()
            name = trade.Trade().Acquirer().Accounts().First().Name()
            curr_ins = trade.Trade().Instrument().Name()
            amount = abs(trade.Trade().Payments().First().Amount())
            bankPos = "BUY" if amount >= 0 else "SELL"
            usdRate = curr_rate(trade, "USD") if curr_rate(trade, "USD") != None else 0
            idrRate = curr_rate(trade, "IDR") if curr_rate(trade, "IDR") != None else 0
            usdAmount = amount if curr_ins == "USD" else usdRate * amount
            idrAmount = amount if curr_ins == "IDR" else idrRate * amount
            remittanceFee = (
                0
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
            data.append(
                [
                    no,
                    date,
                    name,
                    lamp,
                    "-",
                    curr_ins,
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
                    "-",
                ]
            )
            no += 1
    xml_file = xsl_generate(data)
    html_file = transformXML(xml_file, "DLFO01")
    generated_reports = []
    if output_file == ".html":
        generate_html = HTMLGenerator().create_html_file(
            html_file, file_path, report_name, date_today, False
        )
    elif output_file == ".xls":
        generate_html = HTMLGenerator().create_html_file(
            html_file, file_path, report_name, date_today, False
        )
        generate_file_for_other_extension(generate_html, ".xls")
        os.remove(os.path.join(file_path, f"report{date_today}", f"{report_name}.html"))
        xls_file = html_file.split(".")
        xls_file[-1] = "xls"
        xls_file = ".".join(xls_file)
        generated_reports.append(xls_file)
    elif output_file == ".pdf":
        xslfo_file = xslfo_gen(header, data, report_name, file_path, date_today)
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
