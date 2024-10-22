/* update_method=0 */
SELECT 
    t.trdnbr 'TradeId', 
    r.resnbr 'ResetId',
    DISPLAY_ID(t, 'optkey4_chlnbr') 'PROD TYPE',
    p.fullname 'COUNTERPARTY',
    t.nominal_amount > 0 ? 'B' : 'S' 'B/S',
    to_date(t.time) 'TradeDate',
    t.value_day 'Effective Date',
    i.exp_day 'MatDate',
    DISPLAY_ID(i, 'curr') 'Ccy',
    t.nominal_amount 'Notional',
    DISPLAY_ID(l, 'float_rate') 'INTEREST',
    time_to_day(r.read_time) 'FIXING DATE',
    r.value 'NTCS',
    pr.Settle 'SOURCE DATA',
    pr.Day 'SOURCE DATE',
    r.value = pr.Settle ? 'MATCH' : 'UNMATCH' 'STATUS',
    DISPLAY_ID(r, 'updat_usrnbr') 'APPROVAL'
FROM TRADE t, INSTRUMENT i, LEG l, CASHFLOW c, RESET r, PARTY p, PRICE pr
WHERE 
    t.counterparty_ptynbr = p.ptynbr AND
    t.insaddr = i.insaddr AND
    i.insaddr = l.insaddr AND
    l.legnbr = c.legnbr AND
    c.cfwnbr = r.cfwnbr AND
    l.float_rate *= pr.insaddr AND
    r.day *= pr.day AND
    
    DISPLAY_ID(pr, 'ptynbr') LIKE 'EOD_MtM' AND
    
    t.status = 'BO-BO Confirmed' AND
    i.instype IN ('CurrSwap', 'Swap', 'Option') AND
    i.exp_day >= TODAY AND
    time_to_day(r.read_time) >= TODAY
ORDER BY t.trdnbr