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

from . import views
from bkuser_core.apis.v2.constants import LOOKUP_FIELD_NAME

PVAR_PROFILE_ID = r"(?P<%s>[a-z0-9-_]+)" % LOOKUP_FIELD_NAME


urlpatterns = [
    url(
        r"^api/v2/settings/$",
        views.SettingViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="settings",
    ),
    url(
        r"^api/v2/settings/%s/$" % PVAR_PROFILE_ID,
        views.SettingViewSet.as_view(
            {
                "get": "retrieve",
                "delete": "destroy",
            }
        ),
        name="settings.action",
    ),
]
