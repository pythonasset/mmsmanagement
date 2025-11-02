# Backup & Restore Guide

## Overview

The Maintenance Management System includes comprehensive backup and restore functionality to protect your data. This guide explains how to use the backup system effectively.

## Accessing Backup Features

1. Navigate to **⚙️ Administration** in the sidebar
2. Select the **⚙️ System Settings** tab
3. Scroll down to the **💾 Backup & Restore** section

## Backup Types

### Full Backup (Recommended)

**Includes:**
- ✅ Complete SQLite database
- ✅ All uploaded documents
- ✅ Document attachments
- 📋 Configuration file (optional)

**Format:** ZIP file  
**Best for:** Complete system backup, migration, disaster recovery

**When to use:**
- Before major system updates
- Monthly scheduled backups
- Before data migration
- System archival

### Database Only Backup

**Includes:**
- ✅ SQLite database file only

**Format:** .db file  
**Best for:** Quick daily backups, database-only snapshots

**When to use:**
- Daily automated backups
- Quick snapshots before bulk operations
- Testing data changes
- Faster backup when documents haven't changed

## Creating Backups

### Method 1: Full Backup

1. Go to **Administration → System Settings → Backup & Restore**
2. Select the **📥 Create Backup** tab
3. Choose **"Full Backup (Database + Documents)"**
4. Optional: Check **"Include Configuration File"** to backup config.ini
5. Optional: Add a custom backup name (e.g., "before_update", "monthly_backup")
6. Click **"💾 Create Full Backup"**
7. Download the backup file to a safe location

### Method 2: Quick Database Backup

1. Go to **Administration → System Settings → Backup & Restore**
2. Select the **📥 Create Backup** tab
3. Click **"🗄️ Quick Database Backup"**
4. Download the database file

### Backup File Naming

Backups are automatically named with timestamps:

- **Full Backup:** `backup_YYYYMMDD_HHMMSS.zip` or `[custom_name]_YYYYMMDD_HHMMSS.zip`
- **Database Only:** `db_backup_YYYYMMDD_HHMMSS.db`

Example: `backup_20241101_143022.zip` (November 1, 2024, 2:30:22 PM)

## Backup Storage

### Default Location

Backups are stored in: `data/backups/`

This location is configured in `config.ini`:

```ini
[Database]
backup_path = data/backups
```

### External Storage (Recommended)

**Best Practices:**
1. Download important backups to external storage
2. Store backups in multiple locations:
   - Local network drive
   - Cloud storage (OneDrive, Google Drive, Dropbox)
   - External hard drive
   - Off-site location
3. Keep at least 3 copies in different locations (3-2-1 rule)

## Restoring from Backup

### ⚠️ Important Warnings

**Before Restoring:**
- Restoring will **replace all current data**
- A safety backup is created automatically
- Ensure no other users are accessing the system
- Create a current backup first (if needed)

### Restore Procedure

1. Go to **Administration → System Settings → Backup & Restore**
2. Select the **📤 Restore Backup** tab
3. Select the backup to restore from the dropdown list
4. Review the backup details (date, size, type)
5. For full backups, choose restore options:
   - ☑️ **Restore Documents** (recommended)
   - ☐ **Restore Configuration** (optional - will overwrite config.ini)
6. Check the confirmation box: **"I understand that this will replace my current data"**
7. Click **"🔄 Restore Backup"**
8. Wait for the restore to complete
9. Refresh the page to see restored data

### After Restoring

1. **Verify Data Integrity**
   - Check asset counts
   - Verify recent records
   - Test key functions

2. **Test System Functions**
   - Create a test work order
   - Run a report
   - Check document access

3. **Inform Users**
   - Notify team members of the restore
   - Explain any data changes

## Managing Backups

### Viewing Backups

Go to **📤 Manage Backups** tab to see:
- All available backups
- Backup type (Full or Database Only)
- File size
- Creation date and time

### Downloading Backups

1. Select the **🗂️ Manage Backups** tab
2. Select a backup from the list
3. Click **"📥 Download"**
4. Save to your desired location

### Deleting Backups

1. Select the **🗂️ Manage Backups** tab
2. Select the backup to delete
3. Click **"🗑️ Delete"**
4. Confirm deletion

⚠️ **Warning:** Deleted backups cannot be recovered.

### Cleaning Up Old Backups

To automatically remove old backups and save disk space:

1. Select the **🗂️ Manage Backups** tab
2. Set **"Keep Recent Backups"** number (default: 10)
3. Click **"🧹 Clean Up Old Backups"**
4. The system will delete older backups, keeping only the most recent ones

## Backup Schedule Recommendations

### Production Environment

| Frequency | Type | Retention | Storage Location |
|-----------|------|-----------|------------------|
| **Daily** | Database Only | 7 days | Local |
| **Weekly** | Full Backup | 4 weeks | Local + Cloud |
| **Monthly** | Full Backup | 12 months | Cloud + External |
| **Yearly** | Full Backup | Permanent | Off-site Archive |

### Development/Testing Environment

| Frequency | Type | Retention | Storage Location |
|-----------|------|-----------|------------------|
| **Before Changes** | Database Only | 3 days | Local |
| **Weekly** | Full Backup | 2 weeks | Local |

## Backup Best Practices

### ✅ DO

1. **Create regular backups** - Daily for production systems
2. **Test restores periodically** - Ensure backups are valid
3. **Store backups off-site** - Protect against local disasters
4. **Keep multiple versions** - Don't rely on a single backup
5. **Document your backup schedule** - Know what's backed up and when
6. **Backup before major changes** - Updates, migrations, bulk imports
7. **Verify backup integrity** - Check file size and test restore
8. **Secure backup files** - Encrypt sensitive backups

### ❌ DON'T

1. **Don't rely on a single backup** - Always have multiple copies
2. **Don't store backups only locally** - Use cloud or external storage
3. **Don't ignore backup failures** - Check for errors regularly
4. **Don't keep backups indefinitely** - Clean up old backups to save space
5. **Don't share backups publicly** - Contains sensitive organization data
6. **Don't restore without testing** - Verify backup first in test environment
7. **Don't skip documentation** - Record what each backup contains

## Backup File Contents

### Full Backup (.zip) Structure

```
backup_20241101_143022.zip
├── database/
│   └── maintenance_management.db
├── documents/
│   ├── assets/
│   │   ├── [asset_documents]
│   ├── work_orders/
│   │   ├── [work_order_documents]
│   └── inspections/
│       └── [inspection_documents]
└── config.ini (if included)
```

### Database Backup (.db)

Single file: `maintenance_management.db`

Contains all system data:
- Assets and asset hierarchy
- Work orders
- Inspections
- Users
- Configuration settings (in database tables)

## Troubleshooting

### Problem: Backup Creation Fails

**Possible Causes:**
- Insufficient disk space
- File permissions issues
- Database is locked by another process

**Solutions:**
1. Check available disk space
2. Close any database management tools
3. Ensure backup directory has write permissions
4. Restart the application

### Problem: Restore Fails

**Possible Causes:**
- Corrupted backup file
- Incompatible database version
- File permissions issues

**Solutions:**
1. Try a different backup file
2. Check backup file integrity (file size)
3. Ensure you have write permissions
4. Contact support if issue persists

### Problem: Backup File Too Large

**Solutions:**
1. Use "Database Only" backup instead of full backup
2. Clean up old documents before backing up
3. Archive and remove old data
4. Split backups (database separate from documents)

### Problem: Can't Find Backup Files

**Solutions:**
1. Check backup path in Administration → System Settings
2. Look in `data/backups/` directory
3. Search for files: `backup_*.zip` or `db_backup_*.db`
4. Check if backups were downloaded (check Downloads folder)

## Automated Backup Scripts

### Windows Scheduled Task

Create a batch file `backup_daily.bat`:

```batch
@echo off
cd C:\path\to\application
python -c "from backup_manager import BackupManager; from config_loader import get_config; mgr = BackupManager(get_config()); mgr.create_database_only_backup()"
```

Schedule using Windows Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, 2:00 AM)
4. Action: Start a program
5. Program: `C:\path\to\application\backup_daily.bat`

### Linux Cron Job

Add to crontab:

```bash
# Daily database backup at 2:00 AM
0 2 * * * cd /path/to/application && python3 -c "from backup_manager import BackupManager; from config_loader import get_config; mgr = BackupManager(get_config()); mgr.create_database_only_backup()"

# Weekly full backup on Sundays at 3:00 AM
0 3 * * 0 cd /path/to/application && python3 -c "from backup_manager import BackupManager; from config_loader import get_config; mgr = BackupManager(get_config()); mgr.create_backup(include_documents=True)"
```

## Disaster Recovery

### Complete System Failure

1. **Install fresh application**
2. **Copy backup files** to new installation
3. **Restore latest full backup**
4. **Verify data integrity**
5. **Resume operations**

### Data Corruption

1. **Create safety backup** of current state
2. **Restore from last known good backup**
3. **Manually add recent data** if possible
4. **Test system thoroughly**

### Accidental Data Deletion

1. **Don't panic** - data may still be in backup
2. **Identify last good backup** before deletion
3. **Restore from backup**
4. **Verify restored data**
5. **Train users** to prevent recurrence

## Support

For backup-related issues or questions:

- **Email:** support@example.com
- **Documentation:** Refer to this guide
- **System Settings:** Check Administration → System Settings

---

**Remember:** A backup is only as good as your last restore test!

**Last Updated:** November 2024

