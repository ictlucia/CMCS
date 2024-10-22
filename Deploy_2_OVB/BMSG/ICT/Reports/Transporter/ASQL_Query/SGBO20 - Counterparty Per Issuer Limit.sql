/* update_method=0 */
SELECT
    DISPLAY_ID(p, 'insaddr') = 'USD' ? DISPLAY_ID(p, 'curr') : DISPLAY_ID(p, 'insaddr') 'curr',
    DISPLAY_ID(p, 'insaddr') = 'USD' ? 1 / p.settle : p.settle 'settle'
INTO
    priceUSDLastMonth
FROM
    PRICE p,
    INSTRUMENT i
WHERE
    p.insaddr = i.insaddr AND
    i.instype = 'curr' AND
    p.historical = 'yes' AND
    p.day >= YESTERDAY AND
    DISPLAY_ID(p, 'ptynbr') = 'EOD_MtM' AND
    (DISPLAY_ID(p, 'insaddr') = 'USD' OR DISPLAY_ID(p, 'curr') = 'USD')

SELECT
    a.seqnbr,
    p.ptyid 'ptyid',
    '02' 'Branch',
    '' 'DEALNO',
    p.parent_ptynbr 'parent_ptynbr',
    p.swift 'CUST',
    'LIMIT' 'REMARK',
    c.name LIKE '%ALL%' ? 'ALL' : 'FI' 'REM',
    a.end_date = '1/1/0000' ? '' : a.end_date 'EXPDATE',
    ael_s(a, 'Report_Python_P2.FixedCurrencyAppliedRule', a.seqnbr) 'CCY',
    ael_f(a, 'Report_PythonBO_P2.amountThresholdAppRule', a.seqnbr) 'AMOUNT',
    ael_f(tv, 'Report_PythonBO_P2.getUtilizationValThreshold', MIN(tv.seqnbr)) 'UTILIZATION'
INTO
    LimitData
FROM
    AppliedRule a,
    ComplianceRule c,
    ThresholdValue tv,
    Party p
WHERE
    a.compliance_rule = c.seqnbr AND
    tv.applied_rule = a.seqnbr AND
    a.target_seqnbr = p.ptynbr AND
    
    c.name in ('[BMSG] ALL Counterparty Limit', '[BMSG] FI Counterparty Limit')
GROUP BY
    a.seqnbr
ORDER BY
    p.ptyid

SELECT 
    ld.ptyid,
    ld.branch,
    ld.DEALNO,
    p.SWIFT 'GRPID',
    ld.CUST,
    ld.REMARK,
    ld.REM,
    ld.EXPDATE,
    ld.CCY,
    TO_STRING(ld.AMOUNT),
    TO_STRING(ld.AMOUNT * pulm.settle) 'AMOUNT (USD)',
    TO_STRING(abs(ld.UTILIZATION)),
    TO_STRING(abs(ld.UTILIZATION) * pulm.settle) 'UTILIZATION (USD)',
    TO_STRING(abs(ld.AMOUNT * pulm.settle) - abs(ld.UTILIZATION * pulm.settle)) 'Available (USD)'
FROM
    LimitData ld,
    Party p,
    priceUSDLastMonth pulm
WHERE
    p.ptynbr =* ld.parent_ptynbr AND
    ld.CCY = pulm.curr