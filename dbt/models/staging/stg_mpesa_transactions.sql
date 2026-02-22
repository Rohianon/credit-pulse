with source as (
    select * from raw_mpesa_transactions
)

select
    customer_id,
    transaction_id,
    coalesce(received_amount, 0) as received_amount,
    coalesce(sent_amount, 0) as sent_amount,
    coalesce(balance_then, 0) as balance,
    transaction_type,
    cast(transaction_datetime as timestamp) as transaction_at,
    statement_upload_id,
    {{ classify_transaction('transaction_type') }} as tx_category
from source
where transaction_id is not null
