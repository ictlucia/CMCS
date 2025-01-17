USE [NTCSSTGDB]
GO
/****** Object:  Table [dbo].[CUSTODYHOLDING]    Script Date: 10/20/2022 11:29:07 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CUSTODYHOLDING](
	[ID] [uniqueidentifier] NOT NULL,
	[SECURITY_NAME] [nvarchar](100) NOT NULL,
	[ISIN] [nvarchar](100) NOT NULL,
	[AMT_QTY] [numeric](18, 2) NOT NULL,
	[INQ_DATE] [date] NOT NULL,
	[SCA_REF] [varchar](100) NULL,
	[ACTL_ACNT_NUM] [varchar](100) NULL,
	[CUST_ACNT_NUM_STATUS] [varchar](100) NULL,
	[SECURITY_TYPE] [varchar](100) NULL,
	[SECURITY_SUB_TYPE] [varchar](100) NULL,
	[SHRT_NAME] [varchar](100) NULL,
	[ACCOUNT_BALANCE] [numeric](18, 2) NULL,
	[TAX_LOT_COST_BASIS] [numeric](18, 2) NULL,
	[TAX_LOT_QTY] [numeric](18, 2) NULL,
	[AVG_COST_PRICE] [numeric](18, 2) NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[CUSTODYHOLDING_STG]    Script Date: 10/20/2022 11:29:07 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CUSTODYHOLDING_STG](
	[ID] [uniqueidentifier] NOT NULL,
	[SECURITY_NAME] [nvarchar](100) NOT NULL,
	[ISIN] [nvarchar](100) NOT NULL,
	[AMT_QTY] [numeric](18, 2) NOT NULL,
	[INQ_DATE] [date] NOT NULL,
	[SCA_REF] [varchar](100) NULL,
	[ACTL_ACNT_NUM] [varchar](100) NULL,
	[CUST_ACNT_NUM_STATUS] [varchar](100) NULL,
	[SECURITY_TYPE] [varchar](100) NULL,
	[SECURITY_SUB_TYPE] [varchar](100) NULL,
	[SHRT_NAME] [varchar](100) NULL,
	[ACCOUNT_BALANCE] [numeric](18, 2) NULL,
	[TAX_LOT_COST_BASIS] [numeric](18, 2) NULL,
	[TAX_LOT_QTY] [numeric](18, 2) NULL,
	[AVG_COST_PRICE] [numeric](18, 2) NULL
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[CUSTODYHOLDING] ADD  CONSTRAINT [DF_dbo_CUSTODYHOLDING_ID]  DEFAULT (newid()) FOR [ID]
GO
ALTER TABLE [dbo].[CUSTODYHOLDING_STG] ADD  DEFAULT (newid()) FOR [ID]
GO
/****** Object:  StoredProcedure [dbo].[CUSTODY_HOLDING]    Script Date: 10/20/2022 11:29:07 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- ======================================================
-- Author:		<Benedictus Bayu P>
-- Create date: <10 Oktober 2022>
-- Description:	<Upsert data into Custody Holding Table>
-- ======================================================

CREATE PROCEDURE [dbo].[CUSTODY_HOLDING] 

AS
DECLARE @INQ_DATE DATE
SET @INQ_DATE = GETDATE()

BEGIN 
if exists( select ISIN from CUSTODYHOLDING_STG where ISIN IN(SELECT ISIN FROM CUSTODYHOLDING)  AND  INQ_DATE = @INQ_DATE)
    
    BEGIN 
        UPDATE CUSTODYHOLDING
        SET CUSTODYHOLDING.AMT_QTY = CUSTODYHOLDING_STG.AMT_QTY, CUSTODYHOLDING.INQ_DATE = CUSTODYHOLDING_STG.INQ_DATE
        FROM CUSTODYHOLDING_STG 
        WHERE CUSTODYHOLDING_STG.INQ_DATE = @INQ_DATE AND CUSTODYHOLDING.ISIN = CUSTODYHOLDING_STG.ISIN
    END 

ELSE
    BEGIN
        INSERT INTO CUSTODYHOLDING 
        SELECT [ID],[SECURITY_NAME], [ISIN], [AMT_QTY], [INQ_DATE], [SCA_REF], [ACTL_ACNT_NUM], [CUST_ACNT_NUM_STATUS], [SECURITY_TYPE], [SECURITY_SUB_TYPE], [SHRT_NAME], [ACCOUNT_BALANCE], [TAX_LOT_COST_BASIS], [TAX_LOT_QTY], [AVG_COST_PRICE] 
		FROM CUSTODYHOLDING_STG
		WHERE INQ_DATE = @INQ_DATE
	END

END;
GO
/****** Object:  StoredProcedure [dbo].[GetHoldingPositionData]    Script Date: 10/20/2022 11:29:07 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		<Titoyan Dwihandoko>
-- Create date: <07 Oktober 2022>
-- Description:	<Get Holding Position Data>
-- =============================================
CREATE PROCEDURE [dbo].[GetHoldingPositionData]
AS
BEGIN
	select ISIN, CONCAT(RIGHT(REPLACE(INQ_DATE,'-',''),6),'_',CONVERT(INT,AMT_QTY)) HoldPosCustody  from CUSTODYHOLDING
END
GO
