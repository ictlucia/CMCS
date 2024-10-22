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
    Instrument icurr,
    Party p
WHERE
    cl3.seqnbr = tr.optkey3_chlnbr
    AND cl3.seqnbr = tr.optkey3_chlnbr
    AND cl4.seqnbr = tr.optkey4_chlnbr
    AND leg.insaddr = tr.insaddr
    AND leg.end_day - tr.value_day < 360
    AND tr.prfnbr = prf.prfnbr
    AND tr.insaddr = i.insaddr
    AND i.curr = icurr.insaddr
    AND i.insid NOT LIKE 'IDR%'
    AND tr.status IN ('BO-BO Confirmed', 'FO Confirmed', 'Internal')
    AND tr.time = today
    AND tr.counterparty_ptynbr = p.ptynbr
    AND i.instype IN ('BasketRepo/Reverse', 'Deposit')
    AND (
        /*-- Kondisi untuk transaksi dengan port IRT MM, LIQ MM, LIQ BI tanpa counterparty Bank Mandiri atau Mandiri TRS HO*/
        (
        (prf.prfid LIKE 'IRT MM%' OR prf.prfid LIKE 'LIQ MM%' OR prf.prfid LIKE 'LIQ BI%')
         AND p.ptyid NOT IN ('10000000001_BANKMANDIRI', 'Mandiri TRS HO'))
        OR
        /*-- Kondisi untuk transaksi dengan port IRT MM Depo Loan Repo RR dengan counterparty Bank Mandiri atau Mandiri TRS HO*/
        ((prf.prfid LIKE 'IRT MM Depo Loan Repo RR%' OR prf.prfid LIKE 'IRT MM USD') 
        AND p.ptyid IN ('10000000001_BANKMANDIRI', 'Mandiri TRS HO'))
    )
    AND cl3.entry IN ('TD', 'REVREPO', 'REPO', 'DL')
    AND cl4.entry IN (
        'NEGDIS', 'BIDIS', 'CWFSBI', 'IWFGOV', 'IBGOV', 'NEGOTH', 'IWFNON', 'BIOTH', 'IBOH', 'IWFSBI',
        'IBNON', 'BLT', 'CCGV', 'IBSBI', 'IDSD', 'CMP', 'CCBI', 'OVBDIS', 'IDBI', 'OVBOTH', 'FASBI',
        'OVP', 'CWFDIS', 'SUKBI', 'MD', 'CMT','NEGGOV', 'BIGOV', 'CCOTH', 'CWFOTH', 'OVT', 'IWFDIS',
        'NEGNON', 'BINON', 'SHARI','IBDIS', 'BIOB', 'LF', 'NEGSBI', 'BISBI', 'IWFOTH', 'CCND', 'IBBI',
        'CCOH', 'IBOTH', 'OVBGOV', 'CCGOV', 'OVBNON', 'BIOH', 'CWFGOV', 'RDPU', 'OVBSBI', 'IBOB', 
        'CWFNON','DHE', 'BI'
    );