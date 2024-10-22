/* update_method=0 */
SELECT 
    a.name 'SACCT',
    '' 'IO',
    TO_STRING(add_info(a, 'OpeningBalance'), '//' , add_info(a, 'ClosingBalance')) 'AMOUNT',
    'OPENBAL' 'DEALNO',
    CONVERT('date', '', '%d %b %Y') 'EFFDATE',
    '' 'POSTDATE',
    '' 'PRODUCT',
    '' 'TY',
    DISPLAY_ID(a, 'bic_seqnbr') 'REMARKS'
FROM 
    ACCOUNT a
WHERE
    DISPLAY_ID(a, 'ptynbr') IN ('Mandiri TRS SG', 'CPS', 'EXIMBILL')