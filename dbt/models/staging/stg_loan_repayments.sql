with source as (
    select * from raw_loan_repayments
)

select
    customer_id,
    loan_id,
    new_repeat as loan_type,
    cast(strptime(Funded_date, '%m/%d/%Y') as date) as funded_date,
    cast(strptime(due_date, '%m/%d/%Y') as date) as due_date,
    loan_duration,
    loan_amount,
    to_repay as amount_to_repay,
    interest_amount,
    repaid_amount,
    loan_balance,
    case
        when last_paid_date is not null and last_paid_date != ''
        then cast(strptime(last_paid_date, '%m/%d/%Y') as date)
        else null
    end as last_paid_date,
    case
        when loan_balance <= 0 then 0
        else 1
    end as is_defaulted
from source
