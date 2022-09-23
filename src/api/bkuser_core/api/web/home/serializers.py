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

from rest_framework import serializers

from bkuser_core.api.web.department.serializers import DepartmentSerializer
from bkuser_core.categories.models import ProfileCategory


class CategoryOutputSLZ(serializers.ModelSerializer):
    class Meta:
        model = ProfileCategory
        fields = "__all__"


class DepartmentListResultCategoryOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField()
    display_name = serializers.CharField()
    order = serializers.IntegerField
    default = serializers.BooleanField()

    type = serializers.CharField()

    profile_count = serializers.IntegerField()
    departments = DepartmentSerializer(many=True)
