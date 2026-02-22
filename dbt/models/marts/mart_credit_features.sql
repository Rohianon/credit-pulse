with features as (
    select * from {{ ref('int_transaction_features') }}
),

borrowers as (
    select * from {{ ref('int_borrower_profiles') }}
)

select
    b.customer_id,
    b.loan_id,
    b.loan_type,
    b.loan_amount,
    b.amount_to_repay,
    b.repaid_amount,
    b.loan_balance,
    b.is_defaulted,
    b.repayment_ratio,
    b.days_past_due,
    coalesce(f.transaction_count, 0) as transaction_count,
    coalesce(f.active_days, 0) as active_days,
    coalesce(f.transaction_frequency, 0) as transaction_frequency,
    coalesce(f.total_inflows, 0) as total_inflows,
    coalesce(f.total_outflows, 0) as total_outflows,
    coalesce(f.inflow_outflow_ratio, 0) as inflow_outflow_ratio,
    coalesce(f.avg_balance, 0) as avg_balance,
    coalesce(f.min_balance, 0) as min_balance,
    coalesce(f.max_balance, 0) as max_balance,
    coalesce(f.balance_volatility, 0) as balance_volatility,
    coalesce(f.avg_received_amount, 0) as avg_received_amount,
    coalesce(f.max_received_amount, 0) as max_received_amount,
    coalesce(f.spending_consistency, 0) as spending_consistency,
    coalesce(f.days_since_last_transaction, 0) as days_since_last_transaction,
    coalesce(f.account_age_days, 0) as account_age_days,
    coalesce(f.betting_spend_ratio, 0) as betting_spend_ratio,
    coalesce(f.utility_payment_ratio, 0) as utility_payment_ratio,
    coalesce(f.cash_withdrawal_ratio, 0) as cash_withdrawal_ratio,
    coalesce(f.airtime_spend_ratio, 0) as airtime_spend_ratio,
    coalesce(f.merchant_spend_ratio, 0) as merchant_spend_ratio,
    coalesce(f.p2p_transfer_ratio, 0) as p2p_transfer_ratio,
    coalesce(f.loan_product_count, 0) as loan_product_count
from borrowers b
left join features f using (customer_id)
