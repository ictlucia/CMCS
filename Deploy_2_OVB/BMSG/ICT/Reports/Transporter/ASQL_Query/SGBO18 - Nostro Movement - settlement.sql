/* update_method=0 */
SELECT 
    a.name 'SACCT',
    s.amount > 0 ? 'IN' : 'OUT' 'IO',
    s.amount 'AMOUNT',
    t.trdnbr 'DEALNO',
    CONVERT('date', s.value_day, '%d %b %Y') 'EFFDATE',
    DISPLAY_ID(t, 'optkey4_chlnbr') 'PRODUCT',
    DISPLAY_ID(t, 'optkey3_chlnbr') 'TY',
    s.acquirer_ptyid = 'Mandiri TRS SG' ? DISPLAY_ID(a, 'bic_seqnbr') : s.Text 'REMARKS'
FROM
    Settlement s,
    ACCOUNT a,
    TRADE t,
    JournalInformation JI
WHERE
    JI.settlement_seqnbr = s.seqnbr AND
    s.trdnbr = t.trdnbr AND
    (
        (s.acquirer_ptyid = 'Mandiri TRS SG' AND s.acquirer_accname = a.name) OR
        (s.party_ptyid IN ('CPS', 'EXIMBILL') AND s.party_accname = a.name)
    ) AND
    s.value_day = date_add_banking_day(TODAY, 'SGD', -1)
ORDER BY
    t.trdnbr