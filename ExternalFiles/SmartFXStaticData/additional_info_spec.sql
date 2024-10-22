USE [NTCSSTGDB]
GO

/****** Object:  Table [dbo].[additional_info_spec]    Script Date: 7/20/2023 3:43:54 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[additional_info_spec](
	
	[field_name] [char](19) NULL,
	[specnbr] [bigint] NOT NULL,
)


INSERT INTO NTCSSTGDB.dbo.[additional_info_spec] ([field_name],[specnbr]) 
SELECT [field_name],[specnbr]
FROM ADM_MANDIRI_1B_UAT.dbo.[additional_info_spec]
Where field_name in ('NPWP','BranchCode','DOB')


