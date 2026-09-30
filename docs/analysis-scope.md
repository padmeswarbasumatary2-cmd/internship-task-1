# Analyzer behavior and limitations

## Implemented

- Accept pasted resume text or files with PDF, DOCX, TXT, PNG, and JPG extensions; uploads are limited to 10 MB.
- Extract selectable text from PDF/DOCX/TXT and image OCR from images and scanned PDFs. OCR requires the Tesseract executable on the API host; scanned PDF OCR is limited to 30 pages.
- Normalize common Unicode and whitespace variation; use conservative section-header rules and regular expressions to extract contact hints, degree/GPA/year hints, education/work-history section entries, achievement metrics, and canonical skills.
- Map a maintained set of skill aliases to canonical labels (for example JS → JavaScript, React.js → React, and Pandas/NumPy → Python inference).
- Calculate a transparent weighted fit score: skill coverage 40%, experience indicator 30%, education indicator 20%, and lexical text overlap 10%. Persist factors and recommendations with the analysis.
- Do not return raw resume text or extracted personal contact/name fields in API responses. History uses an opaque candidate reference rather than a name.

## Important limits

This is a local, deterministic baseline, not the enterprise ML system described in the concept. It does not include a trained or custom fine-tuned NER model, a validated resume ontology/knowledge graph, transformer sentence embeddings, a vector database, or a demographic fairness audit. Text overlap is lexical, not semantic embedding similarity. Section, degree, experience, and entity extraction are heuristics and should be reviewed by a recruiter. Scores must not be used as the sole basis for screening or hiring decisions.

No annotated training corpus was supplied, so training custom NER would be inappropriate to fabricate. OCR also depends on a separately installed Tesseract system binary; adding the Python wrapper does not install that executable. Blob storage is not configured in this local implementation: resume text is stored in the configured relational database.
