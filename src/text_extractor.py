def extract_text_with_coordinates(pdf, config, logger):
    """
    Extract words with bounding boxes for each page.
    """
    pages_data = {}

    for page_index, page in enumerate(pdf.pages, start=1):
        try:
            words = page.extract_words(
                use_text_flow=config["text_extraction"]["use_text_flow"],
                keep_blank_chars=config["text_extraction"]["keep_blank_chars"]
            )

            if not words:
                logger.warning(f"Page {page_index}: No text found")
                pages_data[page_index] = []
                continue

            cleaned_words = []
            for w in words:
                cleaned_words.append({
                    "text": w.get("text", ""),
                    "x0": float(w.get("x0", 0)),
                    "x1": float(w.get("x1", 0)),
                    "top": float(w.get("top", 0)),
                    "bottom": float(w.get("bottom", 0)),
                    "page": page_index
                })

            pages_data[page_index] = cleaned_words

        except Exception as e:
            logger.error(f"Page {page_index} extraction failed: {e}")
            pages_data[page_index] = []

    return pages_data
