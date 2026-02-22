{% macro classify_transaction(transaction_type) %}
    case
        when {{ transaction_type }} ilike '%airtime%' then 'airtime'
        when {{ transaction_type }} ilike '%bet%' or {{ transaction_type }} ilike '%sportpesa%'
             or {{ transaction_type }} ilike '%betika%' or {{ transaction_type }} ilike '%betway%' then 'betting'
        when {{ transaction_type }} ilike '%kplc%' or {{ transaction_type }} ilike '%kenya power%'
             or {{ transaction_type }} ilike '%safaricom%' or {{ transaction_type }} ilike '%zuku%'
             or {{ transaction_type }} ilike '%nairobi%water%' or {{ transaction_type }} ilike '%dstv%'
             or {{ transaction_type }} ilike '%gotv%' then 'utility'
        when {{ transaction_type }} ilike '%withdraw%' or {{ transaction_type }} ilike '%atm%' then 'cash_withdrawal'
        when {{ transaction_type }} ilike '%m-shwari%' or {{ transaction_type }} ilike '%mshwari%' then 'mshwari'
        when {{ transaction_type }} ilike '%kcb%' then 'kcb_mpesa'
        when {{ transaction_type }} ilike '%fuliza%' then 'fuliza'
        when {{ transaction_type }} ilike '%received%' or {{ transaction_type }} ilike '%receive%' then 'p2p_received'
        when {{ transaction_type }} ilike '%sent%' or {{ transaction_type }} ilike '%send%'
             or {{ transaction_type }} ilike '%paid%' or {{ transaction_type }} ilike '%pay%' then 'p2p_sent'
        when {{ transaction_type }} ilike '%merchant%' or {{ transaction_type }} ilike '%buy goods%'
             or {{ transaction_type }} ilike '%lipa%' or {{ transaction_type }} ilike '%till%' then 'merchant'
        else 'other'
    end
{% endmacro %}
