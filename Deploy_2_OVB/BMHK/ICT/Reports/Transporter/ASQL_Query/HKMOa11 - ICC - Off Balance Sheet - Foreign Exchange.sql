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
    'FE' 'fieldType',
    (
        /* (a) FORWARD */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('FWD')
        ) ? 'Forward' :
        /* (b) SWAPS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('SWAP')
        ) ? 'Swaps' :
        /* (c) BOUGHT OPTION POSITIONS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('OPT') AND
            t.quantity > 0
        ) ? 'BOP' : 
        /* (D) WRITTEN OPTION POSITIONS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('OPT') AND
            t.quantity < 0
        ) ? 'WOP' :
        /* (E) OTHER */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('NDF', 'NS')
        ) ? 'Other' : ''
    ) 'ProdCategory',
    ael_s(p ,'im_purpose_P2.getPortTradingBook', p.prfnbr, 0) 'portType',
    (t.quantity >= 0 ? t.quantity : t.premium) 'nominal',
    ael_f(t ,'im_purpose_P2.getConvertPriceTradeDate', t.trdnbr , 'HKD') 'tradeDatePrice',
    pl_economic(t) * pu.settle 'upl'
INTO
    dataRaw
FROM
    TRADE t,
    INSTRUMENT i,
    PORTFOLIO p,
    PRICEUSED pu
WHERE
    t.prfnbr = p.prfnbr AND
    t.insaddr = i.insaddr AND
    ael_s(p ,'im_purpose_P2.getPortTradingBook', p.prfnbr, 1) = 'BMHK' AND
    t.status IN ('FO Confirmed', 'BO Confirmed', 'BO-BO Confirmed') AND
    
    /* PRODUCT TYPE & CATEGORY FILTER FOR EACH ROW IN 'OTC derivatives other than credit derivatives' SECTION */
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
            t.quantity >= 0 AND
            i.exp_day >= TODAY
        ) OR 
        /* (D) WRITTEN OPTION POSITIONS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('OPT') AND
            t.quantity < 0 AND
            i.exp_day >= TODAY
        ) OR
        /* (E) OTHER */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('NDF', 'NS') AND
            t.value_day >= TODAY
        )
        
    )

SELECT 
    d.fieldType,
    d.ProdCategory,
    d.portType, 
    TO_STRING(d.fieldType, d.ProdCategory, d.portType) 'uniqueCode',
    SUM(d.nominal * d.tradeDatePrice) 'nominalAmount', 
    SUM(d.upl) 'currenctMarketValue'
FROM dataRaw d
GROUP BY d.portType, d.ProdCategory
UNION
SELECT 
    d.fieldType,
    'Subtotal',
    d.portType, 
    TO_STRING(d.fieldType, 'Subtotal', d.portType) 'uniqueCode',
    SUM(d.nominal * d.tradeDatePrice) 'nominalAmount',
    SUM(d.upl) 'Current Market Value'
FROM dataRaw d   
GROUP BY d.portType