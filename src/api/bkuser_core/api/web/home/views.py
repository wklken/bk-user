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

import logging

from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import CategoryOutputSLZ, DepartmentListResultCategoryOutputSLZ
from bkuser_core.api.web.utils import get_operator, is_filter_means_any
from bkuser_core.bkiam.exceptions import IAMPermissionDenied
from bkuser_core.bkiam.permissions import IAMAction, Permission
from bkuser_core.categories.models import ProfileCategory
from bkuser_core.departments.models import Department
from bkuser_core.profiles.models import Profile

logger = logging.getLogger(__name__)


class HomeTreeListApi(generics.ListCreateAPIView):
    def _get_categories(self, operator):
        # 拥有管理权限的目录
        queryset = ProfileCategory.objects.filter(enabled=True)
        if settings.ENABLE_IAM:
            fs = Permission().make_filter_of_category(operator, IAMAction.VIEW_CATEGORY)
            queryset = queryset.filter(fs)
        managed_categories = queryset.all()

        # 拉取所有目录，存在仅对某些部门拥有权限，但是并未拥有目录权限的情况
        all_categories = ProfileCategory.objects.filter(enabled=True).all()

        return managed_categories, all_categories

    # FIXME: add a cache here? move to utils.py
    def _get_category_profile_count(self, category_id):
        return Profile.objects.filter(enabled=True, category_id=category_id).count()

    def _list_department_tops(self, operator):
        """获取最顶层的组织列表[权限中心亲和]"""
        if not settings.ENABLE_IAM:
            return Department.objects.filter(level=0, enabled=True).all()

        try:
            dept_ft = Permission().make_department_filter(operator, IAMAction.MANAGE_DEPARTMENT)
            logger.debug("list_department_tops, make a filter for department: %s", dept_ft)
        except IAMPermissionDenied:
            logger.warning("user %s has no permission to search department", operator)
            return []
        else:
            # 如果是any, 表示有所有一级department的权限, 直接返回
            if is_filter_means_any(dept_ft):
                return Department.objects.filter(level=0, enabled=True).all()

            # 1. 拿到权限中心里授过权的全列表
            queryset = Department.objects.filter(enabled=True).filter(dept_ft)
            # 没有任何权限, 返回空
            if not queryset:
                return []

            # ref: https://github.com/TencentBlueKing/bk-user/issues/641#issuecomment-1248845995
            # TODO: 这两个方案都会全表扫描
            # 2. 如果父节点已经授过权，剔除子节点(这里是原先的查询, 暂时保持不变)
            descendants = Department.tree_objects.get_queryset_descendants(queryset=queryset, include_self=False)
            queryset = queryset.exclude(id__in=descendants.values_list("id", flat=True))
            # replace => TODO: 确定怎么处理比较好
            # queryset = Department.tree_objects.get_queryset_ancestors(queryset=queryset, include_self=True).filter(
            #     level=0
            # )

            # FIXME: 这里为空抛异常? 让用户申请权限? 还是什么都不做
            # if not queryset:
            #     raise IAMPermissionDenied(
            #         detail=_("您没有该操作的权限，请在权限中心申请"),
            #         extra_info=IAMPermissionExtraInfo.from_request(request).to_dict(),
            #     )

            # FIXME: 这里为什么没有限制level=0?
            return queryset.all()

    def get(self, request, *args, **kwargs):
        # serializer = DepartmentListSerializer(data=request.query_params)
        # serializer.is_valid(raise_exception=True)
        # data = serializer.validated_data

        # NOTE: 差异点, 也不支持level
        # level = data.get("level")
        # NOTE: 差异点: 不支持only_enabled
        # only_enabled = data.get("only_enabled", True)

        operator = get_operator(self.request)
        # categories
        managed_categories, all_categories = self._get_categories(operator)

        # TODO: 简化这种的序列化流程
        # 这里展示两类目录：1. 用户拥有该目录下某个组织的权限 2. 用户拥有这个目录的管理权限
        all_categories_map = {x.id: CategoryOutputSLZ(x).data for x in all_categories}

        for category_id, c in all_categories_map.items():
            c["profile_count"] = self._get_category_profile_count(category_id)
            c["departments"] = []

        # 此时拥有管理权限的目录已经被加入到了列表
        managed_categories_map = {x.id: all_categories_map[x.id] for x in managed_categories}

        # FIXME: 这里有性能问题, 当部门数量到达两万的时候
        # FIXME: 如果有所有部门的权限, 这里返回的是所有部门? 还是只返回一级部门? 一级部门很多的时候怎么处理?
        # 这里拉取所有拥有权限的、顶级的目录
        for department in self._list_department_tops(operator):
            # 如果存在当前可展示的全量 category 未包含的部门，舍弃
            dep_cate_id = department.category_id
            if dep_cate_id not in all_categories_map:
                logger.warning(
                    "department<%s>'s category<%s> could not be found",
                    department.id,
                    dep_cate_id,
                )
                continue

            # 如果存在没有管理权限的目录，但是其中的组织有权限，在这里会被加进去
            if dep_cate_id not in managed_categories_map:
                managed_categories_map[dep_cate_id] = all_categories_map[dep_cate_id]
            managed_categories_map[dep_cate_id]["departments"].append(department)

        return Response(
            data=DepartmentListResultCategoryOutputSLZ(managed_categories_map.values(), many=True).data,
            status=status.HTTP_200_OK,
        )