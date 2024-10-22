/* update_method=0 */
SELECT 
    a.name 'NOS',
    '' 'DEALNO',
    'OPENBAL' 'PRODUCT',
    '' 'TYPE',
    CONVERT('date', '', '%d %b %Y') 'VDATE',
    CONVERT('date', '', '%d %b %Y') 'POSTDATE',
    DISPLAY_ID(a, 'bic_seqnbr') 'CMNE',
    TO_STRING(add_info(a, 'OpeningBalance'), '//' , add_info(a, 'ClosingBalance')) 'Balance'
FROM 
    ACCOUNT a
WHERE
    DISPLAY_ID(a, 'ptynbr') IN ('Mandiri TRS SG', 'CPS', 'EXIMBILL')