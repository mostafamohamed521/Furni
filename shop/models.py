from django.db import models

class shop(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='shop/')
    price = models.IntegerField(default=0)

     
    def __str__(self):
        return self.name

class statue(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


class addcart(models.Model):
    