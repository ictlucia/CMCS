USE [NTCSSTGDB]
GO

/****** Object:  StoredProcedure [dbo].[SP_FLAGGINGETL]    Script Date: 4/17/2024 3:05:13 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


-- =============================================
-- Author:		<Gregorius Vito,,Name>
-- Create date: <15 Feb 2023,,>
-- Description:	<Description,,>
-- =============================================
CREATE PROCEDURE [dbo].[SP_FLAGGINGETL]
AS
BEGIN
	INSERT INTO ETL_FLAG (EXPORT_DATE, EXPORT_FLAG) VALUES (GETDATE(),'1')
END
GO


