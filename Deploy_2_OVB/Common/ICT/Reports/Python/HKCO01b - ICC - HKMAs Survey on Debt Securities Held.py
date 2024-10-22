import string
import os
from datetime import date
from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
from Report_Python_P2 import usd_price_mtm

##################################################################################################
# FILTER LIST
##################################################################################################
portfolio = "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"
optkey3 = "('BOND')"
optkey4 = "('ORI', 'INDOIS')"

##################################################################################################
# GENERATE QUERY VALUE
##################################################################################################
def time_bucket_func():
    today_date = date.today().strftime("%d/%m/%Y")
    
    month_range = [0, 1, 3, 6, 12, 24, 60, 120, 240]
    
    time_bucket_list = []
    for low_month, high_month in zip(month_range[:-1], month_range[1:]):
        time_bucket = f"AND value_day > date_add_delta('{today_date}', 0, {low_month}) AND value_day < date_add_delta('{today_date}', 0, {high_month})"
        time_bucket_list.append(time_bucket)
    
    return time_bucket_list + [f"AND value_day > date_add_delta('08/04/2024', 0, {month_range[-1]})"]

def get_trdnbr(buss_status, optkey3="", optkey4="", portfolio=""):    

    optkey3_query = "WHERE DISPLAY_ID(t, 'optkey3_chlnbr') in " + optkey3 + "\n" if optkey3 != "" else ""
    optkey4_query = " AND DISPLAY_ID(t, 'optkey4_chlnbr') in " + optkey4 + "\n" if optkey4 != "" else ""
    portfolio_query = " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio + "\n" if portfolio != "" else ""
    
    query_string = """
        SELECT t.trdnbr, t.insaddr
        FROM Trade t   
    """ + optkey3_query + optkey4_query + portfolio_query
            
    if optkey3 != "" and optkey4 != "" and portfolio != "" :
        query_results = ael.asql(query_string)[1][0]
    else :
        query_results = [[None, None]]
    
    trdinfo_list = []
    for query_result in query_results:
        trdnbr, insaddr = query_result
        
        try :
            business_status = acm.FTrade[trdnbr].Counterparty().AdditionalInfo().Business_Status()
        except :
            business_status = None
        
        if business_status == buss_status:
            trdinfo_list.append(query_result)
    
    return trdinfo_list
    
def get_days_range(trade):
    value_day = datetime.strptime(trade.ValueDay(), "%Y-%m-%d")
    end_date = datetime.strptime(trade.Instrument().EndDate(), "%Y-%m-%d")
    
    try :
        val_on_year = float(str(end_date - value_day).split(" ")[0]) / 365
    except :
        val_on_year = 0
        
    return val_on_year

def get_value(buss_status, optkey3="", optkey4="", portfolio=""):
    trdinfo_list = get_trdnbr(buss_status, optkey3, optkey4, portfolio)
    
    unique_ins = list(set([x[1] for x in trdinfo_list]))
    unique_ins.sort()
    
    row_val = [0, 0] * 10
    
    for ins in unique_ins:
        arm = 0
        
        total_principal_amount = 0
        day_range_and_principal = []
        trade_used = [trdnbr for trdnbr, insaddr in trdinfo_list if insaddr == ins]
        
        row_val_temp = [0, 0]
        for trdnbr in trade_used:
            try :
                trade = acm.FTrade[trdnbr]
            except :
                break
                
            
            context = acm.GetDefaultContext()
            columnId_pv = 'Portfolio Present Value'
            columnId_marketVal = 'Portfolio PL Market Value'
                
            calcSpace = acm.Calculations().CreateCalculationSpace(context, "FTradeSheet")
            calculation_mv = calcSpace.CreateCalculation(trade, columnId_marketVal).FormattedValue().replace(".", "").replace(",", ".")
            calculation_pv = calcSpace.CreateCalculation(trade, columnId_pv).FormattedValue().replace(".", "").replace(",", ".")
            
            amt = calculation_mv if calculation_mv != "" else 0
            pv01 = calculation_pv if calculation_pv != "" else 0
            
            if trade.Instrument().Currency().Name() != "USD" :
                usd_rate = usd_price_mtm(trade, curr_target='USD') if usd_price_mtm(trade, curr_target='USD') != None else 1
            else :
                usd_rate = 1
                
            result_trade = [amt, pv01]
            for i, _ in enumerate(result_trade):
                try :
                    add_val = "".join([x for x in str(result_trade[i]) if x.isdigit() or x == "." or x == "-"])
                    add_val_f = float(add_val) if add_val != "" else 0
                except :
                    add_val = "".join([x for x in str(result_trade[i]) if x.isdigit() or x == "," or x == "-"])
                    add_val_f = float(add_val) if add_val != "" else 0
                    
                row_val_temp[i] += add_val_f * usd_rate
                row_val[i] += add_val_f * usd_rate
                    
            principal_amount = abs(trade.Nominal()) * abs(trade.Price())
            total_days = get_days_range(trade)
            day_range_and_principal.append([principal_amount, total_days])
            total_principal_amount += principal_amount
        
        for list_val in day_range_and_principal:
            try :
                arm += list_val[0] * (list_val[1] / total_principal_amount)
            except :
                arm += 0
        
        if arm <= 30 : start_index = 2
        elif arm > 30 and arm <= 90 : start_index = 4
        elif arm > 90 and arm <= 180 : start_index = 6
        elif arm > 180 and arm <= 365 : start_index = 8
        elif arm > 365 and arm <= 730 : start_index = 10
        elif arm > 730 and arm <= 1825 : start_index = 12
        elif arm > 1825 and arm <= 3650 : start_index = 14
        elif arm > 3650 and arm <= 7300 : start_index = 16
        else : start_index = 18
        
        for i, _ in enumerate(row_val_temp):
            row_val[start_index + i] += row_val_temp[i]
            
    
    return row_val

def get_values_row(buss_status=None, optkey3="", optkey4="", portfolio=""):    
    result_list = get_value(buss_status, optkey3, optkey4, portfolio)
    for i in range(2):
        row_values[i] += result_list[i]
    row_values.extend(result_list)
    
    return row_values

##################################################################################################
### HTML TABLE HEADER, TITLE, SUBTITLE, AND VALUE CONTENT
##################################################################################################
## HEADER CONTENT AND SPAN FORMATING
row_header_1 = ["Types of instrument and issuer / Remaining maturity", "Total", "Remaining maturity"]
row_header_2 = ["1 month (inclusive) or shorter", "1 month up to 3 months (inclusive)", "3 months up to 6 months (inclusive)",
                "6 months up to 1 year (inclusive)", "1 year up to 2 years (inclusive)", "2 years up to 5 years (inclusive)", 
                "5 years up to 10 years (inclusive)", "10 years up to 20 years (inclusive)", "longer than 20 years"]
row_header_3 = ["AMT", "PV01"] * 10

header_cell_span_1 = [["2", "3"], ["2", "2"], ["18", "1"]]
header_cell_span_2 = [["2", "1"]] * 9
header_cell_span_3 = [["1", "1"]] * 20

row_header = [row_header_1, row_header_2, row_header_3]
header_cell_span = [header_cell_span_1, header_cell_span_2, header_cell_span_3]

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 2A
title_A = ["Part 2A - Holdings in debt securities (banking book - Fair value through other comprehensive income/Fair value through profit or loss)", ""]

# BAB 1
subtitle_A1 = ["I. Debt securities other than those reported in section I below", ""]
contents_dict_A1 = {
    "(A) Sovereigns" : get_value("Sovereign", "('BOND')", "('ORI', 'INDOIS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(i) Exchange fund bills and notes" : [0] * 20,
    "(ii) Any Other debt securities issued by the Government of the HKSAR" : get_value(None, "('BOND')", "('SVBLCY', 'SVBUSD')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(iii) US Treasury bills, notes, and bonds" : get_value(None, "('BOND')", "('UST')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(B) Public sector entities" : get_value("Public sector entities"),
    "(C) Banks" : get_value("Banks", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(D) Non-bank financial institutions (e.g. securities firms investment banks, fund houses, insurance companies)" : get_value("Non-bank financial institution", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(E) Investment funds and highly leveraged institutions (e.g. hedge funds)" : get_value("Investment funds and highly leveraged"),
    "(F) Corporates" : get_value("Corporate", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(G) Other entities not covered above" : get_value("Other entities not covered above"),
    "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" : [0] * 20,
    "(i) Amount fully deducted from capital base or subject to 1250% risk-weight" : [0] * 20,
    "(ii) Exposures to sukuk" : [0] * 20,
    "(iii) Goverment Guaranteed" : [0] * 20
}

for key, items in contents_dict_A1.items():
    if key == "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" :
        contents_dict_A1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"] = [round(x, 2) for x in contents_dict_A1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"]]
        break
    for i, val in enumerate(items):
        contents_dict_A1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"][i] += round(float(val), 1)

# BAB 2
subtitle_A2 = ["II. Securitization Products", ""]
contents_dict_A2 = {
    "(I) Securities held by your institution as an investor" : [0] * 20,
    "(i) of which exposures with non-prime components" : [0] * 20,
    "(J) Securities held of which your institution is the organitator" : [0] * 20,
    "(i) of which exposures with non-prime components " : [0] * 20,
    "(K) Sub-total (i.e. (I) + (J))" : [0] * 20,
    "(i) of which of which amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 20,
    "Total (L) (i.e. (H) + (K))" : [0] * 20
}

for key, items in contents_dict_A2.items():
    if key == "(K) Sub-total (i.e. (I) + (J))" :
        break
    for i, val in enumerate(items):
        contents_dict_A2["(K) Sub-total (i.e. (I) + (J))"][i] += float(val)
        contents_dict_A2["Total (L) (i.e. (H) + (K))"][i] += float(val) + contents_dict_A2["(i) of which of which amount fully deducted from capital base or subject to 1250% risk weight"][i]

# BAB 3
subtitle_A3 = ["III. Security feature", ""]
contents_dict_A3 = {
    "(i) Senior secured" : [0] * 20,
    "(ii) Senior Unsecured" : [0] * 20,
    "(iii) Subordinated debts" : [0] * 20,
    "(iv) Convertible Bonds" : [0] * 20,
    "(v) Collateralized debt obligations" : [0] * 20,
    "(vi) Mortage-backed securities" : [0] * 20,
    "(vii) Credit-linked notes, equity-linked notes and currency-linked notes" : [0] * 20,
    "(viii) Others" : [0] * 20,
    "Total" : [0] * 20
}

for key, items in contents_dict_A3.items():
    if key == "Total" :
        break
    for i, val in enumerate(items):
        contents_dict_A3["Total"][i] += float(val)

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 2B
title_B= ["Part 2B - Holdings in debt securities (banking book - Amortised cost)", ""]

# BAB 1
subtitle_B1 = ["I. Debt securities other than those reported in section II below", ""]
contents_dict_B1 = {
    "(A) Sovereigns" : get_value("Sovereign", "('BOND')", "('ORI', 'INDOIS')", "('BB BOND AC BMHK')"),
    "(i) Exchange fund bills and notes" : [0] * 20,
    "(ii) Any Other debt securities issued by the Government of the HKSAR" : get_value(None, "('BOND')", "('SVBLCY', 'SVBUSD')", "('BB BOND AC BMHK')"),
    "(iii) US Treasury bills, notes, and bonds" : get_value(None, "('BOND')", "('UST')", "('BB BOND AC BMHK')"),
    "(B) Public sector entities" : get_value("Public sector entities"),
    "(C) Banks" : get_value("Banks", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND AC BMHK')"),
    "(D) Non-bank financial institutions (e.g. securities firms investment banks, fund houses, insurance companies)" : get_value("Non-bank financial institution", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND AC BMHK')"),
    "(E) Investment funds and highly leveraged institutions (e.g. hedge funds)" : get_value("Investment funds and highly leveraged"),
    "(F) Corporates" : get_value("Corporate", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND AC BMHK')"),
    "(G) Other entities not covered above" : get_value("Other entities not covered above"),
    "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" : [0] * 20,
    "(i) Amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 20,
    "(ii) Exposures to sukuk" : [0] * 20,
    "(iii) Goverment Guaranteed" : [0] * 20,
    "(iv) Book value of (H)" : [0] * 20
}

for key, items in contents_dict_B1.items():
    if key == "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" :
        contents_dict_B1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"] = [round(x, 2) for x in contents_dict_B1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"]]
        break
    for i, val in enumerate(items):
        contents_dict_B1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"][i] += float(val)

# BAB 2
subtitle_B2 = ["II. Securitization Products", ""]
contents_dict_B2 = {
    "(I) Securities held by your institution as an investor" : [0] * 20,
    "(i) of which exposures with non-prime components" : [0] * 20,
    "(J) Securities held of which your institution is the organitator" : [0] * 20,
    "(i) of which exposures with non-prime components " : [0] * 20,
    "(K) Sub-total (i.e. (I) + (J))" : [0] * 20,
    "(i) of which amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 20,
    "&emsp;(ii) Book value of (K)" : [0] * 20,
    "Total (L) (i.e. (H) + (K))" : [0] * 20,
    "&emsp;(i) Book value of (L)" : [0] * 20
}

for key, items in contents_dict_B2.items():
    if key == "(K) Sub-total (i.e. (I) + (J))" :
        break
    for i, val in enumerate(items):
        contents_dict_B2["(K) Sub-total (i.e. (I) + (J))"][i] += float(val)
        contents_dict_B2["Total (L) (i.e. (H) + (K))"][i] += float(val) + contents_dict_B2["(i) of which amount fully deducted from capital base or subject to 1250% risk weight"][i]

# BAB 3
subtitle_B3 = ["III. Security feature", ""]
contents_dict_B3 = {
    "(i) Senior secured" : [0] * 20,
    "(ii) Senior Unsecured" : [0] * 20,
    "(iii) Subordinated debts" : [0] * 20,
    "(iv) Convertible Bonds" : [0] * 20,
    "(v) Collateralized debt obligations" : [0] * 20,
    "(vi) Mortage-backed securities" : [0] * 20,
    "(vii) Credit-linked notes, equity-linked notes and currency-linked notes" : [0] * 20,
    "(viii) Others" : [0] * 20,
    "Total" : [0] * 20
}

for key, items in contents_dict_B3.items():
    if key == "Total" :
        break
    for i, val in enumerate(items):
        contents_dict_B3["Total"][i] += float(val)

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 2C
title_C = ["Part 2C - Holdings in debt securities (Trading book - long positions only)", ""]

# BAB 1
subtitle_C1 = ["I. Debt securities other than those reported in section II below", ""]
contents_dict_C1 = {
    "(A) Sovereigns" : get_value("Sovereign", "('BOND')", "('ORI', 'INDOIS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(i) Exchange fund bills and notes" : [0] * 20,
    "(ii) Any Other debt securities issued by the Government of the HKSAR" : get_value(None, "('BOND')", "('SVBLCY', 'SVBUSD')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(iii) US Treasury bills, notes, and bonds" : get_value(None, "('BOND')", "('UST')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(B) Public sector entities" : get_value("Public sector entities"),
    "(C) Banks" : get_value("Banks", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(D) Non-bank financial institutions (e.g. securities firms investment banks, fund houses, insurance companies)" : get_value("Non-bank financial institution", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(E) Investment funds and highly leveraged institutions (e.g. hedge funds)" : get_value("Investment funds and highly leveraged"),
    "(F) Corporates" : get_value("Corporate", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(G) Other entities not covered above" : get_value("Other entities not covered above"),
    "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" : [0] * 20,
    "(i) Amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 20,
    "(ii) Exposures to sukuk" : [0] * 20,
    "(iii) Goverment Guaranteed" : [0] * 20
}

for key, items in contents_dict_C1.items():
    if key == "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" :
        contents_dict_C1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"] = [round(x, 2) for x in contents_dict_C1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"]]
        break
    for i, val in enumerate(items):
        contents_dict_C1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"][i] += float(val)

# BAB 2
subtitle_C2 = ["II. Securitization Products", ""]
contents_dict_C2 = {
    "(I) Securities held by your institution as an investor" : [0] * 20,
    "(i) of which exposures with non-prime components" : [0] * 20,
    "(J) Securities held of which your institution is the organitator" : [0] * 20,
    "(i) of which exposures with non-prime components " : [0] * 20,
    "(K) Sub-total (i.e. (I) + (J))" : [0] * 20,
    "(i) of which amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 20,
    "Total (L) (i.e. (H) + (K))" : [0] * 20
}

for key, items in contents_dict_C2.items():
    if key == "(K) Sub-total (i.e. (I) + (J))" :
        break
    for i, val in enumerate(items):
        contents_dict_C2["(K) Sub-total (i.e. (I) + (J))"][i] += float(val)
        contents_dict_C2["Total (L) (i.e. (H) + (K))"][i] += float(val) + contents_dict_C2["(i) of which amount fully deducted from capital base or subject to 1250% risk weight"][i]

# BAB 3
subtitle_C3 = ["III. Security feature", ""]
contents_dict_C3 = {
    "(i) Senior secured" : [0] * 20,
    "(ii) Senior Unsecured" : [0] * 20,
    "(iii) Subordinated debts" : [0] * 20,
    "(iv) Convertible Bonds" : [0] * 20,
    "(v) Collateralized debt obligations" : [0] * 20,
    "(vi) Mortage-backed securities" : [0] * 20,
    "(vii) Credit-linked notes, equity-linked notes and currency-linked notes" : [0] * 20,
    "(viii) Others" : [0] * 20,
    "Total" : [0] * 20
}

for key, items in contents_dict_C3.items():
    if key == "Total" :
        break
    for i, val in enumerate(items):
        contents_dict_C3["Total"][i] += float(val)

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 2D
title_D = ["Part 2D - Holdings in debt securities (Trading book - both long and short positions on a net basis)", ""]

# BAB 1
subtitle_D1 = ["I. Debt securities other than those reported in section II", ""]
contents_dict_D1 = {
    "(A) Sovereigns" : get_value("Sovereign", "('BOND')", "('ORI', 'INDOIS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(i) Exchange fund bills and notes" : [0] * 20,
    "(ii) Any Other debt securities issued by the Government of the HKSAR" : get_value(None, "('BOND')", "('SVBLCY', 'SVBUSD')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(iii) US Treasury bills, notes, and bonds" : get_value(None, "('BOND')", "('UST')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(B) Public sector entities" : get_value("Public sector entities"),
    "(C) Banks" : get_value("Banks", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(D) Non-bank financial institutions (e.g. securities firms investment banks, fund houses, insurance companies)" : get_value("Non-bank financial institution", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(E) Investment funds and highly leveraged institutions (e.g. hedge funds)" : get_value("Investment funds and highly leveraged"),
    "(F) Corporates" : get_value("Corporate", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(G) Other entities not covered above" : get_value("Other entities not covered above"),
    "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" : [0] * 20,
    "(i) Amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 20,
    "(ii) Exposures to sukuk" : [0] * 20,
    "(iii) Goverment Guaranteed" : [0] * 20
}

for key, items in contents_dict_D1.items():
    if key == "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" :
        contents_dict_D1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"] = [round(x, 2) for x in contents_dict_D1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"]]
        break
    for i, val in enumerate(items):
        contents_dict_D1["(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))"][i] += float(val)

# BAB 2
subtitle_D2 = ["II. Securitization Products", ""]
contents_dict_D2 = {
    "(I) Securities held by your institution as an investor" : [0] * 20,
    "(i) of which exposures with non-prime components" : [0] * 20,
    "(J) Securities held of which your institution is the organitator" : [0] * 20,
    "(i) of which exposures with non-prime components " : [0] * 20,
    "(K) Sub-total (i.e. (I) + (J))" : [0] * 20,
    "(i) of which amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 20,
    "Total (L) (i.e. (H) + (K))" : [0] * 20
}

for key, items in contents_dict_D2.items():
    if key == "(K) Sub-total (i.e. (I) + (J))" :
        break
    for i, val in enumerate(items):
        contents_dict_D2["(K) Sub-total (i.e. (I) + (J))"][i] += float(val)
        contents_dict_D2["Total (L) (i.e. (H) + (K))"][i] += float(val) + contents_dict_D2["(i) of which amount fully deducted from capital base or subject to 1250% risk weight"][i]

# BAB 3
subtitle_D3 = ["III. Security feature", ""]
contents_dict_D3 = {
    "(i) Senior secured" : [0] * 20,
    "(ii) Senior Unsecured" : [0] * 20,
    "(iii) Subordinated debts" : [0] * 20,
    "(iv) Convertible Bonds" : [0] * 20,
    "(v) Collateralized debt obligations" : [0] * 20,
    "(vi) Mortage-backed securities" : [0] * 20,
    "(vii) Credit-linked notes, equity-linked notes and currency-linked notes" : [0] * 20,
    "(viii) Others" : [0] * 20,
    "Total" : [0] * 20
}

for key, items in contents_dict_D3.items():
    if key == "Total" :
        break
    for i, val in enumerate(items):
        contents_dict_D3["Total"][i] += float(val)

############################################################################################
# GENERATING HTML CODE & CONVERT TO XLS 
############################################################################################
def open_table():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
<table style="width: fit-content">
"""

## HEADER TEMPLATE OF HTML 
def table_header(row_header, header_cell_span):
    style_1 = "text-align : center; font-weight:bold; border:1px solid black; vertical-align: middle;"
    style_2 = "text-align : center; font-weight:bold; border-left:1px solid black; border-right:1px solid black; vertical-align: middle;"
    style_3 = "text-align : center; font-weight:bold; border-left:1px solid black; border-right:1px solid black; border-bottom:1px solid black; vertical-align: middle;"
    html_code = ""

    i = 0
    for row_header_list, span_header_list in zip(row_header, header_cell_span):
        i += 1
        html_code += '<tr>\n<td style="width: 15px"></td>\n'
        for header_content, cell_span in zip(row_header_list, span_header_list):
            background_color_condition = i == 3 and header_content == ""
            style_condition = header_content not in [row_header_2[0], ""] and i != 4
            style_condition2 = header_content not in [row_header_2[0], ""]
            style = f'background-color:{"black" if background_color_condition else "white"};{style_1 if style_condition else style_3 if i == 4 else style_2}'
            html_code += f'<td style="{style}" colspan="{cell_span[0]}" rowspan="{cell_span[1]}"> {header_content} </td>\n'
        html_code += "</tr>\n"
    return html_code

def title_subtitle(list_content, style=''):
    html_code = '<tr>\n<td style="width: 15px"></td>\n'
    cond = 'colspan="22"'
    html_code += f'<td style="{style}" {cond}>{list_content[0]}</td>' + "\n"
    html_code += "</tr>\n"
    
    return html_code
    
## BODY TEMPLATE OF HTML
def table_body(content_dict, style='', with_ofwhich=True, space=2):
    space = 1 if str(list(content_dict.keys())[0]) == "(i) Senior secured" else 2
    include_word = ["(i)", "(ii)", "(iii)", "(iv)", "(v)", "(vi)", "(vii)", "(viii)"]
    html_code = ""
    
    for key_content, list_val_content in content_dict.items():
        html_code += '<tr>\n<td style="width: 15px"></td>\n'
        if any(key in key_content for key in [f"({alphabeth})" for alphabeth in list(string.ascii_uppercase)]):
            if "Total" in key_content :
                html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px; font-weight: bold;">{key_content}</td>\n'
            else :
                html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;">&emsp;{key_content}</td>\n'
        elif any(x in key_content for x in include_word):
            html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;">{"&emsp;&emsp;- of which:<br>" if ("(i)") in key_content and with_ofwhich else ""}{"&emsp;" * space}{key_content}</td>\n'
        else :
            html_code += f'<td colspan="2" style="border-bottom: 1px solid black; border-left: 1px solid black; width:500px;">&emsp;{key_content}</td>\n'

        for i, val_content in enumerate(list_val_content):
            border_sty = "1px solid black"
            content_style = f'background-color:{"#87e8a1" if i <= 1 else ""};border-bottom: {border_sty}; border-left: {border_sty}; border-right: {border_sty if i == len(list_val_content) - 1 else ""}; width: 150px'
            html_code += f'<td style="text-align: right; {content_style}">{val_content}</td>\n'
            
        html_code += "</tr>\n" 
    
    return html_code

def html_to_xls(report_folder, report_name):
    skip_row = '<tr><td>&nbsp;</td><td colspan="22" style="border-bottom: 1px solid">&nbsp;</td></tr>'
    
    code = open_table()
    code += '<tr><td>&nbsp;</td><td style="font-weight: bold"colspan="22">Part 2 - Holding in debt securities - by credit quality</td></tr>'
    code += '<tr><td>&nbsp;</td><td style="border-bottom: 1px black solid" colspan="22">AMT (current market value unless otherwise specified) and PV01 in HK$\'000</td></tr>'
    code += table_header(row_header, header_cell_span)
    
    title_style = "font-weight: bold; border-left: 1px solid black; border-right: 1px solid black;"
    subtitle_style = "font-weight: bold; background-color:#999897; border-left: 1px solid black; border-right: 1px solid black;"
    list_template_order = [
                      title_A, subtitle_A1, contents_dict_A1, subtitle_A2, contents_dict_A2, subtitle_A3, contents_dict_A3, skip_row,
                      title_B, subtitle_B1, contents_dict_B1, subtitle_B2, contents_dict_B2, subtitle_B3, contents_dict_B3, skip_row,
                      title_C, subtitle_C1, contents_dict_C1, subtitle_C2, contents_dict_C2, subtitle_C3, contents_dict_C3, skip_row,
                      title_D, subtitle_D1, contents_dict_D1, subtitle_D2, contents_dict_D2, subtitle_D3, contents_dict_D3]

    for template_order in list_template_order:
        if template_order in [title_A, title_B, title_C, title_D] :
            code += title_subtitle(template_order, style=title_style)
        elif template_order == skip_row:
            code += template_order
        elif template_order in [subtitle_A1, subtitle_A2, subtitle_A3, subtitle_B1, subtitle_B2, subtitle_B3, subtitle_C1, subtitle_C2, subtitle_C3, subtitle_D1, subtitle_D2, subtitle_D3]:
            code += title_subtitle(template_order, style=subtitle_style)
        elif template_order in [contents_dict_A2, contents_dict_B2, contents_dict_C2, contents_dict_D2, contents_dict_A3, contents_dict_B3, contents_dict_C3, contents_dict_D3]:
            code += table_body(template_order, with_ofwhich=False)
        else :
            code += table_body(template_order)
    
    file_path = os.path.join(report_folder, report_name)
    f = open(file_path, "w")
    f.write(code + "</table></body></html>")
    f.close()

##################################################################################

# CREATING A GUI PARAMETER

##################################################################################
ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'HKCO01b - ICC - HKMAs Survey on Debt Securities Held'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'HKCO01b - ICC - HKMAs Survey on Debt Securities Held', 1, 0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Output Files','string', ['.pdf', '.xls'], '.xls', 0 , 0, 'Select Output Extension Type']
]

def ael_main(parameter):
    ## DEFINE GUI PARAMETER IN VARIABLE
    report_name = parameter['report_name'] + ".xls"
    file_path = str(parameter['file_path'])
    output_file = "".join(parameter['output_file'])
    
    folder_name = "report"+date.today().strftime("%Y%m%d")
    report_folder = os.path.join(file_path, folder_name)
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    if ".xls" in output_file:
        html_to_xls(report_folder, report_name)
