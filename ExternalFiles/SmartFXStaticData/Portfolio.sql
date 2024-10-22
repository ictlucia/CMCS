USE [NTCSSTGDB]
GO


CREATE TABLE [dbo].[portfolio](
	[prfnbr] [bigint] NOT NULL,
	[assinf] [char](35) NULL,
	[prfid] [char](39) NULL,
	[updat_time] [datetime] NULL,
	
)
USE [NTCSSTGDB]


INSERT INTO NTCSSTGDB.dbo.portfolio (prfnbr,assinf, prfid, updat_time) 
SELECT prfnbr,assinf, prfid, updat_time 
FROM ADM_MANDIRI_1B_UAT.dbo.portfolio