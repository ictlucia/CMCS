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

def get_trdnbr(buss_status, rating_list, optkey3="", optkey4="", portfolio=""):    

    optkey3_query = "WHERE DISPLAY_ID(t, 'optkey3_chlnbr') in " + optkey3 + "\n" if optkey3 != "" else ""
    optkey4_query = " AND DISPLAY_ID(t, 'optkey4_chlnbr') in " + optkey4 + "\n" if optkey4 != "" else ""
    portfolio_query = " AND DISPLAY_ID(t, 'prfnbr') in " + portfolio + "\n" if portfolio != "" else ""
    
    query_string = """
        SELECT 
            t.trdnbr, t.insaddr
        FROM 
            Trade t
    """ + optkey3_query + optkey4_query + portfolio_query
            
    if optkey3 != "" and optkey4 != "" and portfolio != "":
        query_results = ael.asql(query_string)[1][0]
    else :
        query_results = [[None, None]]
       
    trdinfo_list = []
    for query_result in query_results:
        trdnbr, insaddr = query_result
        
        try :
            rating_snp = acm.FTrade[trdnbr].Instrument().Rating2ChlItem().Name() if acm.FTrade[trdnbr].Instrument().Rating2ChlItem() != None else None        
        except :
            rating_snp = None
        
        try :
            business_status = acm.FTrade[trdnbr].Counterparty().AdditionalInfo().Business_Status()
        except :
            business_status = None
        
        if rating_snp in rating_list and business_status == buss_status:
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

def get_arm(trdinfo_list):
    unique_ins = list(set([x[1] for x in trdinfo_list]))
    unique_ins.sort()
    
    arm = 0
    for ins in unique_ins:
        total_principal_amount = 0
        day_range_and_principal = []
        trade_used = [trdnbr for trdnbr, insaddr in trdinfo_list if insaddr == ins]
        for trdnbr in trade_used:
            try :
                trade = acm.FTrade[trdnbr]
            except :
                break
            principal_amount = abs(trade.Nominal()) * abs(trade.Price())
            total_days = get_days_range(trade)
            day_range_and_principal.append([principal_amount, total_days])
            total_principal_amount += principal_amount
        
        for list_val in day_range_and_principal:
            try :
                arm += list_val[0] * (list_val[1] / total_principal_amount)
            except :
                arm += 0
            
    return arm

def get_value(buss_status, rating_list, optkey3="", optkey4="", portfolio=""):
    trdinfo_list = get_trdnbr(buss_status, rating_list, optkey3, optkey4, portfolio)
    
    row_val = [0, 0, 0]
    for trdnbr, insaddr in trdinfo_list:
        try :
            trade = acm.FTrade[trdnbr]
        except:
            break
            
        context = acm.GetDefaultContext()
        columnId_IC = 'Instrument Convexity'
        columnId_marketVal = 'Portfolio PL Market Value'
            
        calcSpace = acm.Calculations().CreateCalculationSpace(context, "FTradeSheet")
        calculation_mv = calcSpace.CreateCalculation(trade, columnId_marketVal).FormattedValue().replace(".", "").replace(",", ".")
        try :
            calculation_cv = calcSpace.CreateCalculation(trade, columnId_IC).FormattedValue().replace(".", "").replace(",", ".")
        except :
            calculation_cv = 0
        
        amt = calculation_mv if calculation_mv != "" else 0
        cv01 = calculation_cv if calculation_cv != "" else 0
            
        if trade.Instrument().Currency().Name() != "USD" :
            usd_rate = usd_price_mtm(trade, curr_target='USD') if usd_price_mtm(trade, curr_target='USD') != None else 1
        else :
            usd_rate = 1
        
        result_trade = [amt, cv01, 0]
        for i, _ in enumerate(result_trade):
            try :
                add_val = "".join([x for x in str(result_trade[i]) if x.isdigit() or x == "." or x == "-"])
                add_val_f = float(add_val) if add_val != "" else 0
            except :
                add_val = "".join([x for x in str(result_trade[i]) if x.isdigit() or x == "," or x == "-"])
                add_val_f = float(add_val) if add_val != "" else 0
                
            row_val[i] += add_val_f * usd_rate
            
    
    arm = get_arm([trdinfo for trdinfo in trdinfo_list])
    row_val[-1] = float(f"{arm:.2f}") if arm != 0 else 0
    return row_val

def get_values_row(buss_status=None, optkey3="", optkey4="", portfolio=""):
    row_values = [0, 0, 0]
    
    rating_list_2d = [
        ["AAA"],
        ["AA+", "AA", "AA-"],
        ["A+", "A", "A-"],
        ["BBB+", "BBB", "BBB-"],
        ["BB+", "BB", "BB-"],
        ["B+", "B", "B-", "CCC+", "CCC", "CCC-", "CC", "R", "C", "D", "NR"],
        [None]
    ] 
    
    for rating_list in rating_list_2d:
        result_list = get_value(buss_status, rating_list, optkey3, optkey4, portfolio)
        for i in range(3):
            row_values[i] += result_list[i]
        row_values.extend(result_list)
    
    return row_values + [0]*2

##################################################################################################
### HTML TABLE HEADER, TITLE, SUBTITLE, AND VALUE CONTENT
##################################################################################################
## HEADER CONTENT AND SPAN FORMATING
row_header_1 = ["", "Total", "Credit Rating", "of which amount fully deducted from capital base or subjuct to 1250% risk-weight"]
row_header_2 = ["Types of instrument and issuer / Credit ratings", "Long term ratings", 
                "AAA", "AA+ to AA-", "A+ to A-", "BBB+ to BBB-", "BB+ to BB-", "B+ and below", "Unrated"]
row_header_3 = ["Short term ratings", "A-1+", "A-1", "A-2", "A-3", "B or below", ""]
row_header_4 = ([""] + ["AMT", "CV01", "Average remaining maturity"] * 8) + ["Of which amount fully deducted from capital base or subject to 1250% risk-weight", "AMT"]

header_cell_span_1 = [["2", "1"], ["3", "3"], ["22", "1"], ["1", "3"]]
header_cell_span_2 = [["1", "2"], ["1", "1"]] + [["3", "1"]] * 6 + [["4", "2"]]
header_cell_span_3 = [["1", "1"]] + [["3", "1"]] * 6
header_cell_span_4 = [["2", "1"]] + [["1", "1"]] * 26

row_header = [row_header_1, row_header_2, row_header_3, row_header_4]
header_cell_span = [header_cell_span_1, header_cell_span_2, header_cell_span_3, header_cell_span_4]

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 1A
title_A = ["Part 1A - Holdings in debt securities (banking book - Fair value through other comprehensive income/Fair value through profit or loss)", ""]

# BAB 1
subtitle_A1 = ["I. Debt securities other than those reported in section I below", ""]
contents_dict_A1 = {
    "(A) Sovereigns" : get_values_row("Sovereign", "('BOND')", "('ORI', 'INDOIS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(i) Exchange fund bills and notes" : [0] * 26,
    "(ii) Any Other debt securities issued by the Government of the HKSAR" : get_values_row(None, "('BOND')", "('SVBLCY', 'SVBUSD')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(iii) US Treasury bills, notes, and bonds" : get_values_row(None, "('BOND')", "('UST')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(B) Public sector entities" : get_values_row("Public sector entities"),
    "(C) Banks" : get_values_row("Banks", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(D) Non-bank financial institutions (e.g. securities firms investment banks, fund houses, insurance companies)" : get_values_row("Non-bank financial institution", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(E) Investment funds and highly leveraged institutions (e.g. hedge funds)" : get_values_row("Investment funds and highly leveraged"),
    "(F) Corporates" : get_values_row("Corporate", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND OCI BMHK', 'BB BOND PL BMHK')"),
    "(G) Other entities not covered above" : get_values_row("Other entities not covered above"),
    "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" : [0] * 26,
    "(i) Amount fully deducted from capital base or subject to 1250% risk-weight" : [0] * 26,
    "(ii) Exposures to sukuk" : [0] * 26,
    "(iii) Goverment Guaranteed" : [0] * 26
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
    "(I) Securities held by your institution as an investor" : [0] * 26,
    "(i) of which exposures with non-prime components" : [0] * 26,
    "(J) Securities held of which your institution is the organitator" : [0] * 26,
    "(i) of which exposures with non-prime components " : [0] * 26,
    "(K) Sub-total (i.e. (I) + (J))" : [0] * 26,
    "(i) of which of which amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 26,
    "Total (L) (i.e. (H) + (K))" : [0] * 26
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
    "(i) Senior secured" : [0] * 26,
    "(ii) Senior Unsecured" : [0] * 26,
    "(iii) Subordinated debts" : [0] * 26,
    "(iv) Convertible Bonds" : [0] * 26,
    "(v) Collateralized debt obligations" : [0] * 26,
    "(vi) Mortage-backed securities" : [0] * 26,
    "(vii) Credit-linked notes, equity-linked notes and currency-linked notes" : [0] * 26,
    "(viii) Others" : [0] * 26,
    "Total" : [0] * 26
}

for key, items in contents_dict_A3.items():
    if key == "Total" :
        break
    for i, val in enumerate(items):
        contents_dict_A3["Total"][i] += float(val)

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 1B
title_B= ["Part 1B - Holdings in debt securities (banking book - Amortised cost)", ""]

# BAB 1
subtitle_B1 = ["I. Debt securities other than those reported in section II below", ""]
contents_dict_B1 = {
    "(A) Sovereigns" : get_values_row("Sovereign", "('BOND')", "('ORI', 'INDOIS')", "('BB BOND AC BMHK')"),
    "(i) Exchange fund bills and notes" : [0] * 26,
    "(ii) Any Other debt securities issued by the Government of the HKSAR" : get_values_row(None, "('BOND')", "('SVBLCY', 'SVBUSD')", "('BB BOND AC BMHK')"),
    "(iii) US Treasury bills, notes, and bonds" : get_values_row(None, "('BOND')", "('UST')", "('BB BOND AC BMHK')"),
    "(B) Public sector entities" : get_values_row("Public sector entities"),
    "(C) Banks" : get_values_row("Banks", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND AC BMHK')"),
    "(D) Non-bank financial institutions (e.g. securities firms investment banks, fund houses, insurance companies)" : get_values_row("Non-bank financial institution", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND AC BMHK')"),
    "(E) Investment funds and highly leveraged institutions (e.g. hedge funds)" : [0] * 26,
    "(F) Corporates" : get_values_row("Corporate", "('BOND')", "('CBUSD', 'CBVALAS')", "('BB BOND AC BMHK')"),
    "(G) Other entities not covered above" : get_values_row("Other entities not covered above"),
    "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" : [0] * 26,
    "(i) Amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 26,
    "(ii) Exposures to sukuk" : [0] * 26,
    "(iii) Goverment Guaranteed" : [0] * 26,
    "(iv) Book value of (H)" : [0] * 26
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
    "(I) Securities held by your institution as an investor" : [0] * 26,
    "(i) of which exposures with non-prime components" : [0] * 26,
    "(J) Securities held of which your institution is the organitator" : [0] * 26,
    "(i) of which exposures with non-prime components " : [0] * 26,
    "(K) Sub-total (i.e. (I) + (J))" : [0] * 26,
    "(i) of which amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 26,
    "&emsp;(ii) Book value of (K)" : [0] * 26,
    "Total (L) (i.e. (H) + (K))" : [0] * 26,
    "&emsp;(i) Book value of (L)" : [0] * 26
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
    "(i) Senior secured" : [0] * 26,
    "(ii) Senior Unsecured" : [0] * 26,
    "(iii) Subordinated debts" : [0] * 26,
    "(iv) Convertible Bonds" : [0] * 26,
    "(v) Collateralized debt obligations" : [0] * 26,
    "(vi) Mortage-backed securities" : [0] * 26,
    "(vii) Credit-linked notes, equity-linked notes and currency-linked notes" : [0] * 26,
    "(viii) Others" : [0] * 26,
    "Total" : [0] * 26
}

for key, items in contents_dict_B3.items():
    if key == "Total" :
        break
    for i, val in enumerate(items):
        contents_dict_B3["Total"][i] += float(val)

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 1C
title_C = ["Part 1C - Holdings in debt securities (Trading book - long positions only)", ""]

# BAB 1
subtitle_C1 = ["I. Debt securities other than those reported in section II below", ""]
contents_dict_C1 = {
    "(A) Sovereigns" : get_values_row("Sovereign", "('BOND')", "('ORI', 'INDOIS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(i) Exchange fund bills and notes" : [0] * 26,
    "(ii) Any Other debt securities issued by the Government of the HKSAR" : get_values_row(None, "('BOND')", "('SVBLCY', 'SVBUSD')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(iii) US Treasury bills, notes, and bonds" : get_values_row(None, "('BOND')", "('UST')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(B) Public sector entities" : get_values_row("Public sector entities"),
    "(C) Banks" : get_values_row("banks", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(D) Non-bank financial institutions (e.g. securities firms investment banks, fund houses, insurance companies)" : get_values_row("Non-bank financial institution", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(E) Investment funds and highly leveraged institutions (e.g. hedge funds)" : get_values_row("Investment funds and highly leveraged"),
    "(F) Corporates" : get_values_row("Corporate", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(G) Other entities not covered above" : get_values_row("Other entities not covered above"),
    "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" : [0] * 26,
    "(i) Amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 26,
    "(ii) Exposures to sukuk" : [0] * 26,
    "(iii) Goverment Guaranteed" : [0] * 26
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
    "(I) Securities held by your institution as an investor" : [0] * 26,
    "(i) of which exposures with non-prime components" : [0] * 26,
    "(J) Securities held of which your institution is the organitator" : [0] * 26,
    "(i) of which exposures with non-prime components " : [0] * 26,
    "(K) Sub-total (i.e. (I) + (J))" : [0] * 26,
    "(i) of which amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 26,
    "Total (L) (i.e. (H) + (K))" : [0] * 26
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
    "(i) Senior secured" : [0] * 26,
    "(ii) Senior Unsecured" : [0] * 26,
    "(iii) Subordinated debts" : [0] * 26,
    "(iv) Convertible Bonds" : [0] * 26,
    "(v) Collateralized debt obligations" : [0] * 26,
    "(vi) Mortage-backed securities" : [0] * 26,
    "(vii) Credit-linked notes, equity-linked notes and currency-linked notes" : [0] * 26,
    "(viii) Others" : [0] * 26,
    "Total" : [0] * 26
}

for key, items in contents_dict_C3.items():
    if key == "Total" :
        break
    for i, val in enumerate(items):
        contents_dict_C3["Total"][i] += float(val)

# ------------------------------------------------------------------------------------------------------------------------------------------
## PART 1D
title_D = ["Part 1D - Holdings in debt securities (Trading book - both long and short positions on a net basis)", ""]

# BAB 1
subtitle_D1 = ["I. Debt securities other than those reported in section II", ""]
contents_dict_D1 = {
    "(A) Sovereigns" : get_values_row("Sovereign", "('BOND')", "('ORI', 'INDOIS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(i) Exchange fund bills and notes" : [0] * 26,
    "(ii) Any Other debt securities issued by the Government of the HKSAR" : get_values_row(None, "('BOND')", "('SVBLCY', 'SVBUSD')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(iii) US Treasury bills, notes, and bonds" : get_values_row(None, "('BOND')", "('UST')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(B) Public sector entities" : get_values_row("Public sector entities"),
    "(C) Banks" : get_values_row("Banks", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(D) Non-bank financial institutions (e.g. securities firms investment banks, fund houses, insurance companies)" : get_values_row("Non-bank financial institution", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(E) Investment funds and highly leveraged institutions (e.g. hedge funds)" : get_values_row("Investment funds and highly leveraged"),
    "(F) Corporates" : get_values_row("Corporate", "('BOND')", "('CBUSD', 'CBVALAS')", "('IRT DCM 1 BMHK', 'IRT DCM 2 BMHK')"),
    "(G) Other entities not covered above" : get_values_row("Other entities not covered above"),
    "(H) Sub-total (i.e. (A)+(B)+(C)+(D)+(E)+(F)+(G))" : [0] * 26,
    "(i) Amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 26,
    "(ii) Exposures to sukuk" : [0] * 26,
    "(iii) Goverment Guaranteed" : [0] * 26
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
    "(I) Securities held by your institution as an investor" : [0] * 26,
    "(i) of which exposures with non-prime components" : [0] * 26,
    "(J) Securities held of which your institution is the organitator" : [0] * 26,
    "(i) of which exposures with non-prime components " : [0] * 26,
    "(K) Sub-total (i.e. (I) + (J))" : [0] * 26,
    "(i) of which amount fully deducted from capital base or subject to 1250% risk weight" : [0] * 26,
    "Total (L) (i.e. (H) + (K))" : [0] * 26
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
    "(i) Senior secured" : [0] * 26,
    "(ii) Senior Unsecured" : [0] * 26,
    "(iii) Subordinated debts" : [0] * 26,
    "(iv) Convertible Bonds" : [0] * 26,
    "(v) Collateralized debt obligations" : [0] * 26,
    "(vi) Mortage-backed securities" : [0] * 26,
    "(vii) Credit-linked notes, equity-linked notes and currency-linked notes" : [0] * 26,
    "(viii) Others" : [0] * 26,
    "Total" : [0] * 26
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
    cond = 'colspan="28"'
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
            content_style = f'background-color:{"#87e8a1" if i <= 1 else ""};border-bottom: {border_sty}; border-left: {border_sty}; border-right: {border_sty if i == len(list_val_content) - 1 else ""}; width: 180px'
            html_code += f'<td style="text-align: right; {content_style}">{val_content}</td>\n'
            
        html_code += "</tr>\n" 
    
    return html_code

def html_to_xls(report_folder, report_name):
    skip_row = '<tr><td>&nbsp;</td><td colspan="28" style="border-bottom: 1px solid">&nbsp;</td></tr>'
    
    code = open_table()
    code += '<tr><td>&nbsp;</td><td style="font-weight: bold"colspan="28">Part 1 - Holding in debt securities - by credit quality</td></tr>'
    code += '<tr><td>&nbsp;</td><td style="border-bottom: 1px black solid" colspan="28">AMT (current market unless otherwise specified) and CV01 in HK$\'000; Average remaining maturity of years (2 decimal places)</td></tr>'
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
                    'windowCaption':'HKCO01a - ICC - HKMAs Survey on Debt Securities Held'}
                    
ael_variables=[
['report_name','Report Name','string', None, 'HKCO01a - ICC - HKMAs Survey on Debt Securities Held', 1,0],
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
