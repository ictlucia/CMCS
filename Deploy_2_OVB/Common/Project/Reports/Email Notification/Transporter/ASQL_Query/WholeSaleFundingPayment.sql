/* update_method=0 */
select 
    t.trdnbr
from 
    Trade t,
    Instrument i
where 
        t.insaddr = i.insaddr
        and t.status in ('FO Confirmed', 'BO Confirmed', 'BO-BO Confirmed')
        and 
        
             i.instype in ('Deposit', 'BasketRepo/Reverse')
            
             and checkProductType(i, 'DEBT') = 1
            
             and checkCategory(i, 'NCN', 'NCD', 'ZCO', 'BOND') = 1
       
            and getTenor(i) > 1.0
            
        
        