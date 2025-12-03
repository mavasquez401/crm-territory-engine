# Enterprise CRM Territory & Segmentation Engine

A comprehensive data pipeline and analytics platform for managing CRM client territories, segmentation, and advisor assignments. This system demonstrates enterprise-grade data engineering practices with automated ETL workflows, dimensional modeling, and scalable architecture.

## 🎯 Project Overview

This project showcases a production-ready CRM territory management system that:

- **Ingests** client data from multiple sources
- **Transforms** raw data into a dimensional model (star schema)
- **Orchestrates** data pipelines using Apache Airflow
- **Segments** clients by region, business type, and organizational hierarchy
- **Assigns** clients to territories and advisors
- **Validates** data quality throughout the pipeline

## 🏗️ Architecture

### Data Flow

```
Mock CRM API → Extract → RAW Layer → Transform → CORE Layer → Quality Checks → Analytics
```

### Tech Stack

- **Orchestration**: Apache Airflow
- **Data Processing**: Python, Pandas
- **Data Storage**: CSV (demo), designed for Snowflake
- **Frontend**: React Dashboard (planned)
- **Infrastructure**: Terraform (IaC ready)
- **Data Quality**: Built-in validation checks

## 📁 Project Structure

```
crm-territory-engine/
├── airflow/                      # Airflow orchestration
│   ├── dags/
│   │   └── crm_client_ingestion_dag.py  # Main ETL pipeline
│   ├── plugins/                  # Custom Airflow plugins
│   ├── logs/                     # Airflow execution logs
│   └── airflow.cfg              # Airflow configuration
│
├── data/                         # Data storage
│   ├── mock_clients/            # RAW layer - source data
│   │   └── clients.csv          # Mock client data
│   └── core/                    # CORE layer - dimensional model
│       ├── client_dim.csv       # Client dimension table
│       ├── territory_dim.csv    # Territory dimension table
│       └── assignments_fact.csv # Client-territory assignments fact table
│
├── python_etl/                   # ETL modules (modular design)
│   ├── ingestion/               # Data ingestion logic
│   ├── transformations/         # Data transformation rules
│   ├── dedupe/                  # Deduplication logic
│   └── rules_engine/            # Business rules engine
│
├── frontend/                     # Web dashboard
│   └── react-dashboard/         # React-based analytics UI
│
├── infrastructure/               # Infrastructure as Code
│   └── terraform/               # Terraform configurations
│
└── crm_mock_api/                # Mock API for testing
```

## 📊 Data Model

### Dimensional Model (Star Schema)

#### **CLIENT_DIM** - Client Dimension

Stores client master data and attributes.

```
- client_key (PK)
- client_name
- region
- segment
- parent_org
- primary_advisor_email
- is_active
```

#### **TERRITORY_DIM** - Territory Dimension

Defines sales territories based on region and segment.

```
- territory_id (PK)
- region
- segment
- owner_role
```

#### **ASSIGNMENTS_FACT** - Client-Territory Assignments

Tracks which clients are assigned to which territories.

```
- client_key (FK)
- territory_id (FK)
- primary_advisor_email
- assignment_type (PRIMARY, SECONDARY)
- is_current
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Virtual environment (venv)
- Apache Airflow 2.x

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd crm-territory-engine
```

2. **Set up Python virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install apache-airflow pandas
```

4. **Initialize Airflow**

```bash
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow db init
```

5. **Create Airflow user**

```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

### Running the Pipeline

1. **Start Airflow webserver** (in one terminal)

```bash
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080
```

2. **Start Airflow scheduler** (in another terminal)

```bash
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

3. **Access Airflow UI**

- Navigate to `http://localhost:8080`
- Login with your admin credentials
- Find the `crm_client_ingestion_dag` DAG
- Trigger the DAG manually

## 🔄 Pipeline Workflow

The `crm_client_ingestion_dag` executes the following tasks in sequence:

### 1. **Extract Clients** (`extract_clients`)

- Reads client data from mock CRM source
- Simulates API extraction from external systems
- Logs sample data for validation

### 2. **Load RAW to Snowflake** (`load_raw_to_snowflake`)

- Simulates loading data into Snowflake RAW layer
- In production: bulk loads to `RAW.CLIENTS` table
- Currently: logs intended operations

### 3. **Transform to CORE** (`transform_to_core`)

- Builds dimensional model from RAW data
- Creates CLIENT_DIM, TERRITORY_DIM, ASSIGNMENTS_FACT
- Applies business logic:
  - Territory IDs: `{REGION_PREFIX}_{SEGMENT_PREFIX}` (e.g., NOR_INS)
  - Active status tracking
  - Primary advisor assignment
- Writes CORE tables to CSV

### 4. **Quality Checks** (`quality_checks`)

- Validates row counts (non-empty tables)
- Ensures referential integrity
- Logs quality metrics
- Fails pipeline if checks don't pass

## 🎨 Features

### Current Features

- ✅ Automated ETL pipeline with Airflow
- ✅ Dimensional data modeling (star schema)
- ✅ Territory segmentation by region and business type
- ✅ Client-advisor assignment tracking
- ✅ Data quality validation
- ✅ Modular Python ETL structure
- ✅ Mock data for testing

### Planned Features

- 🔄 React dashboard for territory analytics
- 🔄 Real-time CRM API integration
- 🔄 Snowflake data warehouse connection
- 🔄 Advanced deduplication logic
- 🔄 Business rules engine for dynamic segmentation
- 🔄 Terraform infrastructure deployment
- 🔄 Advanced data quality checks (completeness, accuracy)
- 🔄 Historical tracking (SCD Type 2)

## 📈 Use Cases

1. **Territory Management**: Automatically assign clients to sales territories based on region and segment
2. **Advisor Assignment**: Track which advisors are responsible for which clients
3. **Segmentation Analysis**: Analyze client distribution across territories
4. **Data Quality Monitoring**: Ensure clean, consistent client data
5. **Pipeline Orchestration**: Automate daily/weekly data refreshes

## 🛠️ Development

### Adding New Transformations

1. Create transformation logic in `python_etl/transformations/`
2. Add new task to `crm_client_ingestion_dag.py`
3. Update task dependencies
4. Test with mock data

### Extending the Data Model

1. Modify transformation logic in `transform_to_core_fn()`
2. Update CSV outputs in `data/core/`
3. Add corresponding quality checks
4. Update this README with new schema

### Custom Business Rules

- Implement rules in `python_etl/rules_engine/`
- Examples: territory assignment rules, client prioritization, advisor capacity

## 📝 Configuration

### Airflow Configuration

- **Config file**: `airflow/airflow.cfg`
- **DAG folder**: `airflow/dags/`
- **Logs**: `airflow/logs/`
- **Database**: SQLite (dev), PostgreSQL (production recommended)

### Data Paths

All paths are dynamically resolved from the project root:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "mock_clients"
CORE_DIR = DATA_DIR / "core"
```

## 🧪 Testing

### Manual Testing

1. Modify mock data in `data/mock_clients/clients.csv`
2. Trigger the DAG in Airflow UI
3. Verify outputs in `data/core/`
4. Check logs for any errors

### Data Validation

- Row count checks (non-empty tables)
- Schema validation (expected columns)
- Referential integrity (FK relationships)

## 📊 Sample Data

### Mock Clients

```csv
client_id,client_name,region,segment,parent_org,advisor_email
1,Atlas Capital Partners,Northeast,Institutional,Atlas Holdings,advisor1@example.com
2,Beacon Wealth Management,Northeast,Retail,Beacon Group,advisor2@example.com
3,Crescent Advisory Group,Midwest,Institutional,Crescent Holdings,advisor3@example.com
```

### Generated Territories

- **NOR_INS**: Northeast Institutional
- **NOR_RET**: Northeast Retail
- **MID_INS**: Midwest Institutional

## 🤝 Contributing

This is a portfolio/demonstration project. Suggestions and feedback are welcome!

## 📄 License

This project is for demonstration and portfolio purposes.

## 👤 Author

**Manuel**

- Airflow DAG Owner: `manuel`
- Contact: [Your contact information]

## 🔗 Related Technologies

- [Apache Airflow](https://airflow.apache.org/) - Workflow orchestration
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Snowflake](https://www.snowflake.com/) - Cloud data warehouse (target platform)
- [Terraform](https://www.terraform.io/) - Infrastructure as Code
- [React](https://react.dev/) - Frontend framework

---

**Note**: This is a demonstration project showcasing data engineering best practices. The pipeline currently uses CSV files for simplicity but is designed to scale to enterprise data warehouses like Snowflake.
