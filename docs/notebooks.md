# 

Notebooks are organized by data modality first, then by dataset or assay type.
Filenames indicate pipeline stage and iteration date.

Format:
```
NNN__stage__short-description__YYYY-MM-DD.ipynb
```

Example filename:
```
030__eda__cytokine-correlation__2025-01-06.ipynb
050__viz__hla-heatmap__2025-02-01.ipynb
```

## Components
- `NNN`: Three-digit pipeline stage number (e.g., 010 for data loading, 020 for QC, 030 for EDA, 040 for modeling, 050 for visualization)
- `stage`: Short descriptor of the pipeline stage (e.g., eda, qc, etl, viz, analysis)
- `short-description`: Brief description of the notebook’s focus (e.g., cytokine-correlation, hla-heatmap)
- `date`: Date of last major update in YYYY-MM-DD format

### Pipeline Stages by Number

Pipeline Flow

```text
raw data
   ↓
clean data
   ↓
understood data
   ↓
features
   ↓
model
   ↓
evaluation / insight
```

- 010: Data loading and parsing
- 020: Quality control and filtering
- 030: Exploratory data analysis (EDA)
- 040: Statistical analysis and modeling
- 050: Visualization and reporting

### Stage Abbreviations

Core stages:
- data: Load, parse, reshape raw inputs
- qc: Quality control, filtering, thresholds
- eda: Distribution, correlation, sanity checks
- analysis: Statistical tests, association models
- viz: Visualization & communication

Optional stages:
- preprocess: Normalization, scaling, transforms
- features: Feature engineering for modeling
- model: ML/statistical models
- eval: Model evaluation
- integration: Multi-omic integration
- wip: Explicit exploration
