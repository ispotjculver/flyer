# Survey Automation Project

Automates online survey taking with support for generic surveys and replay functionality.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

3. Run the application:
```bash
python app.py
```

## Endpoints

### POST /survey/take?survey_uuid=<uuid>
Takes a generic survey with the specified UUID.

### POST /survey/replay?survey_uuid=<uuid>&replay_uuid=<uuid>
Replays answers from a previous survey (stored in S3) to a new survey.

Request body for replay:
```json
{
  "bucket": "your-s3-bucket-name"
}
```