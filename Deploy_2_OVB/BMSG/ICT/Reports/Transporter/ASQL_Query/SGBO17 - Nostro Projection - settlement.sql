/* update_method=0 */
SELECT
    a.name,
    TO_STRING(s.trdnbr),
    DISPLAY_ID(t, 'optkey4_chlnbr'),
    DISPLAY_ID(t, 'optkey3_chlnbr'),
    CONVERT('date', s.value_day, '%d %b %Y') 'VDATE',
    CONVERT('date', t.time, '%d %b %Y') 'POSTDATE',
    DISPLAY_ID(a, 'bic_seqnbr') 'CMNE',
    s.amount
FROM
    Settlement s,
    ACCOUNT a,
    TRADE t
WHERE
    s.trdnbr = t.trdnbr AND
    (
        (s.acquirer_ptyid = 'Mandiri TRS SG' AND s.acquirer_accname = a.name) OR
        (s.party_ptyid IN ('CPS', 'EXIMBILL') AND s.party_accname = a.name)
    ) AND
    s.value_day >= TODAY AND
    s.value_day <= date_add_banking_day(TODAY, 'HKD', 30)
    