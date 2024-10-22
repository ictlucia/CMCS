/* update_method=0 */
SELECT
   distinct tr.trdnbr
FROM
    Trade tr,
    choicelist cl3,
    choicelist cl4,
    Leg leg,
    Portfolio prf,
    Instrument i,
    Instrument icurr,
    user u
WHERE
    cl3.seqnbr = tr.optkey3_chlnbr
    AND cl3.seqnbr = tr.optkey3_chlnbr
    AND cl4.seqnbr = tr.optkey4_chlnbr
    AND leg.insaddr = tr.insaddr
    AND leg.end_day - tr.value_day < 360
    AND tr.prfnbr = prf.prfnbr
    AND tr.insaddr = i.insaddr
    AND i.curr = icurr.insaddr
	AND tr.trader_usrnbr = u.usrnbr
	AND tr.status IN ('BO-BO Confirmed', 'Internal')
    AND (
        u.userid NOT LIKE '%AUDRIFAJAR%' OR
        u.userid NOT LIKE '%NINA.ARDIANTI%'
        )
    AND (
            (i.insid LIKE 'USD%' AND tr.value_day <= today AND leg.end_day > today AND prf.prfid LIKE 'IRT MM USD') 
            OR
            (i.insid LIKE 'IDR%' AND tr.value_day <= today AND leg.end_day > today AND prf.prfid LIKE 'IRT MM IDR')
        )
    AND cl3.entry IN ('REVREPO', 'REPO', 'DL', 'BONDSREPO')
    AND cl4.entry IN ('CMT','CMP','IBGOV','IWFGOV', 'OVT','GOV', 'OVP','BISBI','BINON','BIOTH',
    'IBSBI','IBGOV','IBDIS','IBNON','IBOTH','CCSBI','CCGV','CCDC','CCND',
    'CCOH','OVBSBI','OVBGOV','OVBDIS','OVBNON','OVBOTH','NEGSBI','NEGGOV',
    'NEGDIS','NEGNON','NEGOTH','BISBI','BIOB','BIOH','BIOH','IBOB','IBOH');