#!/usr/bin/env python3

import aws_cdk as cdk

from nomic_bot.nomic_bot_stack import NomicBotStack

# This is an entrypoint to CDK.
# Here you define App construct,
# and all stacks that should be created.
app = cdk.App()

# NomicBot stack encapsulates all AWS Services
# that are needed for bot to work.
NomicBotStack(app, "nomic-bot")

app.synth()
