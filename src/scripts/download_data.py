import os
import tarfile
import shutil
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class IntegrityChecker:
    """
    Implements Heuristic Structural Verification (The HAC Protocol).
    """
    @staticmethod
    def validate_magic_bytes(file_path: Path, expected_magic: bytes, offset: int = 0) -> bool:
        try:
            with open(file_path, 'rb') as f:
                f.seek(offset)
                actual_magic = f.read(len(expected_magic))
                return actual_magic == expected_magic
        except Exception as e:
            print(f"[-] Formal Integrity Error: {e}")
            return False

    @staticmethod
    def validate_tar_structure(file_path: Path) -> bool:
        try:
            with tarfile.open(file_path, 'r:*') as tar:
                for _ in tar:
                    break 
            return True
        except (tarfile.ReadError, Exception) as e:
            print(f"[-] Logical Integrity Failed (Corrupted Archive): {e}")
            return False


class NanoSquiggleDownloader:
    """
    Handles physical transfer and HAC Protocol validation.
    """
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def download_and_verify(self, url: str, filename: str) -> bool:
        tmp_path = self.output_dir / f"{filename}.tmp"
        file_path = self.output_dir / filename

        print(f"[*] {filename}: Commencing transfer...")

        try:
            # Note: In a production environment, use a robust timeout and retry logic.
            with requests.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()
                expected_size = int(response.headers.get('Content-Length', 0))

                with open(tmp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=65536): # 64KB chunks for higher throughput
                        f.write(chunk)
        except Exception as e:
            print(f"[-] {filename}: Connection Error: {e}")
            if tmp_path.exists(): tmp_path.unlink()
            return False

        # --- THE HAC PROTOCOL GATES ---
        local_size = tmp_path.stat().st_size
        if expected_size > 0 and expected_size != local_size:
            print(f"[-] {filename}: Temporal Integrity Failed. Expected {expected_size}, got {local_size}.")
            tmp_path.unlink()
            return False

        if not IntegrityChecker.validate_magic_bytes(tmp_path, b'\x1f\x8b'):
            print(f"[-] {filename}: Formal Integrity Failed. Missing GZIP magic bytes.")
            tmp_path.unlink()
            return False

        print(f"[*] {filename}: Running Logical Integrity Dry-Run...")
        if not IntegrityChecker.validate_tar_structure(tmp_path):
            tmp_path.unlink()
            return False

        tmp_path.rename(file_path)
        print(f"[+] {filename}: HAC Protocol Passed.")
        return True


class DatasetOrchestrator:
    """
    Manages parallel execution, extraction, and atomic state tracking.
    """
    def __init__(self):
        # Correct Root Resolution: Script is in src/scripts/, root is two levels up.
        self.script_dir = Path(__file__).resolve().parent
        self.project_root = self.script_dir.parent.parent

        self.raw_dir = self.project_root / "data" / "raw"
        self.index_file = self.project_root / "data" / "data_index" / "data_ids.txt"

    def _promote_and_clean(self, target_dir: Path):
        """
        Implements 'Promotional Move' logic for Data Hygiene.
        Moves valid signal files to the root and purges intermediate directories.
        """
        print(f"[*] {target_dir.name}: Executing Promotional Move and Hygiene Cleanup...")

        # Subdirectories typically created by Dorado/ONT workflows
        pass_dir = target_dir / "pod5_pass"
        fail_dir = target_dir / "pod5_fail"

        # 1. Promote files from pod5_pass to the strain root
        if pass_dir.exists() and pass_dir.is_dir():
            for pod5_file in pass_dir.glob("*.pod5"):
                shutil.move(str(pod5_file), str(target_dir / pod5_file.name))
        
        # 2. Purge empty or 'fail' directories
        for folder in [pass_dir, fail_dir]:
            if folder.exists():
                shutil.rmtree(folder)
        
        print(f"[+] {target_dir.name}: Hygiene cleanup successful.")

    def extract_and_organize(self, archive_path: Path, target_dir: Path) -> bool:
        """
        Surgical Extraction with secondary organization.
        """
        print(f"[*] {target_dir.name}: Commencing Surgical Extraction...")
        try:
            with tarfile.open(archive_path, 'r:*') as tar:
                # Security: Never use extractall() without path validation in production
                tar.extractall(path=target_dir)
            
            # Phase 2: Promotional Move & Cleanup
            self._promote_and_clean(target_dir)

            # Phase 3: Destroy the compressed artifact
            archive_path.unlink()
            print(f"[+] {target_dir.name}: Extraction and artifact destruction complete.")
            return True
        except Exception as e:
            print(f"[-] {target_dir.name}: Extraction/Hygiene Failed: {e}")
            return False

    def process_strain(self, strain_id: str, url: str) -> bool:
        """The complete lifecycle of a single data strain."""
        strain_dir = self.raw_dir / strain_id
        strain_dir.mkdir(parents=True, exist_ok=True)
        
        sentinel_file = strain_dir / ".download_complete"
        filename = f"{strain_id}.tar.gz"
        archive_path = strain_dir / filename

        # Atomic State Check
        if sentinel_file.exists():
            print(f"[SKIP] {strain_id}: Sentinel found. Dataset is verified and clean.")
            return True

        # Phase 1: Download & Verify
        downloader = NanoSquiggleDownloader(output_dir=strain_dir)
        if not downloader.download_and_verify(url, filename):
            return False

        # Phase 2: Extract & Organize (Includes Hygiene Cleanup)
        if not self.extract_and_organize(archive_path, strain_dir):
            return False

        # Phase 3: Final Atomic State (Sentinel Shift)
        sentinel_file.touch()
        print(f"[SUCCESS] {strain_id}: Lifecycle complete. Data ready for ingestion.")
        return True

    def execute_pipeline(self, max_workers: int = 4):
        """
        Orchestrates the parallel execution across the dataset index.
        """
        if not self.index_file.exists():
            print(f"[-] FATAL: Index file not found at {self.index_file}")
            return

        with open(self.index_file, 'r') as f:
            strain_ids = [line.strip() for line in f if line.strip()]

        # For the prototype, we construct URLs from the provided base.
        base_url = "https://data.narodni-repozitar.cz/general/datasets/dj8ys-a4r49/files/"
        tasks = {sid: f"{base_url}{sid}_pod5.tar.gz" for sid in strain_ids}

        print(f"[*] Booting Unified Data Engine. Target strains: {len(tasks)}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.process_strain, sid, url): sid 
                for sid, url in tasks.items()
            }

            for future in as_completed(futures):
                strain_id = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"[-] Unhandled Thread Exception on {strain_id}: {e}")

if __name__ == "__main__":
    engine = DatasetOrchestrator()
    engine.execute_pipeline(max_workers=4)
