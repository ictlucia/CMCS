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
    t.trdnbr 'TRADE ID',
    '' 'SETTLEMENT ID',
    'Treasury System' 'APPROVAL SYSTEM',
    '' 'PAYMENT SYSTEM',
    pt.optkey3 'PRODUCT',
    pc.optkey4 'PRODUCT TYPE',
    to_date(t.time) 'TRADE DATE',
    i.insid 'CCY',
    t.premium 'AMOUNT',
    t.curr = 22 ? t.premium : t.premium * p.settle 'IDR_EQ',
    t.status 'STATUS',
    '' 'PAYMENT TYPE'
FROM
    SETTLEMENT s, price_mtm p, TRADE t, INSTRUMENT i, PARTY pa,
    product_type pt, product_category pc
WHERE
    t.status in ('BO-BO Confirmed') AND
    pa.ptynbr = s.counterparty_ptynbr AND
    i.insaddr = t.curr AND
    s.trdnbr = t.trdnbr AND
    (t.curr = p.insaddr OR t.curr = 22)
    AND
    t.optkey3_chlnbr = pt.seqnbr AND
    t.optkey4_chlnbr = pc.seqnbr AND
    to_date(t.time) = p.day AND
    p.curr = 22 AND
    (
        (abs(t.premium * p.settle) > 1000000000000 AND t.curr ~= 22) 
    OR 
        (abs(t.premium) > 1000000000000 AND t.curr = 22)
    )
    AND
    to_date(t.time) = date_add_banking_day(TODAY, 'IDR', -1)
GROUP BY
    t.trdnbr
ORDER BY
    pt.optkey3, i.insid