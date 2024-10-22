/* update_method=0 */
/* --- FX --- */
SELECT 
      B.START_TIME, 
      CR.NAME, 
      AEL_S(
            T, 'Report_Python_P2.GroupLabel', T.SEQNBR
      ) 't_group', 
      B.THRESHOLD, 
      B.WATERMARK_VALUE, 
      DISPLAY_ID(T, 'type') 'threshold_type', 
      T.COMPARISON_TYPE INTO FX 
FROM 
      THRESHOLDVALUE TV, 
      THRESHOLD T, 
      APPLIEDRULE AR, 
      COMPLIANCERULE CR, 
      BREACH B, 
      ALERT A 
WHERE 
      TV.THRESHOLD = T.SEQNBR 
      AND TV.APPLIED_RULE = AR.SEQNBR 
      AND AR.COMPLIANCE_RULE = CR.SEQNBR 
      AND B.ALERT = A.SEQNBR 
      AND A.THRESHOLD_VALUE = TV.SEQNBR 
      AND CR.NAME = '{fx_compliance_name}' 
      AND B.TYPE = 'Utilization' 
      AND AR.TARGET_TYPE = 'Portfolio' 
      AND B.START_TIME BETWEEN '{year}-01-01' 
      AND '{year}-12-31' 
ORDER BY 
      B.START_TIME, 
      CR.NAME ASC 
      /* --- IR --- */
SELECT 
      B.START_TIME, 
      CR.NAME, 
      AEL_S(
            T, 'Report_Python_P2.GroupLabel', T.SEQNBR
      ) 't_group', 
      B.THRESHOLD, 
      B.WATERMARK_VALUE, 
      DISPLAY_ID(T, 'type') 'threshold_type', 
      T.COMPARISON_TYPE INTO IR 
FROM 
      THRESHOLDVALUE TV, 
      THRESHOLD T, 
      APPLIEDRULE AR, 
      COMPLIANCERULE CR, 
      BREACH B, 
      ALERT A 
WHERE 
      TV.THRESHOLD = T.SEQNBR 
      AND TV.APPLIED_RULE = AR.SEQNBR 
      AND AR.COMPLIANCE_RULE = CR.SEQNBR 
      AND B.ALERT = A.SEQNBR 
      AND A.THRESHOLD_VALUE = TV.SEQNBR 
      AND CR.NAME = '{ir_compliance_name}' 
      AND B.TYPE = 'Utilization' 
      AND AR.TARGET_TYPE = 'Portfolio' 
      AND B.START_TIME BETWEEN '{year}-01-01' 
      AND '{year}-12-31' 
ORDER BY 
      B.START_TIME, 
      CR.NAME ASC 
      /* --- TOTAL --- */
SELECT 
      B.START_TIME, 
      CR.NAME, 
      AEL_S(
            T, 'Report_Python_P2.GroupLabel', T.SEQNBR
      ) 't_group', 
      B.THRESHOLD, 
      B.WATERMARK_VALUE, 
      DISPLAY_ID(T, 'type') 'threshold_type', 
      T.COMPARISON_TYPE INTO TOTAL 
FROM 
      THRESHOLDVALUE TV, 
      THRESHOLD T, 
      APPLIEDRULE AR, 
      COMPLIANCERULE CR, 
      BREACH B, 
      ALERT A 
WHERE 
      TV.THRESHOLD = T.SEQNBR 
      AND TV.APPLIED_RULE = AR.SEQNBR 
      AND AR.COMPLIANCE_RULE = CR.SEQNBR 
      AND B.ALERT = A.SEQNBR 
      AND A.THRESHOLD_VALUE = TV.SEQNBR 
      AND CR.NAME = '{total_compliance_name}' 
      AND B.TYPE = 'Utilization' 
      AND AR.TARGET_TYPE = 'Portfolio' 
      AND B.START_TIME BETWEEN '{year}-01-01' 
      AND '{year}-12-31' 
ORDER BY 
      B.START_TIME, 
      CR.NAME ASC 
      /* --- MERGE --- */
SELECT 
      NOT(
            TO_STRING(FX.START_TIME) IS NULL
      ) ? FX.START_TIME : (
            NOT(
                  TO_STRING(IR.START_TIME) IS NULL
            ) ? IR.START_TIME : TOTAL.START_TIME
      ) 'start_time', 
      NOT(
            TO_STRING(FX.T_GROUP) IS NULL
      ) ? FX.T_GROUP : (
            NOT(
                  TO_STRING(IR.T_GROUP) IS NULL
            ) ? IR.T_GROUP : TOTAL.T_GROUP
      ) 't_group', 
      NOT (
            TO_STRING(FX.NAME) IS NULL
      ) ? FX.NAME : '-' 'fx_name', 
      NOT (
            TO_STRING(FX.THRESHOLD) IS NULL 
            OR TO_STRING(FX.THRESHOLD) = 'NaN'
      ) ? FX.THRESHOLD : '-' 'fx_threshold', 
      NOT (
            TO_STRING(FX.WATERMARK_VALUE) IS NULL 
            OR TO_STRING(FX.WATERMARK_VALUE) = 'NaN'
      ) ? FX.WATERMARK_VALUE : '-' 'fx_watermark', 
      NOT(
            TO_STRING(FX.WATERMARK_VALUE) IS NULL 
            OR TO_STRING(FX.WATERMARK_VALUE) = 'NaN'
      ) ? TO_STRING(
            CONVERT(
                  'float', 
                  100 * TO_DOUBLE(FX.WATERMARK_VALUE) / TO_DOUBLE(FX.THRESHOLD), 
                  2
            )
      ) : '-' 'fx_realisasi', 
      NOT (
            TO_STRING(FX.THRESHOLD_TYPE) IS NULL
      ) ? FX.THRESHOLD_TYPE : '-' 'fx_threshold_type', 
      NOT (
            TO_STRING(FX.COMPARISON_TYPE) IS NULL
      ) ? FX.COMPARISON_TYPE : '-' 'fx_comparison_type', 
      NOT (
            TO_STRING(IR.NAME) IS NULL
      ) ? IR.NAME : '-' 'ir_name', 
      NOT (
            TO_STRING(IR.THRESHOLD) IS NULL 
            OR TO_STRING(IR.THRESHOLD) = 'NaN'
      ) ? IR.THRESHOLD : '-' 'ir_threshold', 
      NOT (
            TO_STRING(IR.WATERMARK_VALUE) IS NULL 
            OR TO_STRING(IR.WATERMARK_VALUE) = 'NaN'
      ) ? IR.WATERMARK_VALUE : '-' 'ir_watermark', 
      NOT(
            TO_STRING(IR.WATERMARK_VALUE) IS NULL 
            OR TO_STRING(IR.WATERMARK_VALUE) = 'NaN'
      ) ? TO_STRING(
            CONVERT(
                  'float', 
                  100 * TO_DOUBLE(IR.WATERMARK_VALUE) / TO_DOUBLE(IR.THRESHOLD), 
                  2
            )
      ) : '-' 'ir_realisasi', 
      NOT (
            TO_STRING(IR.THRESHOLD_TYPE) IS NULL
      ) ? IR.THRESHOLD_TYPE : '-' 'ir_threshold_type', 
      NOT (
            TO_STRING(IR.COMPARISON_TYPE) IS NULL
      ) ? IR.COMPARISON_TYPE : '-' 'ir_comparison_type', 
      NOT (
            TO_STRING(TOTAL.NAME) IS NULL
      ) ? TOTAL.NAME : '-' 'total_name', 
      NOT (
            TO_STRING(TOTAL.THRESHOLD) IS NULL 
            OR TO_STRING(TOTAL.THRESHOLD) = 'NaN'
      ) ? TOTAL.THRESHOLD : '-' 'total_threshold', 
      NOT (
            TO_STRING(TOTAL.WATERMARK_VALUE) IS NULL 
            OR TO_STRING(TOTAL.WATERMARK_VALUE) = 'NaN'
      ) ? TOTAL.WATERMARK_VALUE : '-' 'total_watermark', 
      NOT(
            TO_STRING(TOTAL.WATERMARK_VALUE) IS NULL 
            OR TO_STRING(TOTAL.WATERMARK_VALUE) = 'NaN'
      ) ? TO_STRING(
            CONVERT(
                  'float', 
                  100 * TO_DOUBLE(TOTAL.WATERMARK_VALUE) / TO_DOUBLE(TOTAL.THRESHOLD), 
                  2
            )
      ) : '-' 'total_realisasi', 
      NOT (
            TO_STRING(TOTAL.THRESHOLD_TYPE) IS NULL
      ) ? TOTAL.THRESHOLD_TYPE : '-' 'total_threshold_type', 
      NOT (
            TO_STRING(TOTAL.COMPARISON_TYPE) IS NULL
      ) ? TOTAL.COMPARISON_TYPE : '-' 'total_comparison_type' 
FROM 
      FX, 
      IR, 
      TOTAL 
WHERE 
            
      /* THRESHOLD GROUP */
      (
            (
                  FX.T_GROUP = IR.T_GROUP 
                  AND IR.T_GROUP = TOTAL.T_GROUP 
                  AND TOTAL.T_GROUP = FX.T_GROUP
            ) 
            OR (
                  (
                        FX.T_GROUP = IR.T_GROUP 
                        AND FX.T_GROUP *= TOTAL.T_GROUP 
                        AND IR.T_GROUP *= TOTAL.T_GROUP
                  ) 
                  OR (
                        IR.T_GROUP = TOTAL.T_GROUP 
                        AND IR.T_GROUP *= FX.T_GROUP 
                        AND TOTAL.T_GROUP *= FX.T_GROUP
                  ) 
                  OR (
                        FX.T_GROUP = TOTAL.T_GROUP 
                        AND FX.T_GROUP *= IR.T_GROUP 
                        AND TOTAL.T_GROUP *= IR.T_GROUP
                  )
            ) 
            OR (
                  (
                        FX.T_GROUP *= IR.T_GROUP 
                        AND FX.T_GROUP *= TOTAL.T_GROUP
                  ) 
                  OR (
                        IR.T_GROUP *= FX.T_GROUP 
                        AND IR.T_GROUP *= TOTAL.T_GROUP
                  ) 
                  OR (
                        TOTAL.T_GROUP *= FX.T_GROUP 
                        AND TOTAL.T_GROUP *= IR.T_GROUP
                  )
            )
      ) 
      AND 
      /* STARTTIME */
      (
            (
                  FX.START_TIME = IR.START_TIME 
                  AND IR.START_TIME = TOTAL.START_TIME 
                  AND TOTAL.START_TIME = FX.START_TIME
            ) 
            OR (
                  (
                        FX.START_TIME = IR.START_TIME 
                        AND FX.START_TIME *= TOTAL.START_TIME 
                        AND IR.START_TIME *= TOTAL.START_TIME
                  ) 
                  OR (
                        IR.START_TIME = TOTAL.START_TIME 
                        AND IR.START_TIME *= FX.START_TIME 
                        AND TOTAL.START_TIME *= FX.START_TIME
                  ) 
                  OR (
                        FX.START_TIME = TOTAL.START_TIME 
                        AND FX.START_TIME *= IR.START_TIME 
                        AND TOTAL.START_TIME *= IR.START_TIME
                  )
            ) 
            OR (
                  (
                        FX.START_TIME *= IR.START_TIME 
                        AND FX.START_TIME *= TOTAL.START_TIME
                  ) 
                  OR (
                        IR.START_TIME *= FX.START_TIME 
                        AND IR.START_TIME *= TOTAL.START_TIME
                  ) 
                  OR (
                        TOTAL.START_TIME *= FX.START_TIME 
                        AND TOTAL.START_TIME *= IR.START_TIME
                  )
            )
      )
