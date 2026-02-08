import re
from typing import List, Dict
from app.utils import LoggerMixin

class TransformService(LoggerMixin):
    """Service untuk membersihkan dan memperkaya data produk dari string deskripsi"""

    def transform_products(self, products: List[Dict]) -> List[Dict]:
        self.logger.info(f"Starting transformation for {len(products)} products...")
        transformed_list = []

        for p in products:
            raw_desc = p.get('description', '')
            product_name = p.get('product_name', '')

            # 1. Ekstrak Brand (Kata pertama dari nama produk)
            p['brand'] = product_name.split()[0] if product_name else "Unknown"

            # 2. Persiapan Parsing
            # Kita split berdasarkan koma untuk memeriksa tiap komponen
            # Daftar kata yang harus dibuang dari kolom screen/display
            noise_keywords = [
                'apple', 'macbook', 'air', 'acer', 'aspire', 'black', 'white', 
                'silver', 'grey', 'gold', 'blue', 'red'
            ]
            parts = [part.strip() for part in raw_desc.split(',')]
            
            p['screen_size'] = None
            p['display_type'] = None
            p['processor'] = None
            p['hdd'] = None
            p['os'] = None
            p['graphics_card'] = None

            for part in parts:
                part_lower = part.lower()
                
                # --- A. Screen Size ---
                # Mencari pola angka yang diikuti tanda kutip (e.g., 15.6")
                # if re.search(r'\d+(\.\d+)?\s*["”]', part) and not p['screen_size']:
                #     p['screen_size'] = part
                size_match = re.search(r'(\d+(?:\.\d+)?\s*["”])', part)
                
                if size_match:
                    # 1. Ambil ukuran layar saja (e.g., 15.6")
                    full_size_str = size_match.group(1)
                    p['screen_size'] = full_size_str.replace(' ', '')

                    # 2. Ambil sisanya untuk display_type (FHD, IPS, dll)
                    # Hapus ukuran layar dari string aslinya
                    remainder = part.replace(full_size_str, '')
                    
                    # Bersihkan noise (Brand, Warna, Nama Model)
                    for noise in noise_keywords:
                        # Case insensitive replacement
                        remainder = re.sub(re.escape(noise), '', remainder, flags=re.IGNORECASE)
                    
                    # Bersihkan sisa karakter non-alphanumeric di awal/akhir (kecuali Hz)
                    clean_display = remainder.strip(' -/,.')
                    p['display_type'] = clean_display if clean_display else "Standard"
                    continue  # Lanjut ke part berikutnya setelah menemukan screen size

                # --- B. Processor ---
                # Mencari keyword umum processor atau clock speed (GHz)
                elif any(x in part_lower for x in ['core', 'intel', 'amd', 'pentium', 'celeron', 'ghz', 'ryzen']):
                    # Hindari memasukkan "Intel HD Graphics" ke processor jika itu sebenarnya GPU
                    if 'graphics' not in part_lower:
                        p['processor'] = part

                # --- C. Storage (HDD/SSD) ---
                # Logika: Mengandung GB/TB, dan (ada kata SSD/HDD/Hybrid ATAU angka > 32)
                # Angka > 32 digunakan untuk membedakan dengan RAM (biasanya 4GB, 8GB, 16GB)
                storage_match = re.search(r'(\d+)\s*(GB|TB)', part, re.I)
                if storage_match:
                    size = int(storage_match.group(1))
                    is_storage_keyword = any(x in part_lower for x in ['ssd', 'hdd', 'hard drive', 'hybrid'])
                    
                    if is_storage_keyword or size > 32:
                        p['hdd'] = part

                # --- D. Operating System ---
                elif any(x in part_lower for x in ['windows', 'win', 'linux', 'ubuntu', 'mac os', 'dos']):
                    p['os'] = part

                # --- E. Graphics Card ---
                elif any(x in part_lower for x in ['radeon', 'geforce', 'nvidia', 'intel hd', 'graphics', 'rtx', 'gtx']):
                    p['graphics_card'] = part

            # 3. Pembersihan Tambahan (Cleanup)
            # Jika brand terdeteksi dua kali di deskripsi (seperti pada contoh Lenovo),
            # kita pastikan data tidak redundan.
            if p['processor'] and p['brand'].lower() in p['processor'].lower():
                # Jika processor mengandung nama brand di depannya, kita biarkan saja 
                # karena itu biasanya full model name
                pass

            transformed_list.append(p)
        
        self.logger.info("✓ Data transformation with Regex completed")
        return transformed_list