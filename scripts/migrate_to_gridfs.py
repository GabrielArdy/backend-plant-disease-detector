"""
Migration script to transfer existing images from the filesystem to GridFS
"""

import os
import sys
import time
from tqdm import tqdm
import argparse

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.storage import ImageStorage
from app.api.prediction.models import PredictionHistory

# Create Flask app context
app = create_app()

def get_prediction_id_from_filename(filename):
    """Extract prediction ID from filename (remove extension)"""
    return os.path.splitext(filename)[0]

def migrate_files(uploads_dir, dry_run=False, update_db=True):
    """
    Migrate all image files from filesystem to GridFS
    
    Args:
        uploads_dir: Directory containing upload files
        dry_run: If True, don't actually perform migration
        update_db: If True, update prediction records in database
    """
    count = 0
    errors = 0
    migration_map = {}  # Map of old paths to new GridFS IDs
    
    print(f"Scanning directory: {uploads_dir}")
    
    # Walk through all files in the uploads directory
    for root, dirs, files in os.walk(uploads_dir):
        for filename in tqdm(files, desc=f"Migrating files in {os.path.basename(root)}"):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                # Get full path and relative path
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, uploads_dir)
                prediction_id = get_prediction_id_from_filename(filename)
                
                print(f"Processing: {rel_path} (Prediction ID: {prediction_id})")
                
                if dry_run:
                    print(f"[DRY RUN] Would migrate: {rel_path}")
                    count += 1
                    continue
                
                # Migrate file to GridFS
                gridfs_id = ImageStorage.migrate_file_to_gridfs(rel_path, prediction_id)
                
                if gridfs_id:
                    print(f"Migrated: {rel_path} -> {gridfs_id}")
                    migration_map[rel_path] = gridfs_id
                    count += 1
                else:
                    print(f"Error migrating: {rel_path}")
                    errors += 1
    
    print(f"\nMigration summary:")
    print(f"- Total files processed: {count}")
    print(f"- Migration errors: {errors}")
    
    # Update database records if requested
    if update_db and not dry_run and count > 0:
        update_database_records(migration_map)
    
    return count, errors

def update_database_records(migration_map):
    """
    Update prediction records in the database to use new GridFS IDs
    
    Args:
        migration_map: Dictionary mapping old file paths to new GridFS IDs
    """
    with app.app_context():
        # Update database records
        print("\nUpdating database records...")
        updated = 0
        errors = 0
        
        for old_path, new_id in tqdm(migration_map.items(), desc="Updating DB records"):
            try:
                # Find prediction records with this image path
                result = app.mongo.db.prediction_history.update_many(
                    {"image_path": old_path},
                    {"$set": {"image_path": new_id, "storage_type": "gridfs"}}
                )
                
                if result.modified_count > 0:
                    updated += result.modified_count
                    print(f"Updated {result.modified_count} records for {old_path}")
            except Exception as e:
                print(f"Error updating records for {old_path}: {str(e)}")
                errors += 1
        
        print(f"\nDatabase update summary:")
        print(f"- Records updated: {updated}")
        print(f"- Update errors: {errors}")

def verify_migration():
    """Verify that files were correctly migrated to GridFS"""
    with app.app_context():
        print("\nVerifying migration...")
        
        # Count GridFS files
        grid_count = app.mongo.db.fs.files.count_documents({})
        print(f"Total files in GridFS: {grid_count}")
        
        # Check for records still using filesystem paths
        legacy_count = app.mongo.db.prediction_history.count_documents({
            "image_path": {"$regex": "^[^0-9a-f]"}  # Non-ObjectId paths
        })
        
        gridfs_count = app.mongo.db.prediction_history.count_documents({
            "image_path": {"$regex": "^[0-9a-f]{24}$"}  # ObjectId strings
        })
        
        print(f"Records using filesystem paths: {legacy_count}")
        print(f"Records using GridFS: {gridfs_count}")
        
        # Sample some records
        if gridfs_count > 0:
            print("\nSample GridFS records:")
            for record in app.mongo.db.prediction_history.find(
                {"image_path": {"$regex": "^[0-9a-f]{24}$"}},
                {"prediction_id": 1, "image_path": 1}
            ).limit(5):
                print(f"- Prediction: {record.get('prediction_id')}, Image: {record.get('image_path')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate image files from filesystem to GridFS")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without doing it")
    parser.add_argument("--no-db-update", action="store_true", help="Skip updating database records")
    parser.add_argument("--verify", action="store_true", help="Verify migration status")
    
    args = parser.parse_args()
    
    if args.verify:
        with app.app_context():
            verify_migration()
        sys.exit(0)
    
    # Get uploads directory from app config
    uploads_dir = ImageStorage.BASE_DIR
    print(f"Using uploads directory: {uploads_dir}")
    
    start_time = time.time()
    
    with app.app_context():
        count, errors = migrate_files(
            uploads_dir, 
            dry_run=args.dry_run, 
            update_db=not args.no_db_update
        )
    
    elapsed = time.time() - start_time
    print(f"\nMigration completed in {elapsed:.2f} seconds")
    
    if not args.dry_run and errors == 0:
        print("\nMigration successful. You may want to run with --verify to check the results.")
        print("Once verified, you can safely delete the original files if desired.")
