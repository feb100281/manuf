select
"id_company"::int as id, -- pk true
"inn_company"::text as inn,
"name_company"::text as name
from main.companies;