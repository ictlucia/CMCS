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
    CONVERT('date', p.day, '%B %Y') = 'March 2024' AND
    DISPLAY_ID(p, 'curr') = 'IDR' AND
    DISPLAY_ID(p, 'ptynbr') = 'EOD_MtM' AND
    p.historical = 'yes'
        
SELECT DISTINCT
    t.trdnbr,
    DISPLAY_ID(c, 'free2_chlnbr') 'cpty_type',
    DISPLAY_ID(t, 'broker_ptynbr') 'broker', 
    add_info(t, 'DealNo') 'dealNoOpics',
    c.fullname 'counterParty',
    DISPLAY_ID(i, 'curr') 'instrumentCurrency',
    t.quantity 'originalNominal',
    p.settle 'ntr',
    DISPLAY_ID(i, 'curr') = 'IDR' ? abs(t.quantity) : abs(t.quantity) * p.settle 'nominalIDR',
    DISPLAY_ID(t, 'optkey4_chlnbr') 'optkey4ID',
    i.insid 'insId',
    DISPLAY_ID(t, 'prfnbr') 'portID',
    ael_s(t, 'Report_Python_BO.compoundName', DISPLAY_ID(t, 'prfnbr')) 'compound',
    (
        (ael_s(t, 'Report_Python_BO.compoundName', DISPLAY_ID(t, 'prfnbr')) IN ('CLIENT_BOOK') AND DISPLAY_ID(t, 'prfnbr') NOT LIKE '%Marktra%') OR 
        (DISPLAY_ID(c, 'free2_chlnbr') NOT IN ('Bank') AND DISPLAY_ID(t, 'optkey3_chlnbr') IN ('BONDSREPO'))
    ) ? 'Perantara' : 'Pedagang' 'usedTo', 
    (DISPLAY_ID(t, 'broker_ptynbr') = '9999999330_PPAPENYELENGGARAPASARALTERNA') ? 'PPA' : 'OTC Murni' 'rowDesc', 
    DISPLAY_ID(t, 'optkey3_chlnbr') IN ('BONDSREPO') ? 'Transaksi Repurchase Agreement' : 'Transaksi Jual Beli Efek' 'transactionType'
INTO
    tradeUseGeneral
FROM 
    TRADE t,
    INSTRUMENT i,
    priceLastMonth p,
    party c
WHERE 
    t.insaddr = i.insaddr AND
    t.counterparty_ptynbr = c.ptynbr AND
    i.curr *= p.insaddr AND
    CONVERT('date', t.time, ' %d/%m/%Y') *= p.priceDay AND
    
    t.status = 'BO-BO Confirmed' AND
    t.primary_issuance = 'No' AND
    (
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND') OR 
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'BONDSREPO' AND 
         i.insid NOT LIKE '%SBI%' AND 
         i.insid NOT LIKE '%FASBI%' AND 
         i.insid NOT LIKE '%T-BOND%' AND 
         i.insid NOT LIKE '%SUKBI%' AND 
         i.insid NOT LIKE '%SIMA%' AND 
         i.insid NOT LIKE '%SIPA%' AND 
         i.insid NOT LIKE '%SRBI%' AND 
         i.insid NOT LIKE '%SVBI%'
        )
    ) AND
    ael_s(t, 'Report_Python_BO.compoundName', DISPLAY_ID(t, 'prfnbr')) IN ('BANKING_BOOK', 'TRADING_BOOK', 'CLIENT_BOOK') AND
    CONVERT('date', t.time, '%B %Y') = 'March 2024' AND
    NOT (DISPLAY_ID(t, 'trader_usrnbr') = 'TRS.BCP') AND
    
    (i.insid NOT LIKE 'US%' AND i.insid NOT LIKE 'SUKBI%' AND i.insid NOT LIKE 'ID%') AND
    DISPLAY_ID(t, 'optkey4_chlnbr') NOT IN ('SHARI') AND
    i.instype IN ('Bond', 'Bill', 'FRN', 'MBS/ABS') AND
    c.ptyid NOT IN ('222222_DUMMYCUSTOMERCONVERSION', '18003860306_RKKDJPPRKEMENKEUOPS', '10000000001_BANKMANDIRI') 
    
    
SELECT 
    t.trdnbr,
    t.cpty_type,
    t.broker,
    t.dealNoOpics,
    t.counterParty,
    t.portID,
    t.compound,
    t.insid,
    t.instrumentCurrency,
    t.originalNominal,
    t.ntr,
    t.usedTo, 
    t.transactionType,
    t.rowDesc, 
    (convert('string', t.insid, 2) IN ('VR', 'FR') OR convert('string', t.insid, 3) IN ('ORI', 'SPN', 'ROI')) AND convert('string', t.insid, 4) NOT IN ('SPNS') ? abs(t.nominalIDR) : 0 'sbn_val',
    (convert('string', t.insid, 2) IN ('VR', 'FR') OR convert('string', t.insid, 3) IN ('ORI', 'SPN', 'ROI')) AND convert('string', t.insid, 4) NOT IN ('SPNS') ? 1 : 0 'sbn_freq',
    (
        convert('string', t.insid, 2) NOT IN ('VR', 'FR', 'SR') AND 
        convert('string', t.insid, 3) NOT IN ('ORI', 'SPN', 'ROI', 'PBS', 'SBK') AND 
        convert('string', t.insid, 4) NOT IN ('SPNS') AND 
        convert('string', t.insid, 5) NOT IN ('SUKUK') AND 
        convert('string', t.insid, 6) NOT IN ('INDOIS')
    ) ? abs(t.nominalIDR) : 0 'ok_val',
    (
        convert('string', t.insid, 2) NOT IN ('VR', 'FR', 'SR') AND 
        convert('string', t.insid, 3) NOT IN ('ORI', 'SPN', 'ROI', 'PBS', 'SBK') AND 
        convert('string', t.insid, 4) NOT IN ('SPNS') AND 
        convert('string', t.insid, 5) NOT IN ('SUKUK') AND 
        convert('string', t.insid, 6) NOT IN ('INDOIS')
    ) ? 1 : 0 'ok_freq',
    (convert('string', t.insid, 2) IN ('SR') OR convert('string', t.insid, 3) IN ('PBS') OR convert('string', t.insid, 4) IN ('SPNS') OR convert('string', t.insid, 6) IN ('INDOIS')) ? abs(t.nominalIDR) : 0 'sbsn_val',
    (convert('string', t.insid, 2) IN ('SR') OR convert('string', t.insid, 3) IN ('PBS') OR convert('string', t.insid, 4) IN ('SPNS') OR convert('string', t.insid, 6) IN ('INDOIS')) ? 1 : 0 'sbsn_freq',
    t.insId LIKE '%SUKUK%' ? abs(t.nominalIDR) : 0 'sukuk_val',
    t.insId LIKE '%SUKUK%' ? 1 : 0 'sukuk_freq',
    (convert('string', t.insid, 3) IN ('SBK')) ? abs(t.nominalIDR) : 0 'other_val',
    (convert('string', t.insid, 3) IN ('SBK')) ? 1 : 0 'other_freq',
    abs(t.nominalIDR) 'total_val',
    1 'total_freq'
FROM
    tradeUseGeneral t
ORDER BY
    t.usedto,
    t.dealNoOpics,
    t.trdnbr