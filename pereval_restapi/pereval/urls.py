from django.urls import path
from pereval.views import SubmitDataView

urlpatterns = [
    path('submitData/', SubmitDataView.as_view(), name='submit_data'),
]