# Copyright 2016 the Queen's University Biological Station

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.conf.urls import url
from herbarium_data import views


API_TITLE = 'QUBS Herbarium Data API'
API_DESCRIPTION = 'A web API for accessing herbarium data from the Queen\'s University Biological Station\'s Fowler ' \
                  'Herbarium.'


urlpatterns = [
    url(r'^$', views.herbarium_api_root, name='herbarium-api-root'),

    url(r'^specimens/$', views.SpecimenList.as_view(), name='specimen-list'),
    url(r'^specimens/(?P<pk>[0-9]+)/$', views.SpecimenDetail.as_view(), name='specimen-detail'),
]
