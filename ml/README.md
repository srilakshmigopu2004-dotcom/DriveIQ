# DriveIQ ML

**Status: rule-based first. No dataset and no trained model are shipped on purpose.**

The live app uses transparent rule-based logic (`backend/matching/services/`). This folder holds the pipeline
for replacing/augmenting it with an ML model once you have a legitimate dataset.

## Steps
1. Get a real dataset (e.g. a public campus-placement dataset from Kaggle/UCI, or anonymised data your placement
   cell collects with consent). Check its licence.
2. Make a CSV with columns: `cgpa, backlogs, dsa_level, aptitude_level, communication_level, projects_count,
   internships_count, sql_level, programming_level` + a target column (e.g. `placed`). Map the dataset's own
   columns onto these; don't invent values for columns it lacks. Retrain with fewer features if needed.
3. `pip install -r ml/requirements.txt`
4. `cd ml && python train.py --data datasets/your_file.csv --target placed`
5. Metrics (accuracy, precision, recall, F1, 5-fold CV) are written to `evaluation/metrics.json`.
6. Document limitations: dataset size, source, class balance, selection bias, which college it came from.

## Honesty rules
- Never quote accuracy you did not measure on held-out data.
- A model trained on "placed or not" predicts historical patterns, not your chance in a specific drive.
- Keep the model explainable (logistic regression coefficients are shown per prediction).
