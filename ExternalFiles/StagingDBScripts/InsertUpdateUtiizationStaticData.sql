USE [NTCSSTGDB]
GO

/****** Object:  StoredProcedure [dbo].[InsertUpdateUtilizationStaticData]    Script Date: 28-Nov-23 2:30:23 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO





-- =============================================
-- Author:		<FIS>
-- Create date: <15 March 2023>
-- Description:	<Stored procedure to insert/update the values in LIMIT_UTILIZATION table.>
-- =============================================
CREATE PROCEDURE [dbo].[InsertUpdateUtilizationStaticData] 
													@UniqueID                    bigint, 
													@ComplianceRuleName          nvarchar(135), 
													@CCY                         nvarchar(4), 
													@CIF                         nvarchar(19), 
													@LimitType					 nvarchar(20),
													@CounterpartyName            nvarchar(45), 
													@NotionalLimitThresholdValue decimal(18, 2), 
													@RemainingNotionalLimitValue decimal(18, 2), 
													@UsedNotionalLimitValue      decimal(18, 2), 
													@CEMLimitThresholdValue      decimal(18, 2), 
													@RemainingCEM                decimal(18, 2), 
													@UsedCEM                     decimal(18, 2), 
													@AgreementNumber             nvarchar(63), 
													@AgreementDate               datetime, 
													@RenewalNumber               nvarchar(63), 
													@RenewalDate                 datetime, 
													@ApplicationNumber           nvarchar(63), 
													@LimitEffectiveDate          datetime, 
													@LimitExpiryDate             datetime, 
													@Status						 nvarchar(63),
													@UpdateDate				     date												
AS
BEGIN
	IF (SELECT count(UniqueID) from LIMIT_UTILIZATION where UniqueID=@UniqueID) = 0 
	BEGIN
	INSERT INTO LIMIT_UTILIZATION  VALUES(	@UniqueID, @ComplianceRuleName,@CCY,@CIF, @LimitType, @CounterpartyName,@NotionalLimitThresholdValue,@RemainingNotionalLimitValue,@UsedNotionalLimitValue,@CEMLimitThresholdValue,
								@RemainingCEM,@UsedCEM, @AgreementNumber, @AgreementDate, @RenewalNumber, @RenewalDate, @ApplicationNumber, @LimitEffectiveDate, @LimitExpiryDate, @Status, @UpdateDate);
	END
	ELSE
	BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    -- Insert statements for procedure here
	UPDATE LIMIT_UTILIZATION  SET	ComplianceRuleName=@ComplianceRuleName, CCY=@CCY, CIF=@CIF,LimitType = @LimitType, CounterpartyName=@CounterpartyName,
								NotionalLimitThresholdValue=@NotionalLimitThresholdValue,  RemainingNotionalLimitValue=@RemainingNotionalLimitValue,
								UsedNotionalLimitValue=@UsedNotionalLimitValue, CEMLimitThresholdValue=@CEMLimitThresholdValue, RemainingCEM=@RemainingCEM,UsedCEM=@UsedCEM, AgreementNumber=@AgreementNumber, AgreementDate=@AgreementDate, 
								RenewalNumber=@RenewalNumber, RenewalDate=@RenewalDate, ApplicationNumber=@ApplicationNumber, 
								LimitEffectiveDate=@LimitEffectiveDate, LimitExpiryDate=@LimitExpiryDate, Status=@Status, UpdateDate=@UpdateDate where UniqueID=@UniqueID

	END
END
GO

