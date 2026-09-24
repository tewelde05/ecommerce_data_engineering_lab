# Synthetic E-commerce Data Engineering Lab

This project applies the class 12-step data-engineering road map to 500 reproducible synthetic e-commerce transactions.  
The raw file contains deliberate quality problems for profiling and cleaning practice.  
Reusable logic is stored in `src/data_pipeline.py`, and the notebook imports its functions.  
The workflow transforms, enriches, feature-engineers, aggregates, and serializes the data.  
Cleaned results are written in both CSV and JSON formats.

## Project structure

```text
synthetic_ecommerce_lab/
├── data/
│   ├── ecommerce_transactions_raw.csv
│   └── city_metadata.csv
├── notebooks/
│   └── ecommerce_data_engineering_lab.ipynb
├── outputs/
│   ├── cleaned_transactions.csv
│   └── cleaned_transactions.json
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py
│   └── generate_data.py
├── tests/
│   └── test_data_pipeline.py
├── .gitignore
├── README.md
└── requirements.txt
```

The raw dataset is included exactly as generated. Running the notebook never overwrites it.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

The `.venv` name is only a conventional folder name. The environment is **not** included in the repository. Open `notebooks/ecommerce_data_engineering_lab.ipynb` and run all cells from top to bottom.

## Data sources

- Primary file: `data/ecommerce_transactions_raw.csv`, a 500-row synthetic dataset created for this assignment with a fixed random seed. It contains date, customer ID, product, price, quantity, coupon code, and shipping city.
- Secondary file: `data/city_metadata.csv`, a small extract of 2021 census-metropolitan-area population values from [Statistics Canada, Canada at a Glance](https://www150.statcan.gc.ca/n1/pub/12-581-x/2022001/sec1-eng.htm). It enriches shipping cities with province and 2021 metropolitan population.

## Regenerate the primary data

From the project root:

```bash
python -m src.generate_data
```

The fixed seed makes the generated file reproducible. You normally do not need to regenerate it because the original CSV is already included.

## Git workflow

Create a new public repository and run these commands from this project folder:

```bash
git init
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git add data src .gitignore requirements.txt
git commit -m "Add synthetic data and reusable pipeline"
git add notebooks
git commit -m "Add 12-step data engineering notebook"
git add README.md outputs tests
git commit -m "Add documentation, tests, and serialized outputs"
git push -u origin main
```

`git add` selects changes for the next commit; `git commit` records that selected snapshot locally; `git push` sends the commits to GitHub.

## Other projects

- [AI-ML-Class](https://github.com/tewelde05/AI-ML-Class)
