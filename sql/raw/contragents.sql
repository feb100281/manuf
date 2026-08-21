select 
id_contr::text as id,
id_contr::text as inn,
"name_contr"::text as name,
contrAgentType::bigint as cptype_id,
email::text as email,    
"ORGN"::text as ogrn,
"phone"::text as phone,
"address"::text as address,
CASE 
WHEN id_contr in (select id_contr from main.leaseagreements) 
and id_contr not in (select id_contr from main.contracts) 
then 'Арендатор'
WHEN id_contr not in (select id_contr from main.leaseagreements) 
and id_contr in (select id_contr from main.contracts) 
then 'Подрядчик'
ELSE 'Арендатор / Подрядчик'
end as cp_work
from main.contragents
;    