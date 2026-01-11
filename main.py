from src.pdf_loader import load_pdf
from src.text_extractor import extract_text_with_coordinates
from src.config_loader import load_config
from src.logger import setup_logger
from src.pdf_to_image import pdf_pages_to_images
from src.geometry import compute_scale_factor
from src.table_detector import preprocess_image, detect_table_lines, detect_tables
from src.row_column_detector import detect_row_column_lines
from src.cell_detector import detect_cells
from src.text_cell_mapper import map_text_to_cells

def main():
    config = load_config()
    logger = setup_logger(config["log_path"])

    logger.info("Starting Phase 4")

    pdf = load_pdf(config["pdf_input_path"])
    pages_text = extract_text_with_coordinates(pdf, config, logger)

    images = pdf_pages_to_images(
        config["pdf_input_path"],
        dpi=300,
        poppler_path=config.get("poppler_path")
    )

    for page_idx, page in enumerate(pdf.pages, start=1):
        image = images[page_idx - 1]
        page_words = pages_text.get(page_idx, [])

        scale_x, scale_y = compute_scale_factor(page, image)

        thresh = preprocess_image(image)
        table_mask = detect_table_lines(thresh)
        tables = detect_tables(table_mask)

        for t_idx, (tx, ty, tw, th) in enumerate(tables, start=1):
            table_img = image[ty:ty+th, tx:tx+tw]

            h_lines, v_lines = detect_row_column_lines(table_img)
            cells = detect_cells(h_lines, v_lines)

            cell_values = map_text_to_cells(
                cells,
                page_words,
                scale_x,
                scale_y
            )

            logger.info(
                f"Page {page_idx} | Table {t_idx}: "
                f"{len(cell_values)} cell values mapped"
            )

            # TEMP: print first few cells for validation
            for val in cell_values[:5]:
                print(val)

    pdf.close()
    logger.info("Phase 4 completed successfully")
