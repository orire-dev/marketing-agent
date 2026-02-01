# Max Tokens Error - Fixed

## Error

```
BadRequestError: Error code: 400 - max_tokens: 8000 > 4096, which is the maximum allowed number of output tokens for claude-3-haiku-20240307
```

## Problem

The generator was requesting `max_tokens=8000`, but **Claude-3-Haiku** only supports a maximum of **4096 output tokens**.

## Solution

**File**: `app/generator.py` (line ~123)

**Changed**:
- `max_tokens=8000` → `max_tokens=4096`

This respects the model's token limit while still allowing for substantial creative content generation.

## Model Token Limits

- **Claude-3-Haiku**: 4096 max output tokens ✅ (now using)
- **Claude-3-Sonnet**: 4096 max output tokens
- **Claude-3-Opus**: 4096 max output tokens
- **Claude-3.5-Sonnet**: 8192 max output tokens (if available)

## Status

✅ **Fixed** - Server restarted with corrected token limit
✅ **Ready** - Generation should work without BadRequestError

The system will now generate content within the model's token limits. For multiple options, the content will be more concise but still complete.
