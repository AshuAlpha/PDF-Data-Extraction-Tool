from src.pdf_loader import load_pdf
from src.text_extractor import extract_text_with_coordinates
from src.config_loader import load_config
from src.logger import setup_logger
from src.pdf_to_image import pdf_pages_to_images
from src.geometry import compute_scale_factor
from src.table_detector import preprocess_image, detect_table_lines, detect_tables
from src.row_column_detector import detect_row_column_lines
from src.cell_detector import detect_cells

# Main execution function: Advanced Table and Cell Detection

def main():
    config = load_config()
    logger = setup_logger(config["log_path"])

    logger.info("Starting Phase 3")

    pdf = load_pdf(config["pdf_input_path"])
    pages_text = extract_text_with_coordinates(pdf, config, logger)

    images = pdf_pages_to_images(
        config["pdf_input_path"],
        dpi=300,
        poppler_path=config.get("poppler_path")
    )

    for page_idx, page in enumerate(pdf.pages, start=1):
        image = images[page_idx - 1]

        thresh = preprocess_image(image)
        table_mask = detect_table_lines(thresh)
        tables = detect_tables(table_mask)

        logger.info(f"Page {page_idx}: {len(tables)} table(s)")

        for t_idx, (tx, ty, tw, th) in enumerate(tables, start=1):
            table_img = image[ty:ty+th, tx:tx+tw]

            h_lines, v_lines = detect_row_column_lines(table_img)
            cells = detect_cells(h_lines, v_lines)

            logger.info(
                f"Page {page_idx} | Table {t_idx}: {len(cells)} cells detected"
            )

    pdf.close()
    logger.info("Phase 3 completed successfully")

if __name__ == "__main__":
    main()
