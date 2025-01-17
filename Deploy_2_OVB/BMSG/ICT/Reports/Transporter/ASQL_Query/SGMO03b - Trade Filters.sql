/* update_method=0 */
SELECT 
  T.TRDNBR
FROM 
  TRADE T, 
  INSTRUMENT I, 
  PORTFOLIOLINK PL, 
  PORTFOLIO OWNER, 
  PORTFOLIO MEMBER 
WHERE 
  I.INSADDR = T.INSADDR 
  AND T.PRFNBR = PL.MEMBER_PRFNBR 
  AND PL.MEMBER_PRFNBR = MEMBER.PRFNBR 
  AND PL.OWNER_PRFNBR = OWNER.PRFNBR 
  AND DISPLAY_ID(T, 'optkey3_chlnbr') = 'BOND' 
  AND DISPLAY_ID(T, 'optkey4_chlnbr') IN (
    'CBUSD', 'CBVALAS', 'UST', 'BILLS', 
    'ROI', 'ORI', 'SR', 'SBBI', 'SBK', 
    'SPN', 'SPNS', 'FR', 'INDOIS', 'PBS', 
    'NCD', 'SVBLCY', 'SVBUSD'
  ) 
  AND OWNER.PRFID IN (
    'IRT DCM BMSG - ACU', 'IRT Derivative BMSG - ACU', 'IRT MM BMSG - ACU', 'IRT DCM BMSG - DBU', 'IRT Derivative BMSG - DBU', 'IRT MM BMSG - DBU'
  ) 
  AND CONVERT('datetime', T.TIME, '%H:%M:%S') >= '08:00:00' 
  AND CONVERT('datetime', T.TIME, '%H:%M:%S') < '18:00:00' 
  AND I.EXP_DAY >= TODAY
