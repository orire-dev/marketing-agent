# Image Generation Setup

## Overview

The system now supports actual image generation (not just prompts) using OpenAI DALL-E 3.

## Setup

### 1. Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add it to your `.env` file:

```bash
echo "OPENAI_API_KEY=sk-..." >> ~/.env
```

### 2. Install Dependencies

Already included in `requirements.txt`:
- `openai>=1.3.0`
- `requests>=2.31.0`

### 3. How It Works

- **With OpenAI API Key**: Generates actual images using DALL-E 3
- **Without API Key**: Falls back to stub renderer (returns placeholder URIs)

## Image Generation

When you generate creatives:
1. System creates image prompts
2. Calls DALL-E 3 API to generate 1:1 images
3. Returns image URLs in the response
4. Images are stored in `generated_image_uri` field

## Supported Formats

- **Static Image**: 1:1 (1024x1024) DALL-E 3 generation
- **Motion Ad**: Storyboard generated, actual motion rendering coming soon
- **Short Video**: Placeholder for now

## Output Structure

Each creative option now includes:
```json
{
  "prompts": {
    "social_1x1": {
      "en": {
        "image_prompt": "...",
        "generated_image_uri": "https://...",
        "generation_status": "completed"
      }
    }
  }
}
```

## Platform-Specific Copy

The system now generates platform-specific copy:
- **Primary Text**: Main ad copy (follows platform length rules)
- **Headline**: Ad headline
- **Secondary Line**: Optional subhead
- **CTA**: Call-to-action

## Next Steps

1. Add your OpenAI API key to `.env`
2. Restart the server
3. Generate creatives - you'll get actual images!
