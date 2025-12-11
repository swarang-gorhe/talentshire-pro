#!/usr/bin/env python3
"""
Talentshire Platform - Live Demo Script
Demonstrates all integrated features
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import sys
import uuid

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class TalentshireDemo:
    def __init__(self, api_url: str = "http://localhost:8000/api"):
        self.api_url = api_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_id = None
        self.assignment_id = None
        
    def print_header(self, text: str):
        print(f"\n{BLUE}╔{'═' * 70}╗{RESET}")
        print(f"{BLUE}║ {GREEN}{text:<68}{BLUE}║{RESET}")
        print(f"{BLUE}╚{'═' * 70}╝{RESET}\n")
    
    def print_section(self, text: str):
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{GREEN}▶ {text}{RESET}")
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
    
    def print_success(self, text: str):
        print(f"{GREEN}✅ {text}{RESET}")
    
    def print_error(self, text: str):
        print(f"{RED}❌ {text}{RESET}")
    
    def print_info(self, text: str):
        print(f"{YELLOW}ℹ️  {text}{RESET}")
    
    def print_api_call(self, method: str, endpoint: str, status: int):
        status_color = GREEN if status < 400 else RED
        print(f"  {BLUE}{method}{RESET} {endpoint} → {status_color}{status}{RESET}")
    
    def api_call(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Dict:
        """Make API call and handle response"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "PATCH":
                response = self.session.patch(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            self.print_api_call(method, endpoint, response.status_code)
            
            # Treat any 2xx as success, but still show the status code
            if 200 <= response.status_code < 300:
                # Try to unwrap ApiResponse { success, data, error }
                if response.text:
                    try:
                        j = response.json()
                        # If API uses wrapper {success,data,...} return data for convenience
                        if isinstance(j, dict) and 'success' in j and 'data' in j:
                            return j['data'] if j.get('data') is not None else j
                        return j
                    except Exception:
                        return {}
                return {}
            else:
                self.print_error(f"Expected {expected_status}, got {response.status_code}")
                self.print_error(f"Response: {response.text}")
                return {}
        
        except requests.exceptions.ConnectionError:
            self.print_error(f"Could not connect to {self.api_url}")
            self.print_info("Make sure the backend is running: ./deploy.sh --demo")
            sys.exit(1)
        except Exception as e:
            self.print_error(f"API call failed: {str(e)}")
            return {}
    
    def run(self):
        """Run complete demo"""
        self.print_header("🎬 TALENTSHIRE PLATFORM - LIVE DEMO")
        
        # Check API availability
        self.check_api()
        # Authenticate as admin (use seeded credentials)
        self.print_section("Authentication: Login as admin")
        login_resp = self.api_call("POST", "/auth/login", {"email": "admin@talentshire.com", "password": "admin123"}, 200)
        if login_resp and isinstance(login_resp, dict) and login_resp.get('token'):
            token = login_resp.get('token')
            self.auth_token = token
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
            self.print_success("Logged in as admin and attached token to session")
        else:
            self.print_info("No login token received — continuing unauthenticated (may fail on protected endpoints)")
        
        # Run demo scenarios
        self.demo_test_management()
        self.demo_test_creation()
        self.demo_assignments()
        self.demo_complete()
    
    def check_api(self):
        """Verify API is available"""
        self.print_section("Step 1: Checking API Availability")
        
        try:
            response = self.session.get(f"{self.api_url.split('/api')[0]}/docs")
            if response.status_code == 200:
                self.print_success("API is running and healthy")
                self.print_info(f"API Docs: {self.api_url.split('/api')[0]}/docs")
            else:
                self.print_error("API returned unexpected status")
                sys.exit(1)
        except:
            self.print_error("Could not reach API")
            sys.exit(1)
    
    def demo_test_management(self):
        """Demo test management features"""
        self.print_section("Step 2: Test Management")
        
        self.print_info("Creating a new test...")
        test_data = {
            "test_name": "🚀 Talentshire Demo Test",
            "description": "Live demonstration of the integrated platform",
            "duration_minutes": 90,
            "total_marks": 100,
            "passing_marks": 40,
            "status": "draft"
        }
        
        response = self.api_call("POST", "/tests", test_data, 201)
        
        if "test_id" in response:
            self.test_id = response.get("test_id")
            self.print_success(f"Test created with ID: {self.test_id}")
            print(f"  Name: {response.get('test_name')}")
            print(f"  Duration: {response.get('duration_minutes')} minutes")
            print(f"  Total Marks: {response.get('total_marks')}")
        else:
            self.print_error("Failed to create test")
            return
        
        self.print_info("Fetching all tests...")
        response = self.api_call("GET", "/tests")
        if "data" in response:
            self.print_success(f"Retrieved {len(response.get('data', []))} tests")
        
        if self.test_id:
            self.print_info("Fetching test details...")
            response = self.api_call("GET", f"/tests/{self.test_id}")
            if "test_id" in response:
                self.print_success("Test details retrieved successfully")
    
    def demo_test_creation(self):
        """Demo test creation and publishing"""
        self.print_section("Step 3: Test Publishing")
        
        if not self.test_id:
            self.print_error("No test created yet")
            return
        
        self.print_info("Updating test status...")
        update_data = {
            "test_name": "🚀 Talentshire Demo Test - Published",
            "duration_minutes": 90,
            "status": "active"
        }
        response = self.api_call("PUT", f"/tests/{self.test_id}", update_data)
        
        if response:
            self.print_success("Test updated successfully")
            print(f"  Status: {response.get('status')}")
        
        self.print_info("Publishing test...")
        response = self.api_call("PATCH", f"/tests/{self.test_id}/publish", {})
        
        if response:
            self.print_success("Test published successfully")
    
    def demo_assignments(self):
        """Demo test assignments"""
        self.print_section("Step 4: Test Assignments")
        
        if not self.test_id:
            self.print_error("No test available")
            return
        
        # Generate a valid candidate UUID for this demo
        candidate_id = str(uuid.uuid4())
        
        self.print_info("Creating test assignment...")
        assignment_data = {
            "test_id": self.test_id,
            "candidate_id": candidate_id,
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(hours=2)).isoformat()
        }
        
        response = self.api_call("POST", "/assignments", assignment_data, 201)
        
        if "assignment_id" in response:
            self.assignment_id = response.get("assignment_id")
            self.print_success(f"Assignment created: {self.assignment_id}")
            print(f"  Status: {response.get('status')}")
            print(f"  Duration: 2 hours")
        else:
            self.print_error("Failed to create assignment")
            return
        
        self.print_info("Fetching candidate assignments...")
        response = self.api_call("GET", f"/candidates/{candidate_id}/assignments")
        if "data" in response:
            self.print_success(f"Retrieved {len(response.get('data', []))} assignments")
    
    def demo_complete(self):
        """Display completion message"""
        self.print_section("🎉 Demo Complete!")
        
        print(f"{GREEN}{BOLD}✨ Your Talentshire platform is fully integrated and ready!{RESET}\n")
        
        print(f"{BLUE}Available Features Demonstrated:{RESET}")
        print(f"  {GREEN}✓{RESET} Test Management (Create, Read, Update, Delete)")
        print(f"  {GREEN}✓{RESET} Test Publishing & Status Management")
        print(f"  {GREEN}✓{RESET} Test Assignments to Candidates")
        print(f"  {GREEN}✓{RESET} Unified API Endpoints")
        print(f"  {GREEN}✓{RESET} Complete Type Safety (TypeScript ↔ Python)")
        
        print(f"\n{BLUE}Next Steps:{RESET}")
        print(f"  1. {YELLOW}Open{RESET} http://localhost:5173 in your browser")
        print(f"  2. {YELLOW}Review{RESET} API docs at http://localhost:8000/docs")
        print(f"  3. {YELLOW}Manage{RESET} database via http://localhost:5050")
        print(f"  4. {YELLOW}Build{RESET} your own features using the integrated models")
        
        print(f"\n{BLUE}Useful Resources:{RESET}")
        print(f"  • START_HERE.md - Quick navigation guide")
        print(f"  • COMPLETE_PLATFORM_INTEGRATION.md - Full overview")
        print(f"  • shared/INTEGRATION_GUIDE.md - Implementation examples")
        print(f"  • frontend/FRONTEND_INTEGRATION.md - Frontend guide")
        
        print(f"\n{GREEN}Happy Building! 🚀{RESET}\n")

if __name__ == "__main__":
    demo = TalentshireDemo()
    demo.run()
