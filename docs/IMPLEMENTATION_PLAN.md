# Implementation Plan: Enterprise CRM Territory & Segmentation Engine

## 🎯 Strategic Overview

This plan prioritizes features based on:
1. **Dependencies** - What needs to exist before other features can work
2. **Value** - What demonstrates core competencies first
3. **Complexity** - Building from simple to complex
4. **Interview Readiness** - What showcases the project best

---

## 📋 Phase-by-Phase Implementation Plan

### **PHASE 1: Foundation & Core ETL Features** (Days 1-2)
*Goal: Complete Milestone 2 fully, making the ETL pipeline production-ready*

#### Priority 1.1: Modularize ETL Code ⭐ HIGHEST PRIORITY
**Why First**: Current code is all in the DAG file. Need to extract to modules before adding features.

**Tasks**:
1. Create `python_etl/ingestion/extract_clients.py`
   - Move extraction logic from DAG
   - Add support for multiple sources (CSV, API, etc.)
   - Add error handling and logging

2. Create `python_etl/transformations/dimensional_model.py`
   - Move transformation logic from DAG
   - Create reusable functions for CLIENT_DIM, TERRITORY_DIM, ASSIGNMENTS_FACT
   - Add data validation

3. Create `python_etl/transformations/quality_checks.py`
   - Move quality checks from DAG
   - Expand validation (schema, referential integrity, data types)
   - Add data profiling metrics

4. Update `crm_client_ingestion_dag.py`
   - Import from modules instead of inline functions
   - Cleaner, more maintainable code

**Estimated Time**: 2-3 hours
**Dependencies**: None
**Deliverable**: Modular, maintainable ETL codebase

---

#### Priority 1.2: Entity Deduplication (Fuzzy Matching) ⭐ HIGH PRIORITY
**Why Second**: Critical feature mentioned in requirements, demonstrates advanced data quality skills.

**Tasks**:
1. Create `python_etl/dedupe/__init__.py`
2. Create `python_etl/dedupe/fuzzy_matcher.py`
   - Install `rapidfuzz` library (faster than fuzzywuzzy)
   - Implement fuzzy matching on client names
   - Add similarity threshold configuration
   - Return potential duplicates with confidence scores

3. Create `python_etl/dedupe/deduplication_pipeline.py`
   - Process client records
   - Identify duplicates
   - Create merge rules (keep most complete record)
   - Generate deduplication report

4. Add deduplication task to DAG
   - Run after extraction, before transformation
   - Log duplicate findings
   - Optionally auto-merge or flag for review

**Estimated Time**: 3-4 hours
**Dependencies**: Priority 1.1 (modular structure)
**Deliverable**: Working deduplication with configurable thresholds

---

#### Priority 1.3: Conflict Detection (Territory Overlaps) ⭐ HIGH PRIORITY
**Why Third**: Completes Milestone 2, shows data quality thinking.

**Tasks**:
1. Create `python_etl/transformations/conflict_detection.py`
   - Detect when clients might belong to multiple territories
   - Check for advisor assignment conflicts
   - Identify orphaned assignments

2. Add conflict detection to quality checks
   - Flag conflicts in logs
   - Generate conflict report
   - Optionally fail pipeline if critical conflicts found

3. Create conflict resolution rules
   - Priority rules (e.g., explicit assignment > region-based)
   - Manual review flagging

**Estimated Time**: 2-3 hours
**Dependencies**: Priority 1.1 (modular structure)
**Deliverable**: Conflict detection and reporting

---

### **PHASE 2: Rules Engine** (Day 2-3)
*Goal: Complete Milestone 3 - Territory assignment logic*

#### Priority 2.1: Basic Rules Engine Framework ⭐ HIGH PRIORITY
**Why First**: Foundation for all territory assignment logic.

**Tasks**:
1. Create `python_etl/rules_engine/__init__.py`
2. Create `python_etl/rules_engine/base_rule.py`
   - Abstract base class for rules
   - Rule evaluation interface
   - Rule priority/ordering

3. Create `python_etl/rules_engine/territory_assigner.py`
   - Main orchestrator for rule evaluation
   - Apply rules in priority order
   - Handle rule conflicts

4. Create `python_etl/rules_engine/rules/region_rule.py`
   - Region → territory assignment
   - Current logic from DAG, but as a rule

5. Create `python_etl/rules_engine/rules/segment_rule.py`
   - Segment-based assignment
   - Combine with region for territory ID

**Estimated Time**: 3-4 hours
**Dependencies**: Priority 1.1 (modular structure)
**Deliverable**: Extensible rules engine framework

---

#### Priority 2.2: Whitelisting/Blacklisting Rules ⭐ MEDIUM PRIORITY
**Why Second**: Common business requirement, shows rule flexibility.

**Tasks**:
1. Create `python_etl/rules_engine/rules/whitelist_rule.py`
   - Explicit client → territory assignments
   - Override other rules
   - Load from config file or database

2. Create `python_etl/rules_engine/rules/blacklist_rule.py`
   - Prevent certain clients from specific territories
   - Conflict prevention

3. Add whitelist/blacklist configuration
   - JSON/YAML config file
   - Or database table for dynamic rules

4. Integrate into rules engine
   - Whitelist rules have highest priority
   - Blacklist rules prevent assignments

**Estimated Time**: 2-3 hours
**Dependencies**: Priority 2.1 (rules engine framework)
**Deliverable**: Working whitelist/blacklist system

---

#### Priority 2.3: Auto-Segmentation Tiers ⭐ MEDIUM PRIORITY
**Why Third**: Advanced feature, demonstrates business logic implementation.

**Tasks**:
1. Create `python_etl/rules_engine/rules/segmentation_rule.py`
   - Define segmentation tiers (e.g., Tier 1, Tier 2, Tier 3)
   - Based on client attributes (size, revenue, etc.)
   - Assign to appropriate territory tier

2. Create segmentation configuration
   - Tier definitions
   - Assignment rules per tier
   - Advisor capacity per tier

3. Add segmentation to assignment logic
   - Evaluate client attributes
   - Assign tier
   - Route to tier-appropriate territory

**Estimated Time**: 3-4 hours
**Dependencies**: Priority 2.1 (rules engine framework)
**Deliverable**: Auto-segmentation with tier-based assignment

---

#### Priority 2.4: Nightly Assignment Update Job ⭐ MEDIUM PRIORITY
**Why Fourth**: Completes Milestone 3, shows scheduling/orchestration.

**Tasks**:
1. Create new DAG: `territory_assignment_update_dag.py`
   - Scheduled to run nightly
   - Re-evaluate all assignments
   - Update assignment table

2. Create `python_etl/rules_engine/assignment_updater.py`
   - Load current assignments
   - Re-apply rules
   - Detect changes
   - Update assignments (with audit trail)

3. Add change tracking
   - Log what changed
   - Who changed
   - When changed
   - Why changed (which rule)

**Estimated Time**: 2-3 hours
**Dependencies**: Priority 2.1-2.3 (rules engine complete)
**Deliverable**: Automated nightly assignment updates

---

### **PHASE 3: Infrastructure Integration** (Day 3-4)
*Goal: Complete Milestone 1 - Cloud infrastructure*

#### Priority 3.1: Snowflake Database Setup ⭐ HIGH PRIORITY
**Why First**: Core infrastructure, needed before data loading.

**Tasks**:
1. Create `infrastructure/snowflake/setup_databases.sql`
   - CREATE DATABASE RAW
   - CREATE DATABASE STAGE
   - CREATE DATABASE CORE

2. Create `infrastructure/snowflake/setup_schemas.sql`
   - client_hierarchy schema
   - territories schema
   - assignments schema
   - segmentation_rules schema

3. Create `infrastructure/snowflake/create_tables.sql`
   - RAW.CLIENTS table
   - STAGE.CLIENTS_STAGING table
   - CORE.CLIENT_DIM table
   - CORE.TERRITORY_DIM table
   - CORE.ASSIGNMENTS_FACT table

4. Create `infrastructure/snowflake/setup_roles.sql`
   - SYSADMIN role
   - DATA_ENGINEER role
   - CRM_ANALYST role
   - SALES_LEADERSHIP role
   - Grant appropriate permissions

5. Create `infrastructure/snowflake/create_secure_views.sql`
   - Views for SALES_LEADERSHIP role
   - Row-level security if needed

**Estimated Time**: 3-4 hours
**Dependencies**: None (can be done in parallel with Phase 1)
**Deliverable**: Complete Snowflake setup scripts

---

#### Priority 3.2: Snowflake Integration in ETL ⭐ HIGH PRIORITY
**Why Second**: Connect ETL pipeline to Snowflake.

**Tasks**:
1. Install `snowflake-connector-python`
2. Create `python_etl/ingestion/snowflake_loader.py`
   - Connection management
   - Bulk load to RAW.CLIENTS
   - Error handling

3. Create `python_etl/transformations/snowflake_transformer.py`
   - Load from RAW to STAGE
   - Transform in Snowflake (SQL)
   - Load to CORE tables

4. Update DAG to use Snowflake
   - Replace CSV simulation with real Snowflake operations
   - Add connection configuration
   - Add retry logic

**Estimated Time**: 4-5 hours
**Dependencies**: Priority 3.1 (Snowflake setup)
**Deliverable**: Working Snowflake integration

---

#### Priority 3.3: AWS S3 Integration ⭐ MEDIUM PRIORITY
**Why Third**: Complete the CSV→S3→Snowflake pipeline.

**Tasks**:
1. Install `boto3`
2. Create `python_etl/ingestion/s3_uploader.py`
   - Upload CSV to S3 bucket `institutional_clients_raw/`
   - Add timestamped paths
   - Handle errors

3. Create `python_etl/ingestion/s3_to_snowflake.py`
   - Copy from S3 to Snowflake stage
   - Use Snowflake COPY INTO command
   - Handle file formats

4. Update DAG to include S3 step
   - Extract → Upload to S3 → Load to Snowflake

5. Add AWS credentials configuration
   - Environment variables
   - IAM role (for production)

**Estimated Time**: 3-4 hours
**Dependencies**: Priority 3.1 (Snowflake setup)
**Deliverable**: Complete CSV→S3→Snowflake pipeline

---

### **PHASE 4: Frontend & API** (Day 4-5)
*Goal: Complete Milestone 4 - User interface*

#### Priority 4.1: Mock CRM API (Backend First) ⭐ HIGH PRIORITY
**Why First**: Frontend needs API to consume. Build backend before frontend.

**Tasks**:
1. Create `crm_mock_api/requirements.txt`
   - FastAPI (or Flask)
   - SQLAlchemy (or direct Snowflake connection)
   - Pydantic for validation

2. Create `crm_mock_api/main.py`
   - FastAPI app setup
   - CORS configuration
   - API routes

3. Create API endpoints:
   - `GET /api/territories` - List all territories
   - `GET /api/territories/{id}/assignments` - Get assignments for territory
   - `GET /api/clients` - List clients (with filters)
   - `GET /api/clients/{id}` - Get client details
   - `GET /api/clients/hierarchy` - Get client hierarchy tree
   - `GET /api/advisors` - List advisors
   - `GET /api/advisors/{email}/workload` - Get advisor's clients
   - `GET /api/assignments` - List all assignments

4. Create `crm_mock_api/models.py`
   - Pydantic models for request/response
   - Data validation

5. Create `crm_mock_api/database.py`
   - Connection to Snowflake (or CSV for demo)
   - Query functions

6. Add API documentation
   - Swagger/OpenAPI docs (automatic with FastAPI)

**Estimated Time**: 4-5 hours
**Dependencies**: Priority 3.2 (Snowflake integration) or can use CSV for demo
**Deliverable**: Working REST API

---

#### Priority 4.2: React Dashboard - Setup & Core ⭐ HIGH PRIORITY
**Why Second**: Main user interface.

**Tasks**:
1. Initialize React app in `frontend/react-dashboard/`
   ```bash
   npx create-react-app . --template typescript
   # or use Vite for faster setup
   ```

2. Install dependencies:
   - `shadcn/ui` components (per user rules)
   - `lucide-react` for icons (per user rules)
   - `react-router-dom` for routing
   - `axios` or `fetch` for API calls
   - `recharts` or similar for charts

3. Create project structure:
   ```
   frontend/react-dashboard/
   ├── src/
   │   ├── components/
   │   ├── pages/
   │   ├── services/ (API calls)
   │   ├── types/
   │   └── utils/
   ```

4. Create base layout:
   - Navigation sidebar
   - Header
   - Main content area

5. Create routing:
   - `/` - Dashboard home
   - `/territories` - Territory assignments view
   - `/clients` - Client hierarchy explorer
   - `/advisors` - Advisor workloads

**Estimated Time**: 2-3 hours
**Dependencies**: None (can start in parallel with API)
**Deliverable**: React app structure

---

#### Priority 4.3: React Dashboard - Territory Assignments View ⭐ HIGH PRIORITY
**Why Third**: Core feature, demonstrates data visualization.

**Tasks**:
1. Create `src/pages/TerritoryAssignments.tsx`
   - Table/grid of territories
   - Filter by region, segment
   - Show assignment counts
   - Click to see clients in territory

2. Create `src/components/TerritoryCard.tsx`
   - Display territory info
   - Show advisor
   - Show client count

3. Create `src/components/AssignmentTable.tsx`
   - List clients assigned to territory
   - Sortable columns
   - Search/filter

4. Add charts (using shadcn/ui or recharts):
   - Territory distribution pie chart
   - Assignment trends over time

**Estimated Time**: 3-4 hours
**Dependencies**: Priority 4.1 (API), Priority 4.2 (React setup)
**Deliverable**: Working territory assignments page

---

#### Priority 4.4: React Dashboard - Client Hierarchy Explorer ⭐ MEDIUM PRIORITY
**Why Fourth**: Shows organizational structure understanding.

**Tasks**:
1. Create `src/pages/ClientHierarchy.tsx`
   - Tree view of client hierarchy
   - Org → Subsidiary → Advisor structure
   - Expandable/collapsible nodes

2. Create `src/components/HierarchyTree.tsx`
   - Recursive tree component
   - Visual hierarchy representation

3. Add search/filter:
   - Search by client name
   - Filter by region, segment
   - Highlight matches

**Estimated Time**: 3-4 hours
**Dependencies**: Priority 4.1 (API), Priority 4.2 (React setup)
**Deliverable**: Working client hierarchy explorer

---

#### Priority 4.5: React Dashboard - Advisor Workloads ⭐ MEDIUM PRIORITY
**Why Fifth**: Completes the three main views.

**Tasks**:
1. Create `src/pages/AdvisorWorkloads.tsx`
   - List of advisors
   - Show client count per advisor
   - Show capacity/utilization

2. Create `src/components/AdvisorCard.tsx`
   - Advisor info
   - Client list
   - Workload metrics

3. Add charts:
   - Workload distribution
   - Capacity vs. utilization
   - Top advisors by client count

**Estimated Time**: 2-3 hours
**Dependencies**: Priority 4.1 (API), Priority 4.2 (React setup)
**Deliverable**: Working advisor workloads page

---

### **PHASE 5: Docker & Deployment** (Day 5)
*Goal: Containerize and deploy*

#### Priority 5.1: Docker Configuration ⭐ HIGH PRIORITY
**Why First**: Needed for deployment, shows DevOps skills.

**Tasks**:
1. Create `Dockerfile` for ETL/Airflow
   - Python base image
   - Install dependencies
   - Copy code
   - Set up Airflow

2. Create `Dockerfile` for API
   - Python base image
   - Install FastAPI dependencies
   - Copy API code
   - Expose port

3. Create `Dockerfile` for Frontend
   - Node base image
   - Build React app
   - Serve with nginx

4. Create `docker-compose.yml`
   - Airflow service
   - API service
   - Frontend service
   - Network configuration
   - Volume mounts

5. Create `.dockerignore` files
   - Exclude unnecessary files

**Estimated Time**: 3-4 hours
**Dependencies**: Priority 4.1-4.5 (All services complete)
**Deliverable**: Complete Docker setup

---

#### Priority 5.2: Deployment Documentation ⭐ MEDIUM PRIORITY
**Why Second**: Shows production readiness thinking.

**Tasks**:
1. Create `DEPLOYMENT.md`
   - Docker Compose instructions
   - Environment variables
   - Port configuration
   - Volume mounts

2. Add Kubernetes manifests (optional but impressive):
   - `k8s/airflow-deployment.yaml`
   - `k8s/api-deployment.yaml`
   - `k8s/frontend-deployment.yaml`
   - `k8s/services.yaml`

3. Add production considerations:
   - Secrets management
   - Database connections
   - Scaling considerations

**Estimated Time**: 2-3 hours
**Dependencies**: Priority 5.1 (Docker setup)
**Deliverable**: Deployment documentation

---

### **PHASE 6: Documentation & Polish** (Day 5-6)
*Goal: Complete Milestone 5 - Interview assets*

#### Priority 6.1: Architecture Diagram ⭐ HIGH PRIORITY
**Why First**: Visual representation is crucial for interviews.

**Tasks**:
1. Create architecture diagram showing:
   - Data flow (CSV → S3 → Snowflake → CORE)
   - Airflow orchestration
   - API layer
   - Frontend
   - Component interactions

2. Options:
   - Use Lucidchart/Figma (cloud-based, shareable)
   - Use draw.io (free, can export)
   - Use Mermaid (code-based, in README)

3. Save as:
   - PNG/SVG in `docs/architecture.png`
   - Or link to online diagram

**Estimated Time**: 1-2 hours
**Dependencies**: None
**Deliverable**: Architecture diagram

---

#### Priority 6.2: Screenshots ⭐ HIGH PRIORITY
**Why Second**: Visual proof of working system.

**Tasks**:
1. Take screenshots of:
   - Airflow DAG graph view
   - Airflow task execution logs
   - Territory Assignments page
   - Client Hierarchy Explorer
   - Advisor Workloads page
   - API Swagger documentation

2. Save in `docs/screenshots/`
3. Add to README with captions

**Estimated Time**: 1 hour
**Dependencies**: Priority 4.3-4.5 (All pages complete)
**Deliverable**: Screenshot gallery

---

#### Priority 6.3: Enhanced README ⭐ MEDIUM PRIORITY
**Why Third**: Final polish, make it interview-ready.

**Tasks**:
1. Add architecture diagram section
2. Add screenshots section
3. Expand Snowflake role-based access patterns:
   - Explain each role
   - Show example queries
   - Document secure views

4. Add "How It Works" section:
   - Territory assignment logic
   - Rules engine explanation
   - Data flow explanation

5. Add "Key Features" section:
   - Highlight completed features
   - Show code examples

6. Add "Tech Stack" section:
   - All technologies used
   - Why each was chosen

**Estimated Time**: 2-3 hours
**Dependencies**: Priority 6.1-6.2 (Diagram and screenshots)
**Deliverable**: Polished, interview-ready README

---

## 📊 Implementation Timeline

### **Week 1: Core Features (Days 1-3)**
- **Day 1**: Phase 1 (Modularize ETL, Deduplication, Conflict Detection)
- **Day 2**: Phase 2 (Rules Engine - all priorities)
- **Day 3**: Phase 3.1-3.2 (Snowflake setup and integration)

### **Week 2: Frontend & Infrastructure (Days 4-6)**
- **Day 4**: Phase 3.3 (S3 integration) + Phase 4.1 (API)
- **Day 5**: Phase 4.2-4.5 (React Dashboard - all pages)
- **Day 6**: Phase 5 (Docker) + Phase 6 (Documentation)

---

## 🎯 Quick Start Recommendations

### **If you have 1 day:**
Focus on **Phase 1** (Modularize ETL, Deduplication, Conflict Detection)
- Shows code organization
- Demonstrates data quality thinking
- Completes Milestone 2

### **If you have 2-3 days:**
Add **Phase 2** (Rules Engine)
- Shows business logic implementation
- Demonstrates extensible architecture
- Completes Milestone 3

### **If you have 4-5 days:**
Add **Phase 3** (Infrastructure) + **Phase 4** (Frontend)
- Shows full-stack capabilities
- Demonstrates cloud integration
- Completes Milestones 1 & 4

### **If you have 6+ days:**
Complete everything including **Phase 5 & 6**
- Production-ready project
- Interview-ready documentation
- Complete all milestones

---

## 🔄 Parallel Work Opportunities

These can be done simultaneously:

1. **Phase 3.1 (Snowflake Setup)** can be done in parallel with **Phase 1**
   - SQL scripts don't depend on Python code

2. **Phase 4.1 (API)** can be started in parallel with **Phase 4.2 (React Setup)**
   - API can use CSV data initially, switch to Snowflake later

3. **Phase 6.1 (Architecture Diagram)** can be done anytime
   - Doesn't depend on code completion

---

## ✅ Success Criteria

After completing this plan, you should have:

- ✅ **Modular ETL pipeline** with deduplication and conflict detection
- ✅ **Rules engine** with whitelisting, blacklisting, and auto-segmentation
- ✅ **Snowflake integration** with proper role-based security
- ✅ **S3 integration** completing the CSV→S3→Snowflake pipeline
- ✅ **REST API** with all required endpoints
- ✅ **React dashboard** with three main views
- ✅ **Docker setup** for easy deployment
- ✅ **Architecture diagram** and screenshots
- ✅ **Polished README** ready for interviews

---

## 📝 Notes

- **Start with Phase 1** - It's the foundation for everything else
- **Don't skip modularization** - It makes everything else easier
- **Use shadcn/ui and Lucide icons** as per your preferences
- **Add comments** to code as you build (per your rules)
- **Update README** as you complete each phase

---

*Plan Created: December 2025*
*Estimated Total Time: 6-8 days of focused work*

