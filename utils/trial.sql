-- CPTypes
select 
id::int as id,
nameType::text as name
FROM main.typecontragent;

-- Companies
-- select 
-- id_contr::text as id,
-- id_contr::text as inn,
-- "name_contr"::text as name,
-- contrAgentType::int as cptype_id,
-- email::text as email,
-- "ORGN"::text as ogrn,
-- "phone"::text as phone,
-- "address"::text as address,
-- CASE 
-- WHEN id_contr in (select id_contr from main.leaseagreements) 
-- and id_contr not in (select id_contr from main.contracts) 
-- then 'Арендатор'
-- WHEN id_contr not in (select id_contr from main.leaseagreements) 
-- and id_contr in (select id_contr from main.contracts) 
-- then 'Подрядчик'
-- ELSE 'Арендатор / Подрядчик'
-- end as cp_work
-- from main.contragents;

-- lease argeement
select  
"id_agreement"::int as id,
"id_contr"::text as cp_id,
"number_la"::text as number,
TRY_CAST(date_la as date) as date_from,
"date_signed"::text as date_signed,
"date_expired"::text as date_expired,
"Comment"::text as comments,
TRY_CAST("real_area" as double) as real_area,
TRY_CAST("calculated_area" as double) as calculated_area,
TRY_CAST("K_useful_area" as double) as k_useful_area
from main.leaseagreements
where pid is null;

-- sas

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
-- where pid is not null;


-- lttype


select
id_type::int as id,
"name_of_leaseType"::text as name 
from main.leasetermtyps;

-- lt

select
id_leaseTerms::int as id,
"id_agreement"::int as la_id,
"id_type"::int as lttype_id,
TRY_CAST("date_start" as date) as date_start,
TRY_CAST("date_finish" as date) as date_finish,
TRY_CAST("incude_VAT" as bool) as is_vat,
TRY_CAST("VAT" as double) as vat_rate,
TRY_CAST("value" as double) as la_value,
"date_accured"::text as pmt_terms,
"term_description"::text as term_description

from leaseterms;

-- corporate
-- owner
select
"id_company"::int as id, -- pk true
"inn_company"::text as inn,
"name_company"::text as name
from main.companies;

-- bankaccount
SELECT
"id_banAcc"::TEXT AS id,
"id_company"::INT AS owner_id,
TRY_CAST("bb" AS DOUBLE) AS bb,
"currency"::TEXT AS currency,
"name_bank"::TEXT AS bank_name,
"bank_bic"::TEXT AS bank_bic

FROM main.bankaccounts;

-- rp (rent premisses)
-- Property
SELECT
"id_property"::INT AS id,
"id_company"::INT AS owner_id,
"kadast_number"::TEXT AS kadast_number,
"name_property"::TEXT AS name,
"adress"::TEXT AS adress,
COALESCE(TRY_CAST("floors" AS INT), 0) AS total_floors,
COALESCE(TRY_CAST("property_totalArea" AS DOUBLE), 0.0) AS total_area,
"комменты"::text as comments -- text fields
FROM properties_building;

-- PremisType
SELECT
"id_premisType"::int as id,
"name_premisType"::text as name
from main.premistype;

-- PremisStatus
select 
"id_premisStatus"::int as id,
"name_premisStatus"::text as name
from main.premisstatus;



-- Floors
WITH a AS (
    SELECT
        "id_building"::INT AS property_id,
        "floor"::INT AS floor_number,
        COALESCE(TRY_CAST("areaTotal" AS DOUBLE), 0) AS area,
        "nameTexPlan"::TEXT AS name_techplan,
        "comment"::TEXT AS comment
    FROM main.floorarea
),

floors AS (
    SELECT DISTINCT
        f."id_property"::INT AS property_id,
        COALESCE(TRY_CAST(f."premis_floor" AS INT), 0) AS floor_number,
        a.area,
        a.name_techplan,
        a.comment
    FROM main.rentpremises AS f
    LEFT JOIN a
        ON a.property_id = f."id_property"::INT
       AND a.floor_number = COALESCE(TRY_CAST(f."premis_floor" AS INT), 0)
)

SELECT
    row_number() OVER (
        ORDER BY property_id, floor_number
    ) AS id,
    property_id,
    floor_number,
    area,
    name_techplan,
    comment
FROM floors
ORDER BY property_id, floor_number;

select * from main.rentpremises;

-- RentPremis
WITH a AS (
    SELECT
        "id_building"::INT AS property_id,
        "floor"::INT AS floor_number,
        COALESCE(TRY_CAST("areaTotal" AS DOUBLE), 0) AS area,
        "nameTexPlan"::TEXT AS name_techplan,
        "comment"::TEXT AS comment
    FROM main.floorarea
),

floors AS (
    SELECT DISTINCT
        f."id_property"::INT AS property_id,
        COALESCE(TRY_CAST(f."premis_floor" AS INT), 0) AS floor_number,
        a.area,
        a.name_techplan,
        a.comment
    FROM main.rentpremises AS f
    LEFT JOIN a
        ON a.property_id = f."id_property"::INT
       AND a.floor_number = COALESCE(TRY_CAST(f."premis_floor" AS INT), 0)
),

fin as (
SELECT
    row_number() OVER (
        ORDER BY property_id, floor_number
    ) AS id,
    property_id,
    floor_number,
    area,
    name_techplan,
    comment
FROM floors
ORDER BY property_id, floor_number)
select 
x.id,
x.name,
x.premistype_id,
f.id as floor_id,
x.area,
x.characteristic,
x.premisstatus_id
from(
select 
"id_premises"::int as id,
"id_premisStatus"::int as premisstatus_id,
"id_premisType"::int as premistype_id,
"id_property"::int as id_property,
COALESCE(TRY_CAST("premis_floor" as int),0) as floor_number,
"name_premis"::text as name,
"pid_id"::text as pid_id,
COALESCE(TRY_CAST("premis_area" as double),0) as area,
TRY_CAST("Special_Project" as int) as sp_id,
TRY_CAST("type_special_project" as int) as sptype_id,
"Characteristic" as characteristic
from main.rentpremises
) x
left join fin as f on f.property_id = x.id_property and f.floor_number = x.floor_number
;

-- PremissContact
select 
"id"::int as id,
"id_agreement"::int as sa_id,
"id_premises"::int as rentpremiss_id

from main.premisconntact;






