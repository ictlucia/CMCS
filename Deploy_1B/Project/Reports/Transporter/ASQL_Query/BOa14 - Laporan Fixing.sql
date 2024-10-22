/* update_method=0 */
SELECT
    t.trdnbr 'TradeId', 
    r.resnbr 'ResetId',
    p.fullname 'LegalName',
    DISPLAY_ID(t, 'optkey3_chlnbr') 'Type', 
    DISPLAY_ID(t, 'optkey4_chlnbr') 'SubType',
    c.start_day 'Start Date Interest', 
    DISPLAY_ID(t, 'Curr') 'Ccy',
    t.nominal_amount 'Notional',
    r.value 'Amount',
    DISPLAY_ID(l, 'Float_rate') 'INTEREST_dmtndex', 
    convert('String', to_string(l.rolling_period.count, l.rolling_period.unit), 2) 'INTEREST_Term',
    date_add_banking_day(time_to_day(r.read_time), 'IDR', 1) 'Next Fixing', 
    i.exp_day 'MatDate'

FROM 
    TRADE t, INSTRUMENT i, LEG l, CASHFLOW C, RESET r, PARTY P
WHERE
    t.insaddr = i.insaddr AND
    i.insaddr = l.insaddr AND
    l.legnbr = c.legnbr AND
    C.cfwnbr *= r.cfwnbr AND
    t.counterparty_ptynbr = p.ptynbr AND
    
    t.status = 'BO-BO Confirmed' AND
    i.instype IN ('Swap', 'CurrSwap') AND
    DISPLAY_ID(t, 'optkey3_chlnbr') IN ('SWAP') AND
    DISPLAY_ID(t, 'optkey4_chlnbr') IN ('CCS', 'IRS', 'OIS') AND
    i.exp_day >= TODAY AND
    c.type = 'Float Rate' AND
    convert('date', r.read_time, '%B') = convert('date', date_add_delta(TODAY, 0, -1, 0), '%B') AND 
    convert('date', r.read_time, '%Y') = convert('date', date_add_delta(TODAY, 0, -1, 0), '%Y')
ORDER BY
    t.trdnbr, c.start_day