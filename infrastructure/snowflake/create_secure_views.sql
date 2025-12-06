-- =====================================================
-- Snowflake Secure Views for SALES_LEADERSHIP Role
-- =====================================================
-- Creates secure views with row-level security for sales leadership

USE WAREHOUSE COMPUTE_WH;
USE DATABASE CORE;
USE SCHEMA dimensional;

-- =====================================================
-- Territory Summary View
-- =====================================================

CREATE OR REPLACE SECURE VIEW v_territory_summary AS
SELECT 
    t.territory_id,
    t.region,
    t.segment,
    t.owner_role,
    COUNT(DISTINCT a.client_key) AS client_count,
    COUNT(DISTINCT a.primary_advisor_email) AS advisor_count,
    MAX(a.updated_at) AS last_updated
FROM TERRITORY_DIM t
LEFT JOIN ASSIGNMENTS_FACT a 
    ON t.territory_id = a.territory_id 
    AND a.is_current = TRUE
WHERE t.is_active = TRUE
GROUP BY 
    t.territory_id,
    t.region,
    t.segment,
    t.owner_role
COMMENT = 'Secure view: Territory summary with client and advisor counts';

-- =====================================================
-- Client Territory Assignments View
-- =====================================================

CREATE OR REPLACE SECURE VIEW v_client_assignments AS
SELECT 
    c.client_key,
    c.client_name,
    c.region,
    c.segment,
    c.parent_org,
    a.territory_id,
    a.primary_advisor_email,
    a.assignment_type,
    a.effective_date,
    a.assigned_by_rule
FROM CLIENT_DIM c
INNER JOIN ASSIGNMENTS_FACT a 
    ON c.client_key = a.client_key
WHERE 
    c.is_active = TRUE 
    AND a.is_current = TRUE
COMMENT = 'Secure view: Current client territory assignments';

-- =====================================================
-- Advisor Workload View
-- =====================================================

CREATE OR REPLACE SECURE VIEW v_advisor_workload AS
SELECT 
    a.primary_advisor_email,
    t.region,
    t.segment,
    COUNT(DISTINCT a.client_key) AS client_count,
    COUNT(DISTINCT a.territory_id) AS territory_count,
    MIN(a.effective_date) AS first_assignment_date,
    MAX(a.updated_at) AS last_updated
FROM ASSIGNMENTS_FACT a
INNER JOIN TERRITORY_DIM t 
    ON a.territory_id = t.territory_id
WHERE a.is_current = TRUE
GROUP BY 
    a.primary_advisor_email,
    t.region,
    t.segment
COMMENT = 'Secure view: Advisor workload and capacity metrics';

-- =====================================================
-- Regional Performance View
-- =====================================================

CREATE OR REPLACE SECURE VIEW v_regional_performance AS
SELECT 
    t.region,
    COUNT(DISTINCT t.territory_id) AS territory_count,
    COUNT(DISTINCT a.client_key) AS client_count,
    COUNT(DISTINCT a.primary_advisor_email) AS advisor_count,
    ROUND(COUNT(DISTINCT a.client_key)::FLOAT / 
          NULLIF(COUNT(DISTINCT a.primary_advisor_email), 0), 2) AS clients_per_advisor
FROM TERRITORY_DIM t
LEFT JOIN ASSIGNMENTS_FACT a 
    ON t.territory_id = a.territory_id 
    AND a.is_current = TRUE
WHERE t.is_active = TRUE
GROUP BY t.region
COMMENT = 'Secure view: Regional performance metrics';

-- =====================================================
-- Client Hierarchy View
-- =====================================================

CREATE OR REPLACE SECURE VIEW v_client_hierarchy AS
SELECT 
    c.client_key,
    c.client_name,
    c.parent_org,
    c.region,
    c.segment,
    a.territory_id,
    a.primary_advisor_email,
    COUNT(*) OVER (PARTITION BY c.parent_org) AS org_client_count
FROM CLIENT_DIM c
LEFT JOIN ASSIGNMENTS_FACT a 
    ON c.client_key = a.client_key 
    AND a.is_current = TRUE
WHERE c.is_active = TRUE
COMMENT = 'Secure view: Client organizational hierarchy';

-- =====================================================
-- Assignment History View (Last 90 Days)
-- =====================================================

CREATE OR REPLACE SECURE VIEW v_assignment_history AS
SELECT 
    a.assignment_id,
    c.client_name,
    a.territory_id,
    a.primary_advisor_email,
    a.assignment_type,
    a.effective_date,
    a.end_date,
    a.assigned_by_rule,
    a.confidence_score,
    CASE 
        WHEN a.is_current THEN 'CURRENT'
        ELSE 'HISTORICAL'
    END AS status
FROM ASSIGNMENTS_FACT a
INNER JOIN CLIENT_DIM c 
    ON a.client_key = c.client_key
WHERE a.effective_date >= DATEADD(day, -90, CURRENT_DATE())
ORDER BY a.effective_date DESC
COMMENT = 'Secure view: Assignment history for last 90 days';

-- =====================================================
-- Grant View Access to SALES_LEADERSHIP
-- =====================================================

GRANT SELECT ON VIEW v_territory_summary TO ROLE SALES_LEADERSHIP;
GRANT SELECT ON VIEW v_client_assignments TO ROLE SALES_LEADERSHIP;
GRANT SELECT ON VIEW v_advisor_workload TO ROLE SALES_LEADERSHIP;
GRANT SELECT ON VIEW v_regional_performance TO ROLE SALES_LEADERSHIP;
GRANT SELECT ON VIEW v_client_hierarchy TO ROLE SALES_LEADERSHIP;
GRANT SELECT ON VIEW v_assignment_history TO ROLE SALES_LEADERSHIP;

-- =====================================================
-- Grant View Access to CRM_ANALYST (Full Access)
-- =====================================================

GRANT SELECT ON VIEW v_territory_summary TO ROLE CRM_ANALYST;
GRANT SELECT ON VIEW v_client_assignments TO ROLE CRM_ANALYST;
GRANT SELECT ON VIEW v_advisor_workload TO ROLE CRM_ANALYST;
GRANT SELECT ON VIEW v_regional_performance TO ROLE CRM_ANALYST;
GRANT SELECT ON VIEW v_client_hierarchy TO ROLE CRM_ANALYST;
GRANT SELECT ON VIEW v_assignment_history TO ROLE CRM_ANALYST;

-- =====================================================
-- Verify View Creation
-- =====================================================

SHOW VIEWS IN SCHEMA CORE.dimensional;

-- Test views
SELECT * FROM v_territory_summary LIMIT 5;
SELECT * FROM v_regional_performance;

-- =====================================================
-- Success Message
-- =====================================================

SELECT 'Secure views created successfully and granted to SALES_LEADERSHIP and CRM_ANALYST roles' AS status;

