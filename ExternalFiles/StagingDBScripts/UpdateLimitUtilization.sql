USE [NTCSSTGDB]
GO

/****** Object:  StoredProcedure [dbo].[UpdateLimitUtilization]    Script Date: 28-Nov-23 2:31:53 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO




-- =============================================
-- Author:		<FIS>
-- Create date: <15 March 2023>
-- Description:	<Stored procedure to insert/update the values in LIMIT_UTILIZATION table.>
-- =============================================
CREATE PROCEDURE [dbo].[UpdateLimitUtilization] 
													@UniqueID                    bigint, 
													@RemainingNotionalLimitValue decimal(18, 2), 
													@UsedNotionalLimitValue      decimal(18, 2), 
													@RemainingCEM                decimal(18, 2), 
													@UsedCEM                     decimal(18, 2), 
													@UpdateDate				     date												
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    -- Insert statements for procedure here
	UPDATE LIMIT_UTILIZATION  SET	RemainingNotionalLimitValue=@RemainingNotionalLimitValue,
								UsedNotionalLimitValue=@UsedNotionalLimitValue, RemainingCEM=@RemainingCEM, UsedCEM=@UsedCEM, UpdateDate=@UpdateDate where UniqueID=@UniqueID
	
END
GO

