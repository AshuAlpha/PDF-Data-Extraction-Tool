import cv2

def detect_cells(horizontal_lines, vertical_lines, min_width=20, min_height=20):
    """
    Combine row and column lines to detect individual cells.
    """
    table_mask = cv2.add(horizontal_lines, vertical_lines)

    contours, _ = cv2.findContours(
        table_mask,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    cells = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if w >= min_width and h >= min_height:
            cells.append((x, y, w, h))

    # Sort row-wise, then column-wise
    cells.sort(key=lambda b: (b[1], b[0]))
    return cells
