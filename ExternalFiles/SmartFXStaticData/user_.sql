USE [NTCSSTGDB]
GO

/****** Object:  Table [dbo].[user_]    Script Date: 7/20/2023 2:50:58 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[user_](
	
	[name] [char](39) NULL,
	[updat_time] [datetime] NULL,
	[userid] [char](20) NULL,
	[usrnbr] [bigint] NOT NULL

)

	
INSERT INTO NTCSSTGDB.dbo.[user_] ([name],[usrnbr], userid, updat_time) 
SELECT [name],[usrnbr], userid, updat_time
FROM ADM_MANDIRI_1B_UAT.dbo.[user_]
