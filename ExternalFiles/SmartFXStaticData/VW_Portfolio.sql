USE [NTCSSTGDB]
GO

/****** Object:  View [dbo].[VW_Portfolio]    Script Date: 7/17/2024 9:48:47 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [dbo].[VW_Portfolio]
AS
SELECT 
	prfid,
	assinf,
	updat_time
FROM portfolio

GO


