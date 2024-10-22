import ael, acm, os
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import getFilePathSelection
from datetime import date, timedelta

def last_week_date():
    today = date.today()
    
    list_date = [today.strftime("%d/%m/%Y")]
    for day in range(1, 7):
        date_days = today - timedelta(days=day)
        list_date.append(date_days.strftime("%d/%m/%Y"))
    
    return list_date

def get_val_query():
    query = f"""
    SELECT 
    status, type, trdnbr
    FROM 
        TRADE t
    WHERE
        DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND'
    """
    
    query_val_list = ael.asql(query)[1][0]
    
    return query_val_list
    
#print(get_val_query())

def acm_get_val(ael_val, calc_space) :
    status, type, trdnbr = ael_val
    
    trade = acm.FTrade[trdnbr]
    
    year, month, day = trade.TradeTime().split(" ")[0].split("-")
    trade_date = f"{month}/{day}/{year}"
    
    settlement_date = trade.LongFormGetSettlementDate()
    br_code = trade.OptKey1() if trade.OptKey1() != None else ""
    im_code = trade.OptKey1AsEnum() if trade.OptKey1AsEnum() != None else ""
    security_code = trade.Instrument().Name()
    
    b_or_s = trade.BoughtAsString()
    price = trade.Price()
    face_value = trade.FaceValue()
    
    list_row_val = [status, type, trdnbr, trade_date, settlement_date, br_code, im_code, security_code, b_or_s, price, face_value, trdnbr]
    
    return list_row_val

def create_txt_file(query_val_list, report_folder, report_name):
    context = acm.GetDefaultContext( )
    sheet_type = 'FTradeSheet'
    
    calc_space = acm.Calculations().CreateCalculationSpace(context, sheet_type)
    
    date_range = last_week_date()

    header_list_name = [
        "Transaction Status", "Data Type", "TD Reference ID", "Trade Date", "Settlement Date", "BR Code", "IM Code", "Security Code", "B/S", "Price", "Face Value", "TD Reference No"]
    
    output_txt = "|".join(header_list_name)
    
    for row in query_val_list:
        year, month, day = acm.FTrade[row[2]].TradeTime().split(" ")[0].split("-")
        if f"{day}/{month}/{year}" in date_range:
            list_acm_val = acm_get_val(row, calc_space)
            output_txt += "\n" + "|".join([str(x) for x in list_acm_val])
    
    file_path = os.path.join(report_folder, report_name)
    f = open(file_path, "w")
    f.write(output_txt)
    f.close()
    
    return output_txt
    

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'BO48 - Trade Detail Buy'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'BO48 - Trade Detail Buy', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
]

def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE    
    report_name = parameter['report_name'] + ".txt"
    file_path = str(parameter['file_path'])
    
    folder_name = "report"+date.today().strftime("%Y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    
    query_val_list = get_val_query()
    create_txt_file(query_val_list, report_folder, report_name)
