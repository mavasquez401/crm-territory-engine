-- =====================================================
-- Snowflake Role-Based Access Control Setup
-- =====================================================
-- Creates roles with appropriate permissions for different user types

USE WAREHOUSE COMPUTE_WH;

-- =====================================================
-- Create Custom Roles
-- =====================================================

-- DATA_ENGINEER: Full access to all databases for ETL operations
CREATE ROLE IF NOT EXISTS DATA_ENGINEER
    COMMENT = 'Role for data engineers with full ETL access';

-- CRM_ANALYST: Read access to CORE database for analytics
CREATE ROLE IF NOT EXISTS CRM_ANALYST
    COMMENT = 'Role for CRM analysts with read access to CORE';

-- SALES_LEADERSHIP: Restricted read access via secure views only
CREATE ROLE IF NOT EXISTS SALES_LEADERSHIP
    COMMENT = 'Role for sales leadership with restricted access';

-- =====================================================
-- Grant Warehouse Usage
-- =====================================================

-- All roles need warehouse access
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE DATA_ENGINEER;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE CRM_ANALYST;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE SALES_LEADERSHIP;

-- =====================================================
-- DATA_ENGINEER Permissions (Full Access)
-- =====================================================

-- RAW database permissions
GRANT ALL ON DATABASE RAW TO ROLE DATA_ENGINEER;
GRANT ALL ON ALL SCHEMAS IN DATABASE RAW TO ROLE DATA_ENGINEER;
GRANT ALL ON ALL TABLES IN DATABASE RAW TO ROLE DATA_ENGINEER;
GRANT ALL ON FUTURE TABLES IN DATABASE RAW TO ROLE DATA_ENGINEER;

-- STAGE database permissions
GRANT ALL ON DATABASE STAGE TO ROLE DATA_ENGINEER;
GRANT ALL ON ALL SCHEMAS IN DATABASE STAGE TO ROLE DATA_ENGINEER;
GRANT ALL ON ALL TABLES IN DATABASE STAGE TO ROLE DATA_ENGINEER;
GRANT ALL ON FUTURE TABLES IN DATABASE STAGE TO ROLE DATA_ENGINEER;

-- CORE database permissions
GRANT ALL ON DATABASE CORE TO ROLE DATA_ENGINEER;
GRANT ALL ON ALL SCHEMAS IN DATABASE CORE TO ROLE DATA_ENGINEER;
GRANT ALL ON ALL TABLES IN DATABASE CORE TO ROLE DATA_ENGINEER;
GRANT ALL ON FUTURE TABLES IN DATABASE CORE TO ROLE DATA_ENGINEER;

-- =====================================================
-- CRM_ANALYST Permissions (Read Access to CORE)
-- =====================================================

-- CORE database read permissions
GRANT USAGE ON DATABASE CORE TO ROLE CRM_ANALYST;
GRANT USAGE ON ALL SCHEMAS IN DATABASE CORE TO ROLE CRM_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA CORE.dimensional TO ROLE CRM_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA CORE.segmentation_rules TO ROLE CRM_ANALYST;
GRANT SELECT ON FUTURE TABLES IN SCHEMA CORE.dimensional TO ROLE CRM_ANALYST;
GRANT SELECT ON FUTURE TABLES IN SCHEMA CORE.segmentation_rules TO ROLE CRM_ANALYST;

-- =====================================================
-- SALES_LEADERSHIP Permissions (Secure Views Only)
-- =====================================================

-- CORE database usage (views only)
GRANT USAGE ON DATABASE CORE TO ROLE SALES_LEADERSHIP;
GRANT USAGE ON SCHEMA CORE.dimensional TO ROLE SALES_LEADERSHIP;

-- Note: Specific view permissions will be granted in create_secure_views.sql

-- =====================================================
-- Role Hierarchy
-- =====================================================

-- SYSADMIN can manage all custom roles
GRANT ROLE DATA_ENGINEER TO ROLE SYSADMIN;
GRANT ROLE CRM_ANALYST TO ROLE SYSADMIN;
GRANT ROLE SALES_LEADERSHIP TO ROLE SYSADMIN;

-- Optional: Create role hierarchy
-- GRANT ROLE CRM_ANALYST TO ROLE DATA_ENGINEER;

-- =====================================================
-- Verify Role Creation
-- =====================================================

SHOW ROLES LIKE 'DATA_ENGINEER';
SHOW ROLES LIKE 'CRM_ANALYST';
SHOW ROLES LIKE 'SALES_LEADERSHIP';

-- Show grants for each role
SHOW GRANTS TO ROLE DATA_ENGINEER;
SHOW GRANTS TO ROLE CRM_ANALYST;
SHOW GRANTS TO ROLE SALES_LEADERSHIP;

-- =====================================================
-- Success Message
-- =====================================================

SELECT 'Roles created successfully: DATA_ENGINEER, CRM_ANALYST, SALES_LEADERSHIP' AS status;


