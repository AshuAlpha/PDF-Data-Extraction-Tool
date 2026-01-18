from src.pdf_loader import load_pdf
from src.text_extractor import extract_text_with_coordinates
from src.config_loader import load_config
from src.logger import setup_logger

from src.pdf_to_image import pdf_pages_to_images
from src.geometry import compute_scale_factor

from src.table_detector import (
    preprocess_image,
    detect_table_lines,
    detect_tables
)

from src.row_column_detector import detect_row_column_lines
from src.cell_detector import detect_cells
from src.text_cell_mapper import map_text_to_cells

from src.table_reconstructor import (
    group_cells_by_rows,
    rows_to_2d_list,
    build_dataframe
)

from src.excel_writer import write_tables_to_excel

def progress_bar(current, total, bar_length=40):
    """
    Display a progress bar in the console.
    """
    fraction = current / total
    filled_length = int(bar_length * fraction)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    percent = fraction * 100
    print(f'\r|{bar}| {percent:.1f}% Complete', end='\r')
    if current == total:
        print()  # New line on completion

def main():
    # --------------------------------------------------
    # Load configuration & logger
    # --------------------------------------------------
    config = load_config()
    logger = setup_logger(config["log_path"])

    logger.info("Starting PDF → Excel Extraction Pipeline")

    # --------------------------------------------------
    # Phase 1: Load PDF & extract text with coordinates
    # --------------------------------------------------
    pdf = load_pdf(config["pdf_input_path"])
    pages_text = extract_text_with_coordinates(pdf, config, logger)

    # --------------------------------------------------
    # Phase 2: Convert PDF pages → images (in-memory)
    # --------------------------------------------------
    images = pdf_pages_to_images(
        config["pdf_input_path"],
        dpi=300,
        poppler_path=config.get("poppler_path")
    )

    all_tables = []  # collect all extracted tables

    # --------------------------------------------------
    # Process each page
    # --------------------------------------------------
    total_pages = len(pdf.pages)

    for page_idx, page in enumerate(pdf.pages, start=1):
        progress_bar(page_idx, total_pages)
        logger.info(f"Processing Page {page_idx}")

        image = images[page_idx - 1]
        page_words = pages_text.get(page_idx, [])

        if not page_words:
            logger.warning(f"Page {page_idx}: No text found")

        # Compute PDF → image scale factors
        scale_x, scale_y = compute_scale_factor(page, image)

        # --------------------------------------------------
        # Phase 2: Detect table regions
        # --------------------------------------------------
        thresh = preprocess_image(image)
        table_mask = detect_table_lines(thresh)
        tables = detect_tables(table_mask)

        logger.info(f"Page {page_idx}: {len(tables)} table(s) detected")

        # --------------------------------------------------
        # Process each table on the page
        # --------------------------------------------------
        for table_idx, (tx, ty, tw, th) in enumerate(tables, start=1):
            logger.info(f"Page {page_idx} | Table {table_idx}: Processing")

            # Crop table region
            table_img = image[ty:ty + th, tx:tx + tw]

            # --------------------------------------------------
            # Phase 3: Detect rows, columns & cells
            # --------------------------------------------------
            h_lines, v_lines = detect_row_column_lines(table_img)
            raw_cells = detect_cells(h_lines, v_lines)

            if not raw_cells:
                logger.warning(
                    f"Page {page_idx} | Table {table_idx}: No cells detected"
                )
                continue

            # --------------------------------------------------
            # Convert table-local cell coords → full image coords
            # --------------------------------------------------
            cells = []
            for (cx, cy, cw, ch) in raw_cells:
                cells.append((cx + tx, cy + ty, cw, ch))

            # --------------------------------------------------
            # Phase 4: Map text → cells
            # --------------------------------------------------
            cell_values = map_text_to_cells(
                cells=cells,
                page_words=page_words,
                scale_x=scale_x,
                scale_y=scale_y
            )

            # --------------------------------------------------
            # Phase 5: Reconstruct table
            # --------------------------------------------------
            rows = group_cells_by_rows(cells, cell_values)
            table_2d = rows_to_2d_list(rows)
            df = build_dataframe(table_2d)

            logger.info(
                f"Page {page_idx} | Table {table_idx}: "
                f"Reconstructed table with shape {df.shape}"
            )

            # Collect for Excel export
            all_tables.append({
                "page": page_idx,
                "table": table_idx,
                "dataframe": df
            })

    pdf.close()

    # --------------------------------------------------
    # Phase 6: Write Excel output
    # --------------------------------------------------
    if not all_tables:
        logger.warning("No tables extracted. Excel file not created.")
        return

    write_tables_to_excel(
        tables=all_tables,
        output_path=config["excel_output_path"]
    )

    logger.info(
        f"Excel successfully created at: {config['excel_output_path']}"
    )


if __name__ == "__main__":
    main()
