#!/bin/bash

# =====================================================
# Snowflake Setup Script
# =====================================================
# Executes all Snowflake SQL scripts in the correct order
# Usage: ./scripts/setup_snowflake.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
SQL_DIR="$PROJECT_ROOT/infrastructure/snowflake"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Snowflake Setup Script${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if snowsql is installed
if ! command -v snowsql &> /dev/null; then
    echo -e "${RED}Error: snowsql CLI not found${NC}"
    echo "Please install SnowSQL: https://docs.snowflake.com/en/user-guide/snowsql-install-config.html"
    exit 1
fi

# Check for required environment variables
if [ -z "$SNOWFLAKE_ACCOUNT" ] || [ -z "$SNOWFLAKE_USER" ]; then
    echo -e "${RED}Error: Required environment variables not set${NC}"
    echo "Please set:"
    echo "  export SNOWFLAKE_ACCOUNT=your_account"
    echo "  export SNOWFLAKE_USER=your_username"
    echo "  export SNOWFLAKE_PASSWORD=your_password  # or use key-pair authentication"
    exit 1
fi

# Function to execute SQL script
execute_sql() {
    local script_name=$1
    local script_path="$SQL_DIR/$script_name"
    
    echo -e "${BLUE}Executing: $script_name${NC}"
    
    if [ ! -f "$script_path" ]; then
        echo -e "${RED}Error: Script not found: $script_path${NC}"
        return 1
    fi
    
    snowsql \
        -a "$SNOWFLAKE_ACCOUNT" \
        -u "$SNOWFLAKE_USER" \
        -f "$script_path" \
        --variable "env=dev"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $script_name completed successfully${NC}"
        echo ""
    else
        echo -e "${RED}✗ $script_name failed${NC}"
        exit 1
    fi
}

# Execute scripts in order
echo -e "${BLUE}Step 1: Creating databases...${NC}"
execute_sql "setup_databases.sql"

echo -e "${BLUE}Step 2: Creating schemas...${NC}"
execute_sql "setup_schemas.sql"

echo -e "${BLUE}Step 3: Creating tables...${NC}"
execute_sql "create_tables.sql"

echo -e "${BLUE}Step 4: Setting up roles and permissions...${NC}"
execute_sql "setup_roles.sql"

echo -e "${BLUE}Step 5: Creating secure views...${NC}"
execute_sql "create_secure_views.sql"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Snowflake setup complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo "1. Load data into RAW.client_hierarchy.CLIENTS"
echo "2. Run transformations: infrastructure/snowflake/transformations/transform_to_core.sql"
echo "3. Verify data in CORE database"
echo ""
echo "To grant roles to users:"
echo "  GRANT ROLE DATA_ENGINEER TO USER your_username;"
echo "  GRANT ROLE CRM_ANALYST TO USER your_username;"
echo "  GRANT ROLE SALES_LEADERSHIP TO USER your_username;"


