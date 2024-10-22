SELECT DISTINCT 
        Book.name 'Book',
        Treatment.name 'Treatment',
        Treatment.type 'T Type',
        T3.name 'Treatment filter',
        AccountingInstruction.name 'AI Name (Rule)',
        AccountingInstruction.description 'Description (Rule)',
        T2.name 'AI filter',
        AccountingInstruction.type 'Type',
        AccountingInstruction.journal_trigger_type 'Trigger',
        AccountingInstruction.aggregation_level 'AggrLevel',
        JournalValueDef.posting_field_name 'Posting Field',
        JournalValueDef.debit_or_credit 'D/C',
        TAccount.name 'Mapped Account',
        TAccount.number 'Account',
        T1.name 'Account filter',
        ChoiceList.entry 'Category',
        ChoiceList.description 'Description',
        AccountingInstruction.reversal_method 'ReversalMethod',
        AccountingInstruction.start_date_method_chain 'StartDate',
        AccountingInstruction.end_date_method_chain 'EndDate',
        AccountingInstruction.business_day_method 'RollingConv',
        AccountingInstruction.amend_historic_journals 'HistAmend',
        AccountingInstruction.suppress_if_unchanged 'Suppress',
        AccountingInstruction.reversal_exclusion 'RevExclusion',
        AccountingInstruction.reversal_frequency 'RevFreq',
        AccountingInstruction.exclude_fx_conversion 'ExcludeFXConv',
        AccountingInstruction.fx_rate_date_method_chain 'FXConvDate',
        AccountingInstruction.start_date_method_chain = AccountingInstruction.end_date_method_chain ? 'No' : 'Yes' 'Periodic' /*,
        convert('time', AccInstructionMapping.updat_time, '%Y-%m-%d %H:%M:%S') 'AI Mapping Update Time',
        convert('time', TAccountAllocLink.updat_time, '%Y-%m-%d %H:%M:%S'    ) 'TAccount Alloc Link Update Time',
        convert('time', TAccountMapping.updat_time, '%Y-%m-%d %H:%M:%S'      ) 'TAccount Mapping Update Time' */
        
FROM    Book,
        BookLink,
        Treatment,
        TreatmentLink,
        TreatmentMapping,
        AccountingInstruction,
        AccInstructionMapping,
        JournalValueDef,
        TAccountAllocLink,
        TAccountMapping,
        ChartOfAccount,
        TAccount,
        TextObject T1,
        TextObject T2,
        TextObject T3,
        ChoiceList
WHERE   Book.seqnbr=BookLink.book
AND     Treatment.seqnbr=BookLink.treatment
AND     TreatmentLink.treatment=Treatment.seqnbr
AND     AccountingInstruction.seqnbr=TreatmentLink.accounting_instruction
AND     AccountingInstruction.seqnbr=JournalValueDef.accounting_instruction
AND     JournalValueDef.seqnbr=TAccountAllocLink.jvd
AND     TAccountAllocLink.seqnbr=TAccountMapping.t_account_alloc_link
AND     TAccountAllocLink.treatment=Treatment.seqnbr
AND     ChartOfAccount.seqnbr=TAccountAllocLink.chart_of_account
AND     TAccount.seqnbr=ChartOfAccount.t_account
AND     TAccountMapping.query_seqnbr*=T1.seqnbr
AND     AccInstructionMapping.query_seqnbr*=T2.seqnbr
AND     AccInstructionMapping.book_link=BookLink.seqnbr
AND     AccInstructionMapping.treatment_link=TreatmentLink.seqnbr
AND     TAccountMapping.treatment_link=TreatmentLink.seqnbr
AND     TreatmentLink.book=Book.seqnbr
AND     TreatmentMapping.book=Book.seqnbr
AND     TreatmentMapping.book_link=BookLink.seqnbr
AND     TreatmentMapping.query_seqnbr*=T3.seqnbr
AND     TAccount.category_chlnbr*=ChoiceList.seqnbr
ORDER BY Book.name, Treatment.name, AccountingInstruction.name, TAccount.name  
        
