SELECT
    product_code,
    SUM(total_transaction) AS total_transaction,
    SUM(fraud_transaction) AS fraud_transaction,
    ROUND(SAFE_DIVIDE(SUM(fraud_transaction), SUM(total_transaction)), 4) AS fraud_rate_pct,
    ROUND(SAFE_DIVIDE(SUM(total_amount), SUM(total_transaction)), 2) AS avg_txn_amt
FROM production.fraud_risk_summary
GROUP BY product_code
ORDER BY fraud_rate_pct DESC