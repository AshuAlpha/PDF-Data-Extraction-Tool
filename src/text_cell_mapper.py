def pdf_word_to_image_coords(word, scale_x, scale_y):
    """
    Convert PDF word coordinates to image coordinates.
    """
    x0 = word["x0"] * scale_x
    x1 = word["x1"] * scale_x
    y0 = word["top"] * scale_y
    y1 = word["bottom"] * scale_y

    return x0, y0, x1, y1

def is_word_inside_cell(word_bbox, cell_bbox):
    wx0, wy0, wx1, wy1 = word_bbox
    cx, cy, cw, ch = cell_bbox

    return (
        wx0 >= cx and
        wx1 <= cx + cw and
        wy0 >= cy and
        wy1 <= cy + ch
    )

def map_text_to_cells(cells, page_words, scale_x, scale_y):
    """
    Assign PDF words to detected table cells.
    """
    cell_texts = []

    for cell in cells:
        cx, cy, cw, ch = cell
        words_in_cell = []

        for word in page_words:
            word_bbox = pdf_word_to_image_coords(word, scale_x, scale_y)

            if is_word_inside_cell(word_bbox, cell):
                words_in_cell.append(word["text"])

        cell_texts.append(" ".join(words_in_cell).strip())

    return cell_texts

def detect_cells_from_text_positions(page_words, scale_x, scale_y, row_threshold=15, col_threshold=30):
    """
    Detect table cells by clustering text positions (for borderless tables).
    
    Args:
        page_words: List of word dictionaries with coordinates
        scale_x, scale_y: Scale factors for PDF to image conversion
        row_threshold: Y-distance threshold for grouping words into same row
        col_threshold: X-distance threshold for grouping words into same column
    
    Returns:
        List of cell bounding boxes: [(x, y, w, h), ...]
    """
    if not page_words:
        return []
    
    # Convert words to image coordinates and extract centers
    word_centers = []
    for word in page_words:
        x0 = word["x0"] * scale_x
        x1 = word["x1"] * scale_x
        y0 = word["top"] * scale_y
        y1 = word["bottom"] * scale_y
        
        center_x = (x0 + x1) / 2
        center_y = (y0 + y1) / 2
        
        word_centers.append({
            "x0": x0, "y0": y0, "x1": x1, "y1": y1,
            "cx": center_x, "cy": center_y,
            "text": word["text"]
        })
    
    # Sort by Y position (row), then X position (column)
    word_centers.sort(key=lambda w: (w["cy"], w["cx"]))
    
    # Cluster words into rows based on Y proximity
    rows = []
    current_row = [word_centers[0]]
    
    for word in word_centers[1:]:
        # If Y position is within threshold of current row, add to row
        if abs(word["cy"] - current_row[0]["cy"]) <= row_threshold:
            current_row.append(word)
        else:
            rows.append(current_row)
            current_row = [word]
    rows.append(current_row)
    
    # For each row, cluster words into columns
    cells = []
    for row_idx, row in enumerate(rows):
        # Sort by X position within row
        row.sort(key=lambda w: w["cx"])
        
        # Cluster into columns
        columns = []
        current_col = [row[0]]
        
        for word in row[1:]:
            # If X position is within threshold of current column, add to column
            if abs(word["cx"] - current_col[0]["cx"]) <= col_threshold:
                current_col.append(word)
            else:
                columns.append(current_col)
                current_col = [word]
        columns.append(current_col)
        
        # Create cell bounding box for each column
        for col_idx, column in enumerate(columns):
            # Find bounding box of all words in this cell
            min_x = min(w["x0"] for w in column)
            min_y = min(w["y0"] for w in column)
            max_x = max(w["x1"] for w in column)
            max_y = max(w["y1"] for w in column)
            
            cell_width = max_x - min_x
            cell_height = max_y - min_y
            
            cells.append((int(min_x), int(min_y), int(cell_width), int(cell_height)))
    
    return cells