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
    AND i.instype IN ('Bill', 'Bond','Deposit')
    AND tr.status IN ('BO-BO Confirmed')
    AND tr.time = today
    AND (
        prf.prfid LIKE 'Marktra Bonds'
        OR prf.prfid LIKE 'IRT MM Depo Loan Repo RR%'
        OR prf.prfid LIKE 'LIQ%'
        OR prf.prfid LIKE 'IRT Specialist%'
        OR prf.prfid LIKE 'IRT MM Bond RDPU%'
        OR prf.prfid LIKE 'IRT Dept Head Depo Loan Repo RR%'
        OR prf.prfid LIKE 'IRT Dept Head'
        OR prf.prfid LIKE 'IRT Dept Head Bond RDPU Der'
        OR prf.prfid LIKE 'IRT DCM'
        OR prf.prfid LIKE 'Client Bonds'
        )
    AND cl3.entry IN ('TD','DL','SBI')
    AND cl4.entry IN (
       'SRBI', 'IDSD', 'IDBI', 'FASBI', 'SUKBI'
    );