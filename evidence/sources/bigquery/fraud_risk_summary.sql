SELECT
    transaction_date,
    product_code,
    card_network,
    device_type,
    total_transaction,
    fraud_transaction,
    fraud_rate,
    total_amount,
    total_fraud_amount
FROM production.fraud_risk_summary

