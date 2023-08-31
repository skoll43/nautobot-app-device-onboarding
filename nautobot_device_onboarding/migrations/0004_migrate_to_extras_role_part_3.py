from django.db import migrations, models


import nautobot.extras.models 


class Migration(migrations.Migration):

    dependencies = [
        ("nautobot_device_onboarding", "0004_migrate_to_extras_role_part_2"),
    ]


    operations = [
        migrations.RemoveField(
            model_name="onboardingtask",
            name="role",
        ),
        migrations.RenameField(
            model_name="onboardingtask",
            old_name="new_role",
            new_name="role",
        ),
    ]

