## ADDED Requirements

### Requirement: Generate GB standard official document docx
The system SHALL generate official documents in docx format that conform to GB/T 9704-2012 standard for official documents of the Communist Party of China and state administrative organs.

#### Scenario: Generate request document docx
- **WHEN** user provides complete document content and requests a "request" (请示) type document
- **THEN** system generates a docx file with:
  - A4 paper size (210mm × 297mm)
  - Page margins: top 3.7cm, bottom 3.5cm, left 2.8cm, right 2.6cm
  - Red header with organization name in bold red Xiaobiaosong font, 22pt
  - Document number in right-aligned仿宋 font, 16pt
  - Red separator line
  - Centered title in Xiaobiaosong font, 18pt
  - Main body in仿宋 font, 16pt, 1.5 line spacing, first line indent 2 characters
  - Sender and date properly formatted

#### Scenario: Generate report document docx
- **WHEN** user provides complete document content and requests a "report" (汇报) type document
- **THEN** system generates a docx file following GB/T 9704-2012 report format

#### Scenario: Generate notice document docx
- **WHEN** user provides complete document content and requests a "notice" (通知) type document
- **THEN** system generates a docx file following GB/T 9704-2012 notice format

#### Scenario: Generate memo document docx
- **WHEN** user provides complete document content and requests a "memo" (函) type document
- **THEN** system generates a docx file following GB/T 9704-2012 memo format

#### Scenario: Generate meeting minutes docx
- **WHEN** user provides complete document content and requests a "meeting minutes" (会议纪要) type document
- **THEN** system generates a docx file following standard meeting minutes format

---

### Requirement: Docx preview in browser
The system SHALL allow users to preview the generated docx file directly in the browser with 1:1 representation.

#### Scenario: Preview docx after generation
- **WHEN** user clicks "Preview" after document assembly
- **THEN** system displays the docx file using a Vue3 docx preview component
- **AND** the preview shows the document with accurate formatting

#### Scenario: Download docx file
- **WHEN** user clicks "Download" button
- **THEN** system downloads the generated docx file to the user's device
- **AND** the filename follows the pattern: "{document_title}_{timestamp}.docx"
