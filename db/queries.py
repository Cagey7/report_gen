# db/queries.py

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

GET_TN_VEDS_BY_CATEGORY = """
SELECT v.code
FROM tn_veds v
JOIN tn_ved_category_map m ON v.id = m.tn_ved_id
JOIN tn_ved_categories c ON m.tn_ved_category_id = c.id
WHERE c.name = %s AND v.digit = %s;
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
    %s AS country_name,
    r.name AS region_name,
    tv.code AS tn_ved_code,
    tv.name AS tn_ved_name,
    tv.measure AS tn_ved_measure,
    d.year
FROM data d
JOIN countries c ON d.country_id = c.id
JOIN regions r ON d.region_id = r.id
JOIN tn_veds tv ON d.tn_ved_id = tv.id
WHERE c.name_ru = ANY(%s)
AND r.name = %s
AND d.year = %s
AND d.month = ANY(%s)
AND tv.digit = %s
AND tv.code = ANY(%s)
GROUP BY r.name, tv.code, tv.name, tv.measure, d.year;
"""
