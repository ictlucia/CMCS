/* update_method=0 */
SELECT
    t.trdnbr,
    DISPLAY_ID(t, 'optkey3_chlnbr') 'Type',
    DISPLAY_ID(t, 'optkey4_chlnbr') 'Category',
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
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('')
        ) ? 'Bop' : 
        /* (D) WRITTEN OPTION POSITIONS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('')
        ) ? 'Wop' :
        /* (E) OTHER */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('')
        ) ? 'Other' : ''
    ) 'ProdCategory',
    p.prfid 'portfolio',
    ael_s(p ,'im_purpose_P2.getPortTradingBook', p.prfnbr, 0) 'portType',
    (t.quantity >= 0 ? t.quantity : t.premium) 'nominal',
    ael_f(t ,'im_purpose_P2.getConvertPriceTradeDate', t.trdnbr , 'HKD') 'tradeDatePrice',
    ael_f(t ,'im_purpose_P2.getConvertPriceLatest', t.trdnbr , 'HKD') 'latestPrice',
    (t.quantity >= 0 ? t.quantity : t.premium) * ael_f(t ,'im_purpose_P2.getConvertPriceTradeDate', t.trdnbr , 'HKD') 'Notional',
    (t.quantity >= 0 ? t.quantity : t.premium) * ael_f(t ,'im_purpose_P2.getConvertPriceLatest', t.trdnbr , 'HKD') 'Current Market Value'
FROM
    TRADE t,
    INSTRUMENT i,
    PORTFOLIO p
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
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('') AND
            t.value_day >= TODAY
        ) OR 
        /* (D) WRITTEN OPTION POSITIONS */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('') AND
            t.value_day >= TODAY
        ) OR
        /* (E) OTHER */
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('') AND
            t.value_day >= TODAY
        )
        
    )