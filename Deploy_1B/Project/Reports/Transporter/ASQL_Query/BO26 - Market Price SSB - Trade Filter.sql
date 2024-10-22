/* update_method=0 */
SELECT DISTINCT
    t.trdnbr
FROM
    JournalInformation ji,
    journal j,
    trade t,
    instrument i,
    party p
WHERE
    t.insaddr = i.insaddr AND
    ji.seqnbr = j.journal_info_seqnbr AND
    i.issuer_ptynbr = p.ptynbr AND
    (ji.trdnbr NOT IN (0) ? ji.trdnbr : ji.contract_trdnbr) = t.trdnbr AND
    i.instype IN ('Bond', 'Bill', 'FRN', 'MBS/ABS', 'Fund') AND
    j.journal_type = 'Live'