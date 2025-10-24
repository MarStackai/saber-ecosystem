#!/usr/bin/env python3
"""
Automated Test Suite for FIT Intelligence System
Tests all critical requirements
"""

import json
import requests
import re
from typing import Dict, List, Tuple

class FITSystemTester:
    def __init__(self, api_base: str = "http://localhost:5000"):
        self.api_base = api_base
        self.results = {"passed": 0, "failed": 0, "tests": []}
    
    def test_geographic_accuracy(self) -> Tuple[bool, str]:
        """Test that geographic queries return correct postcodes"""
        tests = [
            {
                "query": "wind sites near Aberdeen",
                "must_contain": ["AB"],
                "must_not_contain": ["ML", "BD", "YO", "G1", "EH"],
                "location": "Aberdeen"
            },
            {
                "query": "solar in Yorkshire", 
                "must_contain": ["YO", "HU", "LS", "BD", "WF", "S", "DN"],
                "must_not_contain": ["AB", "ML", "G", "EH"],
                "location": "Yorkshire"
            },
            {
                "query": "wind farms in Edinburgh",
                "must_contain": ["EH"],
                "must_not_contain": ["AB", "G", "ML", "YO"],
                "location": "Edinburgh"
            }
        ]
        
        passed = True
        messages = []
        
        for test in tests:
            response = self._query_api(test["query"])
            
            # Check postcodes
            found_correct = any(pc in response for pc in test["must_contain"])
            found_incorrect = any(pc in response for pc in test["must_not_contain"])
            
            if not found_correct and "No matching" not in response:
                passed = False
                messages.append(f"❌ {test['location']}: No correct postcodes found")
            elif found_incorrect:
                passed = False
                wrong = [pc for pc in test["must_not_contain"] if pc in response]
                messages.append(f"❌ {test['location']}: Wrong postcodes {wrong}")
            else:
                messages.append(f"✅ {test['location']}: Geographic accuracy OK")
        
        return passed, "\n".join(messages)
    
    def test_fit_id_inclusion(self) -> Tuple[bool, str]:
        """Test that FIT IDs are always included"""
        queries = [
            "wind sites over 500kw",
            "solar farms in Scotland",
            "what is site 1585"
        ]
        
        passed = True
        messages = []
        
        for query in queries:
            response = self._query_api(query)
            
            if "No matching" in response:
                messages.append(f"ℹ️ '{query}': No results")
            elif "FIT ID" in response or "Site" in response:
                messages.append(f"✅ '{query}': FIT IDs included")
            else:
                passed = False
                messages.append(f"❌ '{query}': No FIT IDs found")
        
        return passed, "\n".join(messages)
    
    def test_context_handling(self) -> Tuple[bool, str]:
        """Test conversation context"""
        # First query
        response1 = self._query_api("wind farms over 1MW")
        
        # Follow-up
        response2 = self._query_api("what are their FIT IDs?")
        
        if "FIT ID" in response2 or "previous" in response2.lower():
            return True, "✅ Context handling works"
        else:
            return False, "❌ Context not maintained"
    
    def test_specific_fit_id(self) -> Tuple[bool, str]:
        """Test specific FIT ID lookups"""
        test_ids = [1585, 7312]
        passed = True
        messages = []
        
        for fit_id in test_ids:
            response = self._query_api(f"what is the rate for site {fit_id}")
            
            if "p/kWh" in response:
                messages.append(f"✅ FIT ID {fit_id}: Found rate")
            else:
                passed = False
                messages.append(f"❌ FIT ID {fit_id}: Rate not found")
        
        return passed, "\n".join(messages)
    
    def test_no_hallucination(self) -> Tuple[bool, str]:
        """Test that system doesn't make up data"""
        response = self._query_api("what is FIT ID 99999999")
        
        if "not found" in response.lower() or "no matching" in response.lower():
            return True, "✅ Correctly reports non-existent data"
        else:
            return False, "❌ May be hallucinating data"
    
    def _query_api(self, query: str) -> str:
        """Query the API"""
        try:
            response = requests.post(
                f"{self.api_base}/api/chat",
                json={"message": query},
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"API Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("=" * 60)
        print("FIT INTELLIGENCE SYSTEM TEST SUITE")
        print("=" * 60)
        
        tests = [
            ("Geographic Accuracy", self.test_geographic_accuracy),
            ("FIT ID Inclusion", self.test_fit_id_inclusion),
            ("Context Handling", self.test_context_handling),
            ("Specific FIT IDs", self.test_specific_fit_id),
            ("No Hallucination", self.test_no_hallucination)
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 Testing: {test_name}")
            print("-" * 40)
            
            try:
                passed, message = test_func()
                print(message)
                
                if passed:
                    self.results["passed"] += 1
                else:
                    self.results["failed"] += 1
                
                self.results["tests"].append({
                    "name": test_name,
                    "passed": passed,
                    "message": message
                })
            except Exception as e:
                print(f"❌ Test failed with error: {str(e)}")
                self.results["failed"] += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        total = self.results["passed"] + self.results["failed"]
        if total > 0:
            success_rate = (self.results["passed"] / total) * 100
            print(f"✅ Passed: {self.results['passed']}")
            print(f"❌ Failed: {self.results['failed']}")
            print(f"📊 Success Rate: {success_rate:.1f}%")
            
            if success_rate == 100:
                print("\n🎉 ALL TESTS PASSED! System ready for production.")
            elif success_rate >= 80:
                print("\n⚠️ Most tests passed but needs improvement.")
            else:
                print("\n🚨 CRITICAL: System needs significant work.")
        
        # Save results
        with open("test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("\n📁 Results saved to test_results.json")

if __name__ == "__main__":
    tester = FITSystemTester()
    tester.run_all_tests()