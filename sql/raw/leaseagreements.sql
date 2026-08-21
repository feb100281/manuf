select
"id_agreement"::int as id,
"id_contr"::text as cp_id,
"number_la"::text as number,
case
when TRY_CAST(date_la as date)
    between DATE '0001-01-01' and DATE '9999-12-31'
then TRY_CAST(date_la as date)
else null
end as date_from,
"date_signed"::text as date_signed,
"date_expired"::text as date_expired,
"Comment"::text as comments,
TRY_CAST("real_area" as double) as real_area,
TRY_CAST("calculated_area" as double) as calculated_area,
TRY_CAST("K_useful_area" as double) as k_useful_area

from main.leaseagreements
where pid is null