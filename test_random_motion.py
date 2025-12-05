#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试随机动作控制集成功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_random_motion_integration():
    """测试随机动作控制集成"""
    print("🧪 测试随机动作控制集成")
    print("=" * 50)

    try:
        from simple_motion_controller import SimpleMotionController, SimpleMotionConfig
        print("✅ 随机动作控制器导入成功")

        # 测试默认配置
        controller = SimpleMotionController()
        timeline = controller.generate_motion_timeline(5.0)
        print(f"✅ 默认时间线生成: {len(timeline)}个动作段")

        # 测试不同配置
        configs = {
            "轻微点头": SimpleMotionConfig(
                motion_weights={'still': 0.6, 'nod': 0.4, 'tilt': 0.0}
            ),
            "随机混合": SimpleMotionConfig(
                motion_weights={'still': 0.4, 'nod': 0.35, 'tilt': 0.25}
            )
        }

        for name, config in configs.items():
            controller = SimpleMotionController(config)
            timeline = controller.generate_motion_timeline(8.0)
            print(f"✅ {name} 配置: {len(timeline)}个动作段")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_random_motion_integration()
    if success:
        print("\n🎉 随机动作控制集成测试成功！")
        print("现在可以启动app.py测试Web界面功能")
    else:
        print("\n❌ 测试失败")