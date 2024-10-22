/* update_method=0 */
SELECT
    t.trdnbr
FROM
    TRADE t,
    INSTRUMENT i
WHERE
    t.insaddr = i.insaddr AND
    
    t.status IN ('FO Confirmed', 'BO Confirmed', 'BO-BO Confirmed') AND
    (i.exp_day - i.start_day) <= 360 AND
    t.value_day >= TODAY AND
    
    DISPLAY_ID(t, 'optkey3_chlnbr') IN ('REPO', 'DL', 'BOND') AND
    DISPLAY_ID(t, 'optkey4_chlnbr') IN ('IWFSBI', 'CWFGOV', 'CBVALAS', 'CWFDIS', 'SR', 'BA', 'IBOB', 'SVBLCY', 'OVP', 'BILLS', 'CCGV', 'BLT', 'CCDC', 'CMT', 'SBK', 'CCGOV', 'IWFNON', 'IBOTH', 'ROI', 'INDOIS', 'IWFGOV', 'IWFDIS', 'SPNS', 'OVT', 'CWFOTH', 'IBOH', 'SVBUSD', 'NCD', 'PBS', 'SPN', 'MD', 'IBSBI', 'CCOTH', 'SBBI', 'CCBI', 'IWFOTH', 'CCND', 'CWFSBI', 'FR', 'CCOH', 'IBNON', 'CBUSD', 'UST', 'IBGOV', 'IBDIS', 'ORI', 'CMP', 'CCSBI', 'CWFNON') AND
    DISPLAY_ID(t, 'prfnbr') IN ('LIQ IB BMHK', 'CB 6 BMHK', 'BB BOND AC BMHK', 'CB 5 BMHK', 'CB 4 BMHK', 'IBFI 1 BMHK', 'BB BOND SHARIA PL BMHK', 'Commercial 3 BMHK', 'Commercial 2 BMHK', 'Commercial 1 BMHK', 'Commercial 4 BMHK', 'BB BOND PL BMHK', 'BB BOND OCI BMHK', 'Commercial 6 BMHK', 'Commercial 5 BMHK', 'SAM 1 BMHK', 'SAM 3 BMHK', 'SAM 2 BMHK', 'IRT MM Depo Loan Repo RR 2 BMHK', 'IRT MM Depo Loan Repo RR 1 BMHK', 'IRT DCM 2 BMHK', 'IRT DCM 1 BMHK', 'ALM Bilateral Loans BMHK', 'BB BOND SHARIA AC BMHK', 'CB 3 BMHK', 'CB 2 BMHK', 'BB BOND SHARIA OCI BMHK', 'CB 1 BMHK')
    
    