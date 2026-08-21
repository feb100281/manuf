select
    id_leaseTerms::int as id,
    "id_agreement"::int as sa_id,
    "id_type"::int as lttypes_id,
    TRY_CAST("date_start" as date) as date_start,
    TRY_CAST("date_finish" as date) as date_finish,
    TRY_CAST("incude_VAT" as bool) as is_vat,
    TRY_CAST("VAT" as double) as vat_rate,
    TRY_CAST("value" as double) as la_value,
    "date_accured"::text as pmt_terms,
    "term_description"::text as term_description
    from leaseterms;