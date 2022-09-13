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

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import (
    DepartmentCreatedReturnSerializer,
    DepartmentCreateSerializer,
    DepartmentProfileListSerializer,
    DepartmentProfileSerializer,
    DepartmentSearchResultSerializer,
    DepartmentSearchSerializer,
    DepartmentsWithChildrenAndAncestorsSerializer,
)
from bkuser_core.api.web.utils import get_category, get_default_category_id, get_department, get_username
from bkuser_core.api.web.viewset import CustomPagination
from bkuser_core.bkiam.permissions import IAMAction, ManageDepartmentPermission, Permission, ViewDepartmentPermission
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.common.error_codes import error_codes
from bkuser_core.departments.models import Department, DepartmentThroughModel
from bkuser_core.departments.signals import post_department_create
from bkuser_core.profiles.constants import ProfileStatus
from bkuser_core.profiles.models import Profile


class DepartmentListCreateApi(generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = DepartmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # FIXME: category_id is required, can remove this check?
        category_id = data.get("category_id")
        if not category_id:
            category_id = get_default_category_id()
        else:
            if not ProfileCategory.objects.check_writable(category_id):
                raise error_codes.CANNOT_MANUAL_WRITE_INTO

        # category = ProfileCategory.objects.get(id=category_id)
        username = get_username(request)
        category = get_category(category_id)

        dept = {
            "name": data["name"],
            "category_id": category_id,
        }

        parent_id = data.get("parent")
        if parent_id:
            department = get_department(parent_id)
            Permission().allow_category_action(username, IAMAction.MANAGE_DEPARTMENT, department)

            dept.update({"parent": department, "order": department.get_max_order_in_children() + 1})
        else:
            Permission().allow_category_action(username, IAMAction.MANAGE_CATEGORY, category)
            # 不传 parent 默认为根部门
            data["level"] = 0
            max_order = list(
                Department.objects.filter(enabled=True, category_id=category_id, level=0).values_list(
                    "order", flat=True
                )
            )
            max_order = max(max_order or [0])
            dept.update({"level": 0, "order": max_order + 1})

        # 同一个组织下，不能有同名子部门
        try:
            instance = Department.objects.get(
                parent_id=parent_id,
                name=data["name"],
                category_id=category_id,
            )
            # 若是已删除的，将直接启用，未删除的抛出重复错误
            if not instance.enabled:
                instance.enable()
            else:
                raise error_codes.DEPARTMENT_NAME_CONFLICT
        except Department.DoesNotExist:
            instance = Department.objects.create(**dept)

        post_department_create.send(
            sender=self, instance=instance, operator=username, extra_values={"request": request}
        )
        return Response(DepartmentCreatedReturnSerializer(instance).data, status=status.HTTP_201_CREATED)


class DepartmentRetrieveUpdateDeleteApi(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = "id"
    queryset = Department.objects.all()

    serializer_class = DepartmentsWithChildrenAndAncestorsSerializer

    permission_classes = [ManageDepartmentPermission]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # 当组织存在下级时无法删除
        if instance.children.filter(enabled=True).exists():
            # children.filter(enabled=True)
            raise error_codes.CANNOT_DELETE_DEPARTMENT.f(_("当前部门存在下级组织无法删除"))

        if instance.get_profiles().exists():
            raise error_codes.CANNOT_DELETE_DEPARTMENT.f(_("当前部门下存在用户无法删除"))

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DepartmentSearchApi(generics.ListAPIView):

    serializer_class = DepartmentSearchResultSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        serializer = DepartmentSearchSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        category_id = data.get("category_id")

        username = get_username(self.request)
        category = get_category(category_id)
        Permission().allow_category_action(username, IAMAction.VIEW_CATEGORY, category)

        # NOTE: 这里相对原来/api/v3/departments/?category_id 的差异是 enabled=True
        return Department.objects.filter(category_id=category_id, enabled=True)


class DepartmentOperationSwitchOrderApi(generics.UpdateAPIView):
    permission_classes = [ManageDepartmentPermission]
    queryset = Department.objects.filter(enabled=True)
    lookup_url_kwarg = "id"

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()

        another_department = Department.objects.get(id=kwargs["another_id"])

        # switch
        instance.order, another_department.order = another_department.order, instance.order
        instance.save(update_fields=["order"])
        another_department.save(update_fields=["order"])

        return Response()


class DepartmentProfileListApi(generics.ListAPIView):
    permission_classes = [ViewDepartmentPermission]
    pagination_class = CustomPagination
    serializer_class = DepartmentProfileSerializer

    def get_recursive_queryset(self, department):
        # 使用 DB 做 distinct 非常慢，所以先用 id 去重 TODO: 为什么差别这么大，有时间慢慢研究
        department_ids = department.get_descendants(include_self=True).values_list("id", flat=True)
        ids = DepartmentThroughModel.objects.filter(department_id__in=department_ids).values_list(
            "profile_id", flat=True
        )

        # 当后端 DB 不支持 microseconds 时 create_time 会无法准确排序
        return Profile.objects.filter(id__in=ids).exclude(enabled=False).order_by("-id")

    def get_no_recursive_queryset(self, department):
        return department.profiles.exclude(status=ProfileStatus.DELETED.value)

    # def get_queryset(self):
    def list(self, request, *args, **kwargs):
        slz = DepartmentProfileListSerializer(data=self.request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        department_id = self.kwargs["id"]
        department = get_department(department_id)

        # 原来的代码: 递归current_count, 不递归查total_count(I don't know why)
        # https://github.com/TencentBlueking/bk-user/blob/99178a35b96511c0cd4dc7c1944bc80ce2d082dd/src/saas/bkuser_shell/organization/views/departments.py#L84-L88
        # FIXME: 跟前端确认逻辑, 抹掉差异和自定义 => total_count/current_count有没有用, 没用去掉
        current_count = total_count = 0

        # NOTE: duplicated with departments.models.Department.get_profiles
        recursive = data.get("recursive")
        if not recursive:
            queryset = self.get_no_recursive_queryset(department)
            total_count = self.get_recursive_queryset(department).count()
        else:
            queryset = self.get_recursive_queryset(department)
            current_count = self.get_no_recursive_queryset(department).count()

        # filter by keyword
        keyword = data.get("keyword")
        if keyword:
            queryset = queryset.filter(Q(username__icontains=keyword) | Q(display_name__icontains=keyword))

        queryset = queryset.prefetch_related("departments", "leader")

        # build response
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            count = self.paginator.page.paginator.count
            return Response(
                {
                    "count": count,
                    "data": serializer.data,
                    "current_count": current_count,
                    "total_count": total_count,
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
