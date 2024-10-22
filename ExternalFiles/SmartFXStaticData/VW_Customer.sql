USE [NTCSSTGDB]
GO

/****** Object:  View [dbo].[VW_Customer]    Script Date: 7/17/2024 9:36:43 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO




CREATE VIEW [dbo].[VW_Customer]
AS
select 
  party.address, 
  party.address2, 
  party.country, 
  party.hostid, 
  party.fullname, 
  party.fullname2,
  addinfo_npwp.value as npwp,
  addinfo_dob.value as dob,
  party.updat_time,
  party.type,
  addinfo_branchcode.value as branchcode,
  party.ptyid2
from party party 
left join additional_info addinfo_npwp on addinfo_npwp.recaddr = party.ptynbr and addinfo_npwp.addinf_specnbr = (select distinct specnbr from additional_info_spec  where field_name = 'NPWP')
left join additional_info addinfo_branchcode on addinfo_branchcode.recaddr = party.ptynbr and addinfo_branchcode.addinf_specnbr=(select distinct specnbr from additional_info_spec  where field_name='BranchCode')
left join additional_info addinfo_dob on addinfo_dob.recaddr = party.ptynbr and addinfo_dob.addinf_specnbr=(select distinct specnbr from additional_info_spec  where field_name='DOB')
where (party.type=1 or party.type = 2) and hostid is not null and hostid <> ''
GO


