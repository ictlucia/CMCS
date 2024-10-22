/* update_method=0 */
SELECT
    tr.trdnbr
FROM
    Trade tr,
    ChoiceList cl3,
    ChoiceList cl4,
    Leg leg,
    Portfolio prf,
    Instrument i,
    Instrument icurr
WHERE
    cl3.seqnbr = tr.optkey3_chlnbr
    AND cl3.seqnbr = tr.optkey3_chlnbr
    AND cl4.seqnbr = tr.optkey4_chlnbr
    AND leg.insaddr = tr.insaddr
    AND leg.end_day - tr.value_day <= 365
    AND tr.prfnbr = prf.prfnbr
    AND tr.insaddr = i.insaddr
    AND i.curr = icurr.insaddr
    AND i.insid ~= 'IDR'
    AND i.instype IN ('BOND', 'Deposit', 'Repo/Reverse')
    AND tr.status LIKE 'BO-BO Confirmed'
    AND tr.time = today
    AND (
        prf.prfid LIKE 'LIQ%'
        OR prf.prfid LIKE 'IRT Dept Head'
        OR prf.prfid LIKE 'IRT MM%'
        )
    AND cl3.entry IN ('TD','REVREPO', 'REPO', 'DL', 'BOND')
    AND cl4.entry IN (
        'NEGDIS', 'BIDIS', 'CWFSBI', 'IWFGOV', 'IBGOV', 'NEGOTH', 'IWFNON', 'BIOTH', 'IBOH', 'IWFSBI',
        'IBNON', 'BLT', 'CCGV', 'IBSBI', 'IDSD', 'CMP', 'CCBI', 'OVBDIS', 'OVP', 'IDBI', 'OVBOTH', 
        'IDBI', 'FASBI', 'CWFDIS', 'SUKBI', 'MD', 'CMT', 'NEGGOV', 'BIGOV', 'CCOTH', 'CWFOTH', 'OVT', 
        'IWFDIS','NEGNON', 'BINON', 'SHARI', 'IBDIS', 'BIOB', 'LF', 'NEGSBI', 'BISBI', 'IWFOTH', 'CCND', 
        'IBBI','CCOH', 'IBOTH', 'OVBGOV', 'DHE', 'CCGOV', 'CCDC', 'OVBNON', 'BIOH', 'CWFGOV', 'RDPU', 
        'OVBSBI', 'CL', 'IDSV', 'IBOB', 'CWFNON', 'CCSBI'
    );