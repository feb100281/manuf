select  
"id_agreement"::int as id,
COALESCE("pid","id_agreement")::int as la_id,
case 
when STARTS_WITH(LOWER("number_la"),'дс') then 'Доп соглашение'
when STARTS_WITH(LOWER("number_la"),'дc') then 'Доп соглашение'
when STARTS_WITH(LOWER("number_la"),'инд') then 'Индексация'
when STARTS_WITH(LOWER("number_la"),'прод') then 'Продление'
when STARTS_WITH(LOWER("number_la"),'прол') then 'Продление'
when STARTS_WITH(LOWER("number_la"),'пред') then 'Предварительный договор'
when STARTS_WITH(LOWER("number_la"),'пред') then 'Предварительный договор'
when STARTS_WITH(LOWER("number_la"),'соглашение о замене') then 'Согл о замене сторон'
when STARTS_WITH(LOWER("number_la"),'письмо') then 'Письмо'
else 'Основной договор'
end as sa_type,
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
from main.leaseagreements;