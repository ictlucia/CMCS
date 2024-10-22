/* update_method=0 */
select  t.trdnbr
from 
    Trade t, 
    Instrument i,
    Portfolio p, 
    ChoiceList c
where 
    t.insaddr=i.insaddr
    and t.prfnbr = p.prfnbr
    and c.seqnbr = t.optkey3_chlnbr
    and t.value_day = Tomorrow
    and t.status in ('FO Confirmed', 'BO Confirmed', 'BO-BO Confirmed')
    and 
    (
        (
            ( c.list = 'Product Type' and c.entry='FXBN')
            and p.prfid = 'Banknotes Export Import'
            and (i.instype='curr' and isBankNoteCurr(t) = 1)
        )
        or 
        (
            i.instype='Commodity'
        )
    )
