/* update_method=0 */

/* created temp table to get the hedged trades */

select 
    t.trdnbr
into
    tmpTrades
from
    Trade t,
    Trade tt
where
    t.trdnbr = tt.hedge_trdnbr



/* Created another tmp table by join query with above table and trade table */

select

    t.trdnbr,
    tt.trdnbr 'hedge_trdnbr'
into 
    tmp_result

from
    Trade t,
    tmpTrades tt fill,
    Instrument i
    
 
where
    t.trdnbr *= tt.trdnbr
    and t.insaddr = i.insaddr
    and t.status in ('FO Confirmed', 'BO Confirmed', 'BO-BO Confirmed')
    and i.instype = 'Option'
    and checkProductType(i, 'SP') = 1
    and checkCategory(i, 'MCS') = 1
    and 
    (
        i.exp_day <= Today or 
            (i.strike_price < fxRate(t) and isValidTrade(t) = 1)
         
        
    )
     
    
select 
    trdnbr
from
    tmp_result
where
    hedge_trdnbr < 1

 

 

