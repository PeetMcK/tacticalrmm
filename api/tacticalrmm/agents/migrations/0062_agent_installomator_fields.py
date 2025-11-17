# Generated manually for Installomator integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agents", "0061_alter_agent_time_zone"),
    ]

    operations = [
        migrations.AddField(
            model_name="agent",
            name="installomator_installed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="agent",
            name="installomator_version",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
