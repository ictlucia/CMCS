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
    Instrument it
WHERE
    cl3.seqnbr = tr.optkey3_chlnbr
    AND cl3.seqnbr = tr.optkey3_chlnbr
    AND cl4.seqnbr = tr.optkey4_chlnbr
    AND leg.insaddr = tr.insaddr
    AND leg.end_day - tr.value_day <= 365
    AND tr.prfnbr = prf.prfnbr
    AND tr.insaddr = i.insaddr
    AND i.curr = icurr.insaddr
    AND i.insid 
    AND tr.status LIKE 'BO-BO Confirmed'
    AND tr.acquire_day = TODAY
    AND i.instype = 'Deposit'
    AND (
        prf.prfid LIKE 'IRT MM Bond RDPU%' 
        OR prf.prfid LIKE 'IRT MM Depo Loan Repo RR%'
        OR prf.prfid LIKE 'LIQ%'
        OR prf.prfid LIKE 'IRT Dept Head Depo Loan Repo RR'
        OR prf.prfid LIKE 'IRT MM'
        )
    AND cl3.entry IN ('TD','DL')
    AND cl4.entry IN (
        'SHARI', 'OVT', 'OVP', 'DHE', 'BI', 'BLT', 'CL', 'MD', 'CMP', 'CMT'
    );