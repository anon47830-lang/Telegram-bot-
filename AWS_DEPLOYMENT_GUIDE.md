# AWS Lambda Deployment Guide for Telegram Channel Bot

This guide will help you deploy your Telegram Channel Bot on AWS Lambda using the AWS Serverless Application Model (SAM).

## Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions
2. **AWS CLI**: Install and configure AWS CLI
3. **AWS SAM CLI**: Install AWS SAM CLI for deployment
4. **Bot Token**: Your Telegram bot token

## Step 1: Install AWS CLI

### Windows:
1. Download the AWS CLI installer from: https://aws.amazon.com/cli/
2. Run the installer and follow the instructions

### macOS:
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### Linux:
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

## Step 2: Configure AWS CLI

Run the following command and provide your AWS credentials:

```bash
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., `us-east-1`)
- Default output format (use `json`)

## Step 3: Install AWS SAM CLI

### Windows:
1. Download the SAM CLI installer from: https://github.com/aws/aws-sam-cli/releases
2. Run the installer

### macOS:
```bash
brew install aws-sam-cli
```

### Linux:
```bash
# Download the installer
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install
```

## Step 4: Prepare Your Bot Files

1. **Upload all bot files** to a directory on your local machine:
   - `lambda_function.py` (main Lambda handler)
   - `bot_lambda.py` (modified bot class)
   - `config.py` (configuration)
   - `database.py` (database handler)
   - `template.yaml` (SAM template)
   - `requirements_lambda.txt` (Python dependencies)

2. **Create a `.env` file** in the same directory with your bot token:
   ```
   BOT_TOKEN=7797381180:AAFPikEzAxSfK-3SLe-lEwhRKyj5oldpzb0
   ```

## Step 5: Deploy the Bot

1. **Open terminal/command prompt** in your bot directory

2. **Build the SAM application**:
   ```bash
   sam build
   ```

3. **Deploy the application**:
   ```bash
   sam deploy --guided
   ```

   During the guided deployment, you'll be asked:
   - **Stack Name**: Enter `telegram-channel-bot`
   - **AWS Region**: Choose your preferred region (e.g., `us-east-1`)
   - **Parameter BotToken**: Enter your bot token when prompted
   - **Confirm changes before deploy**: Enter `Y`
   - **Allow SAM CLI IAM role creation**: Enter `Y`
   - **Save parameters to samconfig.toml**: Enter `Y`

4. **Wait for deployment** to complete. This may take a few minutes.

## Step 6: Get the Webhook URL

After successful deployment, you'll see output similar to:
```
Outputs:
TelegramBotApi: https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/webhook
```

**Copy this webhook URL** - you'll need it for the next step.

## Step 7: Set Up Telegram Webhook

You need to tell Telegram to send updates to your Lambda function. Replace `YOUR_BOT_TOKEN` and `YOUR_WEBHOOK_URL` in the following command:

```bash
curl -X POST "https://api.telegram.org/bot7797381180:AAFPikEzAxSfK-3SLe-lEwhRKyj5oldpzb0/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "YOUR_WEBHOOK_URL"}'
```

Example:
```bash
curl -X POST "https://api.telegram.org/bot7797381180:AAFPikEzAxSfK-3SLe-lEwhRKyj5oldpzb0/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/webhook"}'
```

You should receive a response like:
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

## Step 8: Test Your Bot

1. **Open Telegram** and search for your bot (`@Instaviralmmsbot`)
2. **Send `/start`** to test if the bot responds
3. **Try the channel verification** process

## Step 9: Monitor Your Bot

### View Logs:
```bash
sam logs -n TelegramBotFunction --stack-name telegram-channel-bot --tail
```

### Check AWS Console:
1. Go to AWS Lambda console
2. Find your function (usually named `telegram-channel-bot-TelegramBotFunction-...`)
3. Check the "Monitoring" tab for metrics and logs

## Updating Your Bot

When you make changes to your bot code:

1. **Update your local files**
2. **Rebuild and redeploy**:
   ```bash
   sam build
   sam deploy
   ```

The webhook URL will remain the same, so you don't need to update it with Telegram.

## Cost Considerations

AWS Lambda free tier includes:
- **1 million free requests per month**
- **400,000 GB-seconds of compute time per month**

For a typical small to medium Telegram bot, this should be sufficient to run completely free.

## Troubleshooting

### Bot Not Responding:
1. Check CloudWatch logs for errors
2. Verify webhook is set correctly:
   ```bash
   curl "https://api.telegram.org/bot7797381180:AAFPikEzAxSfK-3SLe-lEwhRKyj5oldpzb0/getWebhookInfo"
   ```

### Deployment Errors:
1. Ensure AWS CLI is configured correctly
2. Check that you have necessary IAM permissions
3. Verify all required files are in the directory

### Lambda Function Errors:
1. Check CloudWatch logs in AWS Console
2. Ensure all dependencies are listed in `requirements_lambda.txt`
3. Verify environment variables are set correctly

## Removing the Bot

To delete all AWS resources:
```bash
sam delete --stack-name telegram-channel-bot
```

## Support

If you encounter issues:
1. Check the AWS CloudWatch logs
2. Verify your bot token is correct
3. Ensure all required channels have the bot as an admin
4. Check that chat IDs in `config.py` are correct

Your bot should now be running 24/7 on AWS Lambda for free!

