/* update_method=0 */
select 
    ael_s(t, 'Report_Python_BO.weekNo', CONVERT('date', t.time, '%Y-%m-%d')) 'weekNumber',
    DISPLAY_ID(t, 'optkey4_chlnbr') IN ('TOD', 'TOM', 'SPOT') ? ael_f(t, 'Report_Python_BO.amountEqvUsd', t.trdnbr) : 0 'Spot',
    0 'Forward',
    0 'Swap',
    0 'CSO',
    DISPLAY_ID(t, 'optkey4_chlnbr') IN ('NS') ? ael_f(t, 'Report_Python_BO.amountEqvUsd', t.trdnbr) : 0 'DNDF',
    0 'Lainnya1',
    ael_f(t, 'Report_Python_BO.amountEqvUsd', t.trdnbr) 'Total1',
    
    0 'SUN',
    0 'SBN',
    0 'SBK',
    0 'CP',
    0 'IRS',
    0 'Lainnya2',
    0 'Total2'
INTO
    listUsed
FROM 
    TRADE t
WHERE    
    CONVERT('date', t.time, '%B %Y') = CONVERT('date', TODAY, '%B %Y') AND
    ((DISPLAY_ID(t, 'optkey2_chlnbr') IN ('SMART_FX', 'RETM', 'RRTM')) OR (DISPLAY_ID(t, 'optkey2_chlnbr') LIKE '%KOPRA%')) AND
    DISPLAY_ID(t, 'optkey3_chlnbr') = 'FX' AND
    DISPLAY_ID(t, 'optkey4_chlnbr') IN ('TOD', 'TOM', 'SPOT', 'NS') AND
    DISPLAY_ID(t, 'curr') = 'IDR'

SELECT l.weekNumber, sum(to_double(l.spot)), sum(l.forward), sum(l.swap), sum(l.cso), sum(to_double(l.dndf)), sum(l.lainnya1), sum(to_double(l.total1)) 
FROM listUsed l 
GROUP BY l.weekNumber
UNION
SELECT l.weekNumber, sum(to_double(l.sun)), sum(l.sbn), sum(l.sbk), sum(l.cp), sum(to_double(l.irs)), sum(l.lainnya2), sum(to_double(l.total2))
FROM listUsed l 
GROUP BY l.weekNumber