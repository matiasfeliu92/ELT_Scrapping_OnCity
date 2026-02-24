{{ config(materialized='table') }}

with raw_source as (
    select * from {{ source('raw_data', 'scraping_data') }}
)

select
    scraped_at,
    product_id,
    retailer,
    raw_data->>'sku' as product_sku,
    raw_data->>'name' as product_name,
    lower(raw_data->>'brand') as brand,
    raw_data->>'main_category' as main_category,
    raw_data->>'sub_category' as sub_category,
    raw_data->>'list_price' as list_price_raw,
    raw_data->>'cash_price' as cash_price_raw,
    (raw_data->>'stock')::boolean as is_in_stock,
    raw_data->>'link' as product_url,
    raw_data->'installments'->>'Opcion 1' as installment_option_1,
    raw_data->'installments'->>'Opcion 2' as installment_option_2
from raw_source