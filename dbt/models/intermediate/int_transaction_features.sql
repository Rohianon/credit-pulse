with txns as (
    select * from {{ ref('stg_mpesa_transactions') }}
),

customer_agg as (
    select
        customer_id,
        count(*) as transaction_count,
        count(distinct cast(transaction_at as date)) as active_days,
        count(*) * 1.0 / nullif(
            datediff('day', min(transaction_at), max(transaction_at)), 0
        ) as transaction_frequency,
        sum(received_amount) as total_inflows,
        sum(sent_amount) as total_outflows,
        sum(received_amount) * 1.0 / nullif(sum(sent_amount), 0) as inflow_outflow_ratio,
        avg(balance) as avg_balance,
        min(balance) as min_balance,
        max(balance) as max_balance,
        stddev(balance) as balance_volatility,
        avg(case when received_amount > 0 then received_amount end) as avg_received_amount,
        max(received_amount) as max_received_amount,
        stddev(sent_amount) as spending_consistency,
        datediff('day', max(transaction_at), current_timestamp) as days_since_last_transaction,
        datediff('day', min(transaction_at), max(transaction_at)) as account_age_days
    from txns
    group by customer_id
),

category_ratios as (
    select
        customer_id,
        sum(case when tx_category = 'betting' then sent_amount else 0 end)
            * 1.0 / nullif(sum(sent_amount), 0) as betting_spend_ratio,
        sum(case when tx_category = 'utility' then sent_amount else 0 end)
            * 1.0 / nullif(sum(sent_amount), 0) as utility_payment_ratio,
        sum(case when tx_category = 'cash_withdrawal' then sent_amount else 0 end)
            * 1.0 / nullif(sum(sent_amount), 0) as cash_withdrawal_ratio,
        sum(case when tx_category = 'airtime' then sent_amount else 0 end)
            * 1.0 / nullif(sum(sent_amount), 0) as airtime_spend_ratio,
        sum(case when tx_category = 'merchant' then sent_amount else 0 end)
            * 1.0 / nullif(sum(sent_amount), 0) as merchant_spend_ratio,
        sum(case when tx_category in ('p2p_received', 'p2p_sent') then 1 else 0 end)
            * 1.0 / nullif(count(*), 0) as p2p_transfer_ratio,
        count(distinct case when tx_category in ('mshwari', 'kcb_mpesa', 'fuliza')
            then tx_category end) as loan_product_count
    from txns
    group by customer_id
)

select
    a.*,
    c.betting_spend_ratio,
    c.utility_payment_ratio,
    c.cash_withdrawal_ratio,
    c.airtime_spend_ratio,
    c.merchant_spend_ratio,
    c.p2p_transfer_ratio,
    c.loan_product_count
from customer_agg a
join category_ratios c using (customer_id)
