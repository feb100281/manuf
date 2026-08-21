-- CREATE OR REPLACE VIEW bankaccounts AS
-- SELECT *
-- FROM read_parquet('/Users/pavelustenko/manuf/data/parquet/raw/bankaccounts.parquet');

SELECT
    "id_banAcc"::TEXT AS id,
    "id_company"::INT AS owner_id,
    TRY_CAST("bb" AS DOUBLE) AS bb,
    "currency"::TEXT AS currency,
    "name_bank"::TEXT AS bank_name,
    "bank_bic"::TEXT AS bank_bic
    FROM main.bankaccounts;