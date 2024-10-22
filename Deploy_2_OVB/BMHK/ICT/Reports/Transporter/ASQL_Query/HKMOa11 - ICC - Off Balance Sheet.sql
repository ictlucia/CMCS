/* update_method=0 */
SELECT
    DISPLAY_ID(p, 'type_chlnbr') = 'FVTPL' ? 'Trd' : 'Bank' 'portType',
    (
        DISPLAY_ID(t, 'optkey4_chlnbr') = 'SWAP' ? 'swaps' : 
        DISPLAY_ID(t, 'optkey4_chlnbr') = 'FWD' ? 'forward' : ''
    ) 'ProdCategory',
    t.quantity 'nominal',
    ael_f(t ,'im_purpose_P2.getConvertPriceTradeDate', t.trdnbr , 'HKD') 'tradeDatePrice',
    ael_f(t ,'im_purpose_P2.getConvertPriceLatest', t.trdnbr , 'HKD') 'latestPrice'
INTO
    dataRaw
FROM
    TRADE t,
    INSTRUMENT i,
    PORTFOLIO p
WHERE
    t.prfnbr = p.prfnbr AND
    t.insaddr = i.insaddr AND
    
    DISPLAY_ID(t, 'optkey3_chlnbr') = 'FX' AND
    DISPLAY_ID(t, 'optkey4_chlnbr') IN ('SWAP', 'FWD') AND
    t.status IN ('FO Confirmed', 'BO Confirmed', 'BO-BO Confirmed') AND
    t.value_day >= TODAY AND
    
    NOT (DISPLAY_ID(p, 'type_chlnbr') = '') AND
    convert('date', t.time, '%B %Y') >= convert('date', date_add_delta(TODAY, 0, -6, 0), '%B %Y') AND
    convert('date', t.time, '%B %Y') <= convert('date', TODAY, '%B %Y')
    

SELECT 
    d.portType, 
    d.ProdCategory, 
    SUM(d.nominal * d.tradeDatePrice) 'nominalAmount', 
    SUM(d.nominal * d.latestPrice) 'currenctMarketValue'
FROM dataRaw d
GROUP BY d.portType, d.ProdCategory
    