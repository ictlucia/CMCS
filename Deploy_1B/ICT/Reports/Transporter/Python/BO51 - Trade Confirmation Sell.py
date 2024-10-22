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
        status, trdnbr, counterparty_ptynbr 
    FROM 
        trade t, instrument i 
    WHERE 
        t.insaddr = i.insaddr AND i.instype = 'BOND'
    """
    
    query_val_list = ael.asql(query)[1][0]
    
    return query_val_list
    
#print(get_val_query())

def acm_get_val(ael_val, calc_space) :
    status, trdnbr, cptynbr = ael_val
    
    trade = acm.FTrade[trdnbr]
    
    year, month, day = trade.TradeTime().split(" ")[0].split("-")
    trade_date = f"{day}/{month}/{year}"
    
    year, month, day = trade.AcquireDay().split(" ")[0].split("-")
    AcquireDay = f"{day}/{month}/{year}"
    
    settlement_date = trade.LongFormGetSettlementDate()
    br_code = trade.OptKey1() if trade.OptKey1() != None else ""
    im_code = trade.OptKey1AsEnum() if trade.OptKey1AsEnum() != None else ""
    fund_code = trade.Instrument().AbsoluteStrike() if trade.Instrument().AbsoluteStrike() != None else ""
    security_code = trade.Instrument().Name() if trade.Instrument().Name() != None else ""
    lastCouponDate = trade.Instrument().LastCoupDay() if trade.Instrument().LastCoupDay() != None else ""
    nextCouponDate = trade.Instrument().LastCoupDay() if trade.Instrument().LastCoupDay() != None else ""
    borrowing_date = trade.Instrument().DateFrom() if trade.Instrument().DateFrom() != None else ""
    return_date = trade.Instrument().DateTo() if trade.Instrument().DateTo() != None else ""
    days_of_holding_interest = trade.Instrument().ExpiryPeriod_count() if trade.Instrument().ExpiryPeriod_count() != None else ""
    tc_reference_no = trade.TraderId() if trade.TraderId() != None else ""
    acquisitionAmount = trade.AllInPrice() if trade.AllInPrice() != None else ""
    
    trade_fee = trade.Fee()
    tax_fee = trade.Tax()
    purposeText = trade.Text1()
    seccurities_acc_no = trade.OptKey1().Oid() if trade.OptKey1() != None else ""
    trader = trade.Trader().Name() if trade.Broker() != None else ""
    broker = trade.Broker().Name() if trade.Broker() != None else ""
    
    b_or_s = trade.BoughtAsString()
    price = trade.Price()
    face_value = trade.FaceValue()
    
    proceed_amount = calc_space.CalculateValue(trade, "Buy Amount")
    accrued_days = calc_space.CalculateValue(trade, "IDays")
    accrued_interest_amount = round(float("".join([x for x in str(calc_space.CalculateValue(trade, "Portfolio Accrued Interest")) if x.isdigit() or x == "."])),2)
    capital_gain_tax = calc_space.CalculateValue(trade, "CapitalGainTax")
    interest_income_tax = calc_space.CalculateValue(trade, "InterestIncomeTax")
    withholding_tax = calc_space.CalculateValue(trade, "WHT")
    trade_net_premium = "Yes" if calc_space.CalculateValue(trade, "Trade Net Premium") else "No"
    additional_information = calc_space.CalculateValue(trade, "FreeText")
    place_of_trade_type = calc_space.CalculateValue(trade, "Type_Placement")
    repo_rate = calc_space.CalculateValue(trade, "Fixed Rate")
    data_type = calc_space.CalculateValue(trade, "SourceData")
    acquisitionprice = calc_space.CalculateValue(trade, "AcquisitionIDR")
    CapitalGain = calc_space.CalculateValue(trade, "CapitalGain")
    HoldingInterestAmount = calc_space.CalculateValue(trade, "HoldingInterestAmount")
    TotalTaxableIncome = calc_space.CalculateValue(trade, "TotalTaxableIncome")
    
    
    list_row_val = [status, trdnbr, None, trdnbr, trade_date, settlement_date, br_code, im_code, cptynbr, fund_code, security_code, b_or_s, price, face_value, proceed_amount, lastCouponDate, 
                    nextCouponDate, accrued_days, accrued_interest_amount, trade_fee, capital_gain_tax, interest_income_tax, withholding_tax, trade_net_premium, tax_fee, purposeText, seccurities_acc_no,
                    additional_information, trader, trader, place_of_trade_type, broker, broker, repo_rate, borrowing_date, return_date, data_type, tc_reference_no, face_value, AcquireDay, acquisitionprice,
                    acquisitionAmount, CapitalGain, days_of_holding_interest, HoldingInterestAmount, TotalTaxableIncome, tax_fee, tax_fee]
                        
    return list_row_val

def create_txt_file(query_val_list, report_folder, report_name):
    context = acm.GetDefaultContext( )
    sheet_type = 'FTradeSheet'
    
    calc_space = acm.Calculations().CreateCalculationSpace(context, sheet_type)

    date_range = last_week_date()
    
    header_list_name = [
            "Transaction Status", "TC Reference ID", "Data Type", "TC Reference No", "Trade Date", "Settlement Date", "BR Code", "IM Code", "Counterparty Code", "Fund Code", "Security Code", "B/S", "Price",
            "Face Value", "Proceed Account", "last Coupon Date", "Next Coupon Date", "Accrued Days", "Accrued Interest Amount", "Other Fee", "Capital Gain Tax", "Interest Income Tax", "Withholding tax",
            "Net Proceeds", "Seller's Tax ID", "Purpose of Transaction", "Securities Acc No", "Additional Information (if any)", "Authorized Person Name", "Authorized Person Position", "Place of Trade Type", 
            "Repo Tri-party Agent", "Calculation Agent", "Repo Rate", "Purchase/Lending-Borrowing Date", "Re-purchase/Return Date", "Data Type", "TC Reference No.", "Face Value", "Acquisition Date", 
            "Acquisition Date (%)", "Acquisition Amount", "Capital Gain", "Days of Holding Interest", "Holding Interest Amount", "Total Taxable Income", "Tax Rate In %", "Tax Amount"
    ]
    
    output_txt = "|".join(header_list_name)
    
    for row in query_val_list:
        year, month, day = acm.FTrade[row[1]].TradeTime().split(" ")[0].split("-")
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
                    'windowCaption':'BO51 - Trade Confirmation Sell'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'BO51 - Trade Confirmation Sell', 1,0],
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
