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
    AND i.exp_day BETWEEN today+1 AND today+365
    AND tr.value_day <= today
    AND tr.prfnbr = prf.prfnbr
    AND tr.insaddr = i.insaddr
    AND i.curr = icurr.insaddr
    AND i.insid LIKE 'IDR%'
    AND tr.counterparty_ptynbr=p.ptynbr
    AND tr.status LIKE 'BO-BO Confirmed'
    AND p.ptyid NOT LIKE '10000000001_BANKMANDIRI'
    AND (
        prf.prfid LIKE 'IRT MM Depo Loan Repo RR%' 
        OR prf.prfid LIKE 'LIQ%'
        OR prf.prfid LIKE 'IRT MM Bond RDPU%'
        OR prf.prfid LIKE 'ALM Repo'
        OR prf.prfid LIKE 'IRT MM IDR'
        )
    AND cl3.entry IN ('TD', 'REVREPO', 'REPO', 'DL', 'SBI', 'BOND')
    AND cl4.entry IN (
        'NEGDIS', 'BIDIS', 'CWFSBI', 'IWFGOV', 'IBGOV', 'NEGOTH', 
        'IWFNON', 'BIOTH', 'IBOH', 'IWFSBI', 'IBNON', 'BLT', 'CCGV', 
        'IBSBI', 'IDSD', 'CMP', 'CCBI', 'OVBDIS', 'IDBI', 'OVBOTH', 
        'FASBI', 'OVP', 'CWFDIS', 'SUKBI', 'MD', 'CMT', 'NEGGOV', 
        'BIGOV', 'CCOTH', 'CWFOTH', 'OVT', 'IWFDIS', 'NEGNON', 'BINON', 
        'SHARI', 'IBDIS', 'BIOB', 'LF', 'NEGSBI', 'BISBI', 'IWFOTH', 
        'CCND', 'IBBI', 'CCOH', 'IBOTH', 'OVBGOV', 'CCGOV', 'OVBNON', 
        'BIOH', 'CWFGOV', 'RDPU', 'OVBSBI', 'IBOB', 'CWFNON'
    );