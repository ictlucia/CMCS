import acm, ael, random

from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *

from time import sleep, perf_counter

context = acm.GetDefaultContext( )

today = acm.Time.DateToday()

tomorrow = acm.Time.DateAddDelta(today,0,0,1)

yesterday = acm.Time.DateAddDelta(today, 0, 0, -1)

next_month = acm.Time.DateAddDelta(today, 0, 1, 0)

next_year = acm.Time.DateAddDelta(today, 1, 0, 0)

all_trades = acm.FTrade.Select('')

stand_calc = acm.FStandardCalculationsSpaceCollection()

sheet_type = 'FMoneyFlowSheet'    

calc_space = acm.Calculations( ).CreateCalculationSpace( context, sheet_type )

# ================ DATA FILTER COLUMN ================ 

dict_of_column_filter = {

"FX/FW" : {

    "Product Type" : ["FXBN", "FXDU", "FX"],

    "Category" : ["TOD", "TOM", "SPOT", "FWD", "NDF", "NS", "OPT"]

    },

"Interbank Placement" : {

    "Product Type" : ["DL"],

    "Category" : ["CL", "CMP", "OVP", "SHARI"]

    },

"Interbank Taken" : {

    "Product Type" : ["DL"],

    "Category" : ["CL", "MD", "CMT", "OVT", "BLT"]

    },

"LF" : {

    "Product Type" : ["DL"],

    "Category" : ["LF"]

    },

"DF" : {

    "Product Type" : ["DL"],

    "Category" : ["FASBI"]

    },

"Term Deposit" : {

    "Product Type" : ["TD"],

    "Category" : ["BI"]

    },

"Repo BI" : {

    "Product Type" : ["REPO"],

    "Category" : ["BISBI", "BIGOV", "BIDIS", "BINON", "BIOTH"]

    },

"Repo Interbank" : {

    "Product Type" : ["REPO"],

    "Category" : ["IWFSBI", "IWFGOV", "IWFDIS", "IWFNON", "IWFOTH", "CWFSBI", "CWFGOV", "CWFDIS", "CWFNON", "CWFOTH", "IBSBI", "IBGOV", "IBDIS", "IBNON", "IBOTH", "CCBI", "CCGV", "CCDC", "CCND", "CCOH", "OVBSBI", "OVBGOV", "OVBDIS", "OVBNON", "OVBOTH", "NEGSBI", "NEGGOV", "NEGDIS", "NEGNON", "NEGOTH"]

    },

"Reverse Repo BI" : {

    "Product Type" : ["REVREPO"],

    "Category" : ["BISBI", "BIOB", "BIOH"]

    },

"Reverse Repo Interbank" : {

    "Product Type" : ["REVREPO"],

    "Category" : ["IBBI", "IBOB", "IBOH", "OVBSBI", "OVBGOV", "OVBOTH", "CCSBI", "CCGOV", "CCOTH"]

    },

"Surat Berharga Dimiliki" : {

    "Product Type" : ["BOND"],

    "Category" : ["CBUSD", "CBVALAS", "UST", "BILLS", "ROI", "SBBI", "INDOIS", "SBK", "NCD"]

    },

"Coupon SB Dimiliki" : {

    "Product Type" : ["BOND"],

    "Category" : ["CBUSD", "CBVALAS", "UST", "BILLS", "ROI", "SBBI", "INDOIS", "SBK", "NCD"]

    },

"Surat Berharga Terbit" : {

    "Product Type" : ["DEBT"],

    "Category" : ["BOND", "ZCO", "NCD"]

    },

"Coupon SB Terbit" : {

    "Product Type" : ["DEBT"],

    "Category" : ["BOND", "ZCO", "NCD"]

    },

"Reksadana" : {

    "Product Type" : ["BOND"],

    "Category" : ["RDPU", "RDPT"]

    },

"CCS" : {

    "Product Type" : ["SWAP"],

    "Category" : ["CCS"]

    },

"IRS" : {

    "Product Type" : ["SWAP"],

    "Category" : ["IRS"]

    },

"SWAP" : {

    "Product Type" : ["FX"],

    "Category" : ["SWAP"]

    },

"Term Deposit BI" : {

    "Product Type" : ["TD"],

    "Category" : ["BI"]

    },

"SBBI Valas" : {

    "Product Type" : ["SBI"],

    "Category" : ["IDSV"]

    }

}

def getFilePathSelection():

    """ Directory selector dialog """

    selection = acm.FFileSelection()

    selection.PickDirectory(True)

    selection.SelectedDirectory = "C:\\"

    return selection   

def get_currencies():

    all_currency = list(acm.FCurrency.Select(''))

    all_currency.remove(acm.FCurrency['IDR'])

    return all_currency

def get_projected_from_trading_manager(cashflow_object):

    ins = cashflow_object

    #value = acm.FMoneyFlowCalculations(calc_space)

    column_id = 'Cash Analysis Projected'

    value = calc_space.CalculateValue( ins, column_id)

    #value = calc_space.CreateCalculation(ins, column_id).FormattedValue()

    try:

        result = value.Number()

    except:

        traceback.print_exc()

        result = '-'

    return result

def get_projected_from_money_flow(trade, pay_date, cashflow_type):

    moneyflows = trade.MoneyFlows()

    total = 0

    try:

        for i in moneyflows:

            if i.Type() == "Premium" :

                continue

            proj_value = i.Calculation().Projected(stand_calc)

            result = proj_value.Number()

            nominal = trade.Nominal()

            time_range = acm.Time.DateDifference(pay_date, i.PayDate())

            if time_range == 0 and "Amount" not in cashflow_type and result != nominal :

                total += result

                break

            elif time_range == 0 and "Amount" in cashflow_type:

                total += nominal

                break

    except:

        pass

    return total

def get_sum_cashflow_from_trade(trade):

    instrument = trade.Instrument()

    total = 0

    try:

        cashflows = instrument.Legs()[-1].CashFlows()

        for cf in cashflows:

            cashflow_type = cf.CashFlowType()

            if cashflow_type == 'Fixed Rate' or cashflow_type == 'Fixed Amount':

                total += get_projected_from_money_flow(trade, cf.PayDate(), cashflow_type)

                #total += get_projected_from_trading_manager(cf)

        return total

    except:

        traceback.print_exc()

        print("---- Error : Trade nya gaada Cashflow ---")

        return '-'

def get_date_from_cashflow_for_proj_value(trade, date_input):

    instrument = trade.Instrument()

    try:

        cashflows = instrument.Legs()[-1].CashFlows()

        for cf in cashflows:

            time_range = acm.Time.DateDifference(date_input, cf.PayDate())

            cashflow_type = cf.CashFlowType()

            if time_range == 0 and (cashflow_type == 'Fixed Rate' or cashflow_type == 'Fixed Amount'):

                return time_range, cashflow_type

    except:

        pass

    return -1, "-"

def get_value_for_swap_trade(trade, filter_currency):

    # Kalo FX Cash, terus USD/IDR, berarti instrumentnya USD, currencynya IDR

    trade_instrument = trade.Instrument().Name()

    trade_currency = trade.Currency().Name()

    if filter_currency == trade_instrument :

        return trade.Quantity()

    elif filter_currency == trade_currency :

        return trade.Premium()

    else:

        return '-'

def get_nominal_from_trade(valueday, dict_of_column_filter, filter_currency, column_name, title_type):

    total_result, status_empty_transaction = 0, True

    list_category = dict_of_column_filter['Category']

    for i in all_trades[column_name]:

        i = acm.FTrade[i[0]]

        try:

            temp_curr = i.Currency().Name()

            temp_instrument = i.Instrument().Name()

            temp_category = i.OptKey4().Name()

            list_column_ins_date = ['Repo BI', 'Reverse Repo BI', 'Repo Interbank', 'Reverse Repo Interbank']

            list_column_cashflow_date = ['Interbank Placement', 'Interbank Taken', 'LF', 'DF', 'Term Deposit', 'Coupon SB Terbit', 'Coupon SB Dimiliki']

            list_column_trd_time = ["Surat Berharga Dimiliki", "Surat Berharga Terbit"]

            if column_name in list_column_ins_date and title_type == "Maturity" :

                # Kalo Tanggal di baris tabel == End Date nya Instrument

                time_range = acm.Time.DateDifference(valueday, i.Instrument().EndDate())

            elif column_name in list_column_ins_date and title_type == "Over" :

                # Kalo Tanggal di baris tabel == Start Date nya Instrument

                time_range = acm.Time.DateDifference(valueday, i.Instrument().StartDate())

            elif column_name in list_column_cashflow_date :

                # Kalo Tanggal di baris tabel == Pay Date nya di Cashflow

                time_range, cashflow_type = get_date_from_cashflow_for_proj_value(i, valueday)

            else: 

                # Kalo Tanggal di baris tabel == Value Day nya Trade

                time_range = acm.Time.DateDifference(valueday, i.ValueDay())

            trd_time_difference = abs(acm.Time.DateDifference(i.TradeTime(), valueday))

            if dict_of_column_filter['Product Type'] != [] :

                try:

                    status_opt_key_3 = bool(i.OptKey3().Name() in dict_of_column_filter['Product Type'])

                except:

                    status_opt_key_3 = False

            else:

                status_opt_key_3 = True

            list_else = list_column_ins_date + list_column_trd_time + list_column_cashflow_date + ["SWAP"]

            if (filter_currency == temp_curr or filter_currency == temp_instrument) and temp_category in list_category and time_range == 0 and status_opt_key_3:

                if column_name not in list_else:

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "DF" and str(i.InstrumentSubType()) == "Discounted Term Deposit" and i.Premium() >= 0 and temp_curr != 'IDR' and filter_currency != 'IDR' : # Tabel Kiri, DF

                    total_result += get_projected_from_money_flow(i, valueday, cashflow_type)

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "DF" and str(i.InstrumentSubType()) == "Discounted Term Deposit" and i.Premium() >= 0 and temp_curr != 'IDR' and filter_currency != 'IDR': # Tabel Kanan, DF

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "LF" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.Premium() < 0 and temp_curr != 'IDR' and filter_currency != 'IDR': # Tabel Kiri, LF

                    total_result += get_projected_from_money_flow(i, valueday, cashflow_type)

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "LF" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.Premium() < 0 and temp_curr != 'IDR' and filter_currency != 'IDR': # Tabel Kanan, LF

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Interbank Placement" and str(i.InstrumentSubType()) == "Deposit/Loan" and i.Premium() >= 0: # Tabel Kiri, Interbank Placement

                    total_result += get_projected_from_money_flow(i, valueday, cashflow_type)

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Interbank Placement" and str(i.InstrumentSubType()) == "Deposit/Loan" and i.Premium() >= 0: # Tabel Kanan, Interbank Placement

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Interbank Taken" and str(i.InstrumentSubType()) == "Deposit/Loan" and i.Premium() < 0: # Tabel Kiri, Interbank Taken

                    total_result += get_projected_from_money_flow(i, valueday, cashflow_type)

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Interbank Taken" and str(i.InstrumentSubType()) == "Deposit/Loan" and i.Premium() < 0: # Tabel Kanan, Interbank Taken

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "SWAP" and str(i.InstrumentSubType()) == "FX Cash" and i.TradeProcessesToString() == 'Swap Near Leg': # Tabel Kanan, SWAP

                    total_result += get_value_for_swap_trade(i, filter_currency)

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "SWAP" and str(i.InstrumentSubType()) == "FX Cash" and i.TradeProcessesToString() == 'Swap Far Leg': # Tabel Kiri, SWAP

                    total_result += get_value_for_swap_trade(i, filter_currency)

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Repo BI" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.StartCash() >= 0: # Tabel Kiri, Repo BI

                    total_result += get_sum_cashflow_from_trade(i)

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Repo BI" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.StartCash() >= 0: # Tabel Kanan, Repo BI

                    total_result += i.StartCash()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Reverse Repo BI" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.StartCash() < 0: # Tabel Kiri, Reverse Repo BI

                    total_result += get_sum_cashflow_from_trade(i)

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Reverse Repo BI" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.StartCash() < 0: # Tabel Kanan, Reverse Repo BI

                    total_result += i.StartCash()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Repo Interbank" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.StartCash() >= 0: # Tabel Kiri, Repo Interbank

                    total_result += get_sum_cashflow_from_trade(i)

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Repo Interbank" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.StartCash() >= 0: # Tabel Kanan, Repo Interbank

                    total_result += i.StartCash()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Reverse Repo Interbank" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.StartCash() < 0: # Tabel Kiri, Reverse Repo Interbank

                    total_result += get_sum_cashflow_from_trade(i)

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Reverse Repo Interbank" and str(i.InstrumentSubType()) == "Basket Repo/Reverse" and i.StartCash() < 0: # Tabel Kanan, Reverse Repo Interbank

                    total_result += i.StartCash()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Term Deposit" and i.Premium() < 0: # Hanya Tabel Kiri, Term Deposit

                    total_result += get_projected_from_money_flow(i, valueday, cashflow_type)

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Surat Berharga Dimiliki" and trd_time_difference <= 3 : # Tabel Kiri, Surat Berharga Dimiliki

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Surat Berharga Dimiliki" and trd_time_difference > 3 : # Tabel Kanan, Surat Berharga Dimiliki

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Surat Berharga Terbit" and trd_time_difference <= 3 : # Tabel Kiri, Surat Berharga Terbit

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Surat Berharga Terbit" and trd_time_difference > 3 : # Tabel Kanan, Surat Berharga Terbit

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Maturity" and column_name == "Surat Berharga Terbit" and trd_time_difference <= 3 : # Tabel Kiri, Surat Berharga Terbit

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif title_type == "Over" and column_name == "Surat Berharga Terbit" and trd_time_difference > 3 : # Tabel Kanan, Surat Berharga Terbit

                    total_result += i.Premium()

                    status_empty_transaction = False

                elif (title_type == "Maturity" or title_type == "Over") and column_name == "Coupon SB Dimiliki" : # Tabel Kiri, Coupon SB Dimiliki (Hanya Maturity)

                    total_result += get_projected_from_money_flow(i, valueday, cashflow_type)

                    status_empty_transaction = False

                elif (title_type == "Maturity" or title_type == "Over") and column_name == "Coupon SB Terbit" : # Tabel Kiri, Coupon SB Terbit (Hanya Maturity)

                    total_result += get_projected_from_money_flow(i, valueday, cashflow_type)

                    status_empty_transaction = False

        except:

            #print('Error')

            #traceback.print_exc()

            pass

    # DUMMY

    #total_result = random.uniform(1_000_000_000_000_000.0000, 10_000_000_000_000_000.9999)

    #status_empty_transaction = False

    if status_empty_transaction:

        total_result = "-"

    elif filter_currency == 'IDR' :

        # Kalo IDR, dibagi Trilyun, dan di Round

        total_result = total_result / 1_000_000_000_000

        total_result = round_half_up(total_result, 3)

    else:

        # Kalo Non IDR, dibagi Sejuta

        total_result = total_result / 1_000_000

        total_result = round_half_up(total_result, 2)

    return total_result

ael_gui_parameters={'runButtonLabel':'&&Run',

                    'hideExtraControls': True,

                    'windowCaption':'Cashflow Projection (NON IDR)'}

#settings.FILE_EXTENSIONS

ael_variables=[

['report_name','Report Name','string', None, 'Cashflow Projection (NON IDR)', 1,0],

['to_date','To (End Date)','string', ["1M", "6M", "1Y", next_month, next_year], tomorrow, 1,0],

['filter_currency','Currency','string', get_currencies(), 'USD', 1,0, "Select to Filter the Currency", None, 1],

['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],

['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output'],

]  

def ael_main(parameter):

    start_time = perf_counter()

    report_name = parameter['report_name']

    file_path = str(parameter['file_path'])

    to_date = parameter['to_date']

    filter_currency = parameter['filter_currency']

    output_file = parameter['output_file']

    if filter_currency.lower() == "idr":

        raise ValueError('Please select Non IDR values for Currency Field.')

    titles = ['Date', 'Instrument (Maturity)', 'Sub Total', 'Instrument (over Tom/Spot)', 'Sub Total', 'Total', 'Cumulative']

    title_ins_maturity = ['Interbank Placement', 'Interbank Taken', 'FX/FW', 'SWAP', 'Term Deposit', 'Repo BI', 'Reverse Repo BI',

    'Repo Interbank', 'Reverse Repo Interbank', 'Surat Berharga Dimiliki', 'Coupon SB Dimiliki', 'Surat Berharga Terbit', 'Coupon SB Terbit', 'CCS', 'IRS', 'SBBI Valas']

    title_ins_over = ['Interbank Placement', 'Interbank Taken', 'SWAP', 'Term Deposit BI', 'Repo BI', 'Reverse Repo BI', 'Repo Interbank', 'Reverse Repo Interbank', 'Surat Berharga Dimiliki', 'Coupon SB Dimiliki', 'Surat Berharga Terbit', 'Coupon SB Terbit','CCS', 'IRS', 'SBBI Valas']

    list_date, row_ins_maturity, row_ins_over, row_sub_total_maturity, row_sub_total_over, row_total, row_cummulative = [], [], [], [], [], [], []

    #selected_date = get_date_from_input(from_date)

    #end_date = get_date_from_input(to_date, selected_date)

    time_range = acm.Time.DateDifference(to_date, tomorrow) + 1

    count = -1

    global all_trades

    #all_trades = acm.FTrade.Select('status = "BO-BO Confirmed" and tradeTime <= ' + end_date)

    data_optkey3, data_optkey4 = '', ''

    temp_list_optkey3, temp_list_optkey4 = [], []

    all_title = title_ins_maturity+title_ins_over

    all_trades = {}

    for ins in dict_of_column_filter.keys():

        temp_list_optkey3 = dict_of_column_filter[ins]['Product Type']

        temp_list_optkey4 = dict_of_column_filter[ins]['Category']

        data_optkey3 = "('"+"','".join(list(set(temp_list_optkey3))) + "')"

        data_optkey4 = "('"+"','".join(list(set(temp_list_optkey4))) + "')"

        query = f"""

        SELECT t.trdnbr, t.status, display_id(t, 'optkey3_chlnbr'), display_id(t, 'optkey4_chlnbr'), display_id(t, 'insaddr')
        FROM trade t
        WHERE (t.status = 'BO-BO Confirmed')
        AND display_id(t, 'curr') = '{filter_currency}'
        AND display_id(t, 'optkey3_chlnbr') IN {data_optkey3}
        AND display_id(t, 'optkey4_chlnbr') IN {data_optkey4}
        AND t.value_day > TODAY
        """

        trades_data = ael.asql(query)[1][0]

        all_trades[ins] = trades_data

        #print(ins) ; print(len(trades_data)) ; print(query)

    for i in range(time_range):

        temp_date = acm.Time.DateAddDelta(tomorrow, 0, 0, i)

        check_holiday = acm.FCalendar['No Holiday'].CalendarInformation().IsNonBankingDay(temp_date) # Cek apakah hari libur/bukan

        if check_holiday:

            continue

        list_date.append(temp_date)

        temp_row_ins_maturity, temp_row_ins_over, temp_row_sub_total_maturity, temp_row_sub_total_over = [], [], 0, 0

        for maturity in title_ins_maturity:

            title_type = 'Maturity'

            temp_maturity_value = '-'

            # KOLOM-KOLOM MATURITY

            if maturity in list(dict_of_column_filter.keys()):

                temp_maturity_value = get_nominal_from_trade(temp_date, dict_of_column_filter[maturity], filter_currency, maturity, title_type)

            ############## ROW MATURITY ############## 

            temp_row_ins_maturity.append(temp_maturity_value)

            try:

                temp_row_sub_total_maturity += temp_maturity_value

            except:

                pass

        for over in title_ins_over:

            title_type = 'Over'

            temp_over_value = '-'

            # KOLOM-KOLOM OVER

            if over in list(dict_of_column_filter.keys()):

                temp_over_value = get_nominal_from_trade(temp_date, dict_of_column_filter[over], filter_currency, over, title_type)

            ############## ROW OVER ############## 

            temp_row_ins_over.append(temp_over_value)

            try:

                temp_row_sub_total_over += temp_over_value

            except:

                pass

        row_ins_maturity.append(temp_row_ins_maturity)    

        row_ins_over.append(temp_row_ins_over)

        ############## SUB TOTAL MATURITY ############## 

        try:

            if filter_currency == 'IDR' :

                row_sub_total_maturity.append(round_half_up(temp_row_sub_total_maturity, 3))

            else:

                row_sub_total_maturity.append(round_half_up(temp_row_sub_total_maturity, 2))

        except:

            row_sub_total_maturity.append(temp_row_sub_total_maturity)

        ############## SUB TOTAL OVER ############## 

        try:

            if filter_currency == 'IDR' :

                row_sub_total_over.append(round_half_up(temp_row_sub_total_over, 3))

            else:

                row_sub_total_over.append(round_half_up(temp_row_sub_total_over, 2))

        except:

            row_sub_total_over.append(temp_row_sub_total_over)

        ############## TOTAL MATURITY  & OVER ############## 

        temp_total = temp_row_sub_total_maturity + temp_row_sub_total_over

        try:

            if filter_currency == 'IDR' :

                row_total.append(round_half_up(temp_total, 3))

            else:

                row_total.append(round_half_up(temp_total, 2))

        except:

            row_total.append(temp_total)

        ############## CUMMULATIVE ############## 

        if count == -1:

            cummulative_result = temp_total

        else:

            cummulative_result = temp_total + float(row_cummulative[count])

        try:

            if filter_currency == 'IDR' :

                row_cummulative.append(round_half_up(cummulative_result, 3))

            else:

                row_cummulative.append(round_half_up(cummulative_result, 2))

        except:

            row_cummulative.append(cummulative_result)

        count += 1

    ############## WRITE ROWS ############## 

    rows, count = [title_ins_maturity + title_ins_over], 0

    for i in list_date:

        temp_row = [[i] + row_ins_maturity[count] + [row_sub_total_maturity[count]] + row_ins_over[count] + [row_sub_total_over[count]] + [row_total[count]] + [row_cummulative[count]]]

        final_row = []

        for row in temp_row[0] :

            try:

                if filter_currency == 'IDR' :

                    row = "{:,.3f}".format(row)

                else:

                    # Khusus Non IDR, Untuk baris perproduk, jangan di round, cuma di tunjukin 2 angka pertama aja

                    row = get_decimal_without_rounding(row, 2)

                    row = "{:,.2f}".format(row)
                    
                if '-' in row :
                    row = "("+row+")"
                    row = row.replace("-","")
                    
                
                    
                final_row.append(row)

            except:
                    
                final_row.append(row)

        rows += [final_row]

        count += 1

    table_html = create_html_table(titles, rows)

    table_xsl_fo = create_xsl_fo_table(titles, rows)

    dict_len_title = {'Maturity' : 0, 'Over' : 0 }

    for i in titles:

        if 'Instrument' in i :

            if 'Maturity' in i :

                temp_ins_titles = title_ins_maturity

                column_length = str(len(temp_ins_titles))

                dict_len_title['Maturity'] = column_length

            else:

                temp_ins_titles = title_ins_over

                column_length = str(len(temp_ins_titles))

                dict_len_title['Over'] = column_length

            table_html = table_html.replace('<th>'+i+'</th>', '<th colspan="'+column_length+'">'+i+'</th>')

        else:

            table_html = table_html.replace('<th>'+i+'</th>', '<th rowspan="2">'+i+'</th>')

    for maturity in title_ins_maturity:

        table_html = table_html.replace('<td>'+maturity+'</td>', '<td><b>'+maturity+'</b></td>')

        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+maturity+'</fo:block></fo:table-cell>',

        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" text-align="center"><fo:block>'+maturity+'</fo:block></fo:table-cell>')

    for over in title_ins_over:

        table_html = table_html.replace('<td>'+over+'</td>', '<td><b>'+over+'</b></td>')

        table_xsl_fo = table_xsl_fo.replace('<fo:table-cell border-width="1px" border-style="solid" padding="8pt"><fo:block>'+over+'</fo:block></fo:table-cell>',

        '<fo:table-cell border-width="1px" border-style="solid" padding="8pt" font-weight="bold" text-align="center"><fo:block>'+over+'</fo:block></fo:table-cell>')

    current_hour = get_current_hour("")

    current_date = get_current_date("")

    report_name = report_name + " - " + filter_currency

    html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date)

    xsl_fo_file = create_xsl_fo_file(report_name + " " +current_date+current_hour, file_path, [table_xsl_fo], report_name, current_date)

    f = open(xsl_fo_file, "r")

    contents = f.read().replace('<fo:simple-page-master master-name="my_page" margin="0.5in">', '<fo:simple-page-master master-name="my_page" margin="0.5in" page-height="25in" page-width="80in">')

    contents = contents.replace('''<fo:table-header background-color="#666666" color="#ffffff" font-weight="bold">

    <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Date</fo:block></fo:table-cell>

        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Instrument (Maturity)</fo:block></fo:table-cell>

        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Sub Total</fo:block></fo:table-cell>

        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Instrument (over Tom/Spot)</fo:block></fo:table-cell>

        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Sub Total</fo:block></fo:table-cell>

        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Total</fo:block></fo:table-cell>

        <fo:table-cell padding="8pt" border-width="1px" border-style="solid"><fo:block>Cumulative</fo:block></fo:table-cell>

        </fo:table-header>

    <fo:table-body>''',

            '''    <fo:table-body>

            <fo:table-row background-color="#666666" color="#ffffff" font-weight="bold">

            <fo:table-cell padding="8pt" border-width="1px" font-weight="bold" text-align="center" border-style="solid" number-rows-spanned="2"><fo:block>Date</fo:block></fo:table-cell>

            <fo:table-cell padding="8pt" border-width="1px" font-weight="bold" text-align="center" border-style="solid" number-columns-spanned="'''+str(dict_len_title['Maturity'])+'''"><fo:block>Instrument (Maturity)</fo:block></fo:table-cell>

            <fo:table-cell padding="8pt" border-width="1px" font-weight="bold" text-align="center" border-style="solid" number-rows-spanned="2"><fo:block>Sub Total</fo:block></fo:table-cell>

            <fo:table-cell padding="8pt" border-width="1px" font-weight="bold" text-align="center" border-style="solid" number-columns-spanned="'''+str(dict_len_title['Over'])+'''"><fo:block>Instrument (over Tom/Spot)</fo:block></fo:table-cell>

            <fo:table-cell padding="8pt" border-width="1px" font-weight="bold" text-align="center" border-style="solid" number-rows-spanned="2"><fo:block>Sub Total</fo:block></fo:table-cell>

            <fo:table-cell padding="8pt" border-width="1px" font-weight="bold" text-align="center" border-style="solid" number-rows-spanned="2"><fo:block>Total</fo:block></fo:table-cell>

            <fo:table-cell padding="8pt" border-width="1px" font-weight="bold" text-align="center" border-style="solid" number-rows-spanned="2"><fo:block>Cumulative</fo:block></fo:table-cell>

            </fo:table-row>''')

    f = open(xsl_fo_file, "w")

    f.write(contents)

    f.close()

    for i in output_file:

        if i != '.pdf' :

            generate_file_for_other_extension(html_file, i)

        else:

            generate_pdf_from_fo_file(xsl_fo_file)

    try:

        os.remove(xsl_fo_file)

    except:

        pass

    end_time = perf_counter()

    print('Jumlah Hari : ' + str(time_range -1))

    print(f'{filter_currency} Projections, It took {end_time- start_time: 0.2f} second(s) to complete.')

