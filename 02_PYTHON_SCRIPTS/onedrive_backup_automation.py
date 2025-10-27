"""
OneDrive Backup and Removal Automation
Safely backs up OneDrive folder and optionally removes it
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import json

# Configuration
ONEDRIVE_SOURCE = Path(r"C:\Users\fonat\OneDrive")
BACKUP_BASE = Path(r"C:\Users\fonat\Documents")
BACKUP_NAME = f"OneDrive_Backup_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}"

class OneDriveBackup:
    def __init__(self, source: Path, backup_base: Path, backup_name: str):
        self.source = source
        self.backup_dir = backup_base / backup_name
        self.log_file = backup_base / f"{backup_name}_log.json"
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "source": str(source),
            "backup": str(self.backup_dir),
            "files_copied": 0,
            "folders_copied": 0,
            "total_size_bytes": 0,
            "errors": []
        }

    def check_source_exists(self):
        """Check if OneDrive folder exists"""
        if not self.source.exists():
            print(f"✗ Source folder not found: {self.source}")
            return False

        if not self.source.is_dir():
            print(f"✗ Source is not a directory: {self.source}")
            return False

        print(f"✓ Source folder found: {self.source}")
        return True

    def calculate_source_size(self):
        """Calculate total size of source folder"""
        print("\nCalculating source folder size...")
        total_size = 0
        file_count = 0
        folder_count = 0

        for root, dirs, files in os.walk(self.source):
            folder_count += len(dirs)
            for file in files:
                try:
                    file_path = Path(root) / file
                    total_size += file_path.stat().st_size
                    file_count += 1
                except Exception as e:
                    self.stats["errors"].append(f"Error calculating size for {file}: {str(e)}")

        print(f"\nSource folder statistics:")
        print(f"  Files: {file_count:,}")
        print(f"  Folders: {folder_count:,}")
        print(f"  Total size: {self.format_size(total_size)}")

        return total_size, file_count, folder_count

    @staticmethod
    def format_size(bytes_size):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"

    def check_disk_space(self, required_bytes):
        """Check if enough disk space is available"""
        print("\nChecking available disk space...")

        backup_drive = Path(self.backup_dir.drive)
        stat = shutil.disk_usage(backup_drive)

        print(f"  Drive: {backup_drive}")
        print(f"  Free space: {self.format_size(stat.free)}")
        print(f"  Required: {self.format_size(required_bytes)}")

        if stat.free < required_bytes * 1.1:  # 10% buffer
            print(f"✗ Not enough disk space!")
            return False

        print(f"✓ Sufficient disk space available")
        return True

    def create_backup(self):
        """Copy all files from OneDrive to backup folder"""
        print(f"\nCreating backup folder: {self.backup_dir}")

        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"✓ Backup folder created")
        except Exception as e:
            print(f"✗ Failed to create backup folder: {e}")
            return False

        print("\nCopying files (this may take several minutes)...")
        print("-" * 60)

        for root, dirs, files in os.walk(self.source):
            # Calculate relative path
            rel_path = Path(root).relative_to(self.source)
            dest_root = self.backup_dir / rel_path

            # Create directories
            for dir_name in dirs:
                try:
                    dest_dir = dest_root / dir_name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    self.stats["folders_copied"] += 1
                except Exception as e:
                    error_msg = f"Error creating directory {dest_dir}: {str(e)}"
                    self.stats["errors"].append(error_msg)
                    print(f"⚠ {error_msg}")

            # Copy files
            for file_name in files:
                try:
                    source_file = Path(root) / file_name
                    dest_file = dest_root / file_name

                    # Copy file with metadata
                    shutil.copy2(source_file, dest_file)

                    file_size = source_file.stat().st_size
                    self.stats["files_copied"] += 1
                    self.stats["total_size_bytes"] += file_size

                    if self.stats["files_copied"] % 100 == 0:
                        print(f"  Copied {self.stats['files_copied']:,} files... ({self.format_size(self.stats['total_size_bytes'])})")

                except Exception as e:
                    error_msg = f"Error copying {source_file}: {str(e)}"
                    self.stats["errors"].append(error_msg)
                    print(f"⚠ {error_msg}")

        print("-" * 60)
        print(f"\n✓ Backup completed!")
        print(f"  Files copied: {self.stats['files_copied']:,}")
        print(f"  Folders copied: {self.stats['folders_copied']:,}")
        print(f"  Total size: {self.format_size(self.stats['total_size_bytes'])}")

        if self.stats["errors"]:
            print(f"\n⚠ {len(self.stats['errors'])} errors occurred during backup")

        return True

    def verify_backup(self):
        """Verify backup integrity by comparing file counts"""
        print("\nVerifying backup integrity...")

        # Count files in source
        source_files = sum(1 for _ in self.source.rglob('*') if _.is_file())

        # Count files in backup
        backup_files = sum(1 for _ in self.backup_dir.rglob('*') if _.is_file())

        print(f"  Source files: {source_files:,}")
        print(f"  Backup files: {backup_files:,}")

        if source_files == backup_files:
            print(f"✓ File counts match! Backup is complete.")
            return True
        else:
            print(f"⚠ File counts don't match!")
            print(f"  Missing: {abs(source_files - backup_files)} files")
            return False

    def save_log(self):
        """Save backup log to JSON file"""
        self.stats["end_time"] = datetime.now().isoformat()

        with open(self.log_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        print(f"\n✓ Backup log saved: {self.log_file}")

    def remove_source(self):
        """Remove OneDrive source folder"""
        print("\n" + "=" * 60)
        print("WARNING: About to DELETE OneDrive folder!")
        print("=" * 60)
        print(f"\nFolder to delete: {self.source}")
        print(f"Backup location: {self.backup_dir}")

        response = input("\nAre you ABSOLUTELY SURE you want to delete? (yes/no): ")

        if response.lower() != 'yes':
            print("\n✓ Deletion cancelled. Your backup is safe.")
            return False

        print("\nDeleting OneDrive folder...")

        try:
            shutil.rmtree(self.source)
            print(f"✓ OneDrive folder deleted successfully!")
            return True
        except Exception as e:
            print(f"✗ Failed to delete OneDrive folder: {e}")
            print("\nPossible solutions:")
            print("1. Close all programs that might be using files in OneDrive")
            print("2. Run this script as Administrator")
            print("3. Manually delete the folder in File Explorer")
            return False

def main():
    """Main backup execution"""
    print("=" * 60)
    print("OneDrive Backup and Removal Automation")
    print("=" * 60)

    # Initialize backup
    backup = OneDriveBackup(ONEDRIVE_SOURCE, BACKUP_BASE, BACKUP_NAME)

    # Check source exists
    print("\n[Step 1/6] Checking source folder...")
    if not backup.check_source_exists():
        return 1

    # Calculate source size
    print("\n[Step 2/6] Calculating source size...")
    total_size, file_count, folder_count = backup.calculate_source_size()

    # Check disk space
    print("\n[Step 3/6] Checking disk space...")
    if not backup.check_disk_space(total_size):
        print("\n✗ Insufficient disk space. Please free up space and try again.")
        return 1

    # Create backup
    print("\n[Step 4/6] Creating backup...")
    if not backup.create_backup():
        print("\n✗ Backup failed. OneDrive folder not deleted.")
        return 1

    # Verify backup
    print("\n[Step 5/6] Verifying backup...")
    verified = backup.verify_backup()

    # Save log
    backup.save_log()

    # Ask about deletion
    print("\n[Step 6/6] OneDrive folder removal...")

    if not verified:
        print("\n⚠ Backup verification failed!")
        response = input("Do you want to delete OneDrive anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("\n✓ Deletion cancelled. Please check backup manually.")
            return 0

    backup.remove_source()

    print("\n" + "=" * 60)
    print("Backup Complete!")
    print("=" * 60)
    print(f"\nBackup location: {backup.backup_dir}")
    print(f"Log file: {backup.log_file}")
    print(f"\nFiles backed up: {backup.stats['files_copied']:,}")
    print(f"Total size: {backup.format_size(backup.stats['total_size_bytes'])}")

    if backup.stats["errors"]:
        print(f"\nErrors: {len(backup.stats['errors'])}")
        print("Check log file for details.")

    return 0

if __name__ == "__main__":
    exit(main())
