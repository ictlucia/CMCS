/* update_method=0 */
SELECT
    trd.trdnbr
FROM
	Trade trd,
	Party pty,
	ChoiceList clfree2,
	ChoiceList cltype,
	Instrument i
WHERE
	trd.category = 1
	AND pty.ptynbr = trd.counterparty_ptynbr
	AND clfree2.seqnbr = pty.free2_chlnbr
	AND clfree2.entry = 'Bank'
	AND cltype.seqnbr = trd.optkey3_chlnbr
	AND cltype.entry LIKE 'BONDSREPO'
    AND trd.re_acquire_day - time_to_day(trd.time) > 365
    AND trd.re_acquire_day > today