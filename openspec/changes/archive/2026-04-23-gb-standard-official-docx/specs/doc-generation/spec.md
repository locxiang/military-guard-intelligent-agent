## ADDED Requirements

### Requirement: Two-step document generation workflow
The system SHALL support a two-step workflow for official document generation: content generation first, then docx assembly.

#### Scenario: User completes step 1 (content generation)
- **WHEN** user completes the sectioned content generation (or manually edits content)
- **THEN** user can proceed to step 2 by clicking "Generate Standard Official Docx"

#### Scenario: User navigates back from step 2
- **WHEN** user is in step 2 (docx preview) and clicks "Back to Edit"
- **THEN** system returns to step 1 with all generated/edited content preserved

#### Scenario: User generates docx multiple times
- **WHEN** user returns to step 1, edits content, and clicks "Generate Standard Official Docx" again
- **THEN** system regenerates the docx with the updated content

---

### Requirement: Backward compatibility
The system SHALL maintain backward compatibility with existing document generation functionality.

#### Scenario: Existing API endpoints still work
- **WHEN** frontend calls the existing `/api/v1/doc-generate/official` endpoint
- **THEN** the endpoint continues to function as before (Markdown streaming)

#### Scenario: User can choose generation mode
- **WHEN** user accesses the document generation page
- **THEN** user can choose between "Standard GB Format" (new two-step) and "Simple Mode" (existing Markdown)
