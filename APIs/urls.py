from django.urls import path
from . import views

urlpatterns = [
    path('savedata/', views.SaveData, name='savedata'),
    path('result/', views.Calculating_Y, name='calculating_Y'),
    path('det-values/', views.FetchDetails, name='detailvalues'),
    path('calculate_Y_single/', views.Calculating_Y_Single, name='calculating_Y'),
    path('delete-master-data/', views.DeleteMasterData, name="delete-master-data")

]
