from django.urls import path
from .views import get_all_vistors, add_visitor, get_visitor, delete_visitor, update_visitor_signout


urlpatterns = [
    path('visitors', get_all_vistors, name="All visitors"),
    path('visitors/add', add_visitor, name="Create"),
    path('visitors/<int:id>', get_visitor, name="Get visitor"),
    path('visitors/delete/<int:id>', delete_visitor, name="Delete Visitor"),
    path('visitors/update/<int:id>', update_visitor_signout, name="Update Visitor")
]

# {
#     "fullname": "Joyce Offorey",   
#     "phone_number": "092867632763",
#     "decsription": "Demo guest",
#     "signed_in": "2025-10-29T16:30:45+01:00"
# }