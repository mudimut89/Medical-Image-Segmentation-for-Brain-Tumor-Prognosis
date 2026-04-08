# Brain Tumor Segmentation System

**Project Aim**: Create a model which segments medical images so that medical professionals can perform brain tumor examination and give predicted outcomes.

## Project Objectives

### Objective 1: Dataset Collection & Preprocessing
- Collect a dataset of brain MRI images with annotated tumor regions
- Preprocess publicly available data for model training

### Objective 2: Deep Learning Model Development
- Design, develop, and refine a deep learning model for brain tumor segmentation
- Achieve target Dice coefficient of 0.80 for accurate tumor detection

### Objective 3: User Interface & Clinical Integration
- Validate a user interface for MRI scanner integration
- Display tumor sizes and predicted outcomes
- Enable medical professionals to view and respond accurately

## System Overview

A full-stack web application for radiologists to upload MRI scans, segment brain tumors using AI (U-Net architecture), and view prognosis data with clinical decision support.

## Project Structure

```
brain-tumor-segmentation/
├── objective1_dataset/         # Objective 1: Dataset Collection & Preprocessing
│   ├── data_collection.py      # Dataset download and organization
│   ├── preprocessing.py        # Enhanced image preprocessing
│   ├── data_validation.py      # Data quality checks
│   └── datasets/                # Processed datasets
│       ├── brats/              # BraTS processed data
│       ├── kaggle/            # Kaggle processed data
│       └── custom/            # Custom collected data
├── objective2_model/           # Objective 2: Deep Learning Model Development
│   ├── model_architecture.py   # U-Net with Dice optimization
│   ├── training_pipeline.py    # Training with Dice coefficient tracking
│   ├── model_evaluation.py     # Performance evaluation metrics
│   ├── model_optimization.py   # Hyperparameter tuning for 0.80 Dice
│   └── models/                 # Trained models
│       ├── unet_dice_080.h5   # Target achievement model
│       └── checkpoints/        # Training checkpoints
├── objective3_interface/        # Objective 3: User Interface & Clinical Integration
│   ├── backend/                 # FastAPI backend
│   │   ├── main.py             # API endpoints with clinical focus
│   │   ├── clinical_utils.py   # Clinical decision support
│   │   └── requirements.txt    # Python dependencies
│   ├── frontend/               # React + Vite frontend
│   │   ├── src/
│   │   │   ├── components/     # UI components
│   │   │   │   ├── MRIUploader.jsx
│   │   │   │   ├── TumorViewer.jsx
│   │   │   │   └── OutcomePanel.jsx
│   │   │   └── App.jsx         # Main application
│   │   └── package.json        # Node.js dependencies
│   └── clinical_validation/     # Clinical testing framework
├── training/                   # Legacy training scripts
├── data/                       # Legacy data directory
├── start.sh                    # Unix/Linux/macOS startup script
├── start.bat                   # Windows startup script
└── README.md                   # This file
```

## Features (Aligned with Objectives)

### Objective 1 Features
- **Dataset Management**: Automated collection and preprocessing of brain MRI datasets
- **Data Validation**: Quality checks for annotated tumor regions
- **Multi-Source Support**: BraTS, Kaggle, and custom dataset integration

### Objective 2 Features
- **Optimized U-Net Architecture**: Enhanced for Dice coefficient optimization
- **Real-time Training Metrics**: Live tracking of Dice coefficient progress toward 0.80 target
- **Model Evaluation**: Comprehensive performance analysis and validation
- **Hyperparameter Tuning**: Automated optimization for target accuracy

### Objective 3 Features
- **Clinical-Grade Interface**: MRI scanner integration and tumor visualization
- **Tumor Analysis**: Accurate tumor size measurement and location mapping
- **Predicted Outcomes**: Clinical decision support with prognosis information
- **Professional Response Tools**: Interface for medical professionals to review and respond
- **Dual-Pane View**: Side-by-side comparison of original and segmented images
- **Medical-Grade UI**: Clean, clinical dashboard optimized for radiologists

## Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Git** (optional, for cloning)

## Quick Start (Objective-Based)

### Prerequisites
- Python 3.9+ with pip
- Node.js 18+ with npm
- TensorFlow 2.15+
- Medical imaging datasets (BraTS, Kaggle)

### Step 1: Dataset Collection & Preprocessing (Objective 1)

```bash
# Activate virtual environment
medseg_env\Scripts\activate

# Run data collection and preprocessing
cd objective1_dataset
python data_collection.py
python preprocessing.py
python data_validation.py
```

### Step 2: Model Training & Optimization (Objective 2)

```bash
# Train optimized U-Net model
cd objective2_model
python model_architecture.py
python training_pipeline.py
python model_evaluation.py
```

### Step 3: Clinical Interface (Objective 3)

#### Backend Setup
```bash
cd objective3_interface/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd objective3_interface/frontend
npm install
npm run dev
```

### Quick Start Scripts

#### Windows
```batch
cd brain-tumor-segmentation
start.bat
```

#### Unix/Linux/macOS
```bash
cd brain-tumor-segmentation
chmod +x start.sh
./start.sh
```

### Manual Setup

#### Legacy Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Legacy Frontend
```bash
cd frontend
npm install
npm run dev
```

## Usage

### New Objective-Based Interface (Recommended)

1. Open **http://localhost:5173** in your browser
2. Upload MRI scan for AI analysis
3. View comprehensive tumor analysis with clinical insights
4. Review treatment recommendations and follow-up schedule

### Legacy Interface

1. Open **http://localhost:5173** in your browser
2. Drag and drop an MRI scan image (JPEG, PNG, BMP, or TIFF)
3. Click **"Analyze Scan"** to perform segmentation
4. View the segmentation results and prognosis report

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/upload` | POST | Upload MRI and get segmentation results |
| `/model/info` | GET | Get model architecture information |

### API Documentation

Interactive API docs available at **http://localhost:8000/docs**

## Loading Trained Weights

To use your trained U-Net weights:

1. Place your `.h5` weights file in `data/weights/`
2. Update `backend/main.py`:

```python
# In the upload_and_segment function, uncomment:
global model
if model is None:
    model = get_model(weights_path="path/to/your/weights.h5")
mask = model.predict(np.expand_dims(preprocessed, axis=0))[0]
```

## Model Architecture

The U-Net implementation follows the Chapter 3 documentation specifications:

- **Input**: 128×128×1 grayscale MRI
- **Encoder**: 4 blocks (64→128→256→512 filters)
- **Bridge**: 1024 filters
- **Decoder**: 4 blocks with skip connections
- **Output**: Binary segmentation mask

## Preprocessing Pipeline

1. **Resize** to 128×128 pixels
2. **CLAHE** contrast enhancement (clip_limit=2.0)
3. **Normalization** to [0, 1] range

## Datasets

See `data/readme.md` for instructions on integrating:
- Kaggle Brain Tumor MRI Dataset
- BraTS Challenge Dataset

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **TensorFlow/Keras**: Deep learning framework for U-Net model
- **OpenCV**: Computer vision library for image processing
- **NumPy**: Numerical computing for data manipulation
- **Pillow**: Image processing and format conversion
- **Python 3.9+**: Backend programming language

### Frontend
- **React 18**: Modern JavaScript library for building user interfaces
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Lucide React**: Beautiful icon library for React
- **Axios**: Promise-based HTTP client for API communication
- **React Dropzone**: File upload component with drag-and-drop

### Database & Data Storage
- **SQLite**: Lightweight relational database for structured data storage
  - **Patient Records**: Demographics, medical history, scan metadata
  - **Analysis Results**: Segmentation masks, tumor metrics, clinical reports
  - **Model Metadata**: Training history, performance metrics, version tracking
  - **User Sessions**: Authentication, preferences, audit trails
- **PostgreSQL**: Production-grade database for scalable deployment (optional)
  - **Connection Pooling**: Efficient database connection management
  - **Migration Support**: Schema versioning and updates
  - **Full-Text Search**: Advanced search capabilities for medical records
- **Redis**: In-memory caching layer for performance optimization
  - **Session Storage**: Fast user session management
  - **API Response Caching**: Cached analysis results for repeated requests
  - **Model Loading**: Cached model weights for faster inference

### Database Schema
```sql
-- Patients Table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MRI Scans Table
CREATE TABLE mri_scans (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_size VARCHAR(50),
    modality VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis Results Table
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES mri_scans(id),
    tumor_detected BOOLEAN DEFAULT FALSE,
    tumor_size_pixels INTEGER,
    tumor_size_mm2 FLOAT,
    tumor_percentage FLOAT,
    tumor_location VARCHAR(100),
    dice_coefficient FLOAT,
    confidence_score FLOAT,
    segmentation_mask_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clinical Reports Table
CREATE TABLE clinical_reports (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id),
    tumor_grade VARCHAR(50),
    tumor_type VARCHAR(100),
    severity VARCHAR(20),
    recommendations TEXT,
    prognosis_outcome JSONB,
    follow_up_schedule JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database ORM & Migration
- **SQLAlchemy**: Python SQL toolkit and ORM
  - **Model Definitions**: Declarative base models for database tables
  - **Migration Scripts**: Alembic for database schema management
  - **Connection Pooling**: Efficient database connection handling
  - **Query Optimization**: Advanced filtering and indexing strategies
- **Alembic**: Database migration tool
  - **Version Control**: Track database schema changes
  - **Auto-Migration**: Automatic schema updates on deployment
  - **Rollback Support**: Safe database version rollbacks

### Data Access Layer
- **Repository Pattern**: Clean separation of data access logic
- **Connection Management**: Database connection lifecycle management
- **Transaction Support**: ACID compliance for data integrity
- **Query Optimization**: Indexed queries for performance
- **Caching Strategy**: Multi-level caching for frequently accessed data

### Database Configuration
```python
# Database configuration example
DATABASE_CONFIG = {
    'development': {
        'url': 'sqlite:///./brain_tumor_dev.db',
        'echo': True,
        'pool_pre_ping': True
    },
    'production': {
        'url': 'postgresql://user:pass@localhost/brain_tumor_prod',
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30,
        'pool_recycle': 3600
    },
    'cache': {
        'redis_url': 'redis://localhost:6379/0',
        'cache_timeout': 3600,
        'key_prefix': 'brain_tumor:'
    }
}
```

### Development Tools
- **Alembic**: Database migration management
- **SQLite Browser**: Database visualization and debugging
- **pgAdmin**: PostgreSQL administration interface
- **Redis Commander**: Redis instance management
- **Docker Compose**: Containerized database services

### Production Deployment
- **Docker**: Containerized database services
- **Kubernetes**: Orchestration for scalable deployment
- **Nginx**: Reverse proxy and load balancing
- **SSL/TLS**: Encrypted database connections
- **Backup Strategy**: Automated database backups and recovery

## License

For research and educational purposes only.

## Disclaimer

This application is intended for research and educational purposes. Results should be verified by qualified medical professionals before any clinical decisions are made.
