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
from .proxy import BkUserApiProxy


class SyncTaskViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/sync_tasks/")


class SyncTaskLogViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        # FIXME: use a func to do re-map
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/sync_task/4a3cbc71-8141-4f1a-b306-f723d0224d44/logs
        # out: /api/v1/web/sync_tasks/4a3cbc71-8141-4f1a-b306-f723d0224d44/progresses/
        api_path = api_path.replace("/api/v2/sync_task/", "/api/v1/web/sync_tasks/")
        api_path = api_path.replace("/logs", "/progresses/")
        return self.do_proxy(request, rewrite_path=api_path)


class GeneralLogViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/audits/logs/types/general/")


class LoginLogViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/audits/logs/types/login/")


class FieldsManageableViewSet(BkUserApiProxy):
    def get(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/fields/manageable/")


class FieldsVisibleViewSet(BkUserApiProxy):
    def patch(self, request, *args, **kwargs):
        return self.do_proxy(request, rewrite_path="/api/v1/web/fields/visible/")


class FieldsOrderViewSet(BkUserApiProxy):
    def patch(self, request, *args, **kwargs):
        # FIXME: use a func to do re-map
        api_path = BkUserApiProxy.get_api_path(request)
        # in: /api/v2/fields/13/order/5/
        # out: /api/v1/web/fields/13/order/5/
        api_path = api_path.replace("/api/v2/fields/", "/api/v1/web/fields/")
        return self.do_proxy(request, rewrite_path=api_path)


class FieldsViewSet(BkUserApiProxy):
    def list(self, request, *args, **kwargs):
        """获取所有用户字段"""
        return self.do_proxy(request, rewrite_path="/api/v1/web/fields/")

    def create(self, request, *args, **kwargs):
        """创建用户字段"""
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/fields/", "/api/v1/web/fields/")
        return self.do_proxy(request, rewrite_path=api_path)

    def update(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/fields/", "/api/v1/web/fields/")
        return self.do_proxy(request, rewrite_path=api_path)

    def delete(self, request, *args, **kwargs):
        api_path = BkUserApiProxy.get_api_path(request)
        api_path = api_path.replace("/api/v2/fields/", "/api/v1/web/fields/")
        return self.do_proxy(request, rewrite_path=api_path)