# #
# # Copyright (C) 2023, Inria
# # GRAPHDECO research group, https://team.inria.fr/graphdeco
# # All rights reserved.
# #
# # This software is free for non-commercial, research and evaluation use
# # under the terms of the LICENSE.md file.
# #
# # For inquiries contact  george.drettakis@inria.fr
# #
#
# import torch
# from torch import nn
# import numpy as np
# from utils.graphics_utils import getWorld2View2, getProjectionMatrix
#
#
# class Camera(nn.Module):
#     def __init__(self, colmap_id, R, T, FoVx, FoVy, image, gt_alpha_mask,
#                  image_name, uid, trans=np.array([0.0, 0.0, 0.0]),
#                  resolutions=(2, 4), scale=1.0, data_device="cuda"):
#         super(Camera, self).__init__()
#
#         self.uid = uid
#         self.colmap_id = colmap_id
#         self.R = R
#         self.T =  T
#         self.FoVx = FoVx
#         self.FoVy = FoVy
#         self.image_name = image_name
#         self.scale = scale
#         self.trans = trans
#         self.znear = 0.01
#         self.zfar = 100.0
#
#         self.data_device = self._initialize_device(data_device)
#
#         # //////////////// resolution ////////////////
#         original_image = image.clamp(0.0, 1.0).to(self.data_device)
#         self.original_images = [original_image]
#         self.image_widths = [original_image.shape[2]]
#         self.image_heights = [original_image.shape[1]]
#         for resolution in resolutions:
#             image = nn.functional.interpolate(original_image[None], scale_factor=(1.0 / resolution, 1.0 / resolution))[
#                 0]
#             self.original_images.append(image)
#             self.image_widths.append(image.shape[2])
#             self.image_heights.append(image.shape[1])
#
#
#         self.original_image = self.original_images[0]
#         self.image_width = self.image_widths[0]
#         self.image_height = self.image_heights[0]
#         self.gt_alpha_masks = [None] * len(resolutions)
#
#         # MASK
#         if gt_alpha_mask is not None:
#             gt_alpha_mask = gt_alpha_mask.to(self.data_device)
#             self.gt_alpha_masks = [gt_alpha_mask]
#             for resolution in resolutions:
#                 gt_alpha_mask = \
#                     nn.functional.interpolate(gt_alpha_mask[None], scale_factor=(1.0 / resolution, 1.0 / resolution))[0]
#                 self.gt_alpha_masks.append(gt_alpha_mask)
#         self.gt_alpha_mask = self.gt_alpha_masks[0]
#         # //////////////// resolution ////////////////
#
#         self.world_view_transform = self._calculate_world_view_transform()
#         self.projection_matrix = self._calculate_projection_matrix()
#         self.full_proj_transform = (self.world_view_transform.unsqueeze(0).bmm(self.projection_matrix.unsqueeze(0)).squeeze(0))
#         self.camera_center = self.world_view_transform.inverse()[3, :3]
#
#     def _initialize_device(self, data_device):
#         try:
#             return torch.device(data_device)
#         except Exception as e:
#             print(e)
#             print(f"[Warning] Custom device {data_device} failed, fallback to default cuda device")
#             return torch.device("cuda")
#
#     def _calculate_world_view_transform(self):
#
#         return torch.tensor(getWorld2View2(self.R, self.T, self.trans, self.scale)
#                             ).transpose(0, 1).to(self.data_device)
#
#     def _calculate_projection_matrix(self):
#         return getProjectionMatrix(
#             znear=self.znear, zfar=self.zfar, fovX=self.FoVx, fovY=self.FoVy
#         ).transpose(0, 1).to(self.data_device)
#
#     def change_resolution(self, idx):
#         self.original_image = self.original_images[idx]
#         self.image_width = self.image_widths[idx]
#         self.image_height = self.image_heights[idx]
#         self.gt_alpha_mask = self.gt_alpha_masks[idx]
#
#
# class MiniCam:
#     def __init__(self, width, height, fovy, fovx, znear, zfar, world_view_transform, full_proj_transform):
#         self.image_width = width
#         self.image_height = height
#         self.FoVy = fovy
#         self.FoVx = fovx
#         self.znear = znear
#         self.zfar = zfar
#         self.world_view_transform = world_view_transform
#         self.full_proj_transform = full_proj_transform
#         view_inv = torch.inverse(self.world_view_transform)
#         self.camera_center = view_inv[3][:3]

#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

import torch
from torch import nn
import numpy as np
from utils.graphics_utils import getWorld2View2, getProjectionMatrix


class Camera(nn.Module):
    def __init__(self, colmap_id, R, T, FoVx, FoVy, image, gt_alpha_mask,
                 image_name, uid,
                 trans=np.array([0.0, 0.0, 0.0]), resolutions=(2, 4), scale=1.0, data_device="cuda"
                 ):
        super(Camera, self).__init__()

        self.uid = uid
        self.colmap_id = colmap_id
        self.R = R
        self.T = T
        self.FoVx = FoVx
        self.FoVy = FoVy
        self.image_name = image_name
        self.num_resolutions = len(resolutions) + 1
        try:
            self.data_device = torch.device(data_device)
        except Exception as e:
            print(e)
            print(f"[Warning] Custom device {data_device} failed, fallback to default cuda device")
            self.data_device = torch.device("cuda")

        original_image = image.clamp(0.0, 1.0).to(self.data_device)
        self.original_images = [original_image]

        self.image_widths = [original_image.shape[2]]
        self.image_heights = [original_image.shape[1]]
        for resolution in resolutions:
            image = nn.functional.interpolate(original_image[None], scale_factor=(1.0 / resolution, 1.0 / resolution))[
                0]
            self.original_images.append(image)
            self.image_widths.append(image.shape[2])
            self.image_heights.append(image.shape[1])

        self.original_image = self.original_images[0]
        self.image_width = self.image_widths[0]
        self.image_height = self.image_heights[0]
        self.gt_alpha_masks = [None] * len(resolutions)

        if gt_alpha_mask is not None:
            gt_alpha_mask = gt_alpha_mask.to(self.data_device)
            self.gt_alpha_masks = [gt_alpha_mask]
            for resolution in resolutions:
                gt_alpha_mask = \
                nn.functional.interpolate(gt_alpha_mask[None], scale_factor=(1.0 / resolution, 1.0 / resolution))[0]
                self.gt_alpha_masks.append(gt_alpha_mask)
        self.gt_alpha_mask = self.gt_alpha_masks[0]

        self.zfar = 100.0
        self.znear = 0.01

        self.trans = trans
        self.scale = scale

        self.world_view_transform = torch.tensor(getWorld2View2(R, T, trans, scale)).transpose(0, 1).cuda()
        self.projection_matrix = getProjectionMatrix(znear=self.znear, zfar=self.zfar, fovX=self.FoVx,
                                                     fovY=self.FoVy).transpose(0, 1).cuda()
        self.full_proj_transform = (
            self.world_view_transform.unsqueeze(0).bmm(self.projection_matrix.unsqueeze(0))).squeeze(0)
        self.camera_center = self.world_view_transform.inverse()[3, :3]

    def change_resolution(self, idx):
        self.original_image = self.original_images[idx]
        self.image_width = self.image_widths[idx]
        self.image_height = self.image_heights[idx]
        self.gt_alpha_mask = self.gt_alpha_masks[idx]


class MiniCam:
    def __init__(self, width, height, fovy, fovx, znear, zfar, world_view_transform, full_proj_transform):
        self.image_width = width
        self.image_height = height
        self.FoVy = fovy
        self.FoVx = fovx
        self.znear = znear
        self.zfar = zfar
        self.world_view_transform = world_view_transform
        self.full_proj_transform = full_proj_transform
        view_inv = torch.inverse(self.world_view_transform)
        self.camera_center = view_inv[3][:3]
