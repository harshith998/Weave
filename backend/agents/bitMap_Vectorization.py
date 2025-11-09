# clip_consistency.py
"""
Comprehensive scaffold for mapping consistency from clip-to-clip using
vector bitmaps (optical flow / motion vector maps) as conditioning.

Core ideas:
 - compute optical flow from last frames -> produce 2/3 channel bitmap
 - encode vector-bitmap -> conditioning embedding
 - inject embedding into video generator via cross-attention / FiLM
 - temporal consistency: warping + losses

This is a scaffold: plug in your VLM (image encoder), generator (diffusion/auto-regressive),
and training loop as needed.
"""

import os
import cv2
import numpy as np
from typing import Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

# ----------------------------
# Utilities: Optical flow & bitmap conversion
# ----------------------------
def compute_optical_flow(prev_frame: np.ndarray, next_frame: np.ndarray,
                         method: str = "farneback") -> np.ndarray:
    """
    Compute dense optical flow between two frames (H x W x 2 float32)
    prev_frame, next_frame: BGR or grayscale images as numpy arrays (H,W,3) or (H,W)
    Returns flow with shape (H, W, 2), with flows in pixel units (dx, dy).
    """
    # Convert to grayscale
    if prev_frame.ndim == 3:
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    else:
        prev_gray = prev_frame
    if next_frame.ndim == 3:
        next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
    else:
        next_gray = next_frame

    if method == "farneback":
        flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray,
                                            None,
                                            pyr_scale=0.5, levels=3, winsize=15,
                                            iterations=3, poly_n=5, poly_sigma=1.2,
                                            flags=0)
        # flow is H x W x 2
    else:
        raise NotImplementedError("Only farneback implemented in scaffold. Replace with RAFT for better results.")
    return flow.astype(np.float32)


def flow_to_bitmap(flow: np.ndarray,
                   clip_flow_magnitude: float = None,
                   output_mode: str = "uv") -> np.ndarray:
    """
    Convert flow (H,W,2) into a normalized bitmap image suitable for an image encoder.
    output_mode:
      - "uv": 2 channels (u,v) normalized to [-1,1] (returned as H x W x 2 float32)
      - "rgb": 3-channel color-coded flow image (H x W x 3) uint8 (good for visualizing)
      - "uvc": 3 channels (u,v,confidence/magnitude) float32 normalized [-1,1]

    clip_flow_magnitude: optional value to clip and normalize flows. If None, uses dynamic
    max magnitude per-frame (but using fixed clip helps stability).
    """
    u = flow[..., 0]
    v = flow[..., 1]
    mag = np.sqrt(u * u + v * v)
    if clip_flow_magnitude is None:
        # avoid dividing by very small numbers; use percentile to be robust to outliers
        clip_flow_magnitude = max(1.0, np.percentile(mag, 95))
    u_n = np.clip(u / clip_flow_magnitude, -1.0, 1.0).astype(np.float32)
    v_n = np.clip(v / clip_flow_magnitude, -1.0, 1.0).astype(np.float32)
    if output_mode == "uv":
        out = np.stack([u_n, v_n], axis=-1)  # H, W, 2
    elif output_mode == "uvc":
        mag_n = np.clip(mag / clip_flow_magnitude, 0.0, 1.0).astype(np.float32)
        out = np.stack([u_n, v_n, mag_n], axis=-1)
    elif output_mode == "rgb":
        # color wheel visualization (for human inspection)
        hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
        ang = np.arctan2(v, u)  # -pi..pi
        hsv[..., 0] = np.uint8((ang + np.pi) / (2 * np.pi) * 179)  # hue
        hsv[..., 1] = np.uint8(np.minimum(1, mag / clip_flow_magnitude) * 255)  # saturation
        hsv[..., 2] = 255
        out = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    else:
        raise ValueError("Unknown output_mode")
    return out


# ----------------------------
# Torch modules: Flow encoder and conditioning injection
# ----------------------------
class FlowEncoder(nn.Module):
    """
    Small CNN that turns a 2/3-channel flow bitmap into a spatial embedding.
    Output: feature map (B, C, H//s, W//s) or flattened tokens depending on injection type.
    """
    def __init__(self, in_ch: int = 2, base_channels: int = 64, out_dim: int = 512, downsample: int = 4):
        super().__init__()
        self.conv1 = nn.Conv2d(in_ch, base_channels, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(base_channels)
        self.conv2 = nn.Conv2d(base_channels, base_channels * 2, kernel_size=3, stride=2, padding=1)
        self.bn2 = nn.BatchNorm2d(base_channels * 2)
        self.conv3 = nn.Conv2d(base_channels * 2, out_dim, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU(inplace=True)
        self.out_dim = out_dim
        self.downsample = downsample

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (B, in_ch, H, W) float in [-1,1] or [0,1]
        returns: embedding (B, out_dim, H//ds, W//ds)
        """
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.conv3(x)
        return x


class CrossAttentionInjection(nn.Module):
    """
    Insert conditioning via cross-attention-style keys/values for UNet/transformer-based generators.
    This is a minimal adapter: given flow embeddings, produce K/V tensors for cross-attn.
    """
    def __init__(self, flow_channels: int, model_dim: int, num_heads: int = 8):
        super().__init__()
        self.to_k = nn.Conv2d(flow_channels, model_dim, kernel_size=1)
        self.to_v = nn.Conv2d(flow_channels, model_dim, kernel_size=1)
        self.num_heads = num_heads
        self.model_dim = model_dim

    def forward(self, flow_feat: torch.Tensor):
        # flow_feat: (B, C, Hf, Wf)
        k = self.to_k(flow_feat)  # B, D, Hf, Wf
        v = self.to_v(flow_feat)
        # flatten spatial dims -> (B, tokens, D)
        B, D, Hf, Wf = k.shape
        k = k.view(B, D, Hf * Wf).permute(0, 2, 1).contiguous()  # B, T, D
        v = v.view(B, D, Hf * Wf).permute(0, 2, 1).contiguous()
        return k, v


# ----------------------------
# Temporal consistency losses & utilities
# ----------------------------
def warp_image_with_flow(img: torch.Tensor, flow: torch.Tensor) -> torch.Tensor:
    """
    Warp image tensor (B,C,H,W) using flow (B,2,H,W) which is in pixel units.
    Returns warped image (B,C,H,W). This uses grid_sample with normalized coordinates.
    """
    B, C, H, W = img.shape
    # create meshgrid
    yy, xx = torch.meshgrid(torch.arange(H, device=img.device), torch.arange(W, device=img.device), indexing='ij')
    grid_x = xx.float().unsqueeze(0).expand(B, -1, -1) + flow[:, 0, :, :]
    grid_y = yy.float().unsqueeze(0).expand(B, -1, -1) + flow[:, 1, :, :]
    # normalize to [-1,1]
    grid_x = 2.0 * grid_x / max(W - 1, 1) - 1.0
    grid_y = 2.0 * grid_y / max(H - 1, 1) - 1.0
    grid = torch.stack((grid_x, grid_y), dim=-1)  # B, H, W, 2
    warped = F.grid_sample(img, grid, mode="bilinear", padding_mode="border", align_corners=True)
    return warped


class TemporalConsistencyLosses:
    """
    Container for temporal losses used to encourage temporal consistency.
    - warp loss (L1 between warped prev frame and current)
    - perceptual loss (requires a VGG/CLIP feature extractor; stubbed)
    - identity loss (opt)
    """
    def __init__(self, perceptual_model=None):
        self.perceptual_model = perceptual_model

    def warp_l1(self, current: torch.Tensor, prev: torch.Tensor, flow_prev_to_cur: torch.Tensor):
        """
        current, prev: (B, C, H, W)
        flow_prev_to_cur: (B, 2, H, W)
        """
        prev_warped = warp_image_with_flow(prev, flow_prev_to_cur)
        return F.l1_loss(current, prev_warped)

    def perceptual(self, current: torch.Tensor, prev: torch.Tensor):
        if self.perceptual_model is None:
            return torch.tensor(0.0, device=current.device)
        # TODO: extract features using self.perceptual_model (e.g., VGG)
        f1 = self.perceptual_model(current)
        f2 = self.perceptual_model(prev)
        return F.mse_loss(f1, f2)


# ----------------------------
# High-level generator wrapper (sketch)
# ----------------------------
class VideoGeneratorWrapper:
    """
    Wrap an existing video generator model (diffusion or autoregressive) and inject
    the flow conditioning. This is intentionally abstract: replace `.generate()` with
    your model's API.

    Two example conditioning injection strategies:
      - cross-attention keys/values: pass to UNet or transformer block
      - latent concatenation: concat flow encoding to latent channels at first timestep
    """

    def __init__(self, model, flow_encoder: FlowEncoder, injection: CrossAttentionInjection, device="cuda"):
        """
        model: your video generation model (UNet/diffuser/transformer). It must accept
               additional cross-attention keys/values or similar -- adapt as needed.
        flow_encoder: maps flow bitmap -> flow_feature_map
        injection: adapter that maps flow features -> K/V or modulation params
        """
        self.model = model
        self.flow_encoder = flow_encoder
        self.injection = injection
        self.device = device

    def prepare_flow_condition(self, flow_bitmap: np.ndarray) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Accept flow_bitmap as numpy HxWxC (float32), convert to tensor, pass through encoder and adapter.
        Returns k, v tensors (B, T, D).
        """
        x = torch.from_numpy(flow_bitmap).permute(2, 0, 1).unsqueeze(0).to(torch.float32).to(self.device)  # 1,C,H,W
        feat = self.flow_encoder(x)  # (1, C_feat, Hf, Wf)
        k, v = self.injection(feat)
        return k, v

    def generate(self, prompt: str, flow_bitmap: np.ndarray, clip_len: int = 16, **kwargs):
        """
        Generate a clip of length clip_len conditioned on prompt and flow_bitmap.
        This function should adapt to your model API.

        Example (pseudo):
          k, v = prepare_flow_condition(...)
          out = self.model.sample(prompt=prompt, cross_attn_k=k, cross_attn_v=v, frames=clip_len)
        """
        k, v = self.prepare_flow_condition(flow_bitmap)
        # TODO: integrate with your model sampler. Example pseudocode:
        # out = self.model.sample(prompt=prompt, cross_attn_k=k, cross_attn_v=v, frames=clip_len, **kwargs)
        # For scaffold, we return None
        raise NotImplementedError("Plug in your model sampling call here using k/v cross-attention.")


# ----------------------------
# Example inference pipeline (tie it together)
# ----------------------------
def inference_loop_for_clips(prev_clip_last_frame: np.ndarray,
                             prompt_next: str,
                             generator: VideoGeneratorWrapper,
                             compute_flow_fn=compute_optical_flow,
                             flow_mode="uv",
                             device="cuda"):
    """
    prev_clip_last_frame: final frame of previous clip (H,W,3) BGR uint8
    prompt_next: prompt text for next clip
    generator: VideoGeneratorWrapper
    Returns: generated_clip (model-dependent)
    """
    # For motion info, we may prefer last two frames - here we just use a synthetic previous frame
    # If you have last two frames, compute flow between them. If only single frame, you can compute
    # estimated pseudo-motion (e.g., from previous motions or from text).
    # This scaffold assumes you have prev_prev_frame available; adapt as needed.

    # Example: compute flow between prev_prev and prev_last (user should supply prev_prev_frame)
    raise NotImplementedError("This high-level helper expects your runner to provide two frames or tracked motion.")


# ----------------------------
# Example usage and tips
# ----------------------------
if __name__ == "__main__":
    # Example: compute flow between two images and get bitmap
    prev = cv2.imread("prev.png")  # replace
    nex = cv2.imread("next.png")   # replace
    flow = compute_optical_flow(prev, nex)
    bitmap = flow_to_bitmap(flow, output_mode="uvc")
    # Save bitmap for inspection
    # Note: bitmap has floats; convert to image to view:
    cv2.imwrite("flow_uvc_vis.png", ((bitmap[..., :3] + 1.0) / 2.0 * 255).astype(np.uint8))
    print("Wrote flow visualization. Plug bitmap into FlowEncoder -> generator.")
