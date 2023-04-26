from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import gettext as _
# Create your views here.


def home(request):
    message = _("Hoy es 26 de noviembre.")
    # return HttpResponse(message)
    return render(request, "store/index.html",
                  {"name": "Daud Linus Namayala", "message": message}
                  )
