/* update_method=0 */
SELECT
    1/ ((p.ask + p.bid) / 2) 'settle'
INTO
    PRICEUSED
FROM
    PRICE p
WHERE
    DISPLAY_ID(p, 'insaddr') = 'HKD' AND
    DISPLAY_ID(p, 'curr') = 'IDR' AND
    p.day = YESTERDAY AND
    DISPLAY_ID(p, 'ptynbr') = 'REFINITIV_SPOT'

SELECT
    'Ip' 'fieldType',
    ael_s(py ,'im_purpose_P2.partyTypeGroup', DISPLAY_ID(py, 'free2_chlnbr')) 'partyGroup',
    (t.quantity >= 0 ? t.quantity : t.premium) 'nominal',
    ael_f(t ,'im_purpose_P2.getConvertPriceTradeDate', t.trdnbr , 'HKD') 'tradeDatePrice',
    pl_economic(t) * pu.settle 'upl'
INTO
    dataRaw
FROM
    TRADE t,
    INSTRUMENT i,
    PORTFOLIO p,
    Party py,
    PRICEUSED pu
WHERE
    t.prfnbr = p.prfnbr AND
    t.insaddr = i.insaddr AND
    t.counterparty_ptynbr = py.ptynbr AND
    
    ael_s(p ,'im_purpose_P2.getPortTradingBook', p.prfnbr, 1) = 'BMHK' AND
    ael_s(p ,'im_purpose_P2.getPortTradingBook', p.prfnbr, 0) IN ('Trd', 'Bank') AND
    t.status IN ('FO Confirmed', 'BO Confirmed', 'BO-BO Confirmed') AND
    
    (    /* (a) FORWARD */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('FWD') AND
            t.value_day >= TODAY
        ) OR 
        /* (b) SWAPS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('SWAP') AND
            t.value_day >= TODAY
        ) OR 
        /* (c) BOUGHT OPTION POSITIONS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('OPT') AND
            i.exp_day >= TODAY AND
            t.quantity > 0
        ) OR 
        /* (D) WRITTEN OPTION POSITIONS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('OPT') AND
            i.exp_day >= TODAY AND
            t.quantity < 0
        ) OR
        /* (E) OTHER */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('NS', 'NDF') AND
            t.value_day >= TODAY
        )
        
    )

SELECT 
    d.fieldType,
    d.partyGroup,
    '' 'nil',
    TO_STRING(d.fieldType, d.partyGroup) 'uniqueCode',
    SUM(d.nominal * d.tradeDatePrice) 'nominalAmount', 
    SUM(d.upl) 'currenctMarketValue'
FROM dataRaw d
GROUP BY d.fieldType, d.partyGroup