import json
import random
import string

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Users, Group, Charge, OweTable


@csrf_exempt
def register(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        phone_num = body.get('phone_num', '')
        obj, created = Users.objects.get_or_create(phone_num=phone_num)
        if not created:
            return HttpResponse('Already a user')
        return HttpResponse('Successfully Registered')
    else:
        return HttpResponse(json.dumps({}), content_type="application/json", status=405)


@csrf_exempt
def create_group(request, group_id):
    if request.method == 'POST':
        body = json.loads(request.body)
        user_phone_num = body.get('user_phone_num', '')
        self_phone_num = body.get('self_phone_num', '')
        try:
            group_record = Group.objects.get(group_id=group_id, user_phone_num=self_phone_num)
            Group.objects.create(group_id=group_id, user_phone_num=user_phone_num)
            return HttpResponse(
                'Successfully added user {} to the group {}'.format(user_phone_num, group_record.group_id))
        except ObjectDoesNotExist:
            group = Group.objects.filter(group_id=group_id)
            if not group:
                Group.objects.create(group_id=group_id, user_phone_num=self_phone_num)
                Group.objects.create(group_id=group_id, user_phone_num=user_phone_num)
                return HttpResponse('Successfully created group {} with {}'.format(group_id, user_phone_num))
            else:
                return HttpResponse('Group ID already used')
    else:
        return HttpResponse(json.dumps({}), content_type="application/json", status=405)

@csrf_exempt
def post_charge(request, group_id):
    if request.method == 'POST':
        body = json.loads(request.body)
        bill_amount = body.get('bill_amount', '')
        charge_id = body.get('charge_id', '')
        payer_phone_num = body.get('payer_phone_num', '')
        members = Group.objects.filter(group_id=group_id)
        try:
            obj = Charge.objects.get(charge_id=charge_id)
            return HttpResponse('Charge ID already used')
        except ObjectDoesNotExist:
            obj = Charge.objects.create(charge_id=charge_id, grp_id=group_id, bill_amount=bill_amount,
                                        payer_phone_num=payer_phone_num)
            members = Group.objects.filter(group_id=group_id)
            members_num = members.count()
            individual_bill = bill_amount / members_num
            for member in members:
                if member.user_phone_num != payer_phone_num:
                    try:
                        obj = OweTable.objects.get(payer_phone_num=payer_phone_num, lender_phone_num=member.user_phone_num)
                        obj.amount = obj.amount + individual_bill
                        obj.save()
                    except ObjectDoesNotExist:
                        OweTable.objects.create(payer_phone_num=payer_phone_num, lender_phone_num=member.user_phone_num,
                                                      amount=individual_bill)
            return HttpResponse('Successfully added charge to group id {}'.format(group_id))
    else:
        return HttpResponse(json.dumps({}), content_type="application/json", status=405)

def show_charges(request, user_phone_num):
    if request.method == 'GET':
        charges = {}
        response = []
        records = OweTable.objects.filter(payer_phone_num=user_phone_num)
        for record in records:
            charges[record.lender_phone_num] = record.amount
            # charges.append("Person {} owes Rs {} to you".format(record.lender_phone_num, record.amount))
        records = OweTable.objects.filter(lender_phone_num=user_phone_num)
        for record in records:
            charges[record.payer_phone_num] = charges.get(record.payer_phone_num, 0) - record.amount
            # charges.append("You owe Rs {} to Person {}".format(record.amount, record.payer_phone_num))
        for user, amount in charges.items():
            if amount > 0:
                response.append("Person {} owes Rs {} to you".format(user, amount))
            elif amount < 0:
                response.append("You owe Rs {} to Person {}".format(-1*amount, user))
        print(charges)
        return HttpResponse(json.dumps(response), content_type="application/json", status=200)
    else:
        return HttpResponse(json.dumps({}), content_type="application/json", status=405)



def _get_random_id():
    return "".join(random.sample(string.letters, 5))
