from django.shortcuts import render,redirect
from ecommerceApp.models import Contact, Products,Orders,OrderUpdate
from django.contrib import messages
from math import ceil
from ecommerceApp import keys
from django.conf import settings
MERCHANT_KEY=keys.MK    #Important Need to add this or the checkout page wont work 
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum    #pip install pycryptodome

# Create your views here.

def index(request):
    allProds = []
    catProds = Products.objects.values('category','id')  # To display based on category wise
    print(catProds)
    cats = {item['category'] for item in catProds}
    for cat in cats:
        prod = Products.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))         #Using this logic I can get 3 products in one row every row 
        allProds.append([prod,range(1,nSlides),nSlides])

    params = {'allProds':allProds}
    
    return render(request,"index.html", params)

def contact(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        desc=request.POST.get('message')
        number=request.POST.get('pnumber')
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=number)
        myquery.save()
        messages.info(request,"Your message has been sent. Thank you!")
        return render(request,"contact.html")

        
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        Order = Orders(items_json=items_json,name=name,amount=amount,
                       email=email,address1=address1,address2=address2,city=city,
                       state=state,zip_code=zip_code,phone=phone)
        print(amount)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        thank = True

    # Payment Integration ----> All the below code provided by Paytm

        id = Order.order_id       
        oid = str(id) + "Empower"
        param_dict = {

            'MID':keys.MID,         # Merchiant ID and Merchant Key from the PAYTM-DASHBOARD
            'ORDER_ID':oid,         ## All the payment pages expect only Order ID and the Who is the Owner of the Project
            'TXN_AMOUNT':str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE' : 'WEBSTAGING',
            'CHANNEL_ID' : 'WEB',
            'CALLBACK_URL' : 'http://127.0.0.1:8000/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict,MERCHANT_KEY)   
        return render(request,'paytm.html',{'param_dict':param_dict})

 
    return render(request,"checkout.html")


@csrf_exempt
def handlerequest(request):
    # paytm will send us post request here 
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY,checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            a = response_dict['ORDERID']
            b = response_dict['TXNAMOUNT']
            rid = a.replace("Empower","")

            print(rid)
            filter2 = Orders.objects.filter(order_id=rid)
            print(filter2)
            print(a,b)
            for post1 in filter2:
                post1.oid = a
                post1.amount = b
                post1.paymentstatus = "PAID"
                post1.save()
            print("run agevala function")
        else:
            # Add the stuff from the above if block if you want to display the payment rejection/failure
            #status in your database table --> post1.paymentstatus = "UNPAID"
            print("order was not successful because" + response_dict['RESPMSG'])
    return render(request,'paymentstatus.html',{'response_dict':response_dict})      # this When the order is successfull


def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    currentuser = request.user.username    
    items = Orders.objects.filter(email=currentuser)
    rid=""
    for i in items:
        # print(i.oid)
        myid = i.oid
        rid = myid.replace("Empower","")
        # print(rid)
    status = OrderUpdate.objects.filter(order_id=int(rid))
    for j in status:
        print(j.update_desc)
    print(status)
    context = {"items":items, "status":status}
    # print(currentuser)
    return render(request,'profile.html',context)


