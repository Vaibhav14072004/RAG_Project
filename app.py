from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Local catalog (embedded) - for prototype only
CATALOG = [{"id": "JFA", "name": "Job-Focused Assessments (JFA)", "url": "https://www.shl.com/products/assessments/job-focused-assessments/", "type": "Skill/Job-Fit", "desc": "Job-focused simulations and role-specific tasks."}, {"id": "OPQ", "name": "Occupational Personality Questionnaire (OPQ)", "url": "https://www.shl.com/products/product-catalog/view/occupational-personality-questionnaire-opq32r/", "type": "Personality", "desc": "Measures behavioural styles relevant to job performance."}, {"id": "VERIFY_G", "name": "Verify G (Cognitive Ability)", "url": "https://www.shl.com/products/product-catalog/view/verify-g/", "type": "Cognitive", "desc": "General cognitive ability and reasoning assessments."}, {"id": "SJT", "name": "Situational Judgement Tests (SJT)", "url": "https://www.shl.com/products/assessments/behavioral-assessments/situation-judgement-tests-sjt/", "type": "Situational/Behavioral", "desc": "Measures judgement and decision-making in work scenarios."}, {"id": "CODING", "name": "Coding Simulations", "url": "https://www.shl.com/products/assessments/skills-and-simulations/coding-simulations/", "type": "Technical", "desc": "Practical coding tasks and IDE-based challenges."}, {"id": "TECH", "name": "Technical Skills Simulations", "url": "https://www.shl.com/products/assessments/skills-and-simulations/technical-skills/", "type": "Technical", "desc": "Domain-specific technical skills and simulations."}, {"id": "MQ", "name": "Motivational Questionnaire (MQ)", "url": "https://www.shl.com/products/assessments/personality-assessment/motivational-questionnaire/", "type": "Motivational", "desc": "Assesses motivators and drivers that influence behaviour."}, {"id": "CALL", "name": "Call Center Simulations", "url": "https://www.shl.com/products/assessments/skills-and-simulations/call-center-simulations/", "type": "Simulation", "desc": "Simulations for customer service and call handling."}, {"id": "LANG", "name": "Language Evaluation", "url": "https://www.shl.com/products/assessments/skills-and-simulations/language-evaluation/", "type": "Language", "desc": "Written/oral language and communication tests."}, {"id": "EMAIL", "name": "Email Writing / Communication Tests", "url": "https://www.shl.com/shldirect/en/practice-tests/", "type": "Communication", "desc": "Short communication tasks such as email drafting."}, {"id": "VERIFY_TECH", "name": "Verify Technical Checking", "url": "https://www.shl.com/products/product-catalog/view/verify-technical-checking-next-generation/", "type": "Technical", "desc": "Checks technical knowledge and practical technical tasks."}, {"id": "GLOBAL", "name": "Global Skills Development Report", "url": "https://www.shl.com/products/product-catalog/view/global-skills-development-report/", "type": "Report", "desc": "High level skills benchmark and development insights."}, {"id": "ASSESS_CENTER", "name": "Assessment Centre Simulations", "url": "https://www.shl.com/products/assessments/assessment-centre-simulations/", "type": "Simulation", "desc": "Multi-exercise assessment centre style simulations."}, {"id": "LEAD", "name": "Leadership Assessment", "url": "https://www.shl.com/products/assessments/leadership-assessment/", "type": "Leadership", "desc": "Leadership potential and capability assessments."}]

def rule_recommend(query, k=8):
    q = query.lower()
    # same heuristic as server-side generation - simplified mapping
    if any(t in q for t in ['developer','coding','python','java','sdlc','jira']):
        preferred = ['CODING','TECH','VERIFY_G','VERIFY_TECH','JFA','OPQ','SJT','LEAD']
    elif any(t in q for t in ['analyst','sql','data','excel','tableau']):
        preferred = ['VERIFY_G','JFA','VERIFY_TECH','OPQ','GLOBAL','SJT','MQ','LEAD']
    elif any(t in q for t in ['sales','business development','account manager']):
        preferred = ['SJT','OPQ','MQ','GLOBAL','EMAIL','JFA','LEAD','ASSESS_CENTER']
    elif any(t in q for t in ['content','copy','writer','marketing','push notification']):
        preferred = ['LANG','EMAIL','OPQ','SJT','MQ','JFA','GLOBAL','ASSESS_CENTER']
    elif any(t in q for t in ['customer support','call center','support executive','chat']):
        preferred = ['CALL','LANG','SJT','OPQ','MQ','EMAIL','JFA','ASSESS_CENTER']
    else:
        preferred = ['JFA','OPQ','VERIFY_G','SJT','MQ','GLOBAL','EMAIL','LANG']

    # pick top k with basic scoring
    results = []
    score = 1.0
    dec = 0.12
    for pid in preferred:
        for p in CATALOG:
            if p['id'] == pid:
                results.append({'name': p['name'], 'url': p['url'], 'type': p['type'], 'desc': p['desc'], 'score': round(score,3)})
                score = max(0.1, score - dec)
                break
        if len(results) >= k:
            break

    # pad if required
    if len(results) < k:
        for p in CATALOG:
            if all(r['url'] != p['url'] for r in results):
                results.append({'name': p['name'], 'url': p['url'], 'type': p['type'], 'desc': p['desc'], 'score': 0.1})
            if len(results) >= k: break
    return results

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json(force=True)
    q = data.get('query','')
    k = int(data.get('max_k',8))
    recs = rule_recommend(q,k=k)
    return jsonify({'query': q, 'recommendations': recs})

@app.route('/bulk_predict', methods=['POST'])
def bulk_predict():
    # Accept JSON body: { "queries": ["q1","q2", ...], "max_k": 8 }
    data = request.get_json(force=True)
    queries = data.get('queries', [])
    k = int(data.get('max_k',8))
    results = []
    for q in queries:
        recs = rule_recommend(q,k=k)
        results.append({'query': q, 'recommendations': recs})
    return jsonify({'results': results})

@app.route('/download_predictions', methods=['GET'])
def download_predictions():
    # serve the vipul_predictions.csv produced during generation
    p = Path(__file__).resolve().parent.parent / 'vipul_predictions.csv'
    # fallback to current working directory
    alt = Path('vipul_predictions.csv')
    target = p if p.exists() else (alt if alt.exists() else None)
    if target is None:
        return jsonify({'error':'predictions file not found'}), 404
    return send_file(str(target), as_attachment=True, download_name='vipul_predictions.csv')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
