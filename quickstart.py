"""
Quick start example demonstrating the tagging pipeline
"""
import asyncio
from app.services.tagging_service import TaggingService
from app.ml_pipeline.preprocessing import DocumentPreprocessor
from app.ml_pipeline.taxonomy_graph import TaxonomyGraph


async def main():
    """Run quick start example"""
    
    print("=" * 80)
    print("Automated Content Tagging Engine - Quick Start Example")
    print("=" * 80)
    
    # Initialize service
    print("\n📦 Initializing services...")
    service = TaggingService()
    
    if not service.models_loaded:
        print("❌ Models failed to load. Check dependencies.")
        print("Run: pip install -r requirements.txt && python -m spacy download en_core_web_sm")
        return
    
    # Example content
    content = {
        "title": "Getting Started with Distributed Training in PyTorch",
        "content": """
        In this article, we'll explore how to scale your PyTorch models across multiple GPUs 
        and machines using distributed training. PyTorch provides powerful tools for data parallelism
        and model parallelism, enabling efficient training of large neural networks.
        
        We'll cover:
        - Data parallelism with DataDistributedSampler
        - Distributed training with torch.distributed
        - Using PyTorch Lightning for simplified distributed training
        - Performance optimization techniques
        - Best practices for production deployment
        
        Kubernetes deployment is also discussed for containerized training jobs.
        """
    }
    
    print(f"\n📄 Sample Content:")
    print(f"   Title: {content['title']}")
    print(f"   Length: {len(content['content'])} characters")
    
    # Run tagging pipeline
    print("\n🔄 Running tagging pipeline...")
    result = await service.tag_document(
        title=content["title"],
        content=content["content"],
        include_categories=True,
        include_micro_tags=True,
        include_entities=True
    )
    
    # Display results
    print(f"\n✅ Tagging Complete (Processing time: {result.processing_time_ms:.1f}ms)")
    
    print("\n📚 Suggested Categories:")
    for tag in result.suggested_categories[:5]:
        print(f"   • {tag.name:<30} (confidence: {tag.score:.2%})")
    
    print("\n🏷️  Suggested Micro-Tags:")
    for tag in result.suggested_tags[:5]:
        print(f"   • {tag.name:<30} (confidence: {tag.score:.2%})")
    
    print("\n👤 Suggested Entities:")
    for tag in result.suggested_entities[:5]:
        print(f"   • {tag.name:<30} (confidence: {tag.score:.2%})")
    
    print(f"\n📊 Overall Confidence: {result.overall_confidence:.2%}")
    
    # Show JSON-LD schema
    if result.json_ld:
        print("\n📋 Generated JSON-LD Schema:")
        import json
        print(json.dumps(result.json_ld, indent=2)[:200] + "...")
    
    # Test entity resolution
    print("\n🔍 Testing Entity Resolution:")
    test_entities = ["ReactJS", "PyTorch", "Docker"]
    for entity in test_entities:
        node_id, score = service.resolve_entity(entity)
        if node_id:
            node = service.get_taxonomy_node(node_id)
            print(f"   • '{entity}' → '{node.name}' (confidence: {score:.2%})")
        else:
            print(f"   • '{entity}' → Not in taxonomy (similarity: {score:.2%})")
    
    # Show taxonomy structure
    print("\n📊 Taxonomy Structure:")
    print("   Data Science")
    print("   ├── Machine Learning")
    print("   │   └── PyTorch, TensorFlow")
    print("   ├── Deep Learning") 
    print("   │   └── Neural Networks")
    print("   Web Development")
    print("   ├── Frontend")
    print("   │   └── React, Vue, Angular")
    print("   ├── Backend")
    print("   DevOps")
    print("   └── Docker, Kubernetes")
    
    print("\n✨ Quick start complete!")
    print("\nNext steps:")
    print("1. Start the API server: uvicorn app.main:app --reload")
    print("2. Visit API docs: http://localhost:8000/docs")
    print("3. Test endpoints with sample content")
    print("4. Integrate with your CMS platform")


if __name__ == "__main__":
    asyncio.run(main())
