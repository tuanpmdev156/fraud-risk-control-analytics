-- Return records have negative transaction_amount
SELECT
    transaction_id,
    transaction_amount
FROM {{ ref('fct_transaction') }}
WHERE transaction_amount <= 0