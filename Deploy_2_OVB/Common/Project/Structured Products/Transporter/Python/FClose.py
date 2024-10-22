import acm

def close_trade(original_trade, closing_trade):
    trade_key3 = original_trade.optkey3_chlnbr
    if trade_key3 is None:
        return
    if trade_key3.entry != 'SP':
        return
    trade_key4 = original_trade.optkey4_chlnbr
    if trade_key4 is None:
        return
    ins = original_trade.insaddr
    ins_type = original_trade.insaddr.instype
    trade_key4_entry = trade_key4.entry
    if trade_key4_entry == 'MMLD':
        if ins_type == 'Option':
            closing_trade.quantity = -original_trade.quantity
    elif trade_key4_entry == 'MLDR':
        if ins_type == 'Swap':
            closing_trade.quantity = -original_trade.quantity
            closing_ins = closing_trade.insaddr
            o_leg_rate = None
            for o_leg in ins.legs():
                if o_leg.type == 'Fixed':
                    o_leg_rate = o_leg.fixed_rate
                    break
            if o_leg_rate is None:
                return
            for c_leg in closing_ins.legs():
                if c_leg.type == 'Fixed':
                    c_leg.fixed_rate = o_leg_rate
                    break
    elif trade_key4_entry == 'MPF':
        closing_trade.price = original_trade.price
        closing_trade.premium = -original_trade.premium
        closing_trade.quantity = -original_trade.quantity
    elif trade_key4_entry == 'MDS':
        closing_trade.acquire_day = original_trade.acquire_day
        closing_trade.value_day = original_trade.value_day
        closing_trade.price = original_trade.price
    elif ins_type == 'Curr':
        closing_trade.price = original_trade.price
        closing_trade.premium = original_trade.premium
        closing_trade.quantity = original_trade.quantity
