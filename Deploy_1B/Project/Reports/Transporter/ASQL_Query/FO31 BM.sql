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
    AND i.insid = 'IDR'
    AND tr.status LIKE 'BO-BO Confirmed'
    AND tr.time = today
    AND (
        prf.prfid LIKE 'IRT MM' 
        OR prf.prfid LIKE 'IRT MM Depo Loan Repo RR%'
        OR prf.prfid LIKE 'LIQ%'
        )
    AND cl3.entry IN ('DL')
    AND cl4.entry IN (
        'SHARI', 'OVT', 'OVP', 'LF', 'BLT', 'FASBI', 'CMP', 'CMT', 'MD'
    );