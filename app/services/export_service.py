import csv
import os
from datetime import datetime
from typing import List, Dict
from app.utils import LoggerMixin

class ExportService(LoggerMixin):
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        # Pastikan folder exports ada
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def to_csv(self, products: List[Dict], filename: str = None, prefix: str = "raw") -> str:
        """
        Export data ke CSV dengan penamaan yang profesional.
        Args:
            products: List data produk
            filename: Nama file kustom (opsional)
            prefix: Awalan untuk membedakan 'raw' atau 'transformed'
        """
        if not products:
            self.logger.warning(f"No {prefix} products to export.")
            return ""

        if not filename:
            # Format: ecom_scrape_[raw/transformed]_20240207_2246.csv
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"ecom_scrape_{prefix}_{timestamp}.csv"

        filepath = os.path.join(self.export_dir, filename)

        try:
            # Mengambil keys dari dictionary pertama sebagai header
            keys = products[0].keys()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(products)
            
            self.logger.info(f"✓ Data successfully exported to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {e}")
            raise