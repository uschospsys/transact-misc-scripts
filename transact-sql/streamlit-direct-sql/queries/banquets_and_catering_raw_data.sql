SELECT
--Raw Data By Profit Center
CAST ([tdate] AS date) AS Date
	  ,CONVERT(varchar, ([tdatetime]), 8) AS Time
	  ,[trans_id] AS Receipt_#
      ,[profit_location] AS Profit_Center
	  ,[kiosk_name] AS POS_Name
      ,[item_sub_cat_name] AS Subcategory_Name
      --,[description] is tender
	  --[items_count] is amount of line items on receipt. Is not qty of items
	  --,[item_qty] AS QTY
      ,[item_number] AS Item_Number
      ,[item_description] AS Item
	  ,[type] AS Type
      ,[item_discount] AS Discount
	  ,[item_price] AS Item_Price
	  ,[item_base_price] AS Item_Base_Price

FROM [dbo].[view_transactions_full]
      WHERE [item_sub_cat_name] IN ('LAB Happy Hour Drinks', 'Lab Game Day Food', 'Lab Game Day Drinks', 'Lab Food', 'Fee', 'B&C Special Events', 'B&C Moreton Fig', 'B&C McKays Food', 'B&C McKays Drinks', 'B&C Hotel Lobby', 'PEC Special Events', 'B&C Trojan Family Weekend','B&C Non-Hosted Beverages', 'B&C Hosted Beverages','LAB Cocktails')
            AND [tdate] >= '{start_date}' AND [tdatetime] < '{end_date}'
			--AND [profit_location] = 'Catering UPC'
ORDER BY [Profit_Center], [Time]