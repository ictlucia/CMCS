/* update_method=0 */
SELECT
    t.trdnbr, t.insaddr, t.nominal_amount 
INTO
    tradeUsed
FROM
    Trade t, Portfolio p
WHERE
    t.prfnbr = p.prfnbr AND
    t.status = 'BO-BO Confirmed' AND
    DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND' AND
    p.type_chlnbr in (222, 223, 224)
    
SELECT 
    i.insaddr
INTO
    instrumentUsed
FROM 
    instrument i, tradeUsed t
WHERE
    t.insaddr = i.insaddr AND
    i.instype = 'BOND'
GROUP BY
    i.insaddr
HAVING
    abs(sum(t.nominal_amount)) > 0

SELECT 
    t.trdnbr
FROM 
    instrumentUsed i, tradeUsed t
WHERE
    i.insaddr = t.insaddr