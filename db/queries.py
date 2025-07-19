GET_COUNTRY_GROUPS = """
SELECT name FROM country_groups;
"""

GET_COUNTRY_MEMBERS = """
SELECT c.name_ru
FROM countries c
JOIN country_group_membership m ON c.id = m.country_id
JOIN country_groups g ON m.country_group_id = g.id
WHERE g.name = %s;
"""

GET_MAX_MONTH = """
SELECT MAX(month)
FROM data d
JOIN countries c ON d.country_id = c.id
JOIN regions r ON d.region_id = r.id
WHERE c.name_ru = ANY(%s)
AND r.name = %s
AND d.year = %s;
"""

GET_MAX_MONTH_EAEU = """
SELECT MAX(month)
FROM data d
JOIN countries c ON d.country_id = c.id
JOIN regions r ON d.region_id = r.id
WHERE c.name_ru = 'Россия'
AND r.name = %s
AND d.year = %s;
"""

GET_MAX_MONTH_WITHOUT_EAEU = """
SELECT MAX(month)
FROM data d
JOIN countries c ON d.country_id = c.id
JOIN regions r ON d.region_id = r.id
WHERE c.name_ru = 'Китай'
AND r.name = %s
AND d.year = %s;
"""

GET_TN_VEDS_BY_CATEGORY = """
SELECT v.code
FROM tn_veds v
JOIN tn_ved_category_map m ON v.id = m.tn_ved_id
JOIN tn_ved_categories c ON m.tn_ved_category_id = c.id
WHERE c.name = %s;
"""

GET_TN_VEDS_BY_DIGIT = """
SELECT code FROM tn_veds WHERE digit = %s;
"""

FETCH_TRADE_DATA = """
SELECT 
    SUM(d.export_tonn) AS total_ex_tonn,
    SUM(d.export_units) AS total_ex_ad_un,
    SUM(d.export_value) AS total_ex_value,
    SUM(d.import_tonn) AS total_im_tonn,
    SUM(d.import_units) AS total_im_ad_un,
    SUM(d.import_value) AS total_im_value,
    c.name_ru AS country_name,
    r.name AS region_name,
    tv.code AS tn_ved_code,
    tv.name AS tn_ved_name,
    tv.measure AS tn_ved_measure,
    d.year,
    d.month
FROM data d
JOIN countries c ON d.country_id = c.id
JOIN regions r ON d.region_id = r.id
JOIN tn_veds tv ON d.tn_ved_id = tv.id
WHERE c.name_ru = ANY(%s)
AND r.name = %s
AND d.year BETWEEN %s AND %s
AND d.month = ANY(%s)
AND tv.digit = %s
AND tv.code = ANY(%s)
GROUP BY c.name_ru, r.name, tv.code, tv.name, tv.measure, d.year, d.month;
"""

FETCH_TRADE_DATA_CATEGORY = """
WITH grouped AS (
    SELECT
        LEFT(tv.code, %s) AS tn_ved_code,
        c.name_ru AS country_name,
        r.name AS region_name,
        d.year,
        d.month,
        MAX(tv.measure) AS tn_ved_measure,
        SUM(d.export_tonn) AS total_ex_tonn,
        SUM(d.export_units) AS total_ex_ad_un,
        SUM(d.export_value) AS total_ex_value,
        SUM(d.import_tonn) AS total_im_tonn,
        SUM(d.import_units) AS total_im_ad_un,
        SUM(d.import_value) AS total_im_value
    FROM data d
    JOIN countries c ON d.country_id = c.id
    JOIN regions r ON d.region_id = r.id
    JOIN tn_veds tv ON d.tn_ved_id = tv.id
    WHERE c.name_ru = ANY(%s)
      AND r.name = %s
      AND d.year BETWEEN %s AND %s
      AND d.month = ANY(%s)
      AND tv.digit = %s
      AND tv.code = ANY(%s)
    GROUP BY c.name_ru, LEFT(tv.code, %s), r.name, d.year, d.month
)

SELECT
    g.total_ex_tonn,
    g.total_ex_ad_un,
    g.total_ex_value,
    g.total_im_tonn,
    g.total_im_ad_un,
    g.total_im_value,
    g.country_name,
    g.region_name,
    g.tn_ved_code,
    tv4.name AS tn_ved_name,
    g.tn_ved_measure AS tn_ved_measure,
    g.year,
    g.month
FROM grouped g
JOIN tn_veds tv4
  ON tv4.code = g.tn_ved_code
 AND tv4.digit = %s;
"""