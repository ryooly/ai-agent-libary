CONVERT_TEXT_TO_NOTION_PROMPT = """You are an expert Notion content formatter.

Convert the PLAIN TEXT below into Notion API-compatible block objects.
Return ONLY a single JSON object with one top-level key "blocks" whose value is an array of block objects — no prose, no markdown fences.

BLOCK TYPES YOU MAY USE (choose based on the text's structure and meaning):
- "paragraph"           -> normal body text
- "heading_1"           -> top-level title / major section
- "heading_2"           -> subsection
- "heading_3"           -> sub-subsection
- "bulleted_list_item"  -> unordered list entries
- "numbered_list_item"  -> ordered / sequential steps
- "to_do"               -> checklist items (add "checked": false)
- "quote"               -> a quoted / cited passage
- "callout"             -> an important note / tip
- "code"                -> a code snippet (add "language", default "plain text")
- "divider"             -> a visual separator between sections

EXACT SCHEMA for every block:
{
  "object": "block",
  "type": "<block type>",
  "<block type>": {
    "rich_text": [
      { "type": "text", "text": { "content": "<text>" }, "annotations": {} }
    ]
  }
}

FORMATTING RULES (apply inside rich_text annotations):
- **bold**   -> "annotations": {"bold": true}
- *italic*   -> "annotations": {"italic": true}
- `code`     -> "annotations": {"code": true}
- Split a single line into multiple rich_text items when styles change mid-line.

GUIDELINES:
1. Detect headings, lists, steps, and checklists from the text and map them to the right block type.
2. Preserve the original wording and meaning; do NOT invent new content.
3. Keep each paragraph / list item / heading as its own separate block.
4. For a code block, put the language key and plain string content inside "rich_text".

EXAMPLE
Input:
"# Goals
- Ship the MVP
- Finish: the design

Steps:
1. Plan
2. Build"

Output:
{
  "blocks": [
  {"object":"block","type":"heading_1","heading_1":{"rich_text":[{"type":"text","text":{"content":"Goals"},"annotations":{}}]}},
  {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[{"type":"text","text":{"content":"Ship the MVP"},"annotations":{}}]}},
  {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[{"type":"text","text":{"content":"Finish"},"annotations":{"bold":true}},{"type":"text","text":{"content":": the design"},"annotations":{}}]}},
  {"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"Steps:"},"annotations":{}}]}},
  {"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":[{"type":"text","text":{"content":"Plan"},"annotations":{}}]}},
  {"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":[{"type":"text","text":{"content":"Build"},"annotations":{}}]}}
]
}

PLAIN TEXT TO CONVERT:
\"\"\"{text}\"\"\"
"""


def build_convert_prompt(plain_text: str) -> str:
    return CONVERT_TEXT_TO_NOTION_PROMPT.replace("{text}", plain_text)
