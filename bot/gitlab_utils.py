import re
from typing import (
    Dict,
    List
)
from dataclasses import dataclass


@dataclass
class Rule:
    id: int
    is_const: bool
    content: List[str]

    def __str__(self):
        return '\n'.join(self.content) + '\n'


rule_pattern = re.compile(r"(\d+).")
is_const_rule_pattern = re.compile(r'.*`konst`')


def is_rule_start(input_: str) -> bool:
    return rule_pattern.match(input_) is not None


def get_rule_number(input_: str) -> int:
    return int(rule_pattern.match(input_).group(1).strip())


def is_const_rule(input_: str) -> bool:
    return is_const_rule_pattern.match(input_) is not None


def parse_ruleset(
        ruleset: str

) -> Dict[int, Rule]:

    all_rules = {}

    is_current_rule_const = False
    current_rule_number = None
    current_rule_content = []

    skip_until_rule = True

    for line in ruleset.split('\n'):

        # skip markdown headers
        if line.strip().startswith('#'):
            skip_until_rule = True
            continue

        # new rule start
        if is_rule_start(line):
            skip_until_rule = False
            # if it's not a first rule start, save the rule
            if current_rule_content:
                all_rules[current_rule_number] = Rule(
                    id=current_rule_number,
                    is_const=is_current_rule_const,
                    content=current_rule_content
                )
                current_rule_content = []

            is_current_rule_const = is_const_rule(line)
            current_rule_number = get_rule_number(line)
            current_rule_content.append(line)

        # rule content
        else:
            if not skip_until_rule:
                current_rule_content.append(line)

    all_rules[current_rule_number] = Rule(
        id=current_rule_number,
        is_const=is_current_rule_const,
        content=current_rule_content
    )

    return all_rules


def make_rule_set(rules: List[Rule]) -> str:
    top_filler = "# Zasady\n\n## Zasady konstytucyjne\n\n"
    middle_filler = "## Zasady pozakonstytucyjne\n\n"

    const_rules = [rule for rule in rules if rule.is_const]
    nonconst_rules = [rule for rule in rules if not rule.is_const]

    const_rules.sort(key=lambda rule: rule.id)
    nonconst_rules.sort(key=lambda rule: rule.id)

    result = top_filler

    for rule in const_rules:
        result += str(rule)

    result += middle_filler

    for rule in nonconst_rules:
        result += str(rule)
    return result
