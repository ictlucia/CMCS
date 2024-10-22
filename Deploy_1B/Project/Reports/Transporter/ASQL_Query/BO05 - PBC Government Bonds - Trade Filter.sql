/* update_method=0 */
SELECT DISTINCT
    t.trdnbr
FROM
    JournalInformation ji,
    journal j,
    trade t,
    instrument i,
    party p, 
    ChartOfAccount c,
    TAccount ta
WHERE
    t.insaddr = i.insaddr AND
    ji.seqnbr = j.journal_info_seqnbr AND
    i.issuer_ptynbr = p.ptynbr AND
    j.chart_of_account_seqnbr = c.seqnbr AND
    c.t_account = ta.seqnbr AND
    (ji.trdnbr NOT IN (0) ? ji.trdnbr : ji.contract_trdnbr) = t.trdnbr AND
    DISPLAY_ID(i, 'category_chlnbr') NOT IN ('NCD', 'CBIDR', 'CBUSD', 'RDPT', 'RDPU', 'CBVALAS', 'EBA') AND
    DISPLAY_ID(i, 'product_type_chlnbr') IN ('BOND') AND
    j.journal_type = 'Live' AND
    (ta.number LIKE '140%')