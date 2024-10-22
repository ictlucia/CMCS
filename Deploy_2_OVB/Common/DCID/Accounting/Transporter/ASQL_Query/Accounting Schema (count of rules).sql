SELECT  
       count(*)
       
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

        
