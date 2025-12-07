-- =====================================================
-- Snowflake Schema Setup Script
-- =====================================================
-- Creates schemas within each database for organizing tables

USE WAREHOUSE COMPUTE_WH;

-- =====================================================
-- RAW Database Schemas
-- =====================================================

USE DATABASE RAW;

-- Schema for client hierarchy data
CREATE SCHEMA IF NOT EXISTS client_hierarchy
    COMMENT = 'Raw client organizational hierarchy data';

-- Schema for territory definitions
CREATE SCHEMA IF NOT EXISTS territories
    COMMENT = 'Raw territory configuration data';

-- Schema for assignment data
CREATE SCHEMA IF NOT EXISTS assignments
    COMMENT = 'Raw client-territory assignment data';

-- =====================================================
-- STAGE Database Schemas
-- =====================================================

USE DATABASE STAGE;

-- Schema for staging transformations
CREATE SCHEMA IF NOT EXISTS staging
    COMMENT = 'Staging area for data transformations';

-- =====================================================
-- CORE Database Schemas
-- =====================================================

USE DATABASE CORE;

-- Schema for dimensional model
CREATE SCHEMA IF NOT EXISTS dimensional
    COMMENT = 'Star schema dimensional model';

-- Schema for segmentation rules
CREATE SCHEMA IF NOT EXISTS segmentation_rules
    COMMENT = 'Territory segmentation and assignment rules';

-- =====================================================
-- Verify Schema Creation
-- =====================================================

SHOW SCHEMAS IN DATABASE RAW;
SHOW SCHEMAS IN DATABASE STAGE;
SHOW SCHEMAS IN DATABASE CORE;

-- =====================================================
-- Success Message
-- =====================================================

SELECT 'Schemas created successfully in RAW, STAGE, and CORE databases' AS status;


