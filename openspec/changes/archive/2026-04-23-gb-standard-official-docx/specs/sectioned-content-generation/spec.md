## ADDED Requirements

### Requirement: Sectioned content generation with streaming
The system SHALL generate document content section by section using streaming output, allowing users to see progress in real-time.

#### Scenario: Start sectioned content generation
- **WHEN** user submits document generation request with form data and document type
- **THEN** system establishes an SSE (Server-Sent Events) connection
- **AND** system returns a sequence of events indicating each section's generation progress

#### Scenario: Receive section start event
- **WHEN** system begins generating a new section
- **THEN** system sends an SSE event with:
  ```json
  {
    "type": "section_start",
    "section_id": "title",
    "section_name": "公文标题",
    "index": 1,
    "total": 8
  }
  ```

#### Scenario: Receive section content streaming
- **WHEN** system is generating content for a section
- **THEN** system sends SSE events with incremental content chunks:
  ```json
  {
    "type": "content",
    "section_id": "title",
    "content": "关于对张某某涉嫌盗窃一"
  }
  ```

#### Scenario: Receive section complete event
- **WHEN** system finishes generating a section
- **THEN** system sends an SSE event with the complete section content:
  ```json
  {
    "type": "section_complete",
    "section_id": "title",
    "content": "关于对张某某涉嫌盗窃一案立案调查的请示"
  }
  ```

#### Scenario: Receive all complete event
- **WHEN** all sections have been generated
- **THEN** system sends a final SSE event:
  ```json
  {
    "type": "all_complete",
    "sections": {
      "title": "关于对张某某涉嫌盗窃一案立案调查的请示",
      "recipient": "保卫处：",
      "main_body": "我单位在近期工作中发现...",
      ...
    }
  }
  ```

#### Scenario: User edits generated content
- **WHEN** content generation is complete
- **THEN** user can edit any section's content in the browser
- **AND** edited content is used when assembling the final docx

---

### Requirement: Document structure definition per type
The system SHALL define the required sections for each document type.

#### Scenario: Get request document structure
- **WHEN** user selects "request" (请示) document type
- **THEN** system uses the following sections:
  1. title (标题)
  2. recipient (主送机关)
  3. main_body (正文)
  4. attachment (附件说明)
  5. sender (发文机关)
  6. date (成文日期)

#### Scenario: Get report document structure
- **WHEN** user selects "report" (汇报) document type
- **THEN** system uses appropriate sections for reports

#### Scenario: Get notice document structure
- **WHEN** user selects "notice" (通知) document type
- **THEN** system uses appropriate sections for notices

#### Scenario: Get memo document structure
- **WHEN** user selects "memo" (函) document type
- **THEN** system uses appropriate sections for memos

#### Scenario: Get meeting minutes structure
- **WHEN** user selects "meeting minutes" (会议纪要) document type
- **THEN** system uses appropriate sections for meeting minutes
