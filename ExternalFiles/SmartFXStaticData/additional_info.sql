USE [NTCSSTGDB]
GO

/****** Object:  Table [dbo].[additional_info]    Script Date: 7/20/2023 3:34:55 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[additional_info](
	[addinf_specnbr] [bigint] NOT NULL,
	[recaddr] [bigint] NULL,
	[valnbr] [bigint] NOT NULL,
	[value] [char](63) NULL,
)

INSERT INTO NTCSSTGDB.dbo.[additional_info] ([addinf_specnbr],[recaddr],[valnbr],[value]) 
SELECT [addinf_specnbr],[recaddr],[valnbr],[value]
FROM ADM_MANDIRI_1B_UAT.dbo.[additional_info]
where addinf_specnbr in (select specnbr from additional_info_spec where field_name in ('NPWP', 'BranchCode','DOB'))


