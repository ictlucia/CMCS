USE [NTCSSTGDB]
GO

/****** Object:  Table [dbo].[party]    Script Date: 7/20/2023 3:17:19 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[party](
	[address] [nchar](39) NULL,
	[address2] [nchar](39) NULL,
	[country] [nchar](39) NULL,
	[fullname] [nchar](255) NULL,
	[fullname2] [nchar](255) NULL,
	[hostid] [nchar](19) NULL,
	[ptyid] [nchar](39) NULL,
	[ptyid2] [nchar](39) NULL,
	[ptynbr] [bigint] NOT NULL,
	[type] [int] NULL,
	[updat_time] [datetime] NULL,
) 
GO

INSERT INTO NTCSSTGDB.dbo.[party] ([address],[address2],[country],[fullname],[fullname2],[hostid],[ptyid],[ptyid2],[ptynbr],[type],[updat_time]) 
SELECT [address],[address2],[country],[fullname],[fullname2],[hostid],[ptyid],[ptyid2],[ptynbr],[type],[updat_time]
FROM ADM_MANDIRI_1B_UAT.dbo.PARTY
WHERE TYPE IN (1,2,4)
