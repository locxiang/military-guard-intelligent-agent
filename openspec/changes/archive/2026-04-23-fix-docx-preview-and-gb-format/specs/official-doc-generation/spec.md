## ADDED Requirements

### Requirement: Red separator line uses paragraph border
The system SHALL render the official document red separator line using a paragraph bottom border instead of underscore characters.

#### Scenario: Red line is rendered as solid border
- **WHEN** an official document is generated
- **THEN** the red separator line SHALL be a solid red horizontal line

#### Scenario: Red line spans correct width
- **WHEN** an official document is generated
- **THEN** the red separator line SHALL span the same width as the document body

### Requirement: Sender signature and date are right-aligned with four-character indent
The system SHALL position the sender signature and date with four Chinese characters of indentation from the right margin.

#### Scenario: Sender signature is right-indented four characters
- **WHEN** an official document is generated
- **THEN** the sender signature SHALL be positioned with four Chinese characters of space from the right margin

#### Scenario: Date is right-indented four characters
- **WHEN** an official document is generated
- **THEN** the date SHALL be positioned with four Chinese characters of space from the right margin

### Requirement: Document includes version record section
The system SHALL include a complete version record section at the end of official documents.

#### Scenario: Version record includes copy recipients
- **WHEN** an official document with copy recipients is generated
- **THEN** the version record SHALL include a copy recipients line indented one character from the left

#### Scenario: Version record includes issuing organization and date
- **WHEN** an official document is generated
- **THEN** the version record SHALL include the issuing organization indented one character from the left and the issue date indented one character from the right

#### Scenario: Version record has separator lines
- **WHEN** an official document is generated
- **THEN** the version record SHALL have thin solid separator lines above, between, and below sections

## MODIFIED Requirements

### Requirement: Official document conforms to GB/T 9704-2012
The system SHALL generate official documents that fully conform to the GB/T 9704-2012 national standard for official document formatting.

#### Scenario: Document has correct page margins
- **WHEN** an official document is generated
- **THEN** the page margins SHALL be 37mm top, 35mm bottom, 28mm left, and 26mm right

#### Scenario: Document body has correct line spacing
- **WHEN** an official document is generated
- **THEN** the main body text SHALL have 1.5 line spacing

#### Scenario: Document paragraphs have correct first line indent
- **WHEN** an official document is generated
- **THEN** each paragraph SHALL have a first line indent of two Chinese characters
