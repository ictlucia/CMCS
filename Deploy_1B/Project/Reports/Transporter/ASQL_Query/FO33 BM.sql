/* update_method=0 */
SELECT
    tr.trdnbr
FROM
    Trade tr,
    ChoiceList cl3,
    ChoiceList cl4,
    Leg leg,
    Portfolio prf,
    Instrument i
WHERE
    cl3.seqnbr = tr.optkey3_chlnbr
    AND cl3.seqnbr = tr.optkey3_chlnbr
    AND cl4.seqnbr = tr.optkey4_chlnbr
    AND leg.insaddr = tr.insaddr
    AND leg.end_day - tr.value_day <= 365
    AND tr.prfnbr = prf.prfnbr
    AND tr.insaddr = i.insaddr
    AND tr.status LIKE 'BO-BO Confirmed'
    AND tr.time = Today
    AND (
        prf.prfid LIKE 'LIQ%'
        OR prf.prfid LIKE 'IRT MM'
        )
    AND cl3.entry IN ('REVREPO', 'REPO')
    AND cl4.entry IN (
        'OVBOTH', 'OVBDIS', 'NEGOTH', 'NEGDIS', 'BIOTH', 'IBOTH', 'BIDIS', 'IBDIS', 'BIOH', 'CCOTH', 
        'IBOB','OVBSBI', 'OVBNON', 'CCDC', 'NEGSBI', 'NEGNON', 'BISBI', 'BINON', 'IBSBI', 'IBNON', 
        'OVBGOV', 'CCSBI','CCBI', 'IBBI', 'NEGGOV', 'CCGV','BIGOV', 'IBGOV', 'CCGOV', 'BIOB', 'CCOH'
        );