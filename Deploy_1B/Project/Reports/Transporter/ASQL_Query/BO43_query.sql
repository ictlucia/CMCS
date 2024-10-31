/* update_method=0 */
SELECT DISTINCT
    t.trdnbr
FROM 
    trade t, instrument i, leg l, party p 
WHERE
    t.insaddr = i.insaddr AND
    i.insaddr = l.insaddr AND
    t.counterparty_ptynbr = p.ptynbr AND
    t.status = 'BO-BO Confirmed' AND
    convert('date', t.value_day, '%B') = convert('date', date_add_delta(TODAY, 0, -1, 0), '%B') AND
    p.type = 'Client' AND
    DISPLAY_ID(p, 'risk_country_chlnbr') = 'Indonesia' AND
    (
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'SWAP' AND DISPLAY_ID(t, 'optkey4_chlnbr') = 'CCS') OR
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'FX' AND DISPLAY_ID(t, 'optkey4_chlnbr') IN ('SWAP', 'FWD')) OR
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'FX' AND DISPLAY_ID(t, 'optkey4_chlnbr') IN ('TOM', 'TOD', 'SPOT') AND t.quantity < 0)
    ) AND
    (DISPLAY_ID(t, 'curr') = 'IDR' OR DISPLAY_ID(i, 'curr') = 'IDR' OR i.insid = 'IDR')
    