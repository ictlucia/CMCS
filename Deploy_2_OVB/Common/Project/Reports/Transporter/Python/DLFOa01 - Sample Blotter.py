import acm
from math import ceil
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from FReportUtils import *

context = acm.GetDefaultContext()
xslExtension = context.GetExtension("FXSLTemplate", "FObject", 'get_sample_blotter')
xsl = xslExtension.Value()

#print(xsl)

def idr_rate(trade):
    instrument = trade.Instrument()
    ins_name = instrument.Name()
    
    for i in range(len(instrument.Prices())):
        market = instrument.Prices()[i].Market().Name()
        curr = instrument.Prices()[i].Currency().Name()
        if market == "EOD" and curr == "IDR" and ins_name != "IDR":
            return instrument.Prices()[i].Settle() if instrument.Prices()[i].Settle() != None else 0
        else : 0

def create_file(html_content, file_path, file_name, current_date, open_html, extension, folder_with_file_name=False):
        if folder_with_file_name:
            folder_path = file_path + "\\" + file_name + "\\" + current_date
        else:
            folder_path = file_path + "\\report_" + current_date
            
        try:
            os.makedirs(folder_path)
        except:
            #print('Path too long')
            pass
        
        file_url = folder_path + "\\" + file_name + f".{extension}"
        f = open(file_url, "w")
        f.write(html_content)
        f.close()
        url = "file://" + file_url
        
        if open_html:
            webbrowser.open(file_url,new=2)
        
        return file_url

trades = acm.FTrade.Select("")
no = 1
data = []

for trade in trades:
    if trade.Type() == "Account Transfer" and trade.ValueDay() == "2024-01-18" and trade.Trade().TradeConnections().At(1).FromTrade().Oid() == trade.Trade().Oid():
        date = trade.ValueDay()
        name = trade.Trade().Acquirer().Accounts().First().Name()
        usdAmount = abs(trade.Trade().Payments().First().Amount())
        bankPos = "BUY" if usdAmount >= 0 else "SELL"
        idrRate = idr_rate(trade)
        idrAmount = idrRate * usdAmount if idrRate != None else 0
        remittanceFee = o if trade.Trade().Payments().First().Amount() == 0 else 1 if trade.Trade().Payments().First().Amount() < 100 else 2 if trade.Trade().Payments().First().Amount() < 1000 else 3
        receiver = trade.Trade().TradeConnections().At(1).ToTrade().Acquirer().Accounts().First().Name() if trade.Trade().TradeConnections().At(1).FromTrade().Oid() == trade.Trade().Oid() else None
        senderTelp = trade.Trade().Acquirer().Telephone()
        senderAddress = trade.Trade().Acquirer().Address()
        senderId = trade.Name()
        senderCountry = trade.Trade().Acquirer().Country()
        lamp = ceil(no/12)
        data.append([no, date, name, lamp, usdAmount, bankPos, idrRate, idrAmount, remittanceFee, receiver, senderTelp, senderAddress, senderId, senderCountry])
        no+=1

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
            <kode>-</kode>
            <curr>-</curr>
            <usdAmount>{val[4]}</usdAmount>
            <bankPos>{val[5]}</bankPos>
            <rate>{val[6]}</rate>
            <idrAmount>{val[7]}</idrAmount>
            <usd>{val[4]}</usd>
            <idr>{val[6]}</idr>
            <cost>{val[7]}</cost>
            <profit>-</profit>
            <remittanceFee>{val[8]}</remittanceFee>
            <rek>-</rek>
            <namaPenerima>-</namaPenerima>
            <bankPenerima>{val[9]}</bankPenerima>
            <sumberDana>-</sumberDana>
            <telp>{val[10]}</telp>
            <alamat>{val[11]}</alamat>
            <idPengirim>{val[12]}</idPengirim>
            <kewarganegaraan>{val[13]}</kewarganegaraan>
            <localId>-</localId>
            <trx>-</trx>
            <status>-</status>
            <gender>-</gender>
            <tahunLahir>-</tahunLahir>
            <remittanceCost>-</remittanceCost>
        </cust>
    """
    
    return open_code + val_params + '</data1>'
    

xml_file = xsl_generate(data)
html_file = transformXML(xml_file, "get_sample_blotter")
generate_html = create_file(html_file, "C:\Users\emili\OneDrive\Desktop\DLFOa01 - Sample Blotter", "DLFOa01 - Sample Blotter", "11-01-2025", False, "html")
generate_file_for_other_extension(generate_html, '.xls')
    
    
    
    
    

