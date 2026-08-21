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