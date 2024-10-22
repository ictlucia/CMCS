/* update_method=0 */
SELECT 
    p.fullname 'CUSTOMER',
    t.trdnbr 'DEAL NO', 
    l.payleg = 'Yes' ? 'Pay' : 'Receive' 'PAY/RECEIVE (BANK PERSPECTIVE)',
    c.start_day 'Start',
    c.end_day 'End',
    r.day 'Fixing',
    c.end_day - c.start_day 'IDays',
    c.type = 'Float Rate' ? r.value : c.rate 'Rate',
    c.spread 'Spread',
    c.type = 'Float Rate' ? r.value + c.spread : c.rate + c.spread 'AllInRate',
    t.nominal_amount 'Notional',
    c.pay_day 'Pay Date',
    c.projected_cf 'Flows',
    c.type 'Type',
    DISPLAY_ID(i, 'curr') 'Ccy',
    '' 'Zero',
    c.discount_factor 'Discount',
    c.present_value 'Present Value',
    t.status 'Status'
FROM TRADE t, INSTRUMENT i, LEG l, CASHFLOW c, RESET r, PARTY p
WHERE 
    c.cfwnbr *= r.cfwnbr AND
    t.counterparty_ptynbr = p.ptynbr AND
    t.insaddr = i.insaddr AND
    i.insaddr = l.insaddr AND
    l.legnbr = c.legnbr AND
    t.status = 'BO-BO Confirmed' AND
    i.instype IN ('CurrSwap', 'Swap') AND
    i.exp_day >= TODAY AND
    c.pay_day >= TODAY AND
    p.ptyid LIKE '%%'
ORDER BY p.fullname, t.trdnbr