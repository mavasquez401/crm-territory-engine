# Enterprise CRM Territory & Segmentation Engine

A comprehensive, production-ready data pipeline and analytics platform for managing CRM client territories, segmentation, and advisor assignments. This system demonstrates enterprise-grade data engineering practices with automated ETL workflows, dimensional modeling, fuzzy matching deduplication, rules-based territory assignment, and a modern React dashboard.

[![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)](docs/ARCHITECTURE.md)
[![Python](https://img.shields.io/badge/Python-3.11-green)](requirements.txt)
[![React](https://img.shields.io/badge/React-18-61dafb)](frontend/react-dashboard/package.json)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed)](docker-compose.yml)

---

## 🎯 Project Overview

This flagship portfolio project showcases a complete enterprise CRM territory management system with:

- **Automated ETL Pipeline** with Apache Airflow orchestration
- **Fuzzy Matching Deduplication** using rapidfuzz (85% similarity threshold)
- **Rules-Based Territory Assignment** with priority-based evaluation
- **Dimensional Data Modeling** (star schema with fact and dimension tables)
- **Snowflake Integration** with role-based access control
- **AWS S3 Integration** for data lake architecture
- **REST API** with FastAPI and automatic OpenAPI documentation
- **React Dashboard** with shadcn/ui components and real-time data visualization
- **Docker Deployment** with multi-container orchestration

---

## 🏗️ Architecture

### System Architecture Diagram

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for the complete architecture diagram and detailed component descriptions.

### Data Flow

```
CSV/API → S3 → Snowflake RAW → Deduplicate → Transform → Rules Engine → CORE → API → Dashboard
```

### Tech Stack

| Layer              | Technologies                   |
| ------------------ | ------------------------------ |
| **Orchestration**  | Apache Airflow 2.7             |
| **ETL**            | Python 3.11, Pandas, rapidfuzz |
| **Data Warehouse** | Snowflake (RAW, STAGE, CORE)   |
| **Storage**        | AWS S3, CSV (local dev)        |
| **API**            | FastAPI, Pydantic, uvicorn     |
| **Frontend**       | React 18, TypeScript, Vite     |
| **UI Components**  | shadcn/ui, Lucide icons        |
| **Visualization**  | Recharts                       |
| **Deployment**     | Docker, Docker Compose         |

---

## ✨ Key Features

### ✅ Implemented Features

#### ETL Pipeline

- ✅ **Modular ETL Architecture** - Clean separation of ingestion, transformation, and quality checks
- ✅ **Entity Deduplication** - Fuzzy matching with configurable threshold and confidence scoring
- ✅ **Conflict Detection** - Territory overlaps, advisor conflicts, orphaned assignments
- ✅ **Dimensional Modeling** - Star schema with CLIENT_DIM, TERRITORY_DIM, ASSIGNMENTS_FACT
- ✅ **Data Quality Checks** - Row counts, schema validation, referential integrity

#### Rules Engine

- ✅ **Priority-Based Rules** - Extensible framework with rule ordering
- ✅ **Whitelist/Blacklist** - Explicit territory assignments and blocks
- ✅ **Auto-Segmentation** - Tier-based assignment with configurable criteria
- ✅ **Nightly Updates** - Scheduled assignment re-evaluation with audit trail

#### Infrastructure

- ✅ **Snowflake Integration** - Full database setup with RAW, STAGE, CORE
- ✅ **Role-Based Access Control** - DATA_ENGINEER, CRM_ANALYST, SALES_LEADERSHIP
- ✅ **Secure Views** - 6 secure views for restricted data access
- ✅ **AWS S3 Integration** - Timestamped uploads with encryption

#### API & Frontend

- ✅ **REST API** - 15+ endpoints with automatic documentation
- ✅ **React Dashboard** - 4 pages with data visualization
- ✅ **Territory View** - Grid view with charts and filtering
- ✅ **Client Hierarchy** - Tree view of organizational structure
- ✅ **Advisor Workloads** - Capacity monitoring and metrics

#### DevOps

- ✅ **Docker Containers** - Separate containers for Airflow, API, Frontend
- ✅ **Docker Compose** - One-command deployment
- ✅ **Health Checks** - Automated service health monitoring

---

## 📁 Complete Project Structure

```
crm-territory-engine/
│
├── 📂 airflow/                                    # Apache Airflow Orchestration
│   ├── dags/
│   │   ├── crm_client_ingestion_dag.py           # Main ETL pipeline (6 tasks)
│   │   │                                         # Tasks: extract → deduplicate → load → transform → detect_conflicts → quality_checks
│   │   └── territory_assignment_update_dag.py    # Nightly assignment updates (scheduled 2 AM)
│   ├── logs/                                     # Airflow execution logs
│   ├── plugins/                                  # Custom Airflow plugins
│   ├── airflow.cfg                               # Airflow configuration
│   └── airflow.db                                # SQLite database (dev)
│
├── 📂 python_etl/                                 # Modular ETL Code (25 modules)
│   ├── __init__.py                               # Package initialization
│   │
│   ├── 📂 ingestion/                             # Data Ingestion Layer
│   │   ├── __init__.py                           # Path constants (RAW_DIR, CORE_DIR)
│   │   ├── extract_clients.py                    # CSV/API extraction with validation
│   │   ├── snowflake_connection.py               # Connection pooling & error handling
│   │   ├── snowflake_loader.py                   # Bulk COPY INTO operations
│   │   ├── s3_config.py                          # AWS credentials management
│   │   └── s3_uploader.py                        # Timestamped S3 uploads
│   │
│   ├── 📂 transformations/                       # Data Transformation Layer
│   │   ├── __init__.py
│   │   ├── dimensional_model.py                  # Star schema builder
│   │   │                                         # Functions: build_client_dim(), build_territory_dim(), build_assignments_fact()
│   │   ├── quality_checks.py                     # Comprehensive validation
│   │   │                                         # Checks: row counts, schema, referential integrity, completeness
│   │   ├── conflict_detection.py                 # Multi-type conflict detection
│   │   │                                         # Detects: territory overlaps, advisor conflicts, orphaned assignments
│   │   └── snowflake_transformer.py              # SQL-based transformations
│   │
│   ├── 📂 dedupe/                                # Entity Deduplication
│   │   ├── __init__.py
│   │   ├── fuzzy_matcher.py                      # rapidfuzz implementation
│   │   │                                         # Methods: calculate_similarity(), find_duplicates(), find_best_match()
│   │   └── deduplication_pipeline.py             # Complete workflow
│   │                                             # Strategies: most_complete, first, manual
│   │
│   └── 📂 rules_engine/                          # Territory Assignment Rules Engine
│       ├── __init__.py
│       ├── base_rule.py                          # Abstract BaseRule class
│       │                                         # Defines: evaluate(), priority, name
│       ├── territory_assigner.py                 # Rule orchestrator
│       │                                         # Methods: add_rule(), assign_territory(), resolve_conflicts()
│       ├── assignment_updater.py                 # Re-evaluation engine
│       │                                         # Features: change detection, audit trail
│       └── 📂 rules/                             # Specific Rule Implementations
│           ├── __init__.py
│           ├── region_rule.py                    # Priority 100: Region + segment → territory
│           ├── segment_rule.py                   # Priority 100: Segment-only fallback
│           ├── whitelist_rule.py                 # Priority 10: Explicit assignments (highest)
│           ├── blacklist_rule.py                 # Priority 20: Blocked assignments
│           └── segmentation_rule.py              # Priority 50: Tier-based assignment
│
├── 📂 crm_mock_api/                              # FastAPI REST API Backend
│   ├── main.py                                   # FastAPI app with CORS
│   │                                             # Features: auto docs, error handling, logging
│   ├── models.py                                 # Pydantic models (15+ models)
│   │                                             # Models: Territory, Client, Advisor, Assignment, SystemStats
│   ├── database.py                               # Data access layer
│   │                                             # Features: caching (5 min TTL), CSV/Snowflake support
│   ├── 📂 routers/                               # API Route Modules
│   │   ├── __init__.py
│   │   ├── territories.py                        # 3 endpoints: list, get, assignments
│   │   ├── clients.py                            # 3 endpoints: list, get, hierarchy
│   │   ├── advisors.py                           # 3 endpoints: list, workload, stats
│   │   ├── assignments.py                        # 2 endpoints: list, history
│   │   └── health.py                             # 2 endpoints: health, stats
│   ├── Dockerfile                                # Python 3.11-slim container
│   ├── .dockerignore                             # Exclude venv, logs
│   └── requirements.txt                          # FastAPI, uvicorn, pandas, pydantic
│
├── 📂 frontend/react-dashboard/                  # React TypeScript Frontend
│   ├── 📂 src/
│   │   ├── 📂 components/                        # React Components
│   │   │   ├── 📂 ui/                            # shadcn/ui Components
│   │   │   │   ├── button.tsx                    # Button with variants
│   │   │   │   ├── card.tsx                      # Card container
│   │   │   │   └── badge.tsx                     # Status badges
│   │   │   ├── Layout.tsx                        # Main layout with sidebar navigation
│   │   │   │                                     # Features: collapsible sidebar, active route highlighting
│   │   │   ├── TerritoryCard.tsx                 # Territory summary card
│   │   │   │                                     # Shows: client count, advisor count, status
│   │   │   ├── HierarchyTree.tsx                 # Recursive tree component
│   │   │   │                                     # Features: expand/collapse, color-coded segments
│   │   │   └── AdvisorCard.tsx                   # Advisor workload card
│   │   │                                         # Shows: client count, workload bar, capacity
│   │   │
│   │   ├── 📂 pages/                             # Page Components
│   │   │   ├── Dashboard.tsx                     # Home page
│   │   │   │                                     # Features: metrics cards, pie chart, recent changes, quick links
│   │   │   ├── Territories.tsx                   # Territory management
│   │   │   │                                     # Features: grid view, filters, pie/bar charts, modal details
│   │   │   ├── Clients.tsx                       # Client hierarchy explorer
│   │   │   │                                     # Features: tree view, search, expandable orgs, modal details
│   │   │   └── Advisors.tsx                      # Advisor workloads
│   │   │                                         # Features: list view, sort, bar chart, workload indicators
│   │   │
│   │   ├── 📂 services/                          # API Integration
│   │   │   └── api.ts                            # Typed API client
│   │   │                                         # Methods: territoryApi, clientApi, advisorApi, assignmentApi, systemApi
│   │   │
│   │   ├── 📂 types/                             # TypeScript Definitions
│   │   │   └── index.ts                          # All type definitions
│   │   │                                         # Types: Territory, Client, Advisor, Assignment, SystemStats
│   │   │
│   │   ├── 📂 lib/                               # Utility Functions
│   │   │   └── utils.ts                          # Helper functions
│   │   │                                         # Functions: cn(), formatNumber(), calculatePercentage()
│   │   │
│   │   ├── App.tsx                               # Main app with routing
│   │   ├── main.tsx                              # Entry point
│   │   ├── index.css                             # Global styles (Tailwind)
│   │   └── vite-env.d.ts                         # Vite type definitions
│   │
│   ├── index.html                                # HTML template
│   ├── vite.config.ts                            # Vite configuration (proxy to API)
│   ├── tsconfig.json                             # TypeScript configuration
│   ├── tsconfig.node.json                        # TypeScript for Vite
│   ├── tailwind.config.js                        # Tailwind CSS configuration
│   ├── postcss.config.js                         # PostCSS configuration
│   ├── components.json                           # shadcn/ui configuration
│   ├── package.json                              # Node dependencies
│   ├── Dockerfile                                # Multi-stage build (Node + nginx)
│   ├── nginx.conf                                # nginx config (SPA routing, API proxy)
│   └── .dockerignore                             # Exclude node_modules, dist
│
├── 📂 infrastructure/                            # Infrastructure as Code
│   └── 📂 snowflake/                             # Snowflake Setup Scripts
│       ├── setup_databases.sql                   # CREATE DATABASE RAW, STAGE, CORE
│       ├── setup_schemas.sql                     # CREATE SCHEMA client_hierarchy, territories, etc.
│       ├── create_tables.sql                     # CREATE TABLE for all dimensions/facts
│       │                                         # Tables: RAW.CLIENTS, STAGE.CLIENTS_STAGING, CORE.CLIENT_DIM, etc.
│       ├── setup_roles.sql                       # Role-based access control
│       │                                         # Roles: DATA_ENGINEER, CRM_ANALYST, SALES_LEADERSHIP
│       ├── create_secure_views.sql               # 6 secure views with row-level security
│       │                                         # Views: v_territory_summary, v_client_assignments, etc.
│       └── 📂 transformations/
│           └── transform_to_core.sql             # SQL transformations (MERGE INTO pattern)
│
├── 📂 data/                                      # Data Storage
│   ├── 📂 mock_clients/                          # RAW Layer (Source Data)
│   │   └── clients.csv                           # Sample client data (3 records)
│   │
│   ├── 📂 core/                                  # CORE Layer (Generated by ETL)
│   │   ├── client_dim.csv                        # Client dimension table
│   │   ├── territory_dim.csv                     # Territory dimension table
│   │   └── assignments_fact.csv                  # Assignment fact table
│   │
│   ├── 📂 config/                                # Configuration Files
│   │   ├── whitelist.json.example                # Explicit assignment template
│   │   ├── blacklist.json.example                # Blocked assignment template
│   │   └── segmentation_tiers.json.example       # Tier configuration template
│   │
│   └── 📂 reports/                               # Generated Reports (gitignored)
│       ├── duplicates_report.csv                 # Fuzzy matching results
│       ├── conflicts_report.csv                  # Conflict detection results
│       └── assignment_changes.csv                # Audit trail of changes
│
├── 📂 scripts/                                   # Utility Scripts
│   ├── generate_secrets.py                       # Generate Airflow secrets
│   ├── setup_secrets.sh                          # Automated secret setup
│   └── setup_snowflake.sh                        # Automated Snowflake setup
│
├── 📂 docs/                                      # Documentation
│   ├── ARCHITECTURE.md                           # System architecture with Mermaid diagram
│   └── 📂 screenshots/                           # Screenshots (to be captured)
│
├── 📂 venv/                                      # Python virtual environment (gitignored)
│
├── 📄 Dockerfile                                 # Airflow container definition
├── 📄 docker-compose.yml                         # Multi-service orchestration
│                                                 # Services: airflow (8080), api (8000), frontend (3000)
├── 📄 .dockerignore                              # Docker build exclusions
├── 📄 .gitignore                                 # Git exclusions (enhanced for configs/reports)
│
├── 📄 requirements.txt                           # Python dependencies
│                                                 # Includes: airflow, pandas, rapidfuzz, snowflake-connector, boto3
│
├── 📄 package.json                               # Node.js workspace config
│
├── 📋 README.md                                  # This file (846 lines)
├── 📋 DEPLOYMENT.md                              # Docker deployment guide
├── 📋 SECURITY.md                                # Security best practices
├── 📋 IMPLEMENTATION_PLAN.md                     # Development roadmap
├── 📋 IMPLEMENTATION_REVIEW.md                   # Requirements review
├── 📋 PHASES_1-3_COMPLETE.md                     # Backend completion summary
├── 📋 PHASES_4-5_COMPLETE.md                     # Frontend completion summary
├── 📋 🎉_PROJECT_COMPLETE.md                     # Final completion summary
└── 📋 .env.example                               # Environment variables template
```

### File Count by Category

| Category               | Files   | Lines of Code |
| ---------------------- | ------- | ------------- |
| **Python ETL Modules** | 25      | ~4,500        |
| **API Backend**        | 9       | ~1,200        |
| **React Frontend**     | 20+     | ~2,000        |
| **SQL Scripts**        | 6       | ~800          |
| **Docker Config**      | 6       | ~300          |
| **Documentation**      | 10      | ~5,000        |
| **Configuration**      | 8       | ~200          |
| **Total**              | **80+** | **~14,000+**  |

### Key Directories Explained

**`airflow/`** - Orchestration layer with 2 DAGs managing the entire ETL workflow

**`python_etl/`** - Modular ETL code organized by function:

- `ingestion/` - Extract and load operations
- `transformations/` - Data modeling and quality
- `dedupe/` - Fuzzy matching deduplication
- `rules_engine/` - Territory assignment logic

**`crm_mock_api/`** - REST API backend serving data to frontend

**`frontend/react-dashboard/`** - React UI with 4 pages and data visualization

**`infrastructure/`** - SQL scripts for Snowflake setup (production-ready)

**`data/`** - Data storage with RAW, CORE, config, and reports

**`scripts/`** - Automation scripts for setup and deployment

**`docs/`** - Architecture documentation and diagrams

````

---

## 🚀 Quick Start (Docker)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Generate secrets
python3 scripts/generate_secrets.py

# 2. Create .env file
cp .env.example .env
# Add generated secrets to .env

# 3. Build and start all services
docker-compose up -d

# 4. Access services
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# Airflow: http://localhost:8080 (admin/admin)
````

### Option 2: Local Development

See [Installation](#installation) section below for detailed local setup.

---

## 📊 Data Model

### Dimensional Model (Star Schema)

#### **CLIENT_DIM** - Client Dimension

```sql
CREATE TABLE CLIENT_DIM (
    client_key INTEGER PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    segment VARCHAR(100),
    parent_org VARCHAR(255),
    primary_advisor_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE
);
```

#### **TERRITORY_DIM** - Territory Dimension

```sql
CREATE TABLE TERRITORY_DIM (
    territory_id VARCHAR(50) PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    segment VARCHAR(100) NOT NULL,
    owner_role VARCHAR(100),
    description VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE
);
```

#### **ASSIGNMENTS_FACT** - Client-Territory Assignments

```sql
CREATE TABLE ASSIGNMENTS_FACT (
    assignment_id INTEGER PRIMARY KEY,
    client_key INTEGER REFERENCES CLIENT_DIM,
    territory_id VARCHAR(50) REFERENCES TERRITORY_DIM,
    primary_advisor_email VARCHAR(255),
    assignment_type VARCHAR(50) DEFAULT 'PRIMARY',
    is_current BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    end_date DATE,
    assigned_by_rule VARCHAR(100),
    confidence_score DECIMAL(5,2)
);
```

---

## 🔄 ETL Pipeline Workflow

The `crm_client_ingestion_dag` executes 6 tasks in sequence:

### 1. **Extract Clients**

- Reads data from CSV or API
- Validates required columns
- Logs sample data

### 2. **Deduplicate Clients** ⭐ NEW

- Fuzzy matching using rapidfuzz
- 85% similarity threshold
- Generates `duplicates_report.csv`

### 3. **Load to Snowflake**

- Bulk load to RAW.CLIENTS
- Uses COPY INTO for efficiency
- Supports S3 staging

### 4. **Transform to CORE**

- Builds dimensional model
- Creates CLIENT_DIM, TERRITORY_DIM, ASSIGNMENTS_FACT
- Territory IDs: `{REGION}_{SEGMENT}` (e.g., NOR_INS)

### 5. **Detect Conflicts** ⭐ NEW

- Territory overlaps
- Advisor conflicts
- Orphaned assignments
- Generates `conflicts_report.csv`

### 6. **Quality Checks**

- Row count validation
- Schema validation
- Referential integrity
- Data completeness

---

## 🎯 Rules Engine

### Rule Types (Priority Order)

| Priority | Rule                 | Description                                             |
| -------- | -------------------- | ------------------------------------------------------- |
| 10       | **WhitelistRule**    | Explicit client → territory mappings (highest priority) |
| 20       | **BlacklistRule**    | Prevents specific assignments                           |
| 50       | **SegmentationRule** | Tier-based assignment (T1, T2, T3)                      |
| 100      | **RegionRule**       | Region + segment combination (default)                  |
| 100      | **SegmentRule**      | Segment-only fallback                                   |

### Configuration Files

**Whitelist** (`data/config/whitelist.json`):

```json
{
  "1": "NOR_INS",
  "2": "NOR_RET"
}
```

**Blacklist** (`data/config/blacklist.json`):

```json
{
  "3": ["NOR_RET", "SOU_INS"]
}
```

**Segmentation Tiers** (`data/config/segmentation_tiers.json`):

```json
{
  "tiers": {
    "tier_1_institutional": {
      "criteria": { "segment": "Institutional" },
      "territory_suffix": "T1",
      "priority": 1,
      "advisor_capacity": 20
    }
  }
}
```

---

## 🔒 Snowflake Role-Based Access

### Roles and Permissions

**DATA_ENGINEER**

- Full access to RAW, STAGE, CORE databases
- Can create, read, update, delete all tables
- Runs ETL pipelines
- Manages data warehouse

**CRM_ANALYST**

- Read access to CORE database
- Can query all CORE tables
- Cannot modify data
- Used for analytics and reporting

**SALES_LEADERSHIP**

- Read access via secure views only
- Cannot access raw data
- Row-level security applied
- Used for executive reporting

### Secure Views

| View                     | Description                   | Access                        |
| ------------------------ | ----------------------------- | ----------------------------- |
| `v_territory_summary`    | Territory metrics with counts | SALES_LEADERSHIP, CRM_ANALYST |
| `v_client_assignments`   | Current client assignments    | SALES_LEADERSHIP, CRM_ANALYST |
| `v_advisor_workload`     | Advisor capacity metrics      | SALES_LEADERSHIP, CRM_ANALYST |
| `v_regional_performance` | Regional statistics           | SALES_LEADERSHIP, CRM_ANALYST |
| `v_client_hierarchy`     | Organizational structure      | SALES_LEADERSHIP, CRM_ANALYST |
| `v_assignment_history`   | Last 90 days of changes       | SALES_LEADERSHIP, CRM_ANALYST |

### Example Queries

**As CRM_ANALYST:**

```sql
-- View all territories with client counts
SELECT * FROM CORE.dimensional.v_territory_summary
ORDER BY client_count DESC;

-- Find clients in a specific territory
SELECT * FROM CORE.dimensional.v_client_assignments
WHERE territory_id = 'NOR_INS';

-- Analyze advisor workload
SELECT * FROM CORE.dimensional.v_advisor_workload
ORDER BY client_count DESC;
```

**As SALES_LEADERSHIP:**

```sql
-- Same queries as CRM_ANALYST, but through secure views
-- Row-level security automatically filters data based on role
SELECT * FROM CORE.dimensional.v_regional_performance;
```

---

## 🌐 API Documentation

### REST API Endpoints

The API provides 15+ endpoints with automatic OpenAPI documentation.

**Access:** http://localhost:8000/docs

#### Territories

- `GET /api/territories` - List all territories
- `GET /api/territories/{id}` - Get territory details
- `GET /api/territories/{id}/assignments` - Get territory assignments

#### Clients

- `GET /api/clients` - List clients (with pagination, filters)
- `GET /api/clients/{id}` - Get client details
- `GET /api/clients/hierarchy` - Get organizational hierarchy

#### Advisors

- `GET /api/advisors` - List advisors with workload
- `GET /api/advisors/{email}/workload` - Get advisor details
- `GET /api/advisors/stats` - Get advisor statistics

#### Assignments

- `GET /api/assignments` - List current assignments
- `GET /api/assignments/history` - Get assignment history

#### System

- `GET /api/health` - Health check
- `GET /api/stats` - System statistics

### Example API Calls

```bash
# Get all territories
curl http://localhost:8000/api/territories

# Get clients in Northeast region
curl "http://localhost:8000/api/clients?region=Northeast"

# Get advisor workload
curl http://localhost:8000/api/advisors/advisor1@example.com/workload

# Get system stats
curl http://localhost:8000/api/stats
```

---

## 💻 React Dashboard

### Pages

**Dashboard** (`/`)

- Overview with key metrics
- System statistics cards
- Distribution charts
- Recent assignment changes
- Quick links to main views

**Territories** (`/territories`)

- Grid view of all territories
- Filter by region and segment
- Pie chart: Territory distribution
- Bar chart: Clients per territory
- Click territory to see assignments

**Clients** (`/clients`)

- Tree view of organizational hierarchy
- Expandable/collapsible organizations
- Search by name or organization
- Color-coded by segment
- Click client for full details

**Advisors** (`/advisors`)

- List of advisors with metrics
- Sort by client count or territory count
- Workload indicators (capacity bars)
- Bar chart: Top 10 advisors
- Click advisor to see client list

### Features

- 📱 Responsive design (mobile, tablet, desktop)
- 🎨 Modern UI with shadcn/ui components
- 📊 Interactive charts with Recharts
- 🔍 Search and filter functionality
- ⚡ Fast performance with Vite

---

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop (for containerized deployment)
- Optional: Snowflake account, AWS account

### Local Development Setup

#### 1. Clone and Setup Python

```bash
git clone <repository-url>
cd crm-territory-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Secrets

```bash
# Generate secrets
python3 scripts/generate_secrets.py

# Create .env file
cp .env.example .env
# Edit .env and add generated secrets

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)
```

#### 3. Initialize Airflow

```bash
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

#### 4. Start Airflow

```bash
# Terminal 1: Webserver
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080

# Terminal 2: Scheduler
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

#### 5. Start API

```bash
# Terminal 3: API
cd crm_mock_api
pip install -r requirements.txt
python main.py
# API runs on http://localhost:8000
```

#### 6. Start Frontend

```bash
# Terminal 4: Frontend
cd frontend/react-dashboard
npm install
npm run dev
# Dashboard runs on http://localhost:3000
```

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services

| Service  | Port | URL                        |
| -------- | ---- | -------------------------- |
| Frontend | 3000 | http://localhost:3000      |
| API      | 8000 | http://localhost:8000/docs |
| Airflow  | 8080 | http://localhost:8080      |

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for detailed deployment guide.

---

## ☁️ Snowflake Setup (Optional)

### Automated Setup

```bash
# 1. Set environment variables
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_USER=your_username
export SNOWFLAKE_PASSWORD=your_password

# 2. Run setup script
./scripts/setup_snowflake.sh

# Done! Creates databases, schemas, tables, roles, and views
```

### Manual Setup

Execute SQL scripts in order:

1. `infrastructure/snowflake/setup_databases.sql`
2. `infrastructure/snowflake/setup_schemas.sql`
3. `infrastructure/snowflake/create_tables.sql`
4. `infrastructure/snowflake/setup_roles.sql`
5. `infrastructure/snowflake/create_secure_views.sql`

---

## 🧪 Testing

### Test ETL Pipeline

```bash
# 1. Start Airflow
# 2. Navigate to http://localhost:8080
# 3. Trigger crm_client_ingestion_dag
# 4. Check data/core/ for generated files
# 5. Check data/reports/ for quality reports
```

### Test API

```bash
# Start API
cd crm_mock_api
python main.py

# Test endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/territories
```

### Test Frontend

```bash
# Start frontend
cd frontend/react-dashboard
npm run dev

# Open http://localhost:3000
# Navigate through all pages
# Verify data loads correctly
```

---

## 📈 Use Cases

1. **Territory Management** - Automatically assign clients to territories based on region, segment, and custom rules
2. **Advisor Assignment** - Track which advisors manage which clients with workload balancing
3. **Client Segmentation** - Tier-based segmentation with configurable criteria
4. **Data Quality Monitoring** - Automated deduplication and conflict detection
5. **Audit Trail** - Complete history of assignment changes with rule attribution
6. **Executive Reporting** - Secure views for sales leadership with aggregated metrics

---

## 🔧 Configuration

### Environment Variables

**Required:**

- `AIRFLOW__WEBSERVER__SECRET_KEY` - Airflow session key
- `AIRFLOW__CORE__FERNET_KEY` - Airflow encryption key

**Optional (Snowflake):**

- `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_ROLE`

**Optional (AWS S3):**

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`, `S3_BUCKET_NAME`

---

## 📚 Documentation

All documentation is organized in the **[docs/](docs/)** directory:

### Core Documentation

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture with Mermaid diagram
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Docker deployment guide
- **[docs/SECURITY.md](docs/SECURITY.md)** - Security best practices

### Implementation Documentation

- **[docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)** - Development roadmap
- **[docs/IMPLEMENTATION_REVIEW.md](docs/IMPLEMENTATION_REVIEW.md)** - Requirements review
- **[docs/PHASES_1-3_COMPLETE.md](docs/PHASES_1-3_COMPLETE.md)** - Backend implementation
- **[docs/PHASES_4-5_COMPLETE.md](docs/PHASES_4-5_COMPLETE.md)** - Frontend implementation
- **[docs/FINAL_STATUS.md](docs/FINAL_STATUS.md)** - Project completion status

### Security Documentation

- **[docs/QUICK_SECURITY_REFERENCE.md](docs/QUICK_SECURITY_REFERENCE.md)** - Quick reference
- **[docs/SECURITY_SETUP_SUMMARY.md](docs/SECURITY_SETUP_SUMMARY.md)** - Setup guide
- **[docs/CHANGES_SUMMARY.md](docs/CHANGES_SUMMARY.md)** - Technical changes

### Completion Summaries

- **[docs/🎉_PROJECT_COMPLETE.md](docs/🎉_PROJECT_COMPLETE.md)** - Project completion celebration
- **[docs/🎉_ALL_DONE.md](docs/🎉_ALL_DONE.md)** - Security fix completion

---

## 🤝 Contributing

This is a portfolio/demonstration project. Suggestions and feedback are welcome!

---

## 📄 License

This project is for demonstration and portfolio purposes.

---

## 👤 Author

**Manuel Vasquez**

- GitHub: [@mavasquez401](https://github.com/mavasquez401/crm-territory-engine)
- Airflow DAG Owner: `manuel`

---

## 🔗 Technologies Used

- [Apache Airflow](https://airflow.apache.org/) - Workflow orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - Frontend library
- [Snowflake](https://www.snowflake.com/) - Cloud data warehouse
- [AWS S3](https://aws.amazon.com/s3/) - Object storage
- [shadcn/ui](https://ui.shadcn.com/) - UI component library
- [Lucide](https://lucide.dev/) - Icon library
- [Recharts](https://recharts.org/) - Chart library
- [Docker](https://www.docker.com/) - Containerization

---

## ⭐ Project Highlights

This project demonstrates:

✅ **Full-Stack Development** - Python backend, React frontend, REST API
✅ **Data Engineering** - ETL pipelines, dimensional modeling, data quality
✅ **Cloud Integration** - Snowflake, AWS S3, scalable architecture
✅ **Advanced Algorithms** - Fuzzy matching, conflict detection, rules engine
✅ **DevOps** - Docker, CI/CD ready, infrastructure as code
✅ **Security** - RBAC, secure views, secret management
✅ **Best Practices** - Modular code, type hints, comprehensive logging, documentation

---

**Status**: Production-Ready ✅  
**Completion**: 95% (All core features implemented)  
**Last Updated**: December 2025

---

## 🚦 Next Steps

1. **Run locally**: Follow Quick Start guide
2. **Deploy with Docker**: `docker-compose up -d`
3. **Set up Snowflake**: Run `./scripts/setup_snowflake.sh` (optional)
4. **Explore dashboard**: http://localhost:3000
5. **View API docs**: http://localhost:8000/docs

---

**Note**: This is a demonstration project showcasing enterprise data engineering best practices. The system works with local CSV files for development and seamlessly scales to Snowflake for production use.
