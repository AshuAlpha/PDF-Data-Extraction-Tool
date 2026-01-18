from src.pdf_loader import load_pdf
from src.text_extractor import extract_text_with_coordinates
from src.config_loader import load_config
from src.pdf_to_image import pdf_pages_to_images
from src.geometry import compute_scale_factor
from src.table_detector import preprocess_image, detect_table_lines, detect_tables
from src.row_column_detector import detect_row_column_lines
from src.cell_detector import detect_cells
from src.text_cell_mapper import map_text_to_cells

config = load_config()
pdf = load_pdf(config['pdf_input_path'])
pages_text = extract_text_with_coordinates(pdf, config, None)
images = pdf_pages_to_images(config['pdf_input_path'], dpi=300)

page_idx = 1
image = images[0]
page_words = pages_text[page_idx]
scale_x, scale_y = compute_scale_factor(pdf.pages[0], image)

print(f"Scale factors: x={scale_x}, y={scale_y}")
print(f"Number of words: {len(page_words)}\n")

thresh = preprocess_image(image)
table_mask = detect_table_lines(thresh)
tables = detect_tables(table_mask)

print(f"Tables detected: {len(tables)}")
tx, ty, tw, th = tables[0]
print(f"Table region: x={tx}, y={ty}, w={tw}, h={th}\n")

table_img = image[ty:ty + th, tx:tx + tw]

h_lines, v_lines = detect_row_column_lines(table_img)
raw_cells = detect_cells(h_lines, v_lines)

print(f"Raw cells detected: {len(raw_cells)}")

cells = [(cx + tx, cy + ty, cw, ch) for (cx, cy, cw, ch) in raw_cells]
cell_values = map_text_to_cells(cells, page_words, scale_x, scale_y)

print(f"\nCell mapping:")
for idx, (cell, value) in enumerate(zip(cells, cell_values)):
    cx, cy, cw, ch = cell
    print(f'Cell {idx}: ({cx}, {cy}, {cw}, {ch}) -> "{value}"')
