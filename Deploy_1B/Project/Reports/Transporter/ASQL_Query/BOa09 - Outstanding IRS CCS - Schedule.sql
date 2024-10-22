/* update_method=0 */
SELECT 
    t.trdnbr 'TradeId', 
    to_string(r.resnbr) 'ResetId',
    DISPLAY_ID(i, 'Curr') 'Curr',
    c.type = 'Float Rate' ? r.value : c.rate 'Rate',
    r.day,
    to_string(convert('date', r.read_time, '%d/%m/%Y')) 'Fixing_Date',
    convert('date', c.start_day, '%d/%m/%Y') 'Start_Date_Interest',
    c.type 'Type'
INTO FIX_TABLE
FROM TRADE t, INSTRUMENT i, LEG l, CASHFLOW c, RESET r, PARTY p, PRICE pr
WHERE 
    t.insaddr = i.insaddr AND
    i.insaddr = l.insaddr AND
    l.legnbr = c.legnbr AND
    c.cfwnbr *= r.cfwnbr AND
        
    t.status = 'BO-BO Confirmed' AND
    i.instype IN ('Swap', 'CurrSwap') AND
    DISPLAY_ID(t, 'optkey3_chlnbr') IN ('SWAP') AND
    DISPLAY_ID(t, 'optkey4_chlnbr') IN ('CCS', 'IRS', 'OIS') AND
    i.exp_day >= TODAY AND
    (   
        (
            c.type = 'Float Rate' AND 
            convert('date', r.read_time, '%B') = convert('date', date_add_delta(TODAY, 0, -1, 0), '%B') AND 
            convert('date', r.read_time, '%Y') = convert('date', date_add_delta(TODAY, 0, -1, 0), '%Y')) 
        OR (
            c.type = 'Fixed Rate' AND 
            convert('date', c.start_day, '%B') = convert('date', date_add_delta(TODAY, 0, -1, 0), '%B') AND 
            convert('date', c.start_day, '%Y') = convert('date', date_add_delta(TODAY, 0, -1, 0), '%Y')
        )
    )

SELECT 
    TradeId, 
    to_int(ResetId) 'ResetId',
    Curr,
    Rate,
    Fixing_Date,
    Start_Date_Interest 'Start Date Interest',
    Type
FROM FIX_TABLE
ORDER BY TradeId, Type, Fixing_Date