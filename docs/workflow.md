# Development Workflow

## Branching Strategy
- main: stable, readable analyses
- develop: active development

## Commit Message Convention
This repository follows a lightweight Conventional Commits style.

### Format
<type>(<scope>): <summary>

### Types
- FEAT: new capability
- FIX: bug fix
- REF: code restructuring
- DOCS: documentation changes
- TEST: tests
- CHORE: maintenance
- DATA: dataset-related changes
- NB: notebook-only changes

### Scopes
Examples:
- proteomics, genetics, clinical, multiomics
- etl, qc, eda, analysis, viz
- src, tools, notebooks

### Examples
- FEAT(proteomics-qc): add LOD-based filtering
- REF(src): extract plotting utilities
- NB(eda): explore cytokine distributions
- DOCS: document notebook naming convention

## Merge Checklist
- [ ] notebooks run top-to-bottom
- [ ] no private data committed
- [ ] environment files updated if needed
- [ ] README/docs updated if structure changed