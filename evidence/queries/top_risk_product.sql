SELECT
    product_code AS product,
    ROUND(SAFE_DIVIDE(SUM(fraud_transaction), SUM(total_transaction)), 4) AS fraud_rate_pct
FROM production.fraud_risk_summary
GROUP BY product_code
ORDER BY fraud_rate_pct DESC
LIMIT 1

