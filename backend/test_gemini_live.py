import urllib.request
import json

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/test-generation/generate',
    data=json.dumps({
        'requirement_ids': ['BRK-REQ-101'],
        'categories': ['FUNCTIONAL', 'FAULT_INJECTION'],
        'tests_per_requirement': 2,
        'provider': 'gemini'
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Generation Success!")
        print(f"Provider: {data.get('provider')}, Model: {data.get('model')}")
        print(f"Generated {data.get('generated_tests_count')} tests")
        print(f"Validation Summary: {data.get('validation_summary')}")
        for tc in data.get('test_cases', []):
            print(f"  - {tc.get('code')}: {tc.get('title')} [{tc.get('validation_status')}]")
except Exception as e:
    print(f"Request error: {e}")
