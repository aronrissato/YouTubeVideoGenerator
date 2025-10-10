# Background Music

This folder contains the background music used in video generation.

## Current Music

- **File:** `background_music.mp3`
- **Source:** YouTube (https://www.youtube.com/watch?v=fg_wh-qqDf0)
- **Usage:** Background music for Bible video narration
- **Volume:** Configured to 10% by default (configurable in `video_config.json`)

## How to Replace

If you want to use different background music:

1. Replace the `background_music.mp3` file with your own music
2. Ensure the file is in MP3 format
3. Keep the filename as `background_music.mp3` or update the path in `video/video_creator.py`

## Notes

- The music file is included in the repository to avoid downloading from YouTube during GitHub Actions execution
- YouTube blocks yt-dlp in CI/CD environments, so using a local file ensures reliable video generation

