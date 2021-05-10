from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class News(models.Model):
    topic = models.ForeignKey('Topic', on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=300)
    html = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    link = models.URLField()
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class BrokenLink(models.Model):
    news = models.ForeignKey('News', on_delete=models.CASCADE)
    link = models.URLField()
    fixed = models.BooleanField(default=False)

    def __str__(self):
        return self.link
