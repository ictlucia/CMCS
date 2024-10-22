/* update_method=0 */
SELECT 
    DISPLAY_ID(a, 'curr') 'currency',
    a.depository,
    a.account,
    a.name,
    add_info(a, 'ClosingBalance') 'nostro'
FROM 
    ACCOUNT a
WHERE
    DISPLAY_ID(a, 'ptynbr') = 'Mandiri TRS HK' AND
    DISPLAY_ID(a, 'network_alias_type') = 'SWIFT'