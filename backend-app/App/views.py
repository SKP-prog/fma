from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, QueryDict
from App.db_connection import DB


# Initialize Database Server Connection
con = DB("localhost", 27017, "HLJ")


# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello and welcome to my first <u>Django App</u> project!</h1>")


def figure(request):
    """
    Extract figure listing from HLJ
    """
    if request.method != "GET":
        return HttpResponseBadRequest("Only GET request allowed.")

    jan_code = request.GET.get("jan", None)
    page_num = request.GET.get("page", None)
    if page_num is None:
        page_num = 1

    df, meta = con.get_figurine(page_num=int(page_num))
    return JsonResponse({"results": df.to_dict("records"), "metadata": meta})


def favs(request):
    """
    add/view/update Favourites
    """
    con.set_table("Favourite")

    if request.method == "POST":
        jan_code = request.POST.get('jan', None)
        is_delete = request.POST.get("is_delete", False)

        if not is_delete:
            con.add_row({"JAN_code": int(jan_code)})
            return JsonResponse({"results": f"Added {jan_code} to Favourites Table."})
        else:
            con.del_row({"JAN_code": int(jan_code)})
            return JsonResponse({"results": f"Removed {jan_code} from Favourites Table."})

    else:
        return HttpResponseBadRequest("Only POST Request Allowed.")
