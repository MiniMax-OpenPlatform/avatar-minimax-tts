#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版随机动作控制器
纯随机时间间隔切换的头部动作控制
"""

import random
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class SimpleMotionConfig:
    """简化随机动作配置"""

    # 动作切换时间间隔 (秒)
    switch_interval_range: Tuple[float, float] = (2.0, 5.0)

    # 动作类型权重分布
    motion_weights: Dict[str, float] = None

    # 头部动作参数
    nod_range: Tuple[float, float] = (5.0, 10.0)    # 点头角度范围
    tilt_range: Tuple[float, float] = (3.0, 8.0)    # 倾斜角度范围

    def __post_init__(self):
        if self.motion_weights is None:
            self.motion_weights = {
                'still': 0.50,          # 静止 - 增加比例
                'nod': 0.30,            # 点头
                'tilt': 0.20            # 倾斜
            }


class SimpleMotionController:
    """简化版随机动作控制器"""

    def __init__(self, config: SimpleMotionConfig = None):
        self.config = config or SimpleMotionConfig()

        # 动作类型定义
        self.motion_types = {
            'still': '静止',
            'nod': '点头',
            'tilt': '倾斜'
        }

    def generate_motion_timeline(self, duration: float) -> List[Dict]:
        """
        生成随机动作时间线

        Args:
            duration: 总时长 (秒)

        Returns:
            动作时间线列表
        """
        timeline = []
        current_time = 0.0
        motion_id = 0

        while current_time < duration:
            # 随机选择动作类型
            motion_type = self._select_motion_type()

            # 随机生成切换间隔
            interval = random.uniform(*self.config.switch_interval_range)
            end_time = min(current_time + interval, duration)

            # 生成动作参数
            motion_params = self._generate_motion_params(motion_type, interval)

            timeline.append({
                'id': motion_id,
                'type': motion_type,
                'name': self.motion_types[motion_type],
                'start_time': current_time,
                'end_time': end_time,
                'duration': end_time - current_time,
                'params': motion_params
            })

            current_time = end_time
            motion_id += 1

        return timeline

    def _select_motion_type(self) -> str:
        """根据权重随机选择动作类型"""
        types = list(self.config.motion_weights.keys())
        weights = list(self.config.motion_weights.values())
        return random.choices(types, weights=weights)[0]

    def _generate_motion_params(self, motion_type: str, duration: float) -> Dict:
        """生成动作参数"""

        if motion_type == 'still':
            return self._generate_still_params()
        elif motion_type == 'nod':
            return self._generate_nod_params(duration)
        elif motion_type == 'tilt':
            return self._generate_tilt_params(duration)
        else:
            return self._generate_still_params()

    def _generate_still_params(self) -> Dict:
        """生成静止状态参数"""
        return {
            'type': 'still',
            'head_pose': {'pitch': 0, 'yaw': 0, 'roll': 0}
        }

    def _generate_nod_params(self, duration: float) -> Dict:
        """生成点头动作参数"""
        amplitude = random.uniform(*self.config.nod_range)
        frequency = random.uniform(0.5, 1.2)  # 点头频率
        direction = random.choice([1, -1])     # 向上或向下开始

        return {
            'type': 'nod',
            'head_pose': {
                'pitch': amplitude * direction,
                'yaw': 0,
                'roll': 0,
                'amplitude': amplitude,
                'frequency': frequency
            }
        }

    def _generate_tilt_params(self, duration: float) -> Dict:
        """生成倾斜动作参数"""
        amplitude = random.uniform(*self.config.tilt_range)
        direction = random.choice([-1, 1])  # 左倾或右倾

        return {
            'type': 'tilt',
            'head_pose': {
                'pitch': 0,
                'yaw': 0,
                'roll': amplitude * direction,
                'amplitude': amplitude,
                'direction': direction
            }
        }

    def get_pose_at_time(self, timeline: List[Dict], time_point: float) -> Dict:
        """
        获取指定时间点的姿态参数

        Args:
            timeline: 动作时间线
            time_point: 时间点 (秒)

        Returns:
            头部姿态参数
        """
        # 查找当前时间对应的动作
        current_motion = None
        for motion in timeline:
            if motion['start_time'] <= time_point <= motion['end_time']:
                current_motion = motion
                break

        if current_motion is None:
            # 默认静止状态
            return {'head_pose': {'pitch': 0, 'yaw': 0, 'roll': 0}}

        # 计算动作进度
        progress = (time_point - current_motion['start_time']) / current_motion['duration']
        progress = np.clip(progress, 0.0, 1.0)

        # 根据动作类型计算具体姿态
        return self._calculate_pose_for_motion(current_motion, progress)

    def _calculate_pose_for_motion(self, motion: Dict, progress: float) -> Dict:
        """根据动作和进度计算具体姿态"""
        params = motion['params']
        motion_type = params['type']

        if motion_type == 'still':
            return params

        elif motion_type == 'nod':
            # 点头的正弦波运动
            amplitude = params['head_pose']['amplitude']
            frequency = params['head_pose']['frequency']

            angle = 2 * np.pi * frequency * progress
            pitch = amplitude * np.sin(angle)

            return {'head_pose': {'pitch': pitch, 'yaw': 0, 'roll': 0}}

        elif motion_type == 'tilt':
            # 倾斜保持姿态
            return {
                'head_pose': {
                    'pitch': 0,
                    'yaw': 0,
                    'roll': params['head_pose']['roll']
                }
            }

        else:
            return {'head_pose': {'pitch': 0, 'yaw': 0, 'roll': 0}}

    def generate_pose_sequence(self, timeline: List[Dict], duration: float, fps: int = 25) -> np.ndarray:
        """
        生成完整的头部姿态序列

        Args:
            timeline: 动作时间线
            duration: 总时长
            fps: 帧率

        Returns:
            头部姿态序列数组 (frames, 3) - [pitch, yaw, roll]
        """
        total_frames = int(duration * fps)
        head_poses = np.zeros((total_frames, 3))  # [pitch, yaw, roll]

        for frame_idx in range(total_frames):
            time_point = frame_idx / fps
            pose = self.get_pose_at_time(timeline, time_point)

            # 头部姿态
            head_pose = pose['head_pose']
            head_poses[frame_idx] = [
                head_pose['pitch'],
                head_pose['yaw'],
                head_pose['roll']
            ]

        return head_poses

    def print_timeline_summary(self, timeline: List[Dict]):
        """打印时间线摘要"""
        print("随机动作时间线:")
        print("-" * 40)

        for motion in timeline:
            print(f"动作 {motion['id']}: {motion['name']}")
            print(f"  时间: {motion['start_time']:.1f}s - {motion['end_time']:.1f}s ({motion['duration']:.1f}s)")

            params = motion['params']
            if params['type'] != 'still':
                head_pose = params['head_pose']
                if params['type'] == 'nod':
                    print(f"  点头幅度: ±{head_pose['amplitude']:.1f}° 频率: {head_pose['frequency']:.1f}Hz")
                elif params['type'] == 'tilt':
                    print(f"  倾斜角度: {head_pose['roll']:.1f}°")
            print()


# 使用示例
if __name__ == "__main__":
    # 创建随机动作控制器
    config = SimpleMotionConfig(
        switch_interval_range=(2.0, 4.0),  # 2-4秒切换间隔
        motion_weights={
            'still': 0.4,         # 40% 静止
            'nod': 0.4,           # 40% 点头
            'tilt': 0.2           # 20% 倾斜
        }
    )

    controller = SimpleMotionController(config)

    # 生成8秒的随机动作时间线
    timeline = controller.generate_motion_timeline(8.0)

    # 打印时间线
    controller.print_timeline_summary(timeline)

    # 生成姿态序列
    head_poses = controller.generate_pose_sequence(timeline, 8.0)

    print(f"生成的头部姿态序列形状: {head_poses.shape}")

    # 测试几个时间点
    test_times = [1.0, 3.0, 5.0, 7.0]
    print("\n随机时间点测试:")
    for t in test_times:
        pose = controller.get_pose_at_time(timeline, t)
        head = pose['head_pose']
        print(f"时间 {t}s: 头部({head['pitch']:.1f}°,{head['yaw']:.1f}°,{head['roll']:.1f}°)")