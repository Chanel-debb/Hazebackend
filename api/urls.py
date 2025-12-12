from django.urls import path
from .views import (
    get_all_vistors, 
    add_visitor, 
    get_visitor, 
    delete_visitor, 
    update_visitor_signout,
    AnnouncementView, 
    AnnouncementRetrieveUpdateDeletView,
    AccessCodeListcreate,
    AccessCodeRetrieveUpdateDelete,
    make_payment,
    transaction,
    payment,
    create_payment,
    verify_access_code,
    get_security_stats
)


urlpatterns = [
    # Visitor urls
    path('visitors', get_all_vistors, name="All visitors"),
    path('visitors/add', add_visitor, name="Create"),
    path('visitors/<int:id>', get_visitor, name="Get visitor"),
    path('visitors/delete/<int:id>', delete_visitor, name="Delete Visitor"),
    path('visitors/update/<int:id>', update_visitor_signout, name="Update Visitor"),
    # Annoucement urls
    path("announcements", AnnouncementView.as_view(), name="Create Get all Announcements"),
    path("announcements/<int:id>", AnnouncementRetrieveUpdateDeletView.as_view(), name="Create Get ID Delete and Update Announcements"),
    # Access Code urls
    path('access-codes', AccessCodeListcreate.as_view(), name='access-codes'),
    path("access-code/<int:id>", AccessCodeRetrieveUpdateDelete.as_view(), name="Create Get ID Delete and Update AccessCode"),

    # Payment url
    path('make-payment', make_payment, name="Make Payment"),
    path('transactions', transaction, name="Payment Transactions"),
    path('estate-payments', payment, name="Estate Payments"),
    path('create-estate-payment', create_payment, name="Create Estate Payment"),
    path('verify-access-code', verify_access_code, name="Verify Access Code"),
    path('security-stats', get_security_stats, name='security-stats'),
]

# {
#     "fullname": "Joyce Offorey",   
#     "phone_number": "092867632763",
#     "decsription": "Demo guest",
#     "signed_in": "2025-10-29T16:30:45+01:00"
# }