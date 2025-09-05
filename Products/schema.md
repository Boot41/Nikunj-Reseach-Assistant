# Research Paper Storage Schema

This document defines the JSON schema for storing the details of a selected research paper.

## Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Research Paper",
  "description": "Schema for storing details of a selected research paper.",
  "type": "object",
  "properties": {
    "title": {
      "description": "The title of the paper.",
      "type": "string"
    },
    "authors": {
      "description": "A list of the paper's authors.",
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "first_author": {
      "description": "The first author of the paper.",
      "type": "string"
    },
    "summary": {
      "description": "A brief summary of the paper.",
      "type": "string"
    },
    "pdf_url": {
      "description": "The URL to the PDF of the paper.",
      "type": "string",
      "format": "uri"
    },
    "doi": {
      "description": "The Digital Object Identifier (DOI) of the paper.",
      "type": "string"
    },
    "source": {
      "description": "The source from which the paper was fetched (e.g., 'arXiv', 'IEEE').",
      "type": "string"
    }
  },
  "required": [
    "title",
    "authors",
    "first_author",
    "summary",
    "pdf_url",
    "source"
  ]
}
```

## Field Descriptions

*   **`title`**: The title of the paper.
*   **`authors`**: A list of all the authors of the paper.
*   **`first_author`**: The first author of the paper.
*   **`summary`**: A brief summary or abstract of the paper.
*   **`pdf_url`**: The direct URL to the PDF of the paper.
*   **`doi`**: The Digital Object Identifier (DOI) of the paper. This field is optional as it may not always be available.
*   **`source`**: The platform from which the paper was fetched (e.g., "arXiv", "IEEE", etc.).