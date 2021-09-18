from django.db import models

class User(models.Model):
    name = models.CharField(primary_key=True, max_length=200)
    xml = models.TextField()
    processing_task = models.UUIDField(null=True)
    root_node = models.ForeignKey('TreeNode', null=True, on_delete=models.CASCADE)

class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    xml = models.TextField()
    name = models.CharField(max_length=200, blank=False)

class TreeNode(models.Model):
    name = models.CharField(primary_key=True, max_length=200)
    description = models.CharField(max_length=200)
    game_node = models.BooleanField(null=False)
    games = models.ManyToManyField(Game)
    questions = models.ManyToManyField('TreeNode', through='QuestionLink')

class QuestionLink(models.Model):
    from_node = models.ForeignKey(TreeNode, on_delete=models.CASCADE, related_name='+')
    to_node = models.ForeignKey(TreeNode, on_delete=models.CASCADE, related_name='+')
    label = models.CharField(max_length=200, null=False)