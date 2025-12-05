#!/usr/bin/env python3
"""
HeyGem数字人视频循环播放策略配置工具
用于调整视频不足时的循环播放行为
"""

import os
import sys
import configparser

class LoopStrategyConfig:
    def __init__(self, config_path="config/config.ini"):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """加载当前配置"""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            print(f"配置文件不存在: {self.config_path}")
            sys.exit(1)

    def display_current_settings(self):
        """显示当前配置"""
        print("====================================")
        print("当前循环播放策略配置")
        print("====================================")

        # 批次大小
        batch_size = self.config.get('digital', 'batch_size', fallback='4')
        print(f"批次大小 (batch_size): {batch_size}")

        # 其他相关设置
        temp_dir = self.config.get('temp', 'temp_dir', fallback='./')
        result_dir = self.config.get('result', 'result_dir', fallback='./result')
        clean_switch = self.config.get('temp', 'clean_switch', fallback='1')

        print(f"临时目录: {temp_dir}")
        print(f"结果目录: {result_dir}")
        print(f"自动清理: {'开启' if clean_switch == '1' else '关闭'}")

        print("\n循环播放行为说明:")
        print("- 当视频长度 < 音频长度时：视频帧会循环重复播放")
        print("- 当视频长度 > 音频长度时：视频会被截断到音频长度")
        print("- 批次大小影响处理速度和内存使用")
        print("")

    def set_batch_size(self, new_batch_size):
        """设置新的批次大小"""
        try:
            batch_size = int(new_batch_size)
            if batch_size < 1 or batch_size > 16:
                print("批次大小必须在1-16之间")
                return False

            self.config.set('digital', 'batch_size', str(batch_size))
            return True
        except ValueError:
            print("批次大小必须是整数")
            return False

    def save_config(self):
        """保存配置到文件"""
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
        print(f"配置已保存到: {self.config_path}")

    def get_recommendations(self):
        """获取配置建议"""
        print("====================================")
        print("批次大小配置建议")
        print("====================================")
        print("1 - 最精细处理，最稳定，最慢（适合高质量需求）")
        print("2 - 较精细处理（适合质量优先场景）")
        print("4 - 平衡设置（当前默认，推荐大多数场景）")
        print("6 - 较快处理（适合速度优先场景）")
        print("8 - 快速处理，需要更多显存（适合批量处理）")
        print("12+ - 高速处理，需要大量显存（专业批量场景）")
        print("")
        print("注意: 批次大小越大，显存使用越多，但处理速度更快")
        print("")

def main():
    """主函数"""
    config_tool = LoopStrategyConfig()

    while True:
        print("\n====================================")
        print("HeyGem数字人 - 循环播放策略配置")
        print("====================================")
        print("1. 查看当前配置")
        print("2. 修改批次大小")
        print("3. 配置建议")
        print("4. 保存并退出")
        print("5. 退出（不保存）")
        print("")

        choice = input("请选择操作 [1-5]: ").strip()

        if choice == '1':
            config_tool.display_current_settings()

        elif choice == '2':
            config_tool.display_current_settings()
            print("")
            new_batch_size = input("请输入新的批次大小 [1-16]: ").strip()
            if config_tool.set_batch_size(new_batch_size):
                print(f"批次大小已设置为: {new_batch_size}")

        elif choice == '3':
            config_tool.get_recommendations()

        elif choice == '4':
            config_tool.save_config()
            print("配置已保存，请重启服务以生效:")
            print("sudo docker restart heygem-service")
            break

        elif choice == '5':
            print("退出，配置未保存")
            break

        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    main()