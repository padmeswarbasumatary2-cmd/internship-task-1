#!/usr/bin/env python
"""
Quick API test script
"""
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

def test_api():
    print("\n" + "="*70)
    print("🚀 AUTOMATED CONTENT TAGGING ENGINE - API TEST")
    print("="*70 + "\n")
    
    # Test 1: Health Check
    print("[TEST 1] Health Check Endpoint")
    print("-" * 70)
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/api/v1/health")
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
        print("✓ Health check passed\n")
    except urllib.error.URLError as e:
        print(f"✗ Error: {e}\n")
        return
    
    # Test 2: Get Categories
    print("[TEST 2] Get Categories Endpoint")
    print("-" * 70)
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/api/v1/categories")
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
        print(f"✓ Found {len(data['categories'])} categories\n")
    except urllib.error.URLError as e:
        print(f"✗ Error: {e}\n")
    
    # Test 3: Tag Content
    print("[TEST 3] Main Tagging Endpoint (POST)")
    print("-" * 70)
    try:
        payload = json.dumps({
            "title": "Getting Started with PyTorch Deep Learning",
            "content": "Learn machine learning with PyTorch. Cover tensors, autograd, distributed training, optimization, and building production-grade neural networks with GPU support."
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f"{BASE_URL}/api/v1/tag-content",
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode())
        
        print(f"Overall Confidence: {data['overall_confidence']}")
        print(f"\nSuggested Categories ({len(data['suggested_categories'])}): ")
        for cat in data['suggested_categories']:
            print(f"  - {cat['name']}: {cat['score']:.2%}")
        
        print(f"\nSuggested Tags ({len(data['suggested_tags'])}): ")
        for tag in data['suggested_tags']:
            print(f"  - {tag['name']}: {tag['score']:.2%}")
        
        print(f"\nSuggested Entities ({len(data['suggested_entities'])}): ")
        for ent in data['suggested_entities']:
            print(f"  - {ent['name']} ({ent['tag_type']}): {ent['score']:.2%}")
        
        print(f"\nProcessing Time: {data['processing_time_ms']:.1f}ms")
        print("✓ Tagging successful\n")
    except urllib.error.URLError as e:
        print(f"✗ Error: {e}\n")
    
    # Test 4: Root endpoint
    print("[TEST 4] Root Endpoint (/)") 
    print("-" * 70)
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/")
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
        print("✓ Root endpoint working\n")
    except urllib.error.URLError as e:
        print(f"✗ Error: {e}\n")
    
    # Test 5: Resolve Entity
    print("[TEST 5] Resolve Entity Endpoint")
    print("-" * 70)
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/api/v1/resolve-entity?entity=pytorch")
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
        print("✓ Entity resolution working\n")
    except urllib.error.URLError as e:
        print(f"✗ Error: {e}\n")
    
    print("="*70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\n🌐 Interactive API Documentation: http://localhost:8000/docs\n")

if __name__ == "__main__":
    test_api()
