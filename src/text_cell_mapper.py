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
