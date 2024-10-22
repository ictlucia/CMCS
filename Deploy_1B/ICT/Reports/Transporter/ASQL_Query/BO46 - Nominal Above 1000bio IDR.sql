/* update_method=0 */
SELECT seqnbr, entry 'optkey3'
into product_type
FROM ChoiceList
WHERE list = 'Product Type'

SELECT seqnbr, entry 'optkey4'
into product_category
FROM ChoiceList
WHERE list = 'Category'

SELECT 
    p.settle, p.insaddr, p.curr, p.creat_time, pa.ptyid, p.day
INTO
    price_mtm
FROM 
    PRICE p, Party pa, instrument i
WHERE
    pa.ptynbr = p.ptynbr AND
    pa.ptyid LIKE '%EOD_MtM%'  and
    p.curr = 22 AND
    i.insaddr = p.insaddr AND
    i.insid = 'USD' AND
    p.historical = 'yes'

SELECT 
    s.seqnbr 'SETTLEMENT ID',
    'Treasury System' 'APPROVAL SYSTEM',
    s.party_account_network_name 'PAYMENT SYSTEM',
    t.trdnbr 'TRADE ID',
    pt.optkey3 'PRODUCT',
    pc.optkey4 'PRODUCT TYPE',
    s.value_day 'VALUE DATE',
    i.insid 'CCY',
    s.amount 'AMOUNT',
    s.curr = 22 ? s.amount : s.amount * p.settle 'IDR_EQ',
    s.status 'STATUS',
    s.type 'PAYMENT TYPE'
FROM
    SETTLEMENT s, price_mtm p, TRADE t, INSTRUMENT i, PARTY pa,
    product_type pt, product_category pc
WHERE
    s.status in ('Released', 'Acknowledged', 'Pending Closure', 'Closed') AND
    pa.ptynbr = s.counterparty_ptynbr AND
    i.insaddr = t.curr AND
    s.trdnbr = t.trdnbr AND
    (s.curr = p.insaddr OR s.curr = 22)
    AND
    t.optkey3_chlnbr = pt.seqnbr AND
    t.optkey4_chlnbr = pc.seqnbr AND
    s.value_day = p.day AND
    p.curr = 22 AND
    (
        (abs(s.amount * p.settle) > 1000000000000 AND s.curr ~= 22) 
    OR 
        (abs(s.amount) > 1000000000000 AND s.curr = 22)
    )
    AND
    s.value_day = date_add_banking_day(TODAY, 'IDR', -1)
GROUP BY
    s.seqnbr
ORDER BY
    pt.optkey3, i.insid, s.party_account_network_name