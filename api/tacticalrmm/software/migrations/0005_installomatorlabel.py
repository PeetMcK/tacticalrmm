# Generated manually for Installomator integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("software", "0004_alter_installedsoftware_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="InstallomatorLabel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("labels", models.JSONField(default=list)),
                ("version", models.CharField(max_length=20)),
                ("added", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-added"],
            },
        ),
    ]
