from abc import abstractmethod
from typing import List
from discord import Embed


class RulesAPI:

    @abstractmethod
    def print_rules(self, rule_type: str) -> Embed:
        raise NotImplementedError

    @abstractmethod
    def print_rule(self, rule_number: int) -> Embed:
        raise NotImplementedError

    @abstractmethod
    def add_rule(
            self,
            rule_content: List[str],
            player_name: str,
    ) -> Embed:
        raise NotImplementedError

    @abstractmethod
    def edit_rule(
            self,
            rule_id: int,
            rule_content: str,
            player_name: str,
    ) -> Embed:
        raise NotImplementedError

    @abstractmethod
    def transmute_rule(
            self,
            rule_id: int,
            player_name: str,
    ) -> Embed:
        raise NotImplementedError
