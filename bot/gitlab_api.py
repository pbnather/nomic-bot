import copy
import os
from typing import (
    List,
    Dict
)

from discord import Embed
import gitlab

from bot.rules_api import RulesAPI
from bot.gitlab_utils import parse_ruleset, Rule, make_rule_set


class GitlabAPI(RulesAPI):
    GITLAB_PERSONAL_ACCESS_TOKEN_STRING_VARNAME = 'GITLAB_PERSONAL_ACCESS_TOKEN'
    NOMIC_REPOSITORY_NAME = 'nomic'
    BRANCH = 'dev'
    RULES_PATH = 'README.md'

    def __init__(self):
        self.token = os.getenv(self.GITLAB_PERSONAL_ACCESS_TOKEN_STRING_VARNAME)
        if self.token is None:
            raise ValueError(
                f'Please fill `{self.GITLAB_PERSONAL_ACCESS_TOKEN_STRING_VARNAME}` env variable with '
                f'Your Gitlab Personal Access Token.'
                )
        self.gl = gitlab.Gitlab(private_token=self.token)
        self.project = self.gl.projects.list(search=self.NOMIC_REPOSITORY_NAME, owned=True)[0]

    def print_rules(self, rule_type: str) -> Embed:
        assert rule_type in {'const', 'not-const', 'all'}

        rules_raw = self.project.files.raw(file_path=self.RULES_PATH, ref=self.BRANCH)
        rules_raw = rules_raw.decode('UTF-8')
        rules = parse_ruleset(rules_raw)
        embed = Embed(
            title='Const rules'
        )

        for rule_id, rule in rules.items():
            if (
                    rule.is_const and (rule_type == 'const' or rule_type == 'all')
            ) or (
                    not rule.is_const and (rule_type == 'not-const' or rule_type == 'all')
            ):
                embed.add_field(
                    name=str(rule_id),
                    value=str(rule),
                    inline=False
                )

        return embed

    def print_rule(self, rule_number: int) -> Embed:

        rules_raw = self.project.files.raw(file_path=self.RULES_PATH, ref=self.BRANCH)
        rules_raw = rules_raw.decode('UTF-8')
        rules = parse_ruleset(rules_raw)

        rule = rules[rule_number]
        embed = Embed(
            title=f'Rule {rule_number}'
        )
        embed.add_field(
            name='',
            value=str(rule),
            inline=False
        )
        return embed

    def _create_mr_from_player_action_and_rule_set(
            self,
            player_name: str,
            rule_number: int,
            player_action: str,
            rules_dict: Dict[int, Rule]
    ) -> str:

        suffix = 0
        branch_names = {b.name for b in self.project.branches.list()}

        while True:
            new_branch_name = f'{player_action}-{rule_number}-{player_name}-{suffix}'
            if new_branch_name in branch_names:
                suffix += 1
            else:
                break
        branch = self.project.branches.create(
            {
                'branch': new_branch_name,
                'ref': self.BRANCH
            }
        )

        commit_message = None
        action_label = None
        if player_action == 'add':
            commit_message = f'Add new rule {rule_number} by {player_name}'
            action_label = 'add-rule'
        elif player_action == 'edit':
            commit_message = f'Edit rule {rule_number} by {player_name}'
            action_label = 'edit-rule'
        elif player_action == 'transmute':
            commit_message = f'Transmute rule {rule_number} by {player_name}'
            action_label = 'transmute'


        commit = self.project.commits.create(
            {
                'branch': new_branch_name,
                'commit_message': commit_message,
                'actions': [
                    {
                        'action': 'update',
                        'file_path': self.RULES_PATH,
                        'content':  make_rule_set(list(rules_dict.values()))
                    }
                ]
            }
        )

        mr = self.project.mergerequests.create(
            {
                'source_branch': new_branch_name,
                'target_branch': self.BRANCH,
                'title': commit_message,
                'labels': [action_label, player_name]
            }
        )
        mr.save()

        return mr.web_url

    def add_rule(
            self,
            rule_content: List[str],
            player_name: str,
    ) -> Embed:

        rules_raw = self.project.files.raw(file_path=self.RULES_PATH, ref=self.BRANCH)
        rules_raw = rules_raw.decode('UTF-8')
        rules = parse_ruleset(rules_raw)
        new_rule_number = max(rules.keys()) + 1

        rules[new_rule_number] = Rule(
            id=new_rule_number,
            is_const=False,
            content=[f'{new_rule_number}.'] + rule_content
        )

        mr_web_url = self._create_mr_from_player_action_and_rule_set(
            player_name=player_name,
            rules_dict=rules,
            player_action='add',
            rule_number=new_rule_number
        )

        embed = Embed(
            title=f'New rule {new_rule_number} was proposed by {player_name}',
            inline=False
        )

        embed.add_field(
            name='Merge Request URL',
            value=mr_web_url + '/diffs',
            inline=False
        )
        embed.add_field(
            name='New rule content',
            value=str(rules[new_rule_number]),
            inline=False
        )
        return embed

    def edit_rule(
            self,
            rule_id: int,
            rule_content: List[str],
            player_name: str,
    ) -> Embed:
        rules_raw = self.project.files.raw(file_path=self.RULES_PATH, ref=self.BRANCH)
        rules_raw = rules_raw.decode('UTF-8')
        rules = parse_ruleset(rules_raw)

        # Rule that is being edited doesn't exist
        if rule_id not in rules:
            return Embed(
                title=f'There is no rule {rule_id}',
            )

        # Trying to modify a const rule
        if rules[rule_id].is_const:
            return Embed(
                title=f'Rule {rule_id} is const and can\'t be edited',
            )
        old_rule = copy.deepcopy(rules[rule_id])

        rules[rule_id].content = rule_content

        mr_web_url = self._create_mr_from_player_action_and_rule_set(
            player_name=player_name,
            rules_dict=rules,
            player_action='edit',
            rule_number=rule_id
        )

        embed = Embed(
            title=f'Edit of rule {rule_id} was proposed by {player_name}',
            inline=False
        )

        embed.add_field(
            name='Merge Request URL',
            value=mr_web_url + '/diffs',
            inline=False
        )
        embed.add_field(
            name='Old rule conent',
            value=str(old_rule),
            inline=True
        )
        embed.add_field(
            name='New rule content',
            value=str(rules[rule_id]),
            inline=True
        )
        return embed

    def transmute_rule(
            self,
            rule_id: int,
            player_name: str,
    ) -> Embed:

        rules_raw = self.project.files.raw(file_path=self.RULES_PATH, ref=self.BRANCH)
        rules_raw = rules_raw.decode('UTF-8')
        rules = parse_ruleset(rules_raw)

        # Rule that is being edited doesn't exist
        if rule_id not in rules:
            return Embed(
                title=f'There is no rule {rule_id}',
            )

        if rules[rule_id].is_const:
            rules[rule_id].content[0] = rules[rule_id].content[0].replace('`konst`', '').strip()
            rules[rule_id].is_const = False
        else:
            rule_parts = rules[rule_id].content[0].split('.')
            new_first_rule_line = rule_parts[0] + '. `konst`' + '.'.join(rule_parts[1:])
            rules[rule_id].content[0] = new_first_rule_line

        mr_web_url = self._create_mr_from_player_action_and_rule_set(
            player_name=player_name,
            rules_dict=rules,
            player_action='transmute',
            rule_number=rule_id
        )

        embed = Embed(
            title=f'Transmutation of rule {rule_id} was proposed by {player_name}',
            inline=False
        )
        embed.add_field(
            name='Merge Request URL',
            value=mr_web_url + '/diffs',
            inline=False
        )
        embed.add_field(
            name='Transmuted rule content',
            value=str(rules[rule_id]),
            inline=False
        )
        return embed
