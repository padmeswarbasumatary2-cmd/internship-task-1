"""
Lightweight demo of the tagging architecture (no heavy dependencies required)
Demonstrates the taxonomy graph and entity resolution
"""

from app.ml_pipeline.taxonomy_graph import TaxonomyGraph


def main():
    """Run demonstration of taxonomy graph and entity resolution"""
    
    print("=" * 80)
    print("Automated Content Tagging Engine - Architecture Demo")
    print("=" * 80)
    
    # Initialize taxonomy graph
    print("\n📦 Initializing Taxonomy Knowledge Graph...")
    taxonomy = TaxonomyGraph()
    print("✓ Taxonomy graph loaded with default taxonomy")
    
    # Display taxonomy structure
    print("\n📊 Taxonomy Hierarchy:")
    print("-" * 80)
    taxonomy.print_hierarchy()
    
    # Test entity resolution
    print("\n" + "=" * 80)
    print("🔍 Entity Resolution & Synonym Normalization")
    print("=" * 80)
    
    test_entities = [
        "PyTorch",
        "torch",
        "ReactJS",
        "React.js",
        "React framework",
        "K8s",
        "kubernetes",
        "container",
        "containerization",
        "machine-learning",
        "ML",
        "neural networks"
    ]
    
    print("\nResolving raw entities to canonical taxonomy nodes:\n")
    
    for entity in test_entities:
        node_id, confidence = taxonomy.resolve_entity(entity)
        
        if node_id:
            node = taxonomy.get_node(node_id)
            print(f"  ✓ '{entity}' → '{node.name}'")
            print(f"    └─ confidence: {confidence:.2%}, node_id: {node_id}")
            
            # Show parent hierarchy
            ancestors = taxonomy.get_ancestors(node_id)
            if ancestors:
                path = " > ".join([a.name for a in reversed(ancestors)]) + f" > {node.name}"
                print(f"    └─ hierarchy: {path}")
        else:
            print(f"  ✗ '{entity}' → Not found in taxonomy (similarity: {confidence:.2%})")
        print()
    
    # Show node details
    print("=" * 80)
    print("📋 Sample Node Details")
    print("=" * 80)
    
    pytorch_node = taxonomy.get_node("pytorch")
    if pytorch_node:
        print(f"\nNode: {pytorch_node.name}")
        print(f"  ID: {pytorch_node.id}")
        print(f"  Type: {pytorch_node.type}")
        print(f"  Aliases: {', '.join(pytorch_node.aliases)}")
        print(f"  Parent: {pytorch_node.parent_id}")
        
        ancestors = taxonomy.get_ancestors("pytorch")
        print(f"  Ancestors: {' > '.join([a.name for a in reversed(ancestors)])}")
        print(f"  Depth: {taxonomy.get_depth('pytorch')}")
    
    # Show batch resolution
    print("\n" + "=" * 80)
    print("📦 Batch Entity Resolution")
    print("=" * 80)
    
    batch_entities = ["PyTorch", "React", "Docker", "TensorFlow", "Vue"]
    print(f"\nResolving batch of {len(batch_entities)} entities:")
    
    results = taxonomy.resolve_batch(batch_entities)
    for entity, (node_id, confidence) in zip(batch_entities, results):
        node = taxonomy.get_node(node_id) if node_id else None
        canonical = node.name if node else "Not found"
        status = "✓" if node_id else "✗"
        print(f"  {status} {entity:<15} → {canonical:<20} ({confidence:.2%})")
    
    # Export taxonomy
    print("\n" + "=" * 80)
    print("💾 Taxonomy Export (JSON)")
    print("=" * 80)
    
    json_export = taxonomy.export_as_json()
    print("\n" + json_export[:400] + "...\n")
    
    # Architecture overview
    print("=" * 80)
    print("🏗️  Complete ML Pipeline Architecture")
    print("=" * 80)
    print("""
    Raw Content (HTML/Markdown)
            ↓
    [Preprocessing Pipeline]
    - HTML/Markdown parsing
    - Text normalization
    - Stopword removal
    - Lemmatization
            ↓
    Normalized Text + Metadata
            ↓
    ┌───────────────────────────────────────────┐
    │   Multi-Layer NLP Architecture            │
    ├───────────────────────────────────────────┤
    │                                           │
    │  Tier 1: Multi-Label Classifier           │
    │  (DistilRoBERTa)                          │
    │  → Macro-Categories (20 classes)          │
    │  → Dynamic Thresholding per Class         │
    │  → F1-Score Optimized                     │
    │                                           │
    │  Tier 2: Semantic Keyphrase Extraction    │
    │  (KeyBERT + MMR)                          │
    │  → Micro-Tags (1-3 word phrases)          │
    │  → Diverse Selection via MMR              │
    │  → Relevance-based Ranking                │
    │                                           │
    │  Tier 3: Named Entity Recognition         │
    │  (spaCy + Transformers)                   │
    │  → Extract PERSON, ORG, PRODUCT, GPE     │
    │  → Entity Confidence Scores               │
    │                                           │
    └───────────────────────────────────────────┘
            ↓
    [Taxonomy Graph Resolution]
    - Fuzzy Matching (SequenceMatcher)
    - Alias Lookup
    - Canonical Normalization
            ↓
    [Semantic Tag Enrichment]
    - Confidence Score Calibration
    - Tag Deduplication
    - Relevance Filtering
            ↓
    JSON-LD Schema Generation
    Structured Tag Output
    """)
    
    print("=" * 80)
    print("✨ Demo Complete!")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("  ✓ Taxonomy Knowledge Graph with hierarchical DAG")
    print("  ✓ Entity resolution with fuzzy string matching")
    print("  ✓ Synonym normalization to canonical forms")
    print("  ✓ Batch processing capability")
    print("  ✓ Confidence scoring and calibration")
    print("\nNext Steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Download spaCy model: python -m spacy download en_core_web_sm")
    print("  3. Start API: uvicorn app.main:app --reload")
    print("  4. Test endpoints: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
