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