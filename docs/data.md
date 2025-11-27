```markdown
# Data & Dataset Guidance

This project uses synthetic data for demonstration (backend/data/sample_loans.csv). Typical features for credit risk / loan eligibility:

- income: annual income in USD
- employment_length: years employed at current job
- credit_score: FICO-like score (300–850)
- debt_to_income: ratio (0–1)
- loan_amount: requested loan principal
- loan_purpose: categorical (debt_consolidation, home_improvement, small_business, car, other)
- age: applicant age
- sensitive_attribute: e.g., gender or race (used only for fairness evaluation)

Guidance:
- Remove or mask PII before training.
- Use representative datasets and stratify splits.
- Monitor performance across subgroups (protected classes).
- Use data versioning and store seeds for reproducibility.

Synthetic generation in scripts/train_model.py is parameterized and reproducible using a random seed.
```