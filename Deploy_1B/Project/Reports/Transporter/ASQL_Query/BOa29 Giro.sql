/* update_method=0 */
SELECT 
    a.accnbr,
    p.country
INTO
    CorrespondentBankCountry
FROM
    ACCOUNT a,
    PARTY p
WHERE
    a.correspondent_bank_ptynbr = p.ptynbr AND
    NOT (p.country = 'ID')
    
SELECT
    s.seqnbr,
    s.acquirer_account_network_name 'acquirerNetwork',
    s.counterparty_ptynbr 'partyNo',
    s.acquirer_account_ref_seqnbr,
    DISPLAY_ID(s, 'Curr') 'currency',
    s.amount 'amount' 
INTO
    settlementUse
FROM
    SETTLEMENT s,
    TRADE t,
    INSTRUMENT i,
    CorrespondentBankCountry cbc
WHERE
    s.trdnbr = t.trdnbr AND
    t.insaddr = i.insaddr AND
    s.party_account_ref_seqnbr = cbc.accnbr AND
    
    NOT (DISPLAY_ID(s, 'curr') = 'IDR') AND
    CONVERT('date', s.value_day, '%B %Y') = 'August 2024' AND
    s.party_account_network_name = 'SWIFT' AND
    t.status = 'BO-BO Confirmed' AND
    NOT (cbc.country = 'ID') AND
    
    (
        (
            i.instype = 'Curr' AND 
            s.type IN ('Premium', 'Premium 2')
        ) OR
        (
            i.instype IN ('CurrSwap', 'Swap') AND 
            s.type IN ('Fixed Amount', 'Fixed Rate', 'Float Rate')
        ) OR
        (
            i.instype IN ('Deposit') AND 
            s.type IN ('Fixed Amount', 'Fixed Rate', 'Float Rate', 'Premium')
        ) OR
        (
            i.instype IN ('Bill', 'Bond', 'FRN', 'MBS/ABS', 'Fund') AND 
            DISPLAY_ID(t, 'optkey3_chlnbr') NOT IN ('REVREPO', 'REPO', 'BONDSREPO') AND
            s.relation_type IN ('Coupon Net', 'Redemption Net') AND
            s.type IN ('Dividend', 'Dividend Transfer', 'Premium') AND
            (
                (
                    DISPLAY_ID(t, 'optkey4_chlnbr') in ('ROI', 'INDOIS') AND 
                    DISPLAY_ID(i, 'issuer_ptynbr') IN ('ROIGOV_GOVERMENT OF REPUBLIC OF INDONES', 'DEPKUIDR1_DEPARTEMEN KEUANGAN', '2000269170_BANKINDONESIA')
                ) OR
                (
                    DISPLAY_ID(t, 'optkey4_chlnbr') in ('CBUSD', 'CCBI', 'CBVALAS', 'CBIDR') AND
                    DISPLAY_ID(i, 'issuer_ptynbr') NOT IN ('ROIGOV_GOVERMENT OF REPUBLIC OF INDONES', 'DEPKUIDR1_DEPARTEMEN KEUANGAN', '2000269170_BANKINDONESIA')
                ) OR
                (
                    DISPLAY_ID(t, 'optkey4_chlnbr') NOT in ('ROI', 'INDOIS', 'FR', 'CBUSD', 'CCBI', 'CBVALAS', 'CBIDR') 
                )
                
            )
        ) OR
        (
            i.instype NOT IN ('Bond') AND 
            DISPLAY_ID(t, 'optkey3_chlnbr') IN ('REVREPO', 'REPO') AND
            s.type IN ('Fixed Amount', 'Fixed Rate', 'Float Rate', 'Premium')
        ) OR
        (
            i.instype IN ('Option') AND 
            s.type IN ('Termination Fee', 'Premium')
        )
    )

SELECT
    s.seqnbr,
    TO_STRING(
        s.acquirerNetwork = 'SWIFT' ? '3C' : (s.acquirerNetwork = 'EMAS' ? (DISPLAY_ID(p, 'free2_chlnbr') = 'Bank' ? '4A' : '4B') : ''),
        s.currency,
        cbc.country
    ) 'CODE',
    s.acquirerNetwork = 'SWIFT' ? '3C' : (s.acquirerNetwork = 'EMAS' ? (DISPLAY_ID(p, 'free2_chlnbr') = 'Bank' ? '4A' : '4B') : '') 'jenisRekening',
    s.currency,
    cbc.country,
    s.amount
INTO
    DetailGiro
FROM
    settlementUse s,
    CorrespondentBankCountry cbc,
    Party p
WHERE
    s.acquirer_account_ref_seqnbr = cbc.accnbr AND
    s.partyNo = p.ptynbr

SELECT
    dg.code,
    dg.jenisRekening,
    dg.currency,
    dg.country,
    SUM(dg.amount)
FROM
    DetailGiro dg
GROUP BY
    dg.code