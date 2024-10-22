SELECT
    tr.trdnbr
FROM
    Trade tr,
    ChoiceList cl3,
    ChoiceList cl4,
    Portfolio prf
WHERE
    cl3.seqnbr = tr.optkey3_chlnbr
    AND cl3.seqnbr = tr.optkey3_chlnbr
    AND cl4.seqnbr = tr.optkey4_chlnbr
    AND tr.prfnbr   = prf.prfnbr
    AND (
        prf.prfid LIKE 'IRT DCM%'
        OR prf.prfid LIKE 'IRT MM Bond RDPU%'
        OR prf.prfid LIKE 'IRT Dept Head'
        OR prf.prfid LIKE 'IRT Dept Head Bond RDPU Der'
    )
    AND cl3.entry IN ('BOND')
    AND cl4.entry IN (
        'SBBI', 'VR', 'BILLS', 'CBUSD', 'INDOIS', 'SBK', 
        'ROI', 'FR', 'RDPT', 'CBIDR', 'NCD', 'UST', 'RDPU', 
        'SPNS', 'FWD', 'PBS', 'SPN', 'CBVALAS', 'ORI', 'SR', 
        'EBA'
    )
    AND tr.value_day <= today;