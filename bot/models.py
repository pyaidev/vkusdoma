from django.db import models

# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class BotAdmin(BaseModel):
    title = models.CharField(max_length=255)
    user_id = models.IntegerField(unique=True)
    status = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title + ' ' + str(self.user_id)

class Category(BaseModel):
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title
    
class Product(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    
    def __str__(self):
        return self.title
    
class Cart(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    quantity = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.product.title + ' ' + str(self.user_id)
    
class Order(BaseModel):
    carts = models.ManyToManyField(Cart)
    user_id = models.IntegerField()
    total_price = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    is_finished  = models.BooleanField(default=False)
    name = models.CharField(max_length=255,null=True,blank=True)
    adress = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return self.name + ' ' + str(self.user_id) + ' ' + str(self.total_price)
    
class Question(BaseModel):
    user_id = models.IntegerField()
    question = models.TextField()
    message_id = models.IntegerField()
    answer = models.TextField(null=True,blank=True)
    is_answered = models.BooleanField(default=False)
    

    def __str__(self):
        return self.question