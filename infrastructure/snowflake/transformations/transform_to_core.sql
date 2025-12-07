-- =====================================================
-- Transform RAW to CORE Dimensional Model
-- =====================================================
-- SQL equivalent of pandas transformations
-- Builds CLIENT_DIM, TERRITORY_DIM, and ASSIGNMENTS_FACT

USE WAREHOUSE COMPUTE_WH;

-- =====================================================
-- Step 1: Load RAW to STAGE
-- =====================================================

USE DATABASE STAGE;
USE SCHEMA staging;

-- Clear staging table
TRUNCATE TABLE IF EXISTS CLIENTS_STAGING;

-- Load from RAW to STAGE
INSERT INTO CLIENTS_STAGING (
    client_id,
    client_name,
    region,
    segment,
    parent_org,
    advisor_email,
    is_active
)
SELECT 
    client_id,
    client_name,
    region,
    segment,
    parent_org,
    advisor_email,
    TRUE AS is_active
FROM RAW.client_hierarchy.CLIENTS;

-- =====================================================
-- Step 2: Build CLIENT_DIM
-- =====================================================

USE DATABASE CORE;
USE SCHEMA dimensional;

-- Merge into CLIENT_DIM (upsert pattern)
MERGE INTO CLIENT_DIM AS target
USING (
    SELECT 
        client_id AS client_key,
        client_name,
        region,
        segment,
        parent_org,
        advisor_email AS primary_advisor_email,
        TRUE AS is_active,
        CURRENT_DATE() AS effective_date,
        NULL AS end_date,
        TRUE AS is_current
    FROM STAGE.staging.CLIENTS_STAGING
) AS source
ON target.client_key = source.client_key
WHEN MATCHED THEN
    UPDATE SET
        client_name = source.client_name,
        region = source.region,
        segment = source.segment,
        parent_org = source.parent_org,
        primary_advisor_email = source.primary_advisor_email,
        is_active = source.is_active,
        updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (
        client_key,
        client_name,
        region,
        segment,
        parent_org,
        primary_advisor_email,
        is_active,
        effective_date,
        end_date,
        is_current,
        created_at,
        updated_at
    )
    VALUES (
        source.client_key,
        source.client_name,
        source.region,
        source.segment,
        source.parent_org,
        source.primary_advisor_email,
        source.is_active,
        source.effective_date,
        source.end_date,
        source.is_current,
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP()
    );

-- =====================================================
-- Step 3: Build TERRITORY_DIM
-- =====================================================

-- Merge into TERRITORY_DIM
MERGE INTO TERRITORY_DIM AS target
USING (
    SELECT DISTINCT
        CONCAT(
            UPPER(LEFT(region, 3)),
            '_',
            UPPER(LEFT(segment, 3))
        ) AS territory_id,
        region,
        segment,
        'Sales Rep' AS owner_role,
        CONCAT(region, ' - ', segment) AS description,
        TRUE AS is_active
    FROM STAGE.staging.CLIENTS_STAGING
    WHERE region IS NOT NULL AND segment IS NOT NULL
) AS source
ON target.territory_id = source.territory_id
WHEN MATCHED THEN
    UPDATE SET
        region = source.region,
        segment = source.segment,
        owner_role = source.owner_role,
        description = source.description,
        is_active = source.is_active,
        updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (
        territory_id,
        region,
        segment,
        owner_role,
        description,
        is_active,
        created_at,
        updated_at
    )
    VALUES (
        source.territory_id,
        source.region,
        source.segment,
        source.owner_role,
        source.description,
        source.is_active,
        CURRENT_TIMESTAMP(),
        CURRENT_TIMESTAMP()
    );

-- =====================================================
-- Step 4: Build ASSIGNMENTS_FACT
-- =====================================================

-- Mark old assignments as not current
UPDATE ASSIGNMENTS_FACT
SET 
    is_current = FALSE,
    end_date = CURRENT_DATE(),
    updated_at = CURRENT_TIMESTAMP()
WHERE is_current = TRUE;

-- Insert new assignments
INSERT INTO ASSIGNMENTS_FACT (
    client_key,
    territory_id,
    primary_advisor_email,
    assignment_type,
    is_current,
    effective_date,
    assigned_by_rule,
    confidence_score,
    created_at,
    updated_at
)
SELECT 
    c.client_key,
    t.territory_id,
    c.primary_advisor_email,
    'PRIMARY' AS assignment_type,
    TRUE AS is_current,
    CURRENT_DATE() AS effective_date,
    'RegionRule' AS assigned_by_rule,
    95.0 AS confidence_score,
    CURRENT_TIMESTAMP() AS created_at,
    CURRENT_TIMESTAMP() AS updated_at
FROM CLIENT_DIM c
INNER JOIN TERRITORY_DIM t
    ON c.region = t.region
    AND c.segment = t.segment
WHERE c.is_active = TRUE
    AND t.is_active = TRUE;

-- =====================================================
-- Step 5: Data Quality Checks
-- =====================================================

-- Check row counts
SELECT 'CLIENT_DIM' AS table_name, COUNT(*) AS row_count FROM CLIENT_DIM
UNION ALL
SELECT 'TERRITORY_DIM', COUNT(*) FROM TERRITORY_DIM
UNION ALL
SELECT 'ASSIGNMENTS_FACT', COUNT(*) FROM ASSIGNMENTS_FACT WHERE is_current = TRUE;

-- Check for orphaned assignments
SELECT 
    'Orphaned Assignments' AS check_name,
    COUNT(*) AS issue_count
FROM ASSIGNMENTS_FACT a
LEFT JOIN CLIENT_DIM c ON a.client_key = c.client_key
WHERE c.client_key IS NULL AND a.is_current = TRUE;

-- Check for unassigned clients
SELECT 
    'Unassigned Clients' AS check_name,
    COUNT(*) AS issue_count
FROM CLIENT_DIM c
LEFT JOIN ASSIGNMENTS_FACT a 
    ON c.client_key = a.client_key 
    AND a.is_current = TRUE
WHERE a.client_key IS NULL AND c.is_active = TRUE;

-- =====================================================
-- Success Message
-- =====================================================

SELECT 'Transformation to CORE complete: CLIENT_DIM, TERRITORY_DIM, ASSIGNMENTS_FACT' AS status;


