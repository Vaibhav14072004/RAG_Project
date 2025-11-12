# Vaibhav RAG Prototype (Updated)

Updated prototype with improved recommendations (5-8 items per query) and endpoints:

- POST /recommend  -> JSON {'query':'text','max_k':8} = returns recommendations
- POST /bulk_predict -> JSON {'queries':[...],'max_k':8} = returns batch results
- GET /download_predictions -> download vipul_predictions.csv
- GET /health -> health check

Run locally:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The file vaibhav_predictions.csv is included in this project folder.
