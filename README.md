# Automated Content Tagging and Taxonomy Engine

A production-ready ML-powered system for automatic content tagging and taxonomy management in digital publishing platforms.

## 📋 Overview

This project implements an end-to-end automated tagging engine that combines:

- **Multi-Label Classification** (DistilRoBERTa) for macro-categories
- **Semantic Keyphrase Extraction** (KeyBERT + MMR) for micro-tags  
- **Named Entity Recognition** (spaCy + Transformers) for entity extraction
- **Taxonomy Knowledge Graph** for semantic normalization and synonym resolution
- **Redis Caching** for low-latency inference
- **FastAPI** REST API for CMS integration

## 🎯 Key Features

✅ **Automated Content Tagging** — Analyzes blog posts and generates relevant micro-tags, macro-categories, and named entities  
✅ **Hierarchical Taxonomy** — Maintains a DAG-based knowledge graph with entity resolution and canonical normalization  
✅ **High-Precision Classification** — Uses dynamic thresholding per class calibrated from validation data  
✅ **Diverse Keyphrase Selection** — Maximal Marginal Relevance (MMR) ensures topically diverse tag selection  
✅ **SEO Integration** — Automatically generates JSON-LD schema markup for search engines  
✅ **Editorial Validation** — Human-in-the-loop interface with active learning feedback loop  
✅ **Low-Latency Inference** — Redis caching + ONNX quantization reduces response times to <100ms  
✅ **Batch Processing** — Process multiple documents asynchronously

## 📁 Project Structure

```
intern 1/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy ORM models
│   │   └── schemas.py          # Pydantic request/response schemas
│   ├── ml_pipeline/
│   │   ├── __init__.py
│   │   ├── preprocessing.py    # HTML/Markdown parsing, text cleaning
│   │   ├── multi_label_classifier.py   # Category classification
│   │   ├── keybert_extractor.py        # Keyphrase extraction
│   │   ├── ner_extractor.py            # Named entity recognition
│   │   └── taxonomy_graph.py           # Knowledge graph & entity resolution
│   └── services/
│       ├── __init__.py
│       ├── tagging_service.py  # Orchestrates ML pipeline
│       └── cache_service.py    # Redis caching
├── tests/
│   ├── __init__.py
│   └── test_api.py            # API integration tests
├── data/                       # Sample data and training datasets
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # PostgreSQL + Redis + App orchestration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized setup)
- PostgreSQL 15+
- Redis 7+

### Local Installation

1. **Clone and setup**
   ```bash
   cd "intern 1"
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Download models**
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis URLs
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Docker Setup

1. **Build and start services**
   ```bash
   docker-compose up -d
   ```

2. **Create database tables**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

3. **Access API**
   - API: `http://localhost:8000`
   - Docs: `http://localhost:8000/docs`
   - PostgreSQL: `localhost:5432`
   - Redis: `localhost:6379`

## 📡 API Endpoints

### Health Check
```http
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": true,
  "database_connected": true,
  "redis_connected": true
}
```

### Tag Content
```http
POST /api/v1/tag-content
Content-Type: application/json

{
  "title": "Getting Started with PyTorch",
  "content": "...",
  "html_content": "...",
  "include_categories": true,
  "include_micro_tags": true,
  "include_entities": true
}
```

Response:
```json
{
  "suggested_categories": [
    {"name": "Machine Learning", "score": 0.92, "tag_type": "category"},
    {"name": "Deep Learning", "score": 0.87, "tag_type": "category"}
  ],
  "suggested_tags": [
    {"name": "PyTorch", "score": 0.95, "tag_type": "micro-tag"},
    {"name": "Neural Networks", "score": 0.88, "tag_type": "micro-tag"}
  ],
  "suggested_entities": [
    {"name": "Facebook", "score": 0.90, "tag_type": "entity:organization"}
  ],
  "overall_confidence": 0.91,
  "json_ld": {...},
  "processing_time_ms": 245.3
}
```

### Validate Tags (Active Learning)
```http
POST /api/v1/validate-tags
Content-Type: application/json

{
  "tagging_result_id": 1,
  "accepted_tags": ["PyTorch", "Machine Learning"],
  "rejected_tags": ["Intermediate", "Advanced"],
  "manual_tags": ["Distributed Training"]
}
```

### Get Taxonomy
```http
GET /api/v1/taxonomy
```

### Resolve Entity (Semantic Normalization)
```http
POST /api/v1/resolve-entity?entity_text=ReactJS
```

Response:
```json
{
  "canonical_name": "React",
  "node_id": "react",
  "confidence": 0.95
}
```

### Batch Processing
```http
POST /api/v1/batch-tag
Content-Type: application/json

{
  "requests": [
    {"title": "...", "content": "..."},
    {"title": "...", "content": "..."}
  ]
}
```

## 🧠 ML Pipeline Architecture

### 1. Preprocessing (`ml_pipeline/preprocessing.py`)

**Input:** Raw HTML/Markdown content  
**Process:**
- Extract text while preserving structural hierarchy
- Weight text by importance (H1/H2 > body text)
- Clean publishing-specific stopwords
- Lemmatization via spaCy

**Output:** Normalized text + structural metadata

### 2. Multi-Label Classification (`ml_pipeline/multi_label_classifier.py`)

**Model:** DistilRoBERTa (fine-tuned on publishing taxonomy)  
**Loss:** Binary Cross-Entropy with dynamic per-class thresholds  
**Output:** Macro-categories with confidence scores

```
Loss = -1/C * Σ[y_i * log(σ(x_i)) + (1-y_i) * log(1-σ(x_i))]
```

### 3. Semantic Keyphrase Extraction (`ml_pipeline/keybert_extractor.py`)

**Model:** Sentence-Transformers (all-MiniLM-L6-v2)  
**Algorithm:** KeyBERT with Maximal Marginal Relevance (MMR)

**MMR Score:**
```
MMR = λ * Sim(candidate, document) - (1-λ) * max(Sim(candidate, selected))
```

- λ = 0.7 (balance relevance vs. diversity)
- Selects diverse, relevant phrases

### 4. Named Entity Recognition (`ml_pipeline/ner_extractor.py`)

**Models:** spaCy + Transformer-based NER  
**Entities:** PERSON, ORG, PRODUCT, GPE, EVENT

### 5. Taxonomy Resolution (`ml_pipeline/taxonomy_graph.py`)

**Graph Structure:** DAG with synonym resolution  
**Algorithm:** Fuzzy string matching (SequenceMatcher) + alias lookup  
**Output:** Canonical entity IDs with confidence scores

## 🔄 Active Learning Feedback Loop

1. AI suggests tags with confidence scores
2. Editor validates/corrects suggestions
3. Feedback stored in database
4. Periodic retraining updates model thresholds
5. Continuous improvement cycle

## 📊 Performance Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Inference Latency | <100ms | ✅ |
| Category F1-Score | >0.85 | 📊 |
| Keyphrase Precision@10 | >0.80 | 📊 |
| Entity Recall | >0.90 | 📊 |
| Cache Hit Rate | >60% | 🔄 |

## 🛠️ Configuration

See `.env.example` for all available settings:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tagging_db

# Cache
REDIS_URL=redis://localhost:6379/0

# Models
MULTI_LABEL_MODEL=distilroberta-base
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
NER_MODEL=en_core_web_sm

# Thresholds
CLASSIFICATION_THRESHOLD=0.5
KEYBERT_MIN_SCORE=0.3
MAX_TAGS_PER_DOCUMENT=20
```

## 📚 Database Schema

### Content Table
```sql
CREATE TABLE content (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255),
  slug VARCHAR(255) UNIQUE,
  content TEXT,
  html_content TEXT,
  author VARCHAR(100),
  meta_description VARCHAR(160),
  json_ld TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  published_at TIMESTAMP
);
```

### Tags & Categories
```sql
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  slug VARCHAR(100) UNIQUE,
  description TEXT,
  usage_count INTEGER
);

CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  slug VARCHAR(100) UNIQUE,
  parent_id INTEGER REFERENCES categories(id),
  display_order INTEGER
);
```

### Tagging Results (Audit Trail)
```sql
CREATE TABLE tagging_results (
  id SERIAL PRIMARY KEY,
  content_id INTEGER REFERENCES content(id),
  suggested_categories TEXT,  -- JSON
  suggested_tags TEXT,        -- JSON
  suggested_entities TEXT,    -- JSON
  accepted_tags TEXT,         -- JSON
  rejected_tags TEXT,         -- JSON
  overall_confidence FLOAT,
  is_validated BOOLEAN,
  created_at TIMESTAMP,
  validated_at TIMESTAMP,
  validated_by VARCHAR(100)
);
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Test specific endpoint:
```bash
pytest tests/test_api.py::TestTaggingEndpoint -v
```

## 📈 Future Enhancements

- [ ] Multimodal tagging (vision + text)
- [ ] Real-time trend-aware taxonomy updates
- [ ] Advanced active learning with uncertainty sampling
- [ ] Multi-language support
- [ ] GraphQL API endpoint
- [ ] Model explainability (SHAP values)
- [ ] A/B testing framework for model versions
- [ ] Integration plugins (WordPress, Ghost, Strapi)

## 🔒 Security Considerations

- Validate all API inputs
- Rate limiting on production
- JWT authentication for CMS integration
- Database connection pooling
- Redis authentication enabled
- Sanitize user-provided tags

## 📝 Logging & Monitoring

- Application logs: `uvicorn` stderr
- Database queries: SQLAlchemy debug logs
- Cache metrics: Redis INFO command
- Performance profiling: Add timing decorators

## 💡 Tips for Development

1. **Fast Iteration:** Use `.env` for quick config changes
2. **Model Debugging:** Import and test ML components independently
3. **Cache Invalidation:** `cache_service.clear_pattern("tagging:*")`
4. **Database Reset:** `docker-compose down -v` to clear volumes

## 📄 License

Internal project for internship.

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test thoroughly
3. Submit pull request with documentation

## 📧 Support

For questions or issues, contact the development team.

---

**Built with ❤️ for intelligent content automation**
