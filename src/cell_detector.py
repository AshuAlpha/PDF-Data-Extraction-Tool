import cv2

def cell_contains_cell(outer_cell, inner_cell, margin=5):
    """
    Check if outer_cell completely contains inner_cell (with margin tolerance).
    """
    ox, oy, ow, oh = outer_cell
    ix, iy, iw, ih = inner_cell
    
    return (
        ix >= ox - margin and
        iy >= oy - margin and
        ix + iw <= ox + ow + margin and
        iy + ih <= oy + oh + margin and
        (ix > ox + margin or iy > oy + margin or  # Not the same cell
         ix + iw < ox + ow - margin or iy + ih < oy + oh - margin)
    )

def remove_wrapper_cells(cells):
    """
    Remove large wrapper/container cells that encompass other smaller cells.
    Keeps only the actual data cells.
    """
    if len(cells) <= 1:
        return cells
    
    # A cell is a wrapper if it contains multiple other cells
    non_wrapper_cells = []
    
    for i, cell in enumerate(cells):
        contained_count = 0
        for j, other_cell in enumerate(cells):
            if i != j and cell_contains_cell(cell, other_cell):
                contained_count += 1
        
        # If a cell contains many other cells (3+), it's likely a wrapper
        # Keep it only if it doesn't contain too many cells
        if contained_count < 3:
            non_wrapper_cells.append(cell)
    
    return non_wrapper_cells

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
    
    # Remove wrapper cells that contain other cells
    cells = remove_wrapper_cells(cells)
    
    return cells
