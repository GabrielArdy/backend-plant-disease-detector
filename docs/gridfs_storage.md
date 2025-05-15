# GridFS Storage for Plant Disease Images

This document explains how image storage is implemented using GridFS in MongoDB.

## Overview

Plant disease images are now stored in MongoDB using GridFS, which allows for efficient storage and retrieval of large files. GridFS stores files in two collections:

1. `fs.files` - Stores file metadata
2. `fs.chunks` - Stores the actual file data in chunks

## Benefits of GridFS

- **Database-based storage**: All images are stored in the database, making backups and migrations easier
- **No file system dependencies**: No need to worry about file system permissions or directory structures
- **Metadata storage**: File metadata (like user ID, prediction ID) is stored alongside the file
- **Scalability**: GridFS can handle files of any size
- **Consistency**: Database transactions ensure file data and metadata consistency

## Storage Implementation

The `ImageStorage` class in `app/utils/storage.py` provides methods for storing and retrieving images using GridFS:

- `save_prediction_image()`: Saves an uploaded image to GridFS and returns the file ID
- `get_image_from_gridfs()`: Retrieves image data from GridFS using a file ID
- `get_image_as_base64()`: Gets an image as a base64 encoded string (for API responses)
- `get_image_metadata()`: Retrieves metadata for a stored image
- `delete_image()`: Deletes an image from GridFS

## File Metadata

When storing images in GridFS, the following metadata is included:

- `content_type`: The MIME type (usually "image/jpeg")
- `prediction_id`: ID of the associated prediction
- `user_id`: ID of the user who uploaded the image
- `timestamp`: When the file was uploaded
- `filename`: Original filename

## Legacy Support

The system maintains backward compatibility with the old file system-based storage:

- If an image path contains a slash ("/"), it's treated as a legacy path
- `get_image_as_base64()` will try to load from the file system first for legacy paths
- The migration script can move existing files from the file system to GridFS

## Migration

A migration script is provided to transfer existing images from the file system to GridFS:

```bash
# Dry run (shows what would be migrated without making changes)
python scripts/migrate_to_gridfs.py --dry-run

# Run actual migration
python scripts/migrate_to_gridfs.py

# Verify migration results
python scripts/migrate_to_gridfs.py --verify
```

## Database Schema Changes

The `prediction_history` collection now includes a `storage_type` field which can be:

- `"gridfs"`: Indicates the image is stored in GridFS
- `"filesystem"`: Indicates the image is stored in the legacy file system
