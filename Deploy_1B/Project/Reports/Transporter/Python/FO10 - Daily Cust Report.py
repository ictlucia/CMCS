from ICTMODULES_FOR_HTML_AND_XSLFO_GENERATOR import *
import acm, ael

ael_gui_parameters={'runButtonLabel':'&&Run',
                    'hideExtraControls': True,
                    'windowCaption':'Daily Cust Report'}

def get_ins_num(insid):
    instrument = acm.FInstrument[insid]
    return instrument.Oid()
    

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
    
    # QUERY: Sum of FX Transaction (FX TOD TOM SPOT OPT NS)
    value_a = ael.asql(f"""SELECT sum(abs(t.quantity)) 
                            FROM trade t WHERE time >= {str(date[0])} 
                            AND t.time < {acm.Time.DateAddDelta(date[0],0,0,1)}
                            AND t.curr = {str(get_ins_num('IDR'))}
                            AND display_id(t, 'optkey3_chlnbr') = 'FX'
                            AND (display_id(t, 'optkey4_chlnbr') = 'TOD' 
                            OR display_id(t, 'optkey4_chlnbr') = 'TOM'
                            OR display_id(t, 'optkey4_chlnbr') = 'SPOT'
                            OR display_id(t, 'optkey4_chlnbr') = 'FWD')
                        """)
                            
    value_a = value_a[1][0][0][0] if len(value_a[1][0])>0 else 0
    
    # QUERY: Trade Key 3 = FX, Trade Key 4 = NDF
    value_b = ael.asql(f"""SELECT sum(abs(t.quantity))
                            FROM trade t
                            WHERE t.time >= {str(date[0])}
                            AND t.time < {acm.Time.DateAddDelta(date[0],0,0,1)}
                            AND (display_id(t, 'optkey3_chlnbr') = 'FX' AND display_id(t, 'optkey4_chlnbr') = 'NDF')
                        """)
    value_b = value_b[1][0][0][0] if len(value_b[1][0])>0 else 0
    
    # QUERY: SUM of SWAP (CCS, IRS)
    value_c = ael.asql(f"""SELECT sum(abs(t.quantity))
                            FROM trade t WHERE t.time>={str(date[0])} 
                            AND t.time<{acm.Time.DateAddDelta(date[0],0,0,1)}
                            AND display_id(t, 'optkey3_chlnbr') = 'FX'
                            AND (display_id(t, 'optkey4_chlnbr') = 'SWAP')
                        """)
    value_c = value_c[1][0][0][0] if len(value_c[1][0])>0 else 0
    
    # QUERY: Currency = IDR, Instrument = IDR
    value_d = ael.asql("SELECT sum(abs(quantity)) FROM trade WHERE time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and curr~="+str(get_ins_num('IDR'))+" and insaddr~="+str(get_ins_num('IDR')))
    value_d = value_d[1][0][0][0] if len(value_d[1][0])>0 else 0
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MDS
    value_e = ael.asql("SELECT sum(abs(quantity)) FROM trade WHERE time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and optkey4_chlnbr="+str(get_optkey4_oid('MDS')))
    value_e = value_e[1][0][0][0] if len(value_e[1][0])>0 else 0
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MMLD
    value_f = ael.asql("SELECT sum(abs(quantity)) FROM trade WHERE time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and optkey4_chlnbr="+str(get_optkey4_oid('MMLD')))
    value_f = value_f[1][0][0][0] if len(value_f[1][0])>0 else 0
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MDCI
    value_g = ael.asql("SELECT sum(abs(quantity)) FROM trade WHERE time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and optkey4_chlnbr="+str(get_optkey4_oid('MDCI')))
    value_g = value_g[1][0][0][0] if len(value_g[1][0])>0 else 0
    
    # QUERY: Portfolio = Wholesale FX Branch or Wholesale FX & Derivative BO
    value_h = ael.asql("SELECT sum(abs(quantity)) FROM trade t, portfolio p WHERE t.prfnbr = p.prfnbr and t.time>='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and (p.prfid = 'Wholesale FX Branch' or p.prfid = 'Wholesale FX & Derivative BO')")
    value_h = value_h[1][0][0][0] if len(value_h[1][0])>0 else 0
    
    # QUERY: Portfolio = Retail FX BO or Retail FX Branch or Retail SP
    value_i = ael.asql("SELECT sum(abs(quantity)) FROM trade t, portfolio p WHERE t.prfnbr = p.prfnbr and t.time>='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and (p.prfid = 'Retail FX BO' or p.prfid = 'Retail FX Branch' or p.prfid='Retail SP')")
    value_i = value_i[1][0][0][0] if len(value_i[1][0])>0 else 0
    
    # QUERY: Portfolio = Banknotes Branch Settlement or Banknotes Export Import or Banknotes Interbank or Banknotes Trader
    value_j = ael.asql("SELECT sum(abs(quantity)) FROM trade t, portfolio p WHERE t.prfnbr = p.prfnbr and t.time>='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and (p.prfid = 'Banknotes Branch Settlement' or p.prfid = 'Banknotes Export Import' or p.prfid='Banknotes Interbank' or p.prfid='Banknotes Trader')")
    value_j = value_j[1][0][0][0] if len(value_j[1][0])>0 else 0
    
    value_k = ael.asql("SELECT avg(quantity) FROM trade where time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and optkey3_chlnbr = "+str(get_optkey3_oid('FX'))+" and optkey4_chlnbr = "+str(get_optkey4_oid('SWAP'))+" and quantity<0")
    value_k = value_k[1][0][0][0] if len(value_k[1][0])>0 else 0
    
    value_l = ael.asql("SELECT avg(quantity) FROM trade where time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and optkey3_chlnbr = "+str(get_optkey3_oid('FX'))+" and optkey4_chlnbr = "+str(get_optkey4_oid('SWAP'))+" and quantity>0")
    value_l = value_l[1][0][0][0] if len(value_l[1][0])>0 else 0
    
    value_m = ael.asql("SELECT p.ptyid, sum(abs(t.quantity)),free2_chlnbr 'Volume' FROM trade t, party p WHERE p.ptynbr = t.counterparty_ptynbr AND t.quantity > 0 AND t.time >='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' AND t.optkey3_chlnbr="+str(get_optkey3_oid('FX'))+" AND t.optkey4_chlnbr NOT IN ("+str(get_optkey4_oid('SWAP'))+") GROUP BY p.ptyid ORDER BY 2 DESC")
    value_m = value_m[1] if len(value_m[1][0])>0 else '-'
    
    value_n = ael.asql("SELECT p.ptyid, sum(abs(t.quantity)),free2_chlnbr 'Volume' FROM trade t, party p WHERE p.ptynbr = t.counterparty_ptynbr AND t.quantity < 0 AND t.time >='"+str(date[0])+"' and t.time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' AND t.optkey3_chlnbr="+str(get_optkey3_oid('FX'))+" AND t.optkey4_chlnbr NOT IN ("+str(get_optkey4_oid('SWAP'))+") GROUP BY p.ptyid ORDER BY 2 DESC")
    value_n = value_n[1] if len(value_n[1][0])>0 else '-'
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MCS
    value_o = ael.asql("SELECT sum(abs(quantity)) FROM trade WHERE time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and optkey4_chlnbr="+str(get_optkey4_oid('MCS')))
    value_o = value_o[1][0][0][0] if len(value_o[1][0])>0 else 0
    
    # QUERY: Trade Key 3 = SP, Trade Key 4 = MPF
    value_p = ael.asql("SELECT sum(abs(quantity)) FROM trade WHERE time>='"+str(date[0])+"' and time<'"+acm.Time.DateAddDelta(date[0],0,0,1)+"' and optkey3_chlnbr="+str(get_optkey3_oid('SP'))+" and optkey4_chlnbr="+str(get_optkey4_oid('MPF')))
    value_p = value_p[1][0][0][0] if len(value_p[1][0])>0 else 0
    
    total = value_a+value_b+value_c+value_d+value_e+value_f+value_g + value_o + value_p
    
    listdata = {'Total':f"{round(total,2):,}",'A':f"{round(value_a,2):,}",'B':f"{round(value_b,2):,}",'C':f"{round(value_c,2):,}",'D':f"{round(value_d,2):,}",'E':f"{round(value_e,2):,}",'F':f"{round(value_f,2):,}",'G':f"{round(value_g,2):,}",'H':f"{round(value_h,2):,}",'I':f"{round(value_i,2):,}",'J':f"{round(value_j,2):,}",'K':f"{round(value_k,2):,}",'L':f"{round(value_l,2):,}", 'O':f"{round(value_o,2):,}", 'P':f"{round(value_p,2):,}"}
    titles = ['Summary','','Volume (Quantity)']
    rows = [['Total Volume FX Transaction',':','Total'],['Volume FX Transaction Agst IDR',':','A'],['Volume DNDF Transaction',':','B'],['Volume Swap Transaction',':','C'],['Volume Non IDR Transaction',':','D'],['Volume MDS',':','E'],['Volume MMLD',':','F'],['Volume MDCI',':','G'], ['Volume MCS',':','O'], ['Volume MPF',':','P']]
    rows2 = [['','',''],['Transaction Based On Segment','',''],['Volume Wholesale Transaction',':','H'],['Volume retail Transaction',':','I'],['Volume Bank Notes Transaction',':','J'],['','',''],['','','']]
    rows3 = [['Average Rate Cust Sell USDIDR','','K'],['Average Rate Cust Buy USDIDR','','L'],['','',''],['','','']]
    rows4 = [['Top 10 Cust Sell (Non Swap) (Daily in USD)','','']]
    rows5 = [['Top 10 Cust Buy (Non Swap) (Daily)','','']]
    
    if value_n == "-":
        rows4.append(["-", '', "-"])
    else:
    
        for client, quantity,ctype in value_n[0]:
            if "BANK" in client or "bank" in client or 'Mandiri' in client or 'MANDIRI' in client or str(get_ctype_name(ctype))=='Bank':
                continue
            else:
                rows4.append([client, '', f"{round(quantity,2):,}"])
    rows4.append(['','',''])
    
    if value_m == "-":
        rows5.append(["-", '', "-"])
    else:
        for clients,quantities,ctype in value_m[0]:
            if "BANK" in clients or "bank" in clients or 'Mandiri' in clients or 'MANDIRI' in clients or str(get_ctype_name(ctype))=='Bank':
                continue
            else:
                rows5.append([clients,'',f"{round(quantities,2):,}"])
    rows5.append(['','',''])
    
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

