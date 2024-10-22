/* update_method=0 */
SELECT 
    CONVERT('date', p.day, ' %d/%m/%Y') 'priceDay',
    p.insaddr,
    p.settle
INTO 
    priceLastMonth
FROM 
    price p, instrument i
WHERE
    p.insaddr = i.insaddr AND
    i.instype = 'Curr' AND
    CONVERT('date', p.day, '%B %Y') = CONVERT('date', date_add_delta(FIRSTDAYOFMONTH, -1, 0, 0), '%B %Y') AND
    DISPLAY_ID(p, 'curr') = 'IDR' AND
    DISPLAY_ID(p, 'ptynbr') = 'EOD_MtM' AND
    p.historical = 'yes'
        
SELECT DISTINCT
    t.trdnbr, 
    DISPLAY_ID(i, 'curr') = 'IDR' ? abs(t.quantity) : abs(t.quantity) * p.settle 'nominalIDR',
    DISPLAY_ID(t, 'optkey4_chlnbr') 'optkey4ID',
    i.insid 'insId',
    DISPLAY_ID(t, 'prfnbr') IN ('BB BOND EX', 'Clients Bonds Retail', 'IRT DCM EX', 'Clients Bonds FI', 'IRT DCM 2') ? 'Perantara' : 'Pedagang' 'usedTo', 
    DISPLAY_ID(t, 'broker_ptynbr') LIKE '%PPA %' ? 'PPA' : 'OTC Murni' 'rowDesc', 
    DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND' ? 'Transaksi Jual Beli Efek' : 'Transaksi Repurchase Agreement' 'transactionType'
INTO
    tradeUseGeneral
FROM 
    TRADE t,
    INSTRUMENT i,
    priceLastMonth p
WHERE 
    t.insaddr = i.insaddr AND
    i.curr *= p.insaddr AND
    CONVERT('date', t.time, ' %d/%m/%Y') *= p.priceDay AND
    
    t.status = 'BO-BO Confirmed' AND
    t.primary_issuance = 'No' AND
    DISPLAY_ID(t, 'optkey3_chlnbr') IN ('BOND', 'REPO', 'REVREPO') AND
    CONVERT('date', t.time, '%B %Y') = CONVERT('date', date_add_delta(FIRSTDAYOFMONTH, -1, 0, 0), '%B %Y') AND
    
    DISPLAY_ID(i, 'issuer_ptynbr') NOT LIKE '$BANKINDONESIA$' AND
    i.exp_day >= TODAY AND
    i.instype IN ('Bond', 'Bill', 'FRN', 'MBS/ABS')


SELECT 
    t.usedTo, 
    t.transactionType,
    t.rowDesc, 
    sum(t.optkey4ID IN ('VR', 'FR', 'ORI', 'SPN', 'ROI') ? abs(t.nominalIDR) : 0) 'sbn_val',
    sum(t.optkey4ID IN ('VR', 'FR', 'ORI', 'SPN', 'ROI') ? 1 : 0) 'sbn_freq',
    sum(NOT (t.optkey4ID IN ('VR', 'FR', 'ORI', 'SPN', 'ROI', 'PBR', 'SR', 'SPNS', 'INDOIS') OR t.insId LIKE '%SUKUK%' OR t.insId LIKE '%CB%') ? abs(t.nominalIDR) : 0) 'ok_val',
    sum(NOT (t.optkey4ID IN ('VR', 'FR', 'ORI', 'SPN', 'ROI', 'PBR', 'SR', 'SPNS', 'INDOIS') OR t.insId LIKE '%SUKUK%' OR t.insId LIKE '%CB%') ? 1 : 0) 'ok_freq',
    sum(t.optkey4ID IN ('PBR', 'SR', 'SPNS', 'INDOIS') ? abs(t.nominalIDR) : 0) 'sbsn_val',
    sum(t.optkey4ID IN ('PBR', 'SR', 'SPNS', 'INDOIS') ? 1 : 0) 'sbsn_freq',
    sum(t.insId LIKE '%SUKUK%' ? abs(t.nominalIDR) : 0) 'sukuk_val',
    sum(t.insId LIKE '%SUKUK%' ? 1 : 0) 'sukuk_freq',
    sum(t.optkey4ID IN ('SBK') OR t.insId LIKE '%CB%' ? abs(t.nominalIDR) : 0) 'other_val',
    sum(t.optkey4ID IN ('SBK') OR t.insId LIKE '%CB%' ? 1 : 0) 'other_freq',
    sum(abs(t.nominalIDR)) 'total_val',
    sum(1) 'total_freq'
INTO
    summaryTable
FROM
    tradeUseGeneral t
GROUP BY
    t.usedTo, t.transactionType, t.rowDesc

SELECT * FROM summaryTable s WHERE s.usedTo = 'Pedagang'
UNION
SELECT * FROM summaryTable s WHERE s.usedTo = 'Perantara'
