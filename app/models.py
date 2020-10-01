from django.db import models

class Users(models.Model):
    phone_num = models.IntegerField()

class Group(models.Model):
    group_id = models.TextField()
    user_phone_num = models.IntegerField()

class Charge(models.Model):
    charge_id = models.TextField()
    grp_id = models.TextField()
    bill_amount = models.IntegerField()
    payer_phone_num=models.IntegerField()

class OweTable(models.Model):
    payer_phone_num = models.IntegerField()
    lender_phone_num = models.IntegerField()
    amount = models.IntegerField()



