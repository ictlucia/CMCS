USE [NTCSSTGDB]
GO

/****** Object:  View [dbo].[VW_Broker]    Script Date: 7/17/2024 9:48:39 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [dbo].[VW_Broker]
AS
SELECT 
	ptyid,
	ptyid2,
	fullname,
	updat_time
FROM [NTCSSTGDB].[dbo].[party]
where type = 4

GO


