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

from django.conf import settings
from rest_framework import serializers

from bkuser_core.api.web.utils import get_default_category_id
from bkuser_core.api.web.viewset import StringArrayField


class LoginProfileRetrieveSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)


class LoginProfileSerializer(serializers.Serializer):
    username = serializers.SerializerMethodField(required=False)
    logo = serializers.SerializerMethodField(required=False)

    def get_username(self, obj):
        if get_default_category_id() == obj.category_id:
            return obj.username

        return f"{obj.username}@{obj.domain}"

    def get_logo(self, data):
        logo = data.logo
        if not logo:
            return settings.DEFAULT_LOGO_URL

        return logo


class ProfileSearchSerializer(serializers.Serializer):
    # NOTE: 支持了departments, 但是去掉了leaders
    category_id = serializers.IntegerField()

    departments = StringArrayField(required=False, help_text="部门id列表")
    username = serializers.CharField(required=False, help_text="用户名")
    display_name = serializers.CharField(required=False, help_text="中文名")
    email = serializers.CharField(required=False, help_text="邮箱")
    telephone = serializers.CharField(required=False, help_text="电话")
    status = serializers.CharField(required=False, help_text="账户状态")
    staff_status = serializers.CharField(required=False, help_text="在职状态")

    # NOTE: 暂时不支持这四个字段
    # leaders
    # position
    # wx_userid
    # qq


class ProfileSearchResultLeaderSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, read_only=True)
    username = serializers.CharField()
    display_name = serializers.CharField(read_only=True)


class ProfileSearchResultDepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    category_id = serializers.IntegerField(required=False)


class ProfileSearchResultSerializer(serializers.Serializer):
    # FIXME: 不需要返回所有字段吧
    id = serializers.CharField(required=False, help_text="用户ID")
    username = serializers.CharField(required=False, help_text="用户名")
    qq = serializers.CharField(required=False, help_text="QQ")
    email = serializers.CharField(required=False, help_text="邮箱")
    telephone = serializers.CharField(required=False, help_text="电话")
    wx_userid = serializers.CharField(required=False, help_text="微信用户id")
    domain = serializers.CharField(required=False, help_text="域")
    display_name = serializers.CharField(required=False, help_text="中文名")
    status = serializers.CharField(required=False, help_text="账户状态")
    staff_status = serializers.CharField(required=False, help_text="在职状态")
    position = serializers.CharField(required=False, help_text="职位")
    enabled = serializers.BooleanField(required=False, help_text="是否启用", default=True)
    extras = serializers.JSONField(required=False, help_text="扩展字段")
    password_valid_days = serializers.IntegerField(required=False, help_text="密码有效期")
    country_code = serializers.CharField(required=False, help_text="国家码")
    iso_code = serializers.CharField(required=False, help_text="国家码")
    time_zone = serializers.CharField(required=False, help_text="时区")

    last_login_time = serializers.DateTimeField(required=False, help_text="最后登录时间")

    create_time = serializers.DateTimeField(required=False, help_text="创建时间")
    update_time = serializers.DateTimeField(required=False, help_text="更新时间")
    departments = ProfileSearchResultDepartmentSerializer(many=True, required=False, help_text="部门列表")
    leaders = ProfileSearchResultLeaderSerializer(many=True, required=False, help_text="上级列表", source="leader")
