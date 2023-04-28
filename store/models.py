from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
# Create your models here.

# Inlines



class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discout = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = _("promotion")
        verbose_name_plural = _("promotions")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("promotion_detail", kwargs={"pk": self.pk})


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name="+")

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(_("Slug field"))
    description = models.TextField()
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(
        Promotion, verbose_name=_("promotion"), blank=True)

    class Meta:
        ordering = ["title"]
        managed = True
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def get_absolute_url(self):
        return reverse("store:product", args=[self.pk])

    def __str__(self):
        return self.title


class Customer(models.Model):
    class Membership(models.TextChoices):
        Blonze = "B", "Blonze"
        Silver = "S", "Silver"
        Gold = "G", "Gold"

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(_("Your email"), max_length=254, unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=Membership.choices, default=Membership.Blonze)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        Pending = "P", "Pending"
        Complete = "C", "Complete"
        Fail = "F", "Fail"
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PaymentStatus.choices, default=PaymentStatus.Pending)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    product = models.ForeignKey(Product,  on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Cart_detail", kwargs={"pk": self.pk})


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = _("CartItem")
        verbose_name_plural = _("CartItems")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("CartItem_detail", kwargs={"pk": self.pk})


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresss")

    def __str__(self):
        return f"{self.name} {self.city}"
