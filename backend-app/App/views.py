from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from App.db_connection import DB


# Initialize Database Server Connection
con = DB("localhost", 27017, "HLJ")


# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello and welcome to my first <u>Django App</u> project!</h1>")


def figure(request):
    if request.method == "POST":
        return HttpResponseBadRequest("Only GET request allowed.")

    jan_code = request.GET.get("jan", None)
    page_num = request.GET.get("page", None)
    if page_num is None:
        page_num = 1

    df = con.get_figurine(jan_code=int(jan_code) if jan_code is not None else None, page_num=page_num)
    return JsonResponse({"results": df.to_dict("records")})

