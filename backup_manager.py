"""
Backup Manager Module
Handles database and document backups, restoration, and management
"""
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
import streamlit as st


class BackupManager:
    """Manager for creating and restoring system backups"""
    
    def __init__(self, config):
        """Initialize backup manager with configuration"""
        self.config = config
        self.backup_root = Path(config.BACKUP_PATH)
        self.database_path = Path(config.DATABASE_PATH)
        self.documents_path = Path(config.DOCUMENT_ROOT)
        
        # Ensure backup directory exists
        self.backup_root.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, include_documents=True, include_config=False, backup_name=None):
        """
        Create a full backup of the system
        
        Args:
            include_documents: Include documents folder in backup
            include_config: Include configuration file in backup
            backup_name: Custom backup name (optional)
        
        Returns:
            tuple: (success, backup_file_path, message)
        """
        try:
            # Generate backup filename with timestamp
            if backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{backup_name}_{timestamp}.zip"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"backup_{timestamp}.zip"
            
            backup_path = self.backup_root / backup_filename
            
            # Create zip file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add database
                if self.database_path.exists():
                    zipf.write(self.database_path, arcname=f"database/{self.database_path.name}")
                else:
                    return False, None, "Database file not found"
                
                # Add documents if requested
                if include_documents and self.documents_path.exists():
                    for root, dirs, files in os.walk(self.documents_path):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(self.documents_path.parent)
                            zipf.write(file_path, arcname=str(arcname))
                
                # Add config if requested
                if include_config:
                    config_file = Path("config.ini")
                    if config_file.exists():
                        zipf.write(config_file, arcname="config.ini")
            
            # Get file size
            file_size = self._get_readable_size(backup_path.stat().st_size)
            
            return True, str(backup_path), f"Backup created successfully: {backup_filename} ({file_size})"
        
        except Exception as e:
            return False, None, f"Backup failed: {str(e)}"
    
    def create_database_only_backup(self):
        """
        Create a quick database-only backup
        
        Returns:
            tuple: (success, backup_file_path, message)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"db_backup_{timestamp}.db"
            backup_path = self.backup_root / backup_filename
            
            if not self.database_path.exists():
                return False, None, "Database file not found"
            
            # Copy database file
            shutil.copy2(self.database_path, backup_path)
            
            file_size = self._get_readable_size(backup_path.stat().st_size)
            
            return True, str(backup_path), f"Database backup created: {backup_filename} ({file_size})"
        
        except Exception as e:
            return False, None, f"Database backup failed: {str(e)}"
    
    def list_backups(self):
        """
        List all available backups
        
        Returns:
            list: List of dictionaries containing backup information
        """
        backups = []
        
        if not self.backup_root.exists():
            return backups
        
        # Get all backup files (zip and db files)
        backup_files = list(self.backup_root.glob("*.zip")) + list(self.backup_root.glob("*.db"))
        
        for backup_file in backup_files:
            try:
                stat = backup_file.stat()
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size': self._get_readable_size(stat.st_size),
                    'size_bytes': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime),
                    'type': 'Full Backup' if backup_file.suffix == '.zip' else 'Database Only'
                })
            except Exception:
                continue
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups
    
    def restore_backup(self, backup_path, restore_documents=True, restore_config=False):
        """
        Restore system from a backup file
        
        Args:
            backup_path: Path to the backup file
            restore_documents: Restore documents folder
            restore_config: Restore configuration file
        
        Returns:
            tuple: (success, message)
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                return False, "Backup file not found"
            
            # Handle database-only backups (.db files)
            if backup_file.suffix == '.db':
                return self._restore_database_only(backup_file)
            
            # Handle full backups (.zip files)
            if backup_file.suffix == '.zip':
                return self._restore_full_backup(backup_file, restore_documents, restore_config)
            
            return False, "Invalid backup file format"
        
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
    
    def _restore_database_only(self, backup_file):
        """Restore database from a .db backup file"""
        try:
            # Create a backup of current database before restoring
            if self.database_path.exists():
                current_backup = self.database_path.parent / f"{self.database_path.stem}_before_restore.db"
                shutil.copy2(self.database_path, current_backup)
            
            # Restore database
            shutil.copy2(backup_file, self.database_path)
            
            return True, f"Database restored successfully from {backup_file.name}"
        
        except Exception as e:
            return False, f"Database restore failed: {str(e)}"
    
    def _restore_full_backup(self, backup_file, restore_documents, restore_config):
        """Restore from a full .zip backup file"""
        try:
            # Create a safety backup of current database
            if self.database_path.exists():
                safety_backup = self.database_path.parent / f"{self.database_path.stem}_safety_backup.db"
                shutil.copy2(self.database_path, safety_backup)
            
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Extract database
                db_files = [f for f in zipf.namelist() if f.startswith('database/')]
                for db_file in db_files:
                    zipf.extract(db_file, path=self.database_path.parent.parent)
                
                # Extract documents if requested
                if restore_documents:
                    doc_files = [f for f in zipf.namelist() if f.startswith('documents/')]
                    for doc_file in doc_files:
                        zipf.extract(doc_file, path=self.documents_path.parent)
                
                # Extract config if requested
                if restore_config and 'config.ini' in zipf.namelist():
                    zipf.extract('config.ini')
            
            return True, f"System restored successfully from {backup_file.name}"
        
        except Exception as e:
            return False, f"Full restore failed: {str(e)}"
    
    def delete_backup(self, backup_path):
        """
        Delete a backup file
        
        Args:
            backup_path: Path to the backup file to delete
        
        Returns:
            tuple: (success, message)
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                return False, "Backup file not found"
            
            backup_file.unlink()
            
            return True, f"Backup deleted: {backup_file.name}"
        
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def get_backup_statistics(self):
        """
        Get statistics about backups
        
        Returns:
            dict: Statistics about backups
        """
        backups = self.list_backups()
        
        if not backups:
            return {
                'total_backups': 0,
                'total_size': '0 B',
                'total_size_bytes': 0,
                'oldest_backup': None,
                'newest_backup': None
            }
        
        total_size_bytes = sum(b['size_bytes'] for b in backups)
        
        return {
            'total_backups': len(backups),
            'total_size': self._get_readable_size(total_size_bytes),
            'total_size_bytes': total_size_bytes,
            'oldest_backup': backups[-1]['created'] if backups else None,
            'newest_backup': backups[0]['created'] if backups else None
        }
    
    def cleanup_old_backups(self, keep_count=10):
        """
        Delete old backups, keeping only the most recent ones
        
        Args:
            keep_count: Number of recent backups to keep
        
        Returns:
            tuple: (success, deleted_count, message)
        """
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                return True, 0, f"No cleanup needed. Only {len(backups)} backup(s) exist."
            
            # Delete old backups
            backups_to_delete = backups[keep_count:]
            deleted_count = 0
            
            for backup in backups_to_delete:
                try:
                    Path(backup['path']).unlink()
                    deleted_count += 1
                except Exception:
                    continue
            
            return True, deleted_count, f"Deleted {deleted_count} old backup(s). Kept {keep_count} most recent."
        
        except Exception as e:
            return False, 0, f"Cleanup failed: {str(e)}"
    
    def _get_readable_size(self, size_bytes):
        """Convert bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def export_backup_info(self):
        """
        Export backup information for reporting
        
        Returns:
            dict: Backup information suitable for export
        """
        backups = self.list_backups()
        stats = self.get_backup_statistics()
        
        return {
            'statistics': stats,
            'backups': backups,
            'backup_location': str(self.backup_root),
            'database_location': str(self.database_path),
            'documents_location': str(self.documents_path)
        }

