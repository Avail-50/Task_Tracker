# Serverless task tracker

## Architecture

Client -> API Gateway -> Lambda (Python) -> DynamoDB

- **API Gateway** exposes the HTTP routes.
- **Lambda** (Python) validates input and reads/writes tasks.
- **DynamoDB** stores tasks (on-demand billing, partition key `taskID`).
- **IAM:** the function's role is limited to this one table.
- Everything is defined in `template.yaml`, so the whole stack can be recreated with one command.

## API

| Method | Path | Description |
|---|---|---|
| POST | `/tasks` | Create a task. Body: `{"title": "..."}` |
| GET | `/tasks` | Lists all tasks. |
| PATCH | `/tasks/{taskID}` | Set a task's `done` status. Body: `{"done": true}` |

## Deploy

Requires the AWS CLI, SAM CLI and Python.

```bash
sam build
sam deploy --guided
```

The API URL appears in the stack outputs. Run `sam delete` to remove everything.

## Limitations

- No authentication on the API.
- Listing tasks uses a DynamoDB Scan, which doesn't scale.