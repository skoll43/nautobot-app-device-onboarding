"""Datasources to override command_mapper yaml files."""

from nautobot.extras.choices import LogLevelChoices
from nautobot.apps.datasources import DatasourceContent


def refresh_git_command_mappers(repository_record, job_result, delete=False):  # pylint: disable=unused-argument
    """Callback for gitrepository updates on Onboarding Command Mapper Repo."""
    job_result.log(
        "Successfully Pulled Command Mapper Repo",
        level_choice=LogLevelChoices.LOG_DEBUG,
    )


datasource_contents = [
    (
        "extras.gitrepository",
        DatasourceContent(
            name="Onboarding Command Mappers",
            content_identifier="nautobot_device_onboarding.onboarding_command_mappers",
            icon="mdi-paw",
            callback=refresh_git_command_mappers,
        ),
    )
]
