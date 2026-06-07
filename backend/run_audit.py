"""Final integration audit script."""
import urllib.request
import json

base = 'http://localhost:8005'
results = {}


def check(name, url, method='GET', data=None, expect_key=None):
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode()
        res = urllib.request.urlopen(req)
        body = json.loads(res.read().decode())
        if expect_key:
            val = body.get(expect_key)
            results[name] = ('PASS', str(val)[:80])
        else:
            results[name] = ('PASS', str(list(body.keys()) if isinstance(body, dict) else f'{len(body)} items')[:80])
    except Exception as e:
        results[name] = ('FAIL', str(e)[:80])


# 1. Scanners list
check('GET /api/data/scanners', f'{base}/api/data/scanners?limit=5', expect_key='total')
# 2. Dashboard summary
check('GET /api/analytics/summary', f'{base}/api/analytics/summary')
# 3. Risk distribution
check('GET /api/analytics/risk-distribution', f'{base}/api/analytics/risk-distribution')
# 4. Correlations
check('GET /api/analytics/correlations', f'{base}/api/analytics/correlations')
# 5. Age distribution
check('GET /api/analytics/age-distribution', f'{base}/api/analytics/age-distribution')
# 6. Risk by age
check('GET /api/analytics/risk-by-age', f'{base}/api/analytics/risk-by-age')
# 7. Modules distribution
check('GET /api/analytics/modules', f'{base}/api/analytics/modules')
# 8. ML models
check('GET /api/ml/models', f'{base}/api/ml/models', expect_key='best_model')

# 9. Prediction risk
pred_payload = {
    'scanner_data': {
        'Age': 9, 'Maintenance_Cost': 5850, 'Downtime': 12.0,
        'Maintenance_Frequency': 8, 'Failure_Event_Count': 6,
        'MTBF': 30.0, 'Failure_Rate': 0.4, 'Downtime_Per_Failure': 2.0,
        'Maintenance_Intensity': 0.7, 'Affected_Module': 'Cooling / Tube'
    },
    'technician_name': 'Test Audit', 'technician_role': 'technician'
}
check('POST /api/predict/risk', f'{base}/api/predict/risk', method='POST', data=pred_payload, expect_key='prediction_id')

# 10. History
check('GET /api/predict/history', f'{base}/api/predict/history?limit=5')

# 11. SHAP for prediction 1
check('GET /api/predict/1/shap', f'{base}/api/predict/1/shap', expect_key='status')

# 12. PDF generation
try:
    req = urllib.request.Request(f'{base}/api/predict/1/report.pdf')
    res = urllib.request.urlopen(req)
    content = res.read()
    results['GET /api/predict/1/report.pdf'] = ('PASS', f'PDF: {len(content)} bytes')
except Exception as e:
    results['GET /api/predict/1/report.pdf'] = ('FAIL', str(e)[:80])

# 13. Expert module
expert_payload = {
    'scanner_data': {
        'Age': 9, 'Maintenance_Cost': 5850,
        'Failure_Event_Count': 6, 'MTBF': 30.0, 'Failure_Risk': 'High'
    }
}
check('POST /api/predict/module', f'{base}/api/predict/module', method='POST', data=expert_payload, expect_key='predicted_module')

print()
print('=' * 70)
print('FINAL INTEGRATION AUDIT RESULTS')
print('=' * 70)
passed = failed = 0
for name, (status, detail) in results.items():
    icon = '[OK]' if status == 'PASS' else '[FAIL]'
    print(f'{icon}  {status:<4}  {name:<42}  {detail}')
    if status == 'PASS':
        passed += 1
    else:
        failed += 1
print('=' * 70)
print(f'TOTAL: {passed} PASSED, {failed} FAILED')
verdict = 'ALL SYSTEMS OPERATIONAL' if failed == 0 else f'{failed} ISSUE(S) REQUIRE ATTENTION'
print(f'STATUS: {verdict}')
print('=' * 70)
