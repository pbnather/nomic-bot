# Discord Nomic Bot (running on AWS)
This bot will let you play Nomic via Discord, while being hosted on AWS.
For now it's functionality is limited though.

- Bot source code is in `./bot` directory.
- CDK stacks are in `./nomic_bot` directory.

### prerequisites:
- AWS account,
- Registered (Discord Bot)[https://realpython.com/how-to-make-a-discord-bot-python/],
- `.env` file in `./bot` folder with `DISCORD_TOKEN` variable.

## Install vitrualenv and dependencies
1. `python3 -m venv .venv`
2. `source .venv/bin/activate` (`.venv\Scripts\activate.bat` on Windows)
3. `pip install -r requirements.txt`

## Deploy bot on AWS (CDK)

1. Install (aws-cli)[https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html]. 
2. Configure (access keys)[https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html] to your AWS account.
3. `cdk bootstrap` — create once supporting constructs in your account.
4. `cdk synth` — create your cloudformation files.
5. `cdk deploy` — deploy your stacks to AWS.

After changes, you can repeat points `4` and `5` to update your services.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
