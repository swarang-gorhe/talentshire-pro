#!/bin/bash

# Talentshire E2E Quick Test Script
# Run this to verify the entire system is working

set -e

echo ""
echo "=========================================="
echo "🚀 TALENTSHIRE E2E TEST"
echo "=========================================="
echo ""

# Start backend
echo "⏳ Starting backend on localhost:8000..."
cd /Users/swarang.gorhe/Documents/Talentshire-main
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 5

# Start frontend
echo "⏳ Starting frontend on localhost:8080..."
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 8

# Run E2E test
echo "⏳ Running E2E test..."
cd /Users/swarang.gorhe/Documents/Talentshire-main
python3 << 'TEST'
import requests, uuid, time as t, json

API='http://127.0.0.1:8000/api'
results = []

def test(name, func):
    try:
        func()
        results.append((name, True, None))
        print(f"✅ {name}")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"❌ {name}: {e}")

def login():
    r = requests.post(f'{API}/auth/login', json={'email': 'admin@talentshire.com', 'password': 'admin123'}, timeout=5)
    assert r.status_code == 200
    global token, h
    token = r.json()['data']['token']
    h = {'Authorization': f'Bearer {token}'}

def create_test():
    r = requests.post(f'{API}/tests', json={'test_name': f'E2E-{uuid.uuid4().hex[:6]}', 'description': 'Test', 'duration_minutes': 60, 'status': 'draft'}, headers=h, timeout=5)
    assert r.status_code == 201
    global test_id
    test_id = r.json()['data']['test_id']

def publish_test():
    r = requests.patch(f'{API}/tests/{test_id}/publish', headers=h, timeout=5)
    assert r.status_code == 200

def create_assignment():
    cand = str(uuid.uuid4())
    now = t.time()
    r = requests.post(f'{API}/assignments', json={'test_id': str(test_id), 'candidate_id': cand, 'scheduled_start_time': t.strftime('%Y-%m-%dT%H:%M:%SZ', t.gmtime(now)), 'scheduled_end_time': t.strftime('%Y-%m-%dT%H:%M:%SZ', t.gmtime(now + 3600))}, headers=h, timeout=5)
    assert r.status_code == 201
    global assign_id
    assign_id = r.json()['data']['assignment_id']

def start_assignment():
    r = requests.patch(f'{API}/assignments/{assign_id}/start', headers=h, timeout=5)
    assert r.status_code == 200

def get_questions():
    r = requests.get(f'{API}/tests/{test_id}/questions', headers=h, timeout=5)
    assert r.status_code == 200
    global q_data
    q_data = r.json()['data']

def submit_answer():
    mcqs = q_data.get('mcq_questions', [])
    if mcqs:
        r = requests.post(f'{API}/answers', json={'assignment_id': str(assign_id), 'question_id': str(mcqs[0]['question_id']), 'question_type': 'mcq', 'selected_option': 'A'}, headers=h, timeout=5)
        assert r.status_code == 200

def end_assignment():
    r = requests.patch(f'{API}/assignments/{assign_id}/end', headers=h, timeout=5)
    assert r.status_code == 200

def generate_report():
    r = requests.post(f'{API}/reports/{assign_id}/generate', headers=h, timeout=5)
    assert r.status_code == 200
    global report_id
    report_id = r.json()['data']['report_id']

def fetch_report():
    r = requests.get(f'{API}/reports/{report_id}', headers=h, timeout=5)
    assert r.status_code == 200
    global report_data
    report_data = r.json()['data']

print("\n📋 Running Tests:\n")
test("1. Login", login)
test("2. Create Test", create_test)
test("3. Publish Test", publish_test)
test("4. Create Assignment", create_assignment)
test("5. Start Assignment", start_assignment)
test("6. Get Questions", get_questions)
test("7. Submit Answer", submit_answer)
test("8. End Assignment", end_assignment)
test("9. Generate Report", generate_report)
test("10. Fetch Report", fetch_report)

print("\n" + "="*70)
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"Results: {passed}/{total} PASSED")

if passed == total:
    print("✅✅✅ ALL TESTS PASSED ✅✅✅")
    print(f"\nFinal Score: {report_data['total_score']}/{report_data['total_max']} ({report_data['percentage']:.1f}%)")
    print("\n🌐 Services:")
    print("  Frontend: http://localhost:8080")
    print("  Backend:  http://localhost:8000")
    print("\n🚀 System is OPERATIONAL and READY!\n")
else:
    print("\n❌ Some tests failed:")
    for name, ok, err in results:
        if not ok:
            print(f"  - {name}: {err}")
    print()
TEST

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $BACKEND_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true

echo ""
echo "✅ Test complete! Check results above."
echo ""
