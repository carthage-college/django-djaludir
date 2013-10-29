from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader, Context

from djtools.utils.mail import send_mail

"""
if settings.DEBUG:
    TO_LIST = ["larry@carthage.edu",]
else:
    TO_LIST = ["someone@carthage.edu",]
BCC = settings.MANAGERS

def myview(request):
    if request.method=='POST':
        form = MyForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save()
            email = settings.DEFAULT_FROM_EMAIL
            if data.email:
                email = data.email
            subject = "[Submit] %s %s" % (data.first_name,data.last_name)
            send_mail(request,TO_LIST, subject, email,"myapp/email.html", data, BCC)
            return HttpResponseRedirect('/myapp/success/')
    else:
        form = MyForm()
    return render_to_response("myapp/form.html",
        {"form": form,}, context_instance=RequestContext(request))
"""

if settings.DEBUG:
    TO_LIST = ["mkishline@carthage.edu",]
else:
    TO_LIST = ["mkishline@carthage.edu",]

def display(request):
    return render_to_response(
        "manager/display.html",
        context_instance=RequestContext(request)
    )

def update(request):
    return render_to_response(
        "manager/update.html",
        context_instance=RequestContext(request)
    )

def search(request):
    return render_to_response(
        "manager/search.html",
        context_instance=RequestContext(request)
    )

