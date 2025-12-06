-- =====================================================
-- Snowflake Table Creation Script
-- =====================================================
-- Creates tables in RAW, STAGE, and CORE databases

USE WAREHOUSE COMPUTE_WH;

-- =====================================================
-- RAW Layer Tables
-- =====================================================

USE DATABASE RAW;
USE SCHEMA client_hierarchy;

-- Raw clients table (matches CSV structure)
CREATE TABLE IF NOT EXISTS CLIENTS (
    client_id INTEGER NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    segment VARCHAR(100),
    parent_org VARCHAR(255),
    advisor_email VARCHAR(255),
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_file VARCHAR(500),
    PRIMARY KEY (client_id)
) COMMENT = 'Raw client data from source systems';

-- =====================================================
-- STAGE Layer Tables
-- =====================================================

USE DATABASE STAGE;
USE SCHEMA staging;

-- Staging table for client transformations
CREATE TABLE IF NOT EXISTS CLIENTS_STAGING (
    client_id INTEGER NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    segment VARCHAR(100),
    parent_org VARCHAR(255),
    advisor_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    processed_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (client_id)
) COMMENT = 'Staging area for client data transformations';

-- =====================================================
-- CORE Layer Tables (Dimensional Model)
-- =====================================================

USE DATABASE CORE;
USE SCHEMA dimensional;

-- CLIENT_DIM: Client dimension table
CREATE TABLE IF NOT EXISTS CLIENT_DIM (
    client_key INTEGER NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    segment VARCHAR(100),
    parent_org VARCHAR(255),
    primary_advisor_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE DEFAULT CURRENT_DATE(),
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (client_key)
) COMMENT = 'Client dimension - master client data';

-- TERRITORY_DIM: Territory dimension table
CREATE TABLE IF NOT EXISTS TERRITORY_DIM (
    territory_id VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    segment VARCHAR(100) NOT NULL,
    owner_role VARCHAR(100),
    description VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (territory_id)
) COMMENT = 'Territory dimension - territory definitions';

-- ASSIGNMENTS_FACT: Client-territory assignments fact table
CREATE TABLE IF NOT EXISTS ASSIGNMENTS_FACT (
    assignment_id INTEGER AUTOINCREMENT,
    client_key INTEGER NOT NULL,
    territory_id VARCHAR(50) NOT NULL,
    primary_advisor_email VARCHAR(255),
    assignment_type VARCHAR(50) DEFAULT 'PRIMARY',
    is_current BOOLEAN DEFAULT TRUE,
    effective_date DATE DEFAULT CURRENT_DATE(),
    end_date DATE,
    assigned_by_rule VARCHAR(100),
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (assignment_id),
    FOREIGN KEY (client_key) REFERENCES CLIENT_DIM(client_key),
    FOREIGN KEY (territory_id) REFERENCES TERRITORY_DIM(territory_id)
) COMMENT = 'Assignment fact table - client-territory relationships';

-- =====================================================
-- Segmentation Rules Tables
-- =====================================================

USE SCHEMA segmentation_rules;

-- Whitelist table for explicit assignments
CREATE TABLE IF NOT EXISTS WHITELIST (
    whitelist_id INTEGER AUTOINCREMENT,
    client_key INTEGER NOT NULL,
    territory_id VARCHAR(50) NOT NULL,
    reason VARCHAR(500),
    created_by VARCHAR(100),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (whitelist_id)
) COMMENT = 'Whitelist for explicit territory assignments';

-- Blacklist table for blocked assignments
CREATE TABLE IF NOT EXISTS BLACKLIST (
    blacklist_id INTEGER AUTOINCREMENT,
    client_key INTEGER NOT NULL,
    territory_id VARCHAR(50) NOT NULL,
    reason VARCHAR(500),
    created_by VARCHAR(100),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (blacklist_id)
) COMMENT = 'Blacklist for blocked territory assignments';

-- =====================================================
-- Create Indexes for Performance
-- =====================================================

USE DATABASE CORE;
USE SCHEMA dimensional;

-- Indexes on ASSIGNMENTS_FACT for common queries
CREATE INDEX IF NOT EXISTS idx_assignments_client 
    ON ASSIGNMENTS_FACT(client_key);

CREATE INDEX IF NOT EXISTS idx_assignments_territory 
    ON ASSIGNMENTS_FACT(territory_id);

CREATE INDEX IF NOT EXISTS idx_assignments_current 
    ON ASSIGNMENTS_FACT(is_current, effective_date);

-- =====================================================
-- Verify Table Creation
-- =====================================================

SHOW TABLES IN DATABASE RAW;
SHOW TABLES IN DATABASE STAGE;
SHOW TABLES IN DATABASE CORE;

-- =====================================================
-- Success Message
-- =====================================================

SELECT 'Tables created successfully in RAW, STAGE, and CORE databases' AS status;

