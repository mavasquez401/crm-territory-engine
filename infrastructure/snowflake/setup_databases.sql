-- =====================================================
-- Snowflake Database Setup Script
-- =====================================================
-- Creates the three-tier database structure:
-- - RAW: Landing zone for source data
-- - STAGE: Intermediate transformation layer
-- - CORE: Final dimensional model

-- Use appropriate warehouse
USE WAREHOUSE COMPUTE_WH;

-- =====================================================
-- Create Databases
-- =====================================================

-- RAW Database: Landing zone for raw data from sources
CREATE DATABASE IF NOT EXISTS RAW
    COMMENT = 'Raw data landing zone from source systems';

-- STAGE Database: Intermediate transformation layer
CREATE DATABASE IF NOT EXISTS STAGE
    COMMENT = 'Staging area for data transformations';

-- CORE Database: Final dimensional model (star schema)
CREATE DATABASE IF NOT EXISTS CORE
    COMMENT = 'Core dimensional model for analytics';

-- =====================================================
-- Verify Database Creation
-- =====================================================

SHOW DATABASES LIKE 'RAW';
SHOW DATABASES LIKE 'STAGE';
SHOW DATABASES LIKE 'CORE';

-- =====================================================
-- Set Default Database Sizes
-- =====================================================

-- RAW database can use larger warehouse for bulk loads
ALTER DATABASE RAW SET DATA_RETENTION_TIME_IN_DAYS = 7;

-- STAGE database for transformations
ALTER DATABASE STAGE SET DATA_RETENTION_TIME_IN_DAYS = 3;

-- CORE database for production analytics
ALTER DATABASE CORE SET DATA_RETENTION_TIME_IN_DAYS = 30;

-- =====================================================
-- Success Message
-- =====================================================

SELECT 'Databases created successfully: RAW, STAGE, CORE' AS status;

