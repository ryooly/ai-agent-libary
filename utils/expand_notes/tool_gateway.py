import logging

from .tools.text_expand import expand_text
from .tools.text_to_notion import text_to_notion_blocks

logger = logging.getLogger("expand_notes")

# tambahkan blokckcing model sekalian 

def expand_note(text: str, model: str = "openai") -> list[dict]:
    logger.info("[1/2] Expanding text with model=%r", model)
    expanded = expand_text(text, model=model)

    if not expanded or not expanded.strip():
        raise RuntimeError("Expand step returned empty text.")

    logger.info("Expanded text length: %d chars", len(expanded))

    logger.info("[2/2] Converting expanded text to Notion blocks")
    blocks = text_to_notion_blocks(expanded, model=model)

    if not blocks:
        raise RuntimeError("Notion conversion step returned no blocks.")

    logger.info("Generated %d Notion block(s)", len(blocks))
    return blocks


# Nanti di dalam core logikanya apabila dia memanggil function fill_note maka jalankan lebih dulu expand notes kemudain baru itu