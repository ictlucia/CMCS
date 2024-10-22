from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael
from Report_Python import *

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Daily Cust Report'}

def get_ins_num(insid):
    instrument = acm.FInstrument[insid]
    return instrument.Oid()

def get_ins_name(insid):
    instrument = acm.FInstrument[insid]
    return instrument.Name()
    

def get_optkey3_oid(optkey_string):
    optkey = acm.FChoiceList.Select('list=Product Type')
    for name in optkey:
        if name.Name()== optkey_string:
            return name.Oid()

def get_optkey4_oid(optkey_string):
    optkey = acm.FChoiceList.Select('list=Category')
    for name in optkey:
        if name.Name()== optkey_string:
            return name.Oid()

def get_ctype_name(free2_oid):
    all_ctype = acm.FChoiceList.Select('list = Customer Type')
    for each_ctype in all_ctype:
        if each_ctype.Oid()== free2_oid:
            return each_ctype.Name()
            
def get_top10_count(trades,date):
    counterparty_totals = {}
    for transaction in trades:
        counterparty_name = transaction['counterparty']
        currency = transaction['currency']
        if currency == "USD":
            quantity_usd = transaction['quantity']
        else:
            quantity_usd = get_cross_rate(currency,date)*transaction['quantity'] 
        
        if counterparty_name not in counterparty_totals:
            counterparty_totals[counterparty_name] = 0
        
        counterparty_totals[counterparty_name] += quantity_usd

    sorted_counterparties = sorted(counterparty_totals.items(), key=lambda x: x[1], reverse=True)
    return sorted_counterparties[:10]

#settings.FILE_EXTENSIONS
ael_variables=[
['report_name','Report Name','string', None, 'TAS Report - Daily Cust Report', 1,0],
['file_path', 'Folder Path', getFilePathSelection(), None, getFilePathSelection(), 1, 1],
['output_file','Secondary Output Files','string', ['.pdf', '.xls'], '.pdf',0,1, 'Select Secondary Extensions Output'],
['date','Date','string',None,acm.Time.DateToday(),0,1]
]  
def ael_main(parameter):
    report_name = parameter['report_name']
    file_path = str(parameter['file_path'])
    output_file = parameter['output_file']
    date = parameter['date']
    total_a,total_b,total_c,total_d,total_e = 0,0,0,0,0
    total_f,total_g,total_h,total_i,total_j,total_m,total_n,total_o,total_p = 0,0,0,0,0,0,0,0,0
    # QUERY: Sum of FX Transaction (FX TOD TOM SPOT OPT NS)
    value_a = ael.asql(f""" SELECT t.quantity, t.insaddr
                                FROM trade t, portfolio p WHERE
                                t.time >= '{str(date[0])}'
                                and t.time < '{acm.Time.DateAddDelta(date[0],0,0,1)}'
                                and t.curr = '{str(get_ins_num('IDR'))}'
                                AND t.prfnbr = p.prfnbr
                                AND display_id(t, 'optkey3_chlnbr') = 'FX'
                                AND (display_id(t, 'optkey4_chlnbr') = 'TOD' 
                                OR display_id(t, 'optkey4_chlnbr') = 'TOM'
                                OR display_id(t, 'optkey4_chlnbr') = 'SPOT'
                                OR display_id(t, 'optkey4_chlnbr') = 'FWD')
                                and (t.status ~='Internal' or t.status ~='Void')
                                AND (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                                """)
    if len(value_a[1][0])>0:
        for volume,curr in value_a[1][0]:
            if get_ins_name(curr)== "USD":
                total_a += abs(volume)
            else:
                total_a+=get_cross_rate(get_ins_name(curr),date[0])*abs(volume)
    else:
        total_a =0
    
    # QUERY: Trade Key 3 = FX, Trade Key 4 = NS
    value_b = ael.asql(f"""SELECT abs(t.premium),t.curr
                        FROM trade t, portfolio p WHERE t.time>='{str(date[0])}'
                        AND t.time<'{acm.Time.DateAddDelta(date[0],0,0,1)}'
                        AND t.prfnbr = p.prfnbr AND (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                        AND display_id(t, 'optkey3_chlnbr') = 'FX'
                        AND (display_id(t, 'optkey4_chlnbr') = 'NS')
                        AND (t.status ~='Internal' or t.status ~='Void')
                    """)
                        
    if len(value_b[1][0])>0:
        for volume,curr in value_b[1][0]:
            if get_ins_name(curr)== "USD":
                total_b+=volume
            else:
                total_b+=get_cross_rate(get_ins_name(curr),date[0])*volume
    else:
        total_b = 0
    
    # QUERY: SUM of SWAP (FX SWAP)
    value_c = ael.asql(f"""SELECT abs(t.quantity),t.insaddr
                        FROM trade t, portfolio p WHERE t.time>='{str(date[0])}'
                        AND t.time<'{acm.Time.DateAddDelta(date[0],0,0,1)}'
                        AND t.prfnbr = p.prfnbr AND (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                        AND display_id(t, 'optkey3_chlnbr') = 'FX'
                        AND (display_id(t, 'optkey4_chlnbr') = 'SWAP')
                        AND (t.status ~='Internal' or t.status ~='Void')
                    """)
          
    if len(value_c[1][0])>0:
        for volume,curr in value_c[1][0]:
            if get_ins_name(curr)== "USD":
                total_c+=volume
            else:
                total_c+=get_cross_rate(get_ins_name(curr),date[0])*volume
    else:
        total_c = 0
    
    # QUERY: Currency = IDR, Instrument = IDR
    value_d = ael.asql(f"""SELECT t.quantity, t.insaddr 
                            FROM trade t, portfolio p WHERE 
                            t.time >= '{str(date[0])}'
                            AND t.time < '{acm.Time.DateAddDelta(date[0],0,0,1)}'
                            AND t.insaddr ~='{str(get_ins_num('IDR'))}'
                            AND t.curr ~= '{str(get_ins_num('IDR'))}'
                            AND t.prfnbr = p.prfnbr
                            AND (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                            AND display_id(t, 'optkey3_chlnbr') = 'FX'
                            AND (display_id(t, 'optkey4_chlnbr') = 'TOD' 
                            OR display_id(t, 'optkey4_chlnbr') = 'TOM'
                            OR display_id(t, 'optkey4_chlnbr') = 'SPOT'
                            OR display_id(t, 'optkey4_chlnbr') = 'FWD')
                            and (t.status ~='Internal' or t.status ~='Void')
                        """)
                        
    if len(value_d[1][0])>0:
        for volume,curr in value_d[1][0]:
            if get_ins_name(curr)== "USD":
                total_d+=abs(volume)
            else:
                total_d+=get_cross_rate(get_ins_name(curr),date[0])*abs(volume)
    else:
        total_d = 0
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MDS
    value_e = ael.asql("SELECT abs(t.quantity),t.insaddr FROM trade t,instrument i WHERE t.insaddr = i.insaddr and i.instype='Curr' and t.time>='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and t.optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and t.optkey4_chlnbr="+str(get_optkey4_oid('MDS')))
    if len(value_e[1][0])>0:
        for volume,curr in value_e[1][0]:
            if get_ins_name(curr)== "USD":
                total_e+=volume
            else:
                total_e+=get_cross_rate(get_ins_name(curr),date[0])*volume
    else:
        total_e = 0
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MMLD
    value_f = ael.asql("SELECT abs(t.premium),t.curr FROM trade t, instrument i WHERE t.insaddr = i.insaddr and i.instype = 'Option' and t.time>='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and t.optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and t.optkey4_chlnbr="+str(get_optkey4_oid('MMLD')))
    if len(value_f[1][0])>0:
        for volume,curr in value_f[1][0]:
            if get_ins_name(curr)== "USD":
                total_f+=volume
            else:
                total_f+=get_cross_rate(get_ins_name(curr),date[0])*volume
    else:
        total_f = 0
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MDCI
    value_g = ael.asql("SELECT abs(premium),curr FROM trade WHERE time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and optkey4_chlnbr="+str(get_optkey4_oid('MDCI')))
    if len(value_g[1][0])>0:
        for volume,curr in value_g[1][0]:
            if get_ins_name(curr)== "USD":
                total_g+=volume
            else:
                total_g+=get_cross_rate(get_ins_name(curr),date[0])*volume
    else:
        total_g = 0
    
    # QUERY: Portfolio = Wholesale FX Branch or Wholesale FX & Derivative BO & Wholesale SP
    value_h = ael.asql(f"""SELECT abs(t.quantity),t.insaddr,t.curr,t.premium FROM trade t, 
                            instrument i, portfolio p WHERE t.insaddr = i.insaddr and t.prfnbr = p.prfnbr 
                            and t.time>='{str(date[0])}' and t.time<'{acm.Time.DateAddDelta(date[0],0,0,1)}' 
                            and (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO')
                            and (t.status ~='Internal' or t.status ~='Void') AND display_id(t,'curr')='IDR' 
                            """)
    if len(value_h[1][0])>0:
        for volume,curr,curr2,prem in value_h[1][0]:
            if get_ins_name(curr)== "USD":
                total_h+=volume
            else:
                if get_cross_rate(get_ins_name(curr),date[0]):
                    total_h+=get_cross_rate(get_ins_name(curr),date[0])*volume
                else:
                    total_h+=get_cross_rate(get_ins_name(curr2),date[0])*prem
    else:
        value_h = 0                        
    
    
    # QUERY: Portfolio = Retail FX BO or Retail FX Branch or Retail SP
    value_i = ael.asql(f"""SELECT abs(t.quantity),t.insaddr,t.curr,t.premium FROM trade t, 
                            instrument i, portfolio p WHERE t.insaddr = i.insaddr and t.prfnbr = p.prfnbr 
                            and t.time>='{str(date[0])}' and t.time<'{acm.Time.DateAddDelta(date[0],0,0,1)}' 
                            and (p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                            and (t.status ~='Internal' or t.status ~='Void') AND display_id(t,'curr')='IDR' 
                            """)
    if len(value_i[1][0])>0:
        for volume,curr,curr2,prem in value_i[1][0]:
            if get_ins_name(curr)== "USD":
                total_i+=volume
            else:
                if get_cross_rate(get_ins_name(curr),date[0]):
                    total_i+=get_cross_rate(get_ins_name(curr),date[0])*volume
                else:
                    total_i+=get_cross_rate(get_ins_name(curr2),date[0])*prem
    else:
        value_i = 0    
    
    # QUERY: Portfolio = Banknotes Branch Settlement or Banknotes Export Import or Banknotes Interbank or Banknotes Trader
    value_j = ael.asql(f"""SELECT abs(t.quantity),t.insaddr,t.curr,t.premium FROM trade t, 
                            instrument i, portfolio p WHERE t.insaddr = i.insaddr and t.prfnbr = p.prfnbr 
                            and t.time>='{str(date[0])}' and t.time<'{acm.Time.DateAddDelta(date[0],0,0,1)}' 
                            and (p.prfid = 'Banknotes Branch Settlement' or p.prfid='Banknotes Interbank')
                            and (t.status ~='Internal' or t.status ~='Void') AND display_id(t,'curr')='IDR' 
                            """)
                            
    if len(value_j[1][0])>0:
        for volume,curr,curr2,prem in value_j[1][0]:
            if get_ins_name(curr)== "USD":
                total_j+=volume
            else:
                if get_cross_rate(get_ins_name(curr),date[0]):
                    total_j+=get_cross_rate(get_ins_name(curr),date[0])*volume
                else:
                    total_j+=get_cross_rate(get_ins_name(curr2),date[0])*prem
    else:
        value_j = 0
        
    value_k = ael.asql(f"""SELECT avg(abs(t.premium/t.quantity)) 
                                FROM trade t,portfolio p where t.time>='{str(date[0])}' and 
                                t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' and 
                                t.insaddr = '{str(get_ins_num('USD'))}' and t.curr = 
                                '{str(get_ins_num('IDR'))}' and t.quantity>0 and 
                                t.optkey4_chlnbr~='{str(get_optkey4_oid('FWD'))}' and t.optkey4_chlnbr~='{str(get_optkey4_oid('SWAP'))}' and t.optkey4_chlnbr~='{str(get_optkey4_oid('NS'))}'
                                and t.prfnbr = p.prfnbr and (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                                and (t.status ~='Internal' or t.status ~='Void')
                                """)
    value_k = value_k[1][0][0][0] if len(value_k[1][0])>0 else 0
    
    value_l = ael.asql(f"""SELECT avg(abs(t.premium/t.quantity)) 
                                FROM trade t,portfolio p where t.time>='{str(date[0])}' and 
                                t.time<'{acm.Time.DateAddDelta(date,0,0,1)}' and 
                                t.insaddr = '{str(get_ins_num('USD'))}' and t.curr = 
                                '{str(get_ins_num('IDR'))}' and t.quantity<0 and 
                                t.optkey4_chlnbr~='{str(get_optkey4_oid('FWD'))}'and t.optkey4_chlnbr~='{str(get_optkey4_oid('SWAP'))}' and t.optkey4_chlnbr~='{str(get_optkey4_oid('NS'))}'
                                and t.prfnbr = p.prfnbr and (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO' or p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch')
                                and (t.status ~='Internal' or t.status ~='Void')
                                """)
                                
    value_l = value_l[1][0][0][0] if len(value_l[1][0])>0 else 0
    
    value_m = ael.asql(f"""SELECT p.ptyid, abs(t.premium),t.curr,t.insaddr,abs(t.quantity) FROM trade t, party p, portfolio pf 
                                WHERE t.prfnbr = pf.prfnbr and t.counterparty_ptynbr = p.ptynbr and 
                                (pf.prfid = 'Wholesale FX & Derivative BO' or pf.prfid='Wholesale FX Branch' or
                                pf.prfid = 'Retail FX BO' or pf.prfid='Retail FX Branch') AND t.quantity < 0 
                                AND t.time >='{str(date[0])}' and t.time<'{acm.Time.DateAddDelta(date[0],0,0,1)}' 
                                AND t.optkey3_chlnbr='{str(get_optkey3_oid('FX'))}' AND t.optkey4_chlnbr NOT IN 
                                ('{str(get_optkey4_oid('SWAP'))}') AND (t.status ~='Internal' and t.status~='Void')
                                AND display_id(t,'curr')='IDR' ORDER BY 1 DESC
                                """)
                    
    all_buy_nasabah=[]
    
    for row in value_m[1][0]:
        counterparty,premium,currency,ins,quantity = row
        if currency == "IDR":
            all_buy_nasabah.append({
                'counterparty':counterparty,
                'quantity':quantity,
                'currency':get_ins_name(currency)
            })
        else:
            all_buy_nasabah.append({
                'counterparty':counterparty,
                'quantity':premium,
                'currency':get_ins_name(currency)
            })
            
    top10_buy = get_top10_count(all_buy_nasabah,date[0])
    
    value_n = ael.asql(f"""SELECT p.ptyid, abs(t.premium),t.curr,t.insaddr,abs(t.quantity) FROM trade t, party p, portfolio pf 
                                WHERE t.prfnbr = pf.prfnbr and t.counterparty_ptynbr = p.ptynbr and 
                                (pf.prfid = 'Wholesale FX & Derivative BO' or pf.prfid='Wholesale FX Branch' or
                                pf.prfid = 'Retail FX BO' or pf.prfid='Retail FX Branch') AND t.quantity > 0 
                                AND t.time >='{str(date[0])}' and t.time<'{acm.Time.DateAddDelta(date[0],0,0,1)}' 
                                AND t.optkey3_chlnbr='{str(get_optkey3_oid('FX'))}' AND t.optkey4_chlnbr NOT IN 
                                ('{str(get_optkey4_oid('SWAP'))}') AND (t.status ~='Internal' and t.status~='Void')
                                AND display_id(t,'curr')='IDR' ORDER BY 1 DESC
                                """)
    
    all_sell_nasabah=[]
    for row in value_n[1][0]:
        counterparty,premium,currency,ins,quantity = row
        if currency == "IDR":
            all_sell_nasabah.append({
                'counterparty':counterparty,
                'quantity':quantity,
                'currency':get_ins_name(ins)
            })
        else:
            all_sell_nasabah.append({
                'counterparty':counterparty,
                'quantity':premium,
                'currency':get_ins_name(currency)
            })
        
    top10_sell = get_top10_count(all_sell_nasabah,date[0])
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MCS
    value_o = ael.asql("SELECT abs(t.quantity),t.curr FROM trade t, instrument i WHERE t.insaddr = i.insaddr and i.instype = 'Option' and t.time>='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and t.optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and t.optkey4_chlnbr="+str(get_optkey4_oid('MCS')))
    if len(value_o[1][0])>0:
        for volume,curr in value_o[1][0]:
            if get_ins_name(curr)== "USD":
                total_o+=volume
            else:
                total_o+=get_cross_rate(get_ins_name(curr),date[0])*volume
    else:
        total_o = 0
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MPF
    value_p = ael.asql("SELECT abs(t.quantity),t.insaddr FROM trade t, instrument i WHERE t.insaddr = i.insaddr and i.instype = 'Curr' and t.time>='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and t.optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and t.optkey4_chlnbr="+str(get_optkey4_oid('MPF')))
    if len(value_p[1][0])>0:
        for volume,curr in value_p[1][0]:
            if get_ins_name(curr)== "USD":
                total_p+=volume
            else:
                total_p+=get_cross_rate(get_ins_name(curr),date[0])*volume
    else:
        total_p = 0
    
    total = total_a+total_b+total_c+total_d+total_e+total_f+total_g + total_o + total_p
    
    listdata = {'Total':f"{round(total,2):,}",'A':f"{round(total_a,2):,}",'B':f"{round(total_b,2):,}",'C':f"{round(total_c,2):,}",'D':f"{round(total_d,2):,}",'E':f"{round(total_e,2):,}",'F':f"{round(total_f,2):,}",'G':f"{round(total_g,2):,}",'H':f"{round(total_h,2):,}",'I':f"{round(total_i,2):,}",'J':f"{round(total_j,2):,}",'K':f"{round(value_k,2):,}",'L':f"{round(value_l,2):,}", 'O':f"{round(total_o,2):,}", 'P':f"{round(total_p,2):,}"}
    titles = ['Summary','','Volume (Quantity)']
    rows = [['Total Volume FX Transaction',':','Total'],['Volume FX Transaction Agst IDR',':','A'],['Volume DNDF Transaction',':','B'],['Volume Swap Transaction',':','C'],['Volume Non IDR Transaction',':','D'],['Volume MDS',':','E'],['Volume MMLD',':','F'],['Volume MDCI',':','G'], ['Volume MCS',':','O'], ['Volume MPF',':','P']]
    rows2 = [['','',''],['Transaction Based On Segment','',''],['Volume Wholesale Transaction',':','H'],['Volume retail Transaction',':','I'],['Volume Bank Notes Transaction',':','J'],['','',''],['','','']]
    rows3 = [['Average Rate Cust Sell USDIDR','','K'],['Average Rate Cust Buy USDIDR','','L'],['','',''],['','','']]
    rows4 = [['Top 10 Cust Sell (Non Swap) (Daily in USD)','','']]
    rows5 = [['Top 10 Cust Buy (Non Swap) (Daily in USD)','','']]
    
    if len(top10_sell)>0:
        for each_nasabah_sell in top10_sell:
            rows4.append([each_nasabah_sell[0],'',f"{round(each_nasabah_sell[1],2):,}"])
    else:
        rows4.append(['-','','-'])
    
    if len(top10_buy)>0:
        for each_nasabah_buy in top10_buy:
            rows5.append([each_nasabah_buy[0],'',f"{round(each_nasabah_buy[1],2):,}"])
    else:
        rows5.append(['-','','-'])
    
    
    rows=rows+rows2+rows3+rows4+rows5
    table_html = create_html_table(titles, rows)
    table_xsl_fo = create_xsl_fo_table(titles, rows)
    table_html=table_html.replace('<th>Summary</th>','<th style="background-color:orange">Summary</th>')
    table_html=table_html.replace('<td>Transaction Based On Segment</td>','<td style="background-color:orange">Transaction based on Segment</td>')
    for keys,val in listdata.items():
        table_html=table_html.replace("<td>"+keys+"</td>","<td>"+str(val)+"</td>")
        table_xsl_fo = table_xsl_fo.replace("<fo:block>"+keys+"</fo:block>","<fo:block>"+str(val)+"</fo:block>")
    current_hour = get_current_hour("")
    current_date = get_current_date("")
    html_file = create_html_file(report_name + " " +current_date+current_hour, file_path, [table_html], report_name, current_date)
    xsl_fo_file = create_xsl_fo_file(report_name + " " +current_date+current_hour, file_path, [table_xsl_fo], report_name, current_date)
    for i in output_file:
        if i != '.pdf' :
            generate_file_for_other_extension(html_file, i)
        else:
            generate_pdf_from_fo_file(xsl_fo_file)
    
    try:
        os.remove(xsl_fo_file)
    except:
        pass

