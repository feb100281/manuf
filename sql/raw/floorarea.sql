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
