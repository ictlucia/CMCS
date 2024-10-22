/* update_method=0 */
SELECT 
    p.insaddr, p.time_last
INTO
    price_update_bval
FROM 
    PRICE p, Party pa
WHERE
    pa.ptynbr = p.ptynbr AND
    (pa.ptyid LIKE '%BB_BVAL%') 
GROUP BY 
    p.insaddr

SELECT 
    p.insaddr, p.time_last
INTO
    price_update_ibpa
FROM 
    PRICE p, Party pa
WHERE
    pa.ptynbr = p.ptynbr AND
    (pa.ptyid LIKE '%BB_IBPA%') 
GROUP BY 
    p.insaddr

SELECT
    t.trdnbr
FROM
    Trade t, Instrument i, price_update_bval pb, price_update_ibpa pi
WHERE
    t.insaddr = i.insaddr AND
    t.insaddr = pb.insaddr AND
    t.insaddr = pi.insaddr AND
    (pb.time_last BETWEEN time_of TODAY + 0 AND TODAY + 24*0*0 OR pi.time_last BETWEEN time_of TODAY + 0 AND TODAY + 24*0*0) AND
    t.value_day >= TODAY AND
    i.instype in ('BasketRepo/Reverse', 'Bond')