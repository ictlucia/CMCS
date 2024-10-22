/* update_method=0 */
SELECT DISTINCT
    t.trdnbr
FROM 
    TRADE t,
    INSTRUMENT i,
    PARTY p,
    DealPackageTrdLink d
WHERE
    t.insaddr = i.insaddr AND
    t.counterparty_ptynbr = p.ptynbr AND
    t.trdnbr *= d.trdnbr AND
    
    t.status = 'BO-BO Confirmed' AND
    (
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'FX' AND t.value_day > TODAY ) OR
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'BOND' AND DISPLAY_ID(t, 'optkey4_chlnbr') IN ('OPT', 'FWD') AND t.value_day > TODAY ) OR
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'SWAP' AND DISPLAY_ID(t, 'optkey4_chlnbr') IN ('CCS', 'IRS', 'OIS') AND i.exp_day > TODAY) OR
        (DISPLAY_ID(t, 'optkey3_chlnbr') = 'SP' AND i.exp_day > TODAY AND
            (
            (DISPLAY_ID(t, 'optkey4_chlnbr') IN ('MMLD', 'MDCI', 'MCS') AND i.instype = 'Option') OR
            (DISPLAY_ID(t, 'optkey4_chlnbr') IN ('MLDR') AND i.instype = 'SWAP') OR
            (DISPLAY_ID(t, 'optkey4_chlnbr') IN ('MDS') AND i.instype = 'Curr' AND d.name = 'FXSwapFar')
            )
        )
        
    ) AND
    p.type = 'Client' AND
    p.fullname = '3000604378_TreasuryCoreSystem01'