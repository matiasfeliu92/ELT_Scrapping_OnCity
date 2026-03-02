SELECT * FROM "raw".scraping_data
ORDER BY id ASC 


SELECT * FROM "catalog".product_catalog


SELECT
	catal.product_id,
	catal.brand,
	catal.model,
	catal.main_category,
	catal.sub_category,
	catal.retailer,
	catal.link,
	scraped.scraped_at as updated_at,
	scraped.raw_data ->> 'sku' as scraped_sku,
	scraped.raw_data ->> 'name' as scraped_name,
	scraped.raw_data ->> 'main_category' as scraped_main_category,
	scraped.raw_data ->> 'sub_category' as scraped_sub_category,
	scraped.raw_data ->> 'list_price' as scraped_list_price,
	scraped.raw_data ->> 'cash_price' as scraped_cash_price,
	scraped.raw_data ->> 'stock' as scraped_stock
FROM
	"raw".scraping_data AS scraped
JOIN
	"catalog".product_catalog AS catal 
	ON scraped.product_id = catal.product_id 
	and scraped.retailer = catal.retailer


SELECT DISTINCT ON (scraped.product_id, scraped.retailer)
    catal.product_id,
    catal.brand,
    catal.model,
    catal.main_category,
    catal.sub_category,
    catal.retailer,
    catal.link,
    scraped.scraped_at AS updated_at,
    scraped.raw_data ->> 'sku' AS scraped_sku,
    scraped.raw_data ->> 'name' AS scraped_name,
    scraped.raw_data ->> 'main_category' AS scraped_main_category,
    scraped.raw_data ->> 'sub_category' AS scraped_sub_category,
    scraped.raw_data ->> 'list_price' AS scraped_list_price,
    scraped.raw_data ->> 'cash_price' AS scraped_cash_price,
    scraped.raw_data ->> 'stock' AS scraped_stock
FROM
    raw.scraping_data AS scraped
JOIN
    catalog.product_catalog AS catal 
    ON scraped.product_id = catal.product_id 
    AND scraped.retailer = catal.retailer
ORDER BY
    scraped.product_id,
    scraped.retailer,
    scraped.scraped_at DESC;


SELECT *
FROM (
    SELECT
        raw.scraping_data.id,
        raw.scraping_data.scraped_at,
        raw.scraping_data.product_id,
        raw.scraping_data.retailer,
        raw.scraping_data.raw_data,
        ROW_NUMBER() OVER (
            PARTITION BY raw.scraping_data.product_id,
                         raw.scraping_data.retailer
            ORDER BY raw.scraping_data.scraped_at DESC
        ) AS rn
    FROM raw.scraping_data
) AS anon_1
WHERE rn = 1;




WITH ranked AS (
    SELECT
        catal.product_id,
        catal.brand,
        catal.model,
        catal.main_category,
        catal.sub_category,
        catal.retailer,
        catal.link,
        scraped.scraped_at AS updated_at,
        scraped.raw_data ->> 'sku' AS scraped_sku,
        scraped.raw_data ->> 'name' AS scraped_name,
        scraped.raw_data ->> 'main_category' AS scraped_main_category,
        scraped.raw_data ->> 'sub_category' AS scraped_sub_category,
        scraped.raw_data ->> 'list_price' AS scraped_list_price,
        scraped.raw_data ->> 'cash_price' AS scraped_cash_price,
        scraped.raw_data ->> 'stock' AS scraped_stock,
        ROW_NUMBER() OVER (
            PARTITION BY scraped.product_id, scraped.retailer
            ORDER BY scraped.scraped_at DESC
        ) AS rn
    FROM raw.scraping_data AS scraped
    JOIN catalog.product_catalog AS catal
        ON scraped.product_id = catal.product_id
        AND scraped.retailer = catal.retailer
)
SELECT *
FROM ranked
WHERE rn = 1;




WITH ranked AS (
    SELECT
        catal.product_id,
        catal.brand,
        catal.model,
        catal.main_category,
        catal.sub_category,
        catal.retailer,
        catal.link,
        scraped.scraped_at AS updated_at,
        scraped.raw_data ->> 'sku' AS scraped_sku,
        scraped.raw_data ->> 'name' AS scraped_name,
        scraped.raw_data ->> 'main_category' AS scraped_main_category,
        scraped.raw_data ->> 'sub_category' AS scraped_sub_category,
        scraped.raw_data ->> 'list_price' AS scraped_list_price,
        scraped.raw_data ->> 'cash_price' AS scraped_cash_price,
        scraped.raw_data ->> 'stock' AS scraped_stock,
        ROW_NUMBER() OVER (
            PARTITION BY scraped.product_id, scraped.retailer
            ORDER BY scraped.scraped_at DESC
        ) AS rn
    FROM raw.scraping_data AS scraped
    JOIN catalog.product_catalog AS catal
        ON scraped.product_id = catal.product_id
        AND scraped.retailer = catal.retailer
)
SELECT *
FROM ranked
WHERE rn != 1;




WITH price_lags AS (
    SELECT 
        raw_data->>'sku' as sku,
        (raw_data->>'cash_price')::text as price_str,
        scraped_at,
        LAG(raw_data->>'cash_price') OVER (
            PARTITION BY raw_data->>'sku' 
            ORDER BY scraped_at ASC
        ) as previous_price_str
    FROM raw.scraping_data
)
SELECT 
    sku,
    COUNT(*) as total_changes
FROM price_lags
WHERE price_str IS DISTINCT FROM previous_price_str 
  AND previous_price_str IS NOT NULL
GROUP BY sku;