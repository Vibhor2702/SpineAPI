# GitHub Actions Secrets Configuration

The SpineAPI project uses GitHub Actions for CI/CD automation. To enable all features, you need to configure the following secrets in your GitHub repository settings.

## Required Secrets

### Docker Hub Integration (Optional)
- **DOCKER_USERNAME**: Your Docker Hub username
- **DOCKER_PASSWORD**: Your Docker Hub access token or password

Used for building and pushing Docker images to Docker Hub registry.

### PyPI Publishing (Optional)
- **PYPI_API_TOKEN**: Your PyPI API token for publishing packages

Used for automatically publishing releases to PyPI.

### Slack Notifications (Optional)
- **SLACK_WEBHOOK_URL**: Webhook URL for Slack notifications

Used for sending build status notifications to Slack channels.

## How to Configure Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the appropriate name and value

## Notes

- These secrets are optional - the CI will still work without them
- Docker and PyPI publishing steps will be skipped if secrets are not configured
- Slack notifications will be disabled if webhook URL is not provided
- The project can be built and tested locally without any secrets

## Security Best Practices

- Never commit secrets to the repository
- Use fine-grained access tokens when possible
- Regularly rotate secrets and tokens
- Monitor secret usage in the Actions logs
