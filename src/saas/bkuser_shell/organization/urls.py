# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.conf.urls import url

from .views.departments import DepartmentViewSet
from .views.misc import SearchViewSet
from .views.profiles import ProfilesViewSet

# 1.
# DELETE /api/v2/batch/profiles/ [{"id":"1026"}]
# PATCH /api/v2/batch/profiles/  [{"id":1027,"departments":[1,20207]}]

# 2.
# GET /api/v2/departments/?only_enabled=false/true

# 3.
# GET /api/v2/search/detail/?keyword=xxxx&max_items=40&only_enabled=true

urlpatterns = [
    ###################
    # Profile related #
    ###################
    url(
        r"^api/v2/batch/profiles/$",
        ProfilesViewSet.as_view({"patch": "multiple_update", "delete": "multiple_delete"}),
        name="profiles.batch.actions",
    ),
    ##########
    # search #
    ##########
    url(
        r"^api/v2/search/detail/$",
        SearchViewSet.as_view({"get": "search"}),
        name="profiles.login_info",
    ),
    ######################
    # Department related #
    ######################
    url(r"^api/v2/departments/$", DepartmentViewSet.as_view({"get": "list", "post": "create"}), name="departments"),
]
