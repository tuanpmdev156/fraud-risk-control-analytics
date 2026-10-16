WITH raw_indentity AS (
    SELECT * FROM {{ source('raw', 'ext_identity') }}
),
transformed_identity AS (
    SELECT
        CAST(TransactionID AS INT64) AS transaction_id,
        LOWER(TRIM(CAST(DeviceType AS STRING))) AS device_type,
        LOWER(TRIM(CAST(DeviceInfo AS STRING))) AS device_info,
        LOWER(TRIM(CAST(id_30 AS STRING))) AS os_version,
        LOWER(TRIM(CAST(id_31 AS STRING))) AS browser
    FROM raw_indentity
)
SELECT
    transaction_id,
    device_type,
    device_info,
    os_version,
    browser
FROM transformed_identity