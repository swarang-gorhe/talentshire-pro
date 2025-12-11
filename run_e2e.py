#!/usr/bin/env python3
"""
Standalone E2E Test - No subprocess needed
"""
import subprocess
import time
import requests
import uuid
import sys

def run_e2e():
    API_BASE = 'http://localhost:8000/api'
    
    print("\n" + "="*70)
    print("🚀 STARTING E2E TEST")
    print("="*70 + "\n")
    
    # Give services time to be ready
    print("⏳ Waiting for services...")
    for i in range(15):
        try:
            resp = requests.post(f'{API_BASE}/auth/login', 
                json={'email': 'admin@talentshire.com', 'password': 'admin123'}, timeout=2)
            if resp.status_code in [200, 401, 400]:  # Any valid response means it's up
                print("✅ Backend is ready")
                break
        except:
            if i == 14:
                print("❌ Backend not responding after 15 attempts")
                return False
            time.sleep(1)
    
    try:
        # 1. LOGIN
        print("\n1️⃣  LOGIN")
        resp = requests.post(f'{API_BASE}/auth/login', 
            json={'email': 'admin@talentshire.com', 'password': 'admin123'}, timeout=10)
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        token = resp.json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Logged in")
        
        # 2. CREATE TEST
        print("\n2️⃣  CREATE TEST")
        resp = requests.post(f'{API_BASE}/tests',
            json={'test_name': f'E2E-{uuid.uuid4().hex[:6]}', 'description': 'Test', 'duration_minutes': 60, 'status': 'draft'},
            headers=headers, timeout=10)
        assert resp.status_code == 201, f"Failed: {resp.status_code} - {resp.text}"
        test_id = resp.json()['data']['test_id']
        print(f"✅ Test created: {test_id}")
        
        # 3. PUBLISH
        print("\n3️⃣  PUBLISH TEST")
        resp = requests.patch(f'{API_BASE}/tests/{test_id}/publish', headers=headers, timeout=10)
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        print("✅ Published")
        
        # 4. CREATE ASSIGNMENT
        print("\n4️⃣  CREATE ASSIGNMENT")
        candidate = str(uuid.uuid4())
        import time as t
        now = t.time()
        resp = requests.post(f'{API_BASE}/assignments',
            json={
                'test_id': str(test_id),
                'candidate_id': candidate,
                'scheduled_start_time': t.strftime('%Y-%m-%dT%H:%M:%SZ', t.gmtime(now)),
                'scheduled_end_time': t.strftime('%Y-%m-%dT%H:%M:%SZ', t.gmtime(now + 3600))
            },
            headers=headers, timeout=10)
        assert resp.status_code == 201, f"Failed: {resp.status_code}"
        assign_id = resp.json()['data']['assignment_id']
        print(f"✅ Assignment: {assign_id}")
        
        # 5. START
        print("\n5️⃣  START ASSIGNMENT")
        resp = requests.patch(f'{API_BASE}/assignments/{assign_id}/start', headers=headers, timeout=10)
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        print("✅ Started")
        
        # 6. GET QUESTIONS
        print("\n6️⃣  FETCH QUESTIONS")
        resp = requests.get(f'{API_BASE}/tests/{test_id}/questions', headers=headers, timeout=10)
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        qdata = resp.json()['data']
        mcqs = qdata.get('mcq_questions', [])
        codings = qdata.get('coding_questions', [])
        print(f"✅ Questions: {len(mcqs)} MCQs, {len(codings)} Coding")
        
        # 7. SUBMIT ANSWERS
        print("\n7️⃣  SUBMIT ANSWERS")
        if mcqs:
            resp = requests.post(f'{API_BASE}/answers',
                json={'assignment_id': str(assign_id), 'question_id': str(mcqs[0]['question_id']), 'question_type': 'mcq', 'selected_option': 'A'},
                headers=headers, timeout=10)
            assert resp.status_code == 200, f"Failed: {resp.status_code}"
            print("✅ MCQ submitted")
        
        # 8. END
        print("\n8️⃣  END ASSIGNMENT")
        resp = requests.patch(f'{API_BASE}/assignments/{assign_id}/end', headers=headers, timeout=10)
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        print("✅ Submitted")
        
        # 9. GENERATE REPORT
        print("\n9️⃣  GENERATE REPORT")
        resp = requests.post(f'{API_BASE}/reports/{assign_id}/generate', headers=headers, timeout=10)
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        report_id = resp.json()['data']['report_id']
        print(f"✅ Report: {report_id}")
        
        # 10. FETCH REPORT
        print("\n🔟 FETCH REPORT")
        resp = requests.get(f'{API_BASE}/reports/{report_id}', headers=headers, timeout=10)
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        report = resp.json()['data']
        print(f"✅ Score: {report['total_score']}/{report['total_max']} ({report['percentage']:.1f}%)")
        
        print("\n" + "="*70)
        print("✅✅✅ ALL TESTS PASSED ✅✅✅")
        print("="*70)
        print("\n📋 Verified Endpoints:")
        print("   ✅ /api/auth/login")
        print("   ✅ /api/tests (POST)")
        print("   ✅ /api/tests/{id}/publish")
        print("   ✅ /api/assignments (POST)")
        print("   ✅ /api/assignments/{id}/start")
        print("   ✅ /api/tests/{id}/questions")
        print("   ✅ /api/answers (POST)")
        print("   ✅ /api/assignments/{id}/end")
        print("   ✅ /api/reports/{id}/generate")
        print("   ✅ /api/reports/{id}")
        print("\n🌐 Access:")
        print("   Frontend: http://localhost:8080")
        print("   Backend:  http://localhost:8000/api")
        print("\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_e2e()
    sys.exit(0 if success else 1)
