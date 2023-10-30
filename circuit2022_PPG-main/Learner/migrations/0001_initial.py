# Generated by Django 4.0.4 on 2022-08-17 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('keyword', models.TextField()),
                ('preference', models.CharField(blank=True, max_length=200)),
                ('pages', models.IntegerField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_id', models.IntegerField()),
                ('URL', models.CharField(max_length=400)),
                ('image_path', models.CharField(max_length=500)),
                ('image_code', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='keyword_URL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword_text', models.CharField(max_length=200)),
                ('individual_URL', models.CharField(max_length=400)),
                ('date_scraped', models.DateTimeField()),
                ('score', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='LinkQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword_text', models.CharField(max_length=200)),
                ('link0', models.CharField(max_length=400)),
                ('link1', models.CharField(max_length=400)),
                ('link2', models.CharField(max_length=400)),
                ('link3', models.CharField(max_length=400)),
                ('link4', models.CharField(max_length=400)),
                ('link5', models.CharField(max_length=400)),
                ('link6', models.CharField(max_length=400)),
                ('link7', models.CharField(max_length=400)),
                ('link8', models.CharField(max_length=400)),
                ('link9', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keywords', models.CharField(max_length=400)),
                ('title', models.CharField(max_length=200)),
                ('URL', models.CharField(max_length=400)),
                ('selected', models.BooleanField(default=False)),
                ('video_id', models.IntegerField(default=0)),
                ('description', models.CharField(max_length=1000)),
                ('coreqs', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='chunked',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=5000)),
                ('keywords', models.CharField(max_length=400)),
                ('page_title', models.CharField(max_length=200)),
                ('chunk_title', models.CharField(max_length=200)),
                ('URL', models.CharField(max_length=400)),
                ('coreqs', models.CharField(default='', max_length=200)),
                ('chunkID', models.IntegerField(default=0)),
                ('topic', models.CharField(max_length=200)),
                ('selected', models.BooleanField(default=False)),
                ('written', models.BooleanField(default=False)),
                ('next_chunk', models.IntegerField(default=0)),
                ('images', models.ManyToManyField(to='Learner.image')),
            ],
        ),
    ]