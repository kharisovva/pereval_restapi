from django.urls import path

from pereval.views import SubmitDataView

urlpatterns = [
    path("submitData/", SubmitDataView.as_view(), name="submit_data"),
    path("submitData/<int:id>/", SubmitDataView.as_view(), name="submit_data_detail"),
]
