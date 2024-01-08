# samplesdb

## Rationale
This repo intends to give tools and flexibility when working with a database of musics: 
 * Standardise business information
 * Downloading locally music
 * Upload and enrich music in the database
 * Expose music to other potential listeners


## Install 
TODO
`pip install`

##  Features

### Track Management

With samplesdb, you can easily manage your music tracks. This includes:

* Adding New Tracks: Upload new tracks to the database with metadata.
* Updating Tracks: Modify existing track information as needed.
* Deleting Tracks: Remove tracks that are no longer needed.

### Metadata Enrichment - TODO 
Enhance your tracks with rich metadata:
* **Automatic Tagging**: Auto-tag tracks with genre, mood, and other relevant tags.
* **Manual Tagging**: Manually add or edit tags for greater control.

### Local Download
Download tracks directly to your local machine:

**Batch Download**: Download multiple tracks at once.
**Selective Download**: Choose specific tracks to download based on criteria like genre or popularity.

## Usage
Here's a quick guide on how to use samplesdb:

### Adding a New Track
To add a new track to the database:

```python
from samplesdb import TrackManager
track_manager = TrackManager()
track_manager.add_track('path/to/your/track.mp3', metadata={'artist': 'Artist Name', 'title': 'Track Title'})
```

### Searching for Tracks
To search for tracks in the database:

```python
tracks = track_manager.search_tracks(artist='Artist Name', genre='Genre')
for track in tracks:
    print(track)
```

### Downloading Tracks
To download tracks:

```python
track_manager.download_tracks(tracks, download_folder='path/to/download')
```

## Contributing
Contributions to samplesdb are welcome! Please read our CONTRIBUTING.md for guidelines on how to contribute.

## License
samplesdb is released under the MIT License.

## Contact
For any questions or feedback, please contact us at arthur@stackadoc.com and paul@stackadoc.com

## Acknowledgments
Thanks to all contributors and users of samplesdb for your support and feedback.