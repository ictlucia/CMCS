/* update_method=0 */

select 

    t.trdnbr

from

    Trade t,

    Instrument i,

    Instrument c

where

    t.insaddr = i.insaddr

    and i.curr = c.insaddr
    
    and t.status in ('FO Confirmed', 'BO Confirmed', 'BO-BO Confirmed')

    and c.insid ~= 'IDR'

    and i.instype = 'BasketRepo/Reverse'

    and i.exp_day = bankday_adjust(TODAY-1, 'USD', 'Mod. Following')