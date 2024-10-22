USE [NTCSSTGDB]
GO

/****** Object:  Table [dbo].[LIMIT_UTILIZATION]    Script Date: 28-Nov-23 2:28:59 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[LIMIT_UTILIZATION](
	[UniqueID] [int] NOT NULL,
	[ComplianceRuleName] [varchar](135) NOT NULL,
	[CCY] [varchar](4) NULL,
	[CIF] [varchar](19) NULL,
	[LimitType] [varchar](20) NULL,
	[CounterpartyName] [varchar](45) NULL,
	[NotionalLimitThresholdValue] [decimal](18, 2) NULL,
	[RemainingNotionalLimitValue] [decimal](18, 2) NULL,
	[UsedNotionalLimitValue] [decimal](18, 2) NULL,
	[CEMLimitThresholdValue] [decimal](18, 2) NULL,
	[RemainingCEM] [decimal](18, 2) NULL,
	[UsedCEM] [decimal](18, 2) NULL,
	[AgreementNumber] [varchar](63) NULL,
	[AgreementDate] [datetime] NULL,
	[RenewalNumber] [varchar](63) NULL,
	[RenewalDate] [datetime] NULL,
	[ApplicationNumber] [varchar](63) NULL,
	[LimitEffectiveDate] [datetime] NULL,
	[LimitExpiryDate] [datetime] NULL,
	[Status] [varchar](10) NOT NULL,
	[UpdateDate] [date] NOT NULL
) ON [PRIMARY]
GO

