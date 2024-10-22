/* update_method=0 */
SELECT DISTINCT
    t.trdnbr
FROM
    JournalInformation ji,
    journal j,
    trade t,
    instrument i,
    ChartOfAccount c,
    TAccount ta
WHERE
    t.insaddr = i.insaddr AND
    ji.insaddr = i.insaddr AND
    (ji.trdnbr NOT IN (0) ? ji.trdnbr : ji.contract_trdnbr) = t.trdnbr AND
    ji.seqnbr = j.journal_info_seqnbr AND
    j.chart_of_account_seqnbr = c.seqnbr AND
    c.t_account = ta.seqnbr AND
    
    j.journal_type = 'Live' AND
    to_string(ta.number) NOT IN ('23012101', '14512101') AND
    (to_string(ta.number) LIKE '145%' OR to_string(ta.number) LIKE '230%') AND
    (
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FXDU', 'FXBN') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('FWD') AND
            t.value_day > TODAY
        ) OR
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('FX') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('OPT', 'SWAP', 'NS', 'NDF') AND
            t.value_day > TODAY
        ) OR
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('SWAP') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('CCS', 'IRS', 'OIS', 'FRA') AND
            i.exp_day > TODAY
        ) OR
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('BOND') AND
            DISPLAY_ID(t, 'optkey4_chlnbr') IN ('OPT', 'FWD') AND
            t.value_day > TODAY
        ) OR
        (
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('SP') AND
            i.exp_day > TODAY AND
            (
                (DISPLAY_ID(t, 'optkey4_chlnbr') IN ('MDS') AND i.instype = 'Curr') OR
                (DISPLAY_ID(t, 'optkey4_chlnbr') IN ('MMLD', 'MDCI', 'MCS') AND i.instype = 'Option') OR
                (DISPLAY_ID(t, 'optkey4_chlnbr') IN ('MLDR') AND i.instype = 'Swap') OR
                (DISPLAY_ID(t, 'optkey4_chlnbr') IN ('MPF') AND i.instype = 'Curr')
            )
        )
    )