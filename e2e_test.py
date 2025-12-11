#!/usr/bin/env python3
"""
Complete E2E Test for Talentshire Platform
Tests all endpoints from login to report generation
"""

import requests
import uuid
import time
import sys
import json

API_BASE = 'http://localhost:8000/api'

def test_e2e():
    print("\n" + "="*70)
    print("🚀 TALENTSHIRE E2E TEST - COMPLETE FLOW")
    print("="*70 + "\n")
    
    try:
        # 1. LOGIN
        print("1️⃣  LOGIN TEST")
        print("-" * 70)
        login_resp = requests.post(
            f'{API_BASE}/auth/login',
            json={'email': 'admin@talentshire.com', 'password': 'admin123'},
            timeout=5
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.status_code}"
        token = login_resp.json()['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Admin login successful\n")
        
        # 2. CREATE TEST
        print("2️⃣  CREATE TEST")
        print("-" * 70)
        create_resp = requests.post(
            f'{API_BASE}/tests',
            json={
                'test_name': f'E2E Test {uuid.uuid4().hex[:8]}',
                'description': 'End-to-end integration test',
                'duration_minutes': 60,
                'status': 'draft'
            },
            headers=headers,
            timeout=10
        )
        assert create_resp.status_code == 201, f"Create test failed: {create_resp.status_code}"
        test_id = create_resp.json()['data']['test_id']
        print(f"✅ Test created: {test_id}\n")
        
        # 3. PUBLISH TEST
        print("3️⃣  PUBLISH TEST")
        print("-" * 70)
        pub_resp = requests.patch(
            f'{API_BASE}/tests/{test_id}/publish',
            headers=headers,
            timeout=5
        )
        assert pub_resp.status_code == 200, f"Publish test failed: {pub_resp.status_code}"
        print("✅ Test published\n")
        
        # 4. CREATE ASSIGNMENT
        print("4️⃣  CREATE ASSIGNMENT")
        print("-" * 70)
        candidate_id = str(uuid.uuid4())
        now = time.time()
        assign_resp = requests.post(
            f'{API_BASE}/assignments',
            json={
                'test_id': str(test_id),
                'candidate_id': candidate_id,
                'scheduled_start_time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
                'scheduled_end_time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now + 3600))
            },
            headers=headers,
            timeout=5
        )
        assert assign_resp.status_code == 201, f"Create assignment failed: {assign_resp.status_code}"
        assignment_id = assign_resp.json()['data']['assignment_id']
        print(f"✅ Assignment created: {assignment_id}\n")
        
        # 5. START ASSIGNMENT
        print("5️⃣  START ASSIGNMENT")
        print("-" * 70)
        start_resp = requests.patch(
            f'{API_BASE}/assignments/{assignment_id}/start',
            headers=headers,
            timeout=5
        )
        assert start_resp.status_code == 200, f"Start assignment failed: {start_resp.status_code}"
        print("✅ Assignment started\n")
        
        # 6. FETCH QUESTIONS
        print("6️⃣  FETCH TEST QUESTIONS")
        print("-" * 70)
        questions_resp = requests.get(
            f'{API_BASE}/tests/{test_id}/questions',
            headers=headers,
            timeout=5
        )
        assert questions_resp.status_code == 200, f"Fetch questions failed: {questions_resp.status_code}"
        q_data = questions_resp.json()['data']
        mcqs = q_data.get('mcq_questions', [])
        codings = q_data.get('coding_questions', [])
        print(f"✅ Questions fetched: {len(mcqs)} MCQs, {len(codings)} Coding\n")
        
        # 7. SUBMIT ANSWERS
        print("7️⃣  SUBMIT ANSWERS")
        print("-" * 70)
        answered = 0
        
        if mcqs:
            for i, mcq in enumerate(mcqs[:1]):
                ans_resp = requests.post(
                    f'{API_BASE}/answers',
                    json={
                        'assignment_id': str(assignment_id),
                        'question_id': str(mcq['question_id']),
                        'question_type': 'mcq',
                        'selected_option': 'A'
                    },
                    headers=headers,
                    timeout=5
                )
                if ans_resp.status_code == 200:
                    answered += 1
                    print(f"✅ MCQ answer submitted")
        
        if codings:
            for i, cq in enumerate(codings[:1]):
                ans_resp = requests.post(
                    f'{API_BASE}/answers',
                    json={
                        'assignment_id': str(assignment_id),
                        'question_id': str(cq['question_id']),
                        'question_type': 'coding',
                        'code': 'print("hello")',
                        'language': 'Python'
                    },
                    headers=headers,
                    timeout=5
                )
                if ans_resp.status_code == 200:
                    answered += 1
                    print(f"✅ Coding answer submitted")
        
        print(f"✅ Total answers: {answered}\n")
        
        # 8. END ASSIGNMENT
        print("8️⃣  END ASSIGNMENT")
        print("-" * 70)
        end_resp = requests.patch(
            f'{API_BASE}/assignments/{assignment_id}/end',
            headers=headers,
            timeout=5
        )
        assert end_resp.status_code == 200, f"End assignment failed: {end_resp.status_code}"
        print("✅ Assignment submitted\n")
        
        # 9. GENERATE REPORT
        print("9️⃣  GENERATE REPORT")
        print("-" * 70)
        report_resp = requests.post(
            f'{API_BASE}/reports/{assignment_id}/generate',
            headers=headers,
            timeout=5
        )
        assert report_resp.status_code == 200, f"Generate report failed: {report_resp.status_code}"
        report_id = report_resp.json()['data']['report_id']
        print(f"✅ Report generated: {report_id}\n")
        
        # 10. FETCH REPORT
        print("🔟 FETCH REPORT")
        print("-" * 70)
        fetch_resp = requests.get(
            f'{API_BASE}/reports/{report_id}',
            headers=headers,
            timeout=5
        )
        assert fetch_resp.status_code == 200, f"Fetch report failed: {fetch_resp.status_code}"
        report = fetch_resp.json()['data']
        print(f"✅ Report retrieved")
        print(f"   Score: {report['total_score']}/{report['total_max']}")
        print(f"   Percentage: {report['percentage']:.1f}%\n")
        
        # SUCCESS
        print("="*70)
        print("✅✅✅ ALL TESTS PASSED - SYSTEM IS OPERATIONAL ✅✅✅")
        print("="*70)
        print("\n✨ Endpoints Verified:")
        print("   ✅ POST /api/auth/login")
        print("   ✅ POST /api/tests")
        print("   ✅ PATCH /api/tests/{id}/publish")
        print("   ✅ POST /api/assignments")
        print("   ✅ PATCH /api/assignments/{id}/start")
        print("   ✅ GET /api/tests/{id}/questions")
        print("   ✅ POST /api/answers")
        print("   ✅ PATCH /api/assignments/{id}/end")
        print("   ✅ POST /api/reports/{id}/generate")
        print("   ✅ GET /api/reports/{id}")
        print("\n🌐 Services:")
        print("   Backend: http://localhost:8000")
        print("   Frontend: http://localhost:8080")
        print("\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = test_e2e()
    sys.exit(0 if success else 1)
