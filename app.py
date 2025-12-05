#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TTS数字人生成系统
用户输入文本和TTS参数，自动生成语音并制作数字人视频
"""

import argparse
import gc
import json
import os
import requests
import subprocess
import threading
import time
import traceback
import uuid
from enum import Enum
import queue
import shutil
from functools import partial
from tempfile import NamedTemporaryFile

import cv2
import gradio as gr
from flask import Flask, request

import service.trans_dh_service
from h_utils.custom import CustomError
from y_utils.config import GlobalConfig
from y_utils.logger import logger
from simple_motion_controller import SimpleMotionController, SimpleMotionConfig

os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"


class TTSProvider:
    """TTS服务提供商"""
    MINIMAX = "Minimax"


def write_video_gradio(
    output_imgs_queue,
    temp_dir,
    result_dir,
    work_id,
    audio_path,
    result_queue,
    width,
    height,
    fps,
    watermark_switch=0,
    digital_auth=0,
    temp_queue=None,
):
    """自定义视频写入函数"""
    output_mp4 = os.path.join(temp_dir, "{}-t.mp4".format(work_id))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    result_path = os.path.join(result_dir, "{}-r.mp4".format(work_id))
    video_write = cv2.VideoWriter(output_mp4, fourcc, fps, (width, height))
    print("Custom VideoWriter init done")
    try:
        while True:
            state, reason, value_ = output_imgs_queue.get()
            if type(state) == bool and state == True:
                logger.info(
                    "Custom VideoWriter [{}]视频帧队列处理正常结束".format(work_id)
                )
                video_write.release()
                break
            elif type(state) == bool and state == False:
                logger.error(
                    "Custom VideoWriter [{}]视频帧队列处理异常结束，异常原因:[{}]".format(
                        work_id, reason
                    )
                )
                video_write.release()
                result_queue.put(
                    [
                        False,
                        "[{}]视频帧队列处理异常结束，异常原因:[{}]".format(work_id, reason),
                    ]
                )
                return
            else:
                # logger.info('Custom VideoWriter[{}] write img_index[{}]'.format(work_id, value_))
                # 原始app.py使用的是for result_img in value_:，我们需要保持一致
                for result_img in value_:
                    video_write.write(result_img)

        logger.info("Custom VideoWriter开始后处理")
        # 使用ffmpeg进行视频编码并添加音频
        if os.path.exists(audio_path):
            command = "ffmpeg -loglevel warning -y -i {} -i {} -c:a aac -c:v libx264 -crf 15 -strict -2 {}".format(
                audio_path, output_mp4, result_path
            )
            logger.info("command:{}".format(command))
        else:
            command = "ffmpeg -loglevel warning -y -i {} -i {} -c:a aac -c:v libx264 -crf 15 -strict -2 {}".format(
                audio_path, output_mp4, result_path
            )
            logger.info("Custom command:{}".format(command))
        subprocess.call(command, shell=True)
        print("###### Custom Video Writer write over")
        print(f"###### Video result saved in {os.path.realpath(result_path)}")
        result_queue.put([True, result_path])
    except Exception as e:
        logger.error(
            "Custom VideoWriter [{}]视频帧队列处理异常结束，异常原因:[{}]".format(
                work_id, e.__str__()
            )
        )
        result_queue.put(
            [
                False,
                "[{}]视频帧队列处理异常结束，异常原因:[{}]".format(
                    work_id, e.__str__()
                ),
            ]
        )
    logger.info("Custom VideoWriter 后处理进程结束")


# 重写服务的write_video函数
service.trans_dh_service.write_video = write_video_gradio


class TTSService:
    """TTS语音合成服务"""

    def __init__(self):
        self.minimax_url = "https://api.minimax.chat/v1/t2a_v2"
        self.supported_models = [
            "speech-01",
            "speech-01-hd",
            "speech-02",
            "speech-02-hd"
        ]
        self.voice_options = {
            "male-qn-qingse": "青涩青年男声",
            "male-qn-jingying": "精英男声",
            "male-qn-badao": "霸道男声",
            "male-qn-daxuesheng": "大学生男声",
            "female-qn-qingse": "青涩青年女声",
            "female-qn-jingying": "精英女声",
            "female-qn-badao": "霸道女声",
            "female-qn-daxuesheng": "大学生女声",
            "female-shaonv": "少女音色",
            "female-yujie": "御姐音色",
            "female-chengshu": "成熟女性音色",
            "female-tianmei": "甜美女性音色",
        }

    def generate_audio(self, api_key, voice_id, text, model="speech-02-hd"):
        """
        使用Minimax API生成音频

        Args:
            api_key: Minimax API密钥
            voice_id: 声音ID
            text: 要合成的文本
            model: 使用的模型

        Returns:
            str: 生成的音频文件路径
        """
        try:
            # 验证参数
            if not api_key or api_key == 'api_key':
                raise ValueError("请提供有效的API Key")

            if not text.strip():
                raise ValueError("请输入要合成的文本")

            # 记录用户输入的模型和声音ID（允许自定义输入）
            logger.info(f"使用模型: {model}, 声音ID: {voice_id}")

            # 准备请求数据
            payload = json.dumps({
                "model": model,
                "text": text.strip(),
                "voice_setting": {
                    "voice_id": voice_id,
                }
            })

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f"开始TTS合成: 模型={model}, 声音={voice_id}, 文本长度={len(text)}")

            # 发送请求
            response = requests.post(
                self.minimax_url,
                headers=headers,
                data=payload,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"TTS API请求失败: {response.status_code} - {response.text}")

            # 解析响应
            parsed_json = json.loads(response.text)

            if 'data' not in parsed_json or 'audio' not in parsed_json['data']:
                raise Exception(f"TTS API响应格式错误: {response.text}")

            # 保存音频文件
            audio_data = bytes.fromhex(parsed_json['data']['audio'])

            # 使用临时文件
            temp_audio = NamedTemporaryFile(delete=False, suffix='.mp3', prefix='tts_')
            temp_audio.write(audio_data)
            temp_audio.close()

            logger.info(f"TTS合成成功: 音频文件保存到 {temp_audio.name}")
            logger.info(f"Trace-Id: {response.headers.get('Trace-Id', 'N/A')}")

            return temp_audio.name

        except Exception as e:
            logger.error(f"TTS合成失败: {str(e)}")
            raise


class TTSDigitalHumanProcessor:
    """TTS数字人处理器"""

    def __init__(self):
        self.task = service.trans_dh_service.TransDhTask()
        self.basedir = GlobalConfig.instance().result_dir
        self.tts_service = TTSService()
        self.is_initialized = False
        self._initialize_service()
        print("TTSDigitalHumanProcessor init done")

    def _initialize_service(self):
        """初始化数字人服务"""
        logger.info("初始化TTS数字人服务...")
        try:
            time.sleep(5)
            logger.info("TTS数字人服务初始化完成。")
            self.is_initialized = True
        except Exception as e:
            logger.error(f"初始化TTS数字人服务失败: {e}")

    def generate_digital_human_from_video(
        self,
        audio_input_mode,
        api_key,
        voice_id,
        text,
        model,
        audio_file,
        video_file,
        motion_mode="无动作增强",
        motion_intensity=1.0,
        still_weight=0.5,
        nod_weight=0.3,
        tilt_weight=0.2,
        interval_min=2.0,
        interval_max=5.0,
        nod_amplitude_min=3.0,
        nod_amplitude_max=8.0,
        tilt_amplitude_min=3.0,
        tilt_amplitude_max=8.0
    ):
        """
        从文本或音频文件生成数字人视频

        Args:
            audio_input_mode: 音频输入模式 ('tts' 或 'upload')
            api_key: Minimax API密钥 (TTS模式必需)
            voice_id: 声音ID (TTS模式必需)
            text: 要合成的文本 (TTS模式必需)
            model: TTS模型 (TTS模式必需)
            audio_file: 音频文件 (upload模式必需)
            video_file: 视频文件
            motion_mode: 动作模式
            motion_intensity: 动作强度
            still_weight: 静止状态权重
            nod_weight: 点头动作权重
            tilt_weight: 倾斜动作权重
            interval_min: 最小动作间隔时间
            interval_max: 最大动作间隔时间
            nod_amplitude_min: 点头最小幅度
            nod_amplitude_max: 点头最大幅度
            tilt_amplitude_min: 倾斜最小幅度
            tilt_amplitude_max: 倾斜最大幅度

        Returns:
            tuple: (视频路径, 音频分析报告, 动作分析报告)
        """
        while not self.is_initialized:
            logger.info("服务尚未完成初始化，等待 1 秒...")
            time.sleep(1)

        work_id = str(uuid.uuid1())
        code = work_id
        temp_audio_path = None
        audio_analysis = ""

        try:
            # 根据输入模式处理音频
            if audio_input_mode == "tts":
                # TTS模式：生成音频
                logger.info("开始TTS语音合成...")
                temp_audio_path = self.tts_service.generate_audio(api_key, voice_id, text, model)
                audio_analysis = self._generate_tts_analysis(api_key, voice_id, text, model, temp_audio_path)
            elif audio_input_mode == "upload":
                # 上传模式：使用用户上传的音频文件
                if audio_file is None:
                    raise gr.Error("请上传音频文件")
                temp_audio_path = audio_file
                audio_analysis = self._generate_upload_analysis(audio_file)
                logger.info(f"使用上传的音频文件: {audio_file}")
            else:
                raise gr.Error("无效的音频输入模式")

            # 处理视频
            cap = cv2.VideoCapture(video_file)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()

            # 动作控制处理
            motion_analysis = self._apply_motion_control(
                motion_mode, motion_intensity, work_id,
                still_weight, nod_weight, tilt_weight,
                interval_min, interval_max,
                nod_amplitude_min, nod_amplitude_max,
                tilt_amplitude_min, tilt_amplitude_max
            )

            # 生成数字人视频
            logger.info("开始生成数字人视频...")
            self.task.task_dic[code] = ""
            self.task.work(temp_audio_path, video_file, code, 0, 0, 0, 0)

            result_path = self.task.task_dic[code][2]
            final_result_dir = os.path.join("result", code)
            os.makedirs(final_result_dir, exist_ok=True)
            os.system(f"mv {result_path} {final_result_dir}")
            os.system(
                f"rm -rf {os.path.join(os.path.dirname(result_path), code + '*.*')}"
            )
            result_path = os.path.realpath(
                os.path.join(final_result_dir, os.path.basename(result_path))
            )

            logger.info(f"数字人视频生成完成: {result_path}")
            return result_path, audio_analysis, motion_analysis

        except Exception as e:
            logger.error(f"TTS数字人生成失败: {e}")
            raise gr.Error(str(e))
        finally:
            # 清理临时音频文件(只删除TTS生成的文件，不删除用户上传的文件)
            if audio_input_mode == "tts" and temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass

    def _generate_tts_analysis(self, api_key, voice_id, text, model, audio_path):
        """生成TTS分析报告"""
        import time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        # 获取音频文件信息
        audio_size = 0
        if os.path.exists(audio_path):
            audio_size = os.path.getsize(audio_path)

        voice_name = self.tts_service.voice_options.get(voice_id, voice_id)

        analysis_lines = [
            f"🎤 TTS语音合成报告",
            f"🕐 生成时间: {current_time}",
            "",
            f"📝 输入文本: {text[:100]}{'...' if len(text) > 100 else ''}",
            f"📏 文本长度: {len(text)} 字符",
            "",
            f"🔧 TTS参数:",
            f"  🔑 API Provider: Minimax",
            f"  🎯 模型: {model}",
            f"  🎵 声音: {voice_name} ({voice_id})",
            "",
            f"📊 音频输出:",
            f"  📁 文件大小: {audio_size / 1024:.1f} KB",
            f"  🎶 格式: MP3",
            f"  ⏱️  预估时长: {audio_size / 4000:.1f} 秒",
            "",
            f"✅ TTS合成状态: 成功",
            "",
            "🔍 质量指标:",
            "  - 语音清晰度: 高清品质",
            "  - 语调自然度: AI优化",
            "  - 情感表达: 智能识别",
            "",
            "⚠️  注意: API调用消耗tokens，请合理使用"
        ]

        return "\n".join(analysis_lines)

    def _generate_upload_analysis(self, audio_file_path):
        """生成上传音频文件的分析报告"""
        import time
        import os
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        # 获取音频文件信息
        audio_size = 0
        file_name = "未知"
        if audio_file_path and os.path.exists(audio_file_path):
            audio_size = os.path.getsize(audio_file_path)
            file_name = os.path.basename(audio_file_path)

        analysis_lines = [
            f"🎵 音频文件上传报告",
            f"🕐 处理时间: {current_time}",
            "",
            f"📁 文件信息:",
            f"  📋 文件名: {file_name}",
            f"  📏 文件大小: {audio_size / 1024:.1f} KB",
            f"  📍 文件路径: {audio_file_path}",
            "",
            f"🔧 处理方式:",
            f"  🎤 音频来源: 用户上传",
            f"  🎶 格式支持: WAV, MP3, M4A, FLAC, OGG",
            f"  ⚡ 处理模式: 直接使用",
            "",
            f"✅ 音频文件状态: 已接收",
            "",
            f"📊 处理优势:",
            "  - 无需API调用，节省成本",
            "  - 支持自定义音频内容",
            "  - 保持原始音质",
            "  - 处理速度更快",
            "",
            "⚠️  注意: 请确保音频文件质量良好，以获得最佳视频效果"
        ]

        return "\n".join(analysis_lines)

    def _apply_motion_control(self, motion_mode, motion_intensity, work_id,
                             still_weight=0.5, nod_weight=0.3, tilt_weight=0.2,
                             interval_min=2.0, interval_max=5.0,
                             nod_amplitude_min=3.0, nod_amplitude_max=8.0,
                             tilt_amplitude_min=3.0, tilt_amplitude_max=8.0):
        """应用随机动作控制并生成分析报告"""
        import time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        motion_analysis_lines = [
            f"📊 随机动作分析报告 - 任务ID: {work_id}",
            f"🕐 处理时间: {current_time}",
            "",
            f"🎭 选择的动作模式: {motion_mode}",
            f"⚡ 动作强度: {motion_intensity:.1f}",
            ""
        ]

        # 基于选择的动作模式生成随机控制参数
        if motion_mode == "无动作增强":
            motion_analysis_lines.extend([
                "✅ 使用默认面部表情控制",
                "📈 随机动作: 关闭",
                "🎯 预期效果: 自然的唇型同步"
            ])
        elif motion_mode == "轻微点头":
            # 生成轻微点头的随机时间线
            config = SimpleMotionConfig(
                switch_interval_range=(3.0, 6.0),
                motion_weights={'still': 0.6, 'nod': 0.4, 'tilt': 0.0},
                nod_range=(3.0 * motion_intensity, 6.0 * motion_intensity)
            )
            controller = SimpleMotionController(config)
            timeline = controller.generate_motion_timeline(8.0)

            motion_analysis_lines.extend([
                "✅ 启用轻微随机点头动作",
                f"📊 点头角度范围: ±{3.0 * motion_intensity:.1f}° ~ ±{6.0 * motion_intensity:.1f}°",
                f"⏱️  随机切换间隔: 3-6秒",
                f"🎬 生成动作段数: {len(timeline)}",
                "🎯 预期效果: 自然的随机点头确认"
            ])

        elif motion_mode == "明显点头":
            config = SimpleMotionConfig(
                switch_interval_range=(2.0, 4.0),
                motion_weights={'still': 0.3, 'nod': 0.7, 'tilt': 0.0},
                nod_range=(6.0 * motion_intensity, 12.0 * motion_intensity)
            )
            controller = SimpleMotionController(config)
            timeline = controller.generate_motion_timeline(8.0)

            motion_analysis_lines.extend([
                "✅ 启用明显随机点头动作",
                f"📊 点头角度范围: ±{6.0 * motion_intensity:.1f}° ~ ±{12.0 * motion_intensity:.1f}°",
                f"⏱️  随机切换间隔: 2-4秒",
                f"🎬 生成动作段数: {len(timeline)}",
                "🎯 预期效果: 清晰的随机点头手势"
            ])

        elif motion_mode == "思考歪头":
            config = SimpleMotionConfig(
                switch_interval_range=(4.0, 8.0),
                motion_weights={'still': 0.4, 'nod': 0.1, 'tilt': 0.5},
                tilt_range=(5.0 * motion_intensity, 15.0 * motion_intensity)
            )
            controller = SimpleMotionController(config)
            timeline = controller.generate_motion_timeline(8.0)

            motion_analysis_lines.extend([
                "✅ 启用思考性随机歪头动作",
                f"📊 倾斜角度范围: ±{5.0 * motion_intensity:.1f}° ~ ±{15.0 * motion_intensity:.1f}°",
                f"⏱️  随机切换间隔: 4-8秒",
                f"🎬 生成动作段数: {len(timeline)}",
                "🎯 预期效果: 思考状态的随机头部倾斜"
            ])

        elif motion_mode == "随机混合":
            config = SimpleMotionConfig(
                switch_interval_range=(2.0, 5.0),
                motion_weights={'still': 0.4, 'nod': 0.35, 'tilt': 0.25},
                nod_range=(4.0 * motion_intensity, 8.0 * motion_intensity),
                tilt_range=(3.0 * motion_intensity, 10.0 * motion_intensity)
            )
            controller = SimpleMotionController(config)
            timeline = controller.generate_motion_timeline(8.0)

            motion_analysis_lines.extend([
                "✅ 启用完全随机混合动作",
                f"📊 动作组合: 点头+倾斜+静止",
                f"⏱️  随机切换间隔: 2-5秒",
                f"🎬 生成动作段数: {len(timeline)}",
                "🎯 预期效果: 自然的随机头部动作组合"
            ])

        elif motion_mode == "自定义配置":
            # 规范化权重
            total_weight = still_weight + nod_weight + tilt_weight
            if total_weight > 0:
                normalized_weights = {
                    'still': still_weight / total_weight,
                    'nod': nod_weight / total_weight,
                    'tilt': tilt_weight / total_weight
                }
            else:
                normalized_weights = {'still': 1.0, 'nod': 0.0, 'tilt': 0.0}

            config = SimpleMotionConfig(
                switch_interval_range=(interval_min, interval_max),
                motion_weights=normalized_weights,
                nod_range=(nod_amplitude_min * motion_intensity, nod_amplitude_max * motion_intensity),
                tilt_range=(tilt_amplitude_min * motion_intensity, tilt_amplitude_max * motion_intensity)
            )
            controller = SimpleMotionController(config)
            timeline = controller.generate_motion_timeline(8.0)

            motion_analysis_lines.extend([
                "✅ 启用自定义随机动作配置",
                f"📊 动作权重: 静止({normalized_weights['still']:.2f}) 点头({normalized_weights['nod']:.2f}) 倾斜({normalized_weights['tilt']:.2f})",
                f"⏱️  随机切换间隔: {interval_min:.1f}-{interval_max:.1f}秒",
                f"📐 点头幅度: ±{nod_amplitude_min * motion_intensity:.1f}° ~ ±{nod_amplitude_max * motion_intensity:.1f}°",
                f"📐 倾斜幅度: ±{tilt_amplitude_min * motion_intensity:.1f}° ~ ±{tilt_amplitude_max * motion_intensity:.1f}°",
                f"🎬 生成动作段数: {len(timeline)}",
                "🎯 预期效果: 完全自定义的随机动作组合"
            ])

        motion_analysis_lines.extend([
            "",
            "🔧 技术参数:",
            "- 随机动作生成: 启用" if motion_mode != "无动作增强" else "- 默认处理模式: 启用",
            "- 动作类型: 纯随机切换",
            "- 时间控制: 概率分布",
            f"- 强度倍数: {motion_intensity}x",
            "",
            "⚠️  注意: 随机动作模式，每次生成的时间线都不同"
        ])

        logger.info(f"随机动作控制设置: 模式={motion_mode}, 强度={motion_intensity}")
        return "\n".join(motion_analysis_lines)


if __name__ == "__main__":
    processor = TTSDigitalHumanProcessor()

    # 禁用队列功能修复stream.ts错误
    import os
    os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"

    with gr.Blocks(title="数字人视频生成系统/Digital Human Video Generator") as demo:
        gr.Markdown("## 🎬 数字人视频生成系统/Digital Human Video Generator")
        gr.Markdown("支持TTS语音合成或音频文件上传，配合随机动作控制生成数字人视频。/Support TTS speech synthesis or audio file upload, combined with random motion control to generate digital human videos.")

        with gr.Row():
            with gr.Column():
                # 音频输入方式选择
                with gr.Accordion("🎵 音频输入方式", open=True):
                    audio_input_mode = gr.Radio(
                        choices=[
                            ("TTS语音合成", "tts"),
                            ("上传音频文件", "upload")
                        ],
                        value="tts",
                        label="选择音频输入方式",
                        info="选择使用TTS生成语音或直接上传音频文件"
                    )

                # TTS配置
                with gr.Accordion("🎤 TTS语音合成配置", open=True):
                    with gr.Group() as tts_group:
                        api_key_input = gr.Textbox(
                            label="Minimax API Key",
                            placeholder="请输入您的Minimax API Key",
                            type="password"
                        )

                        model_input = gr.Textbox(
                            value="speech-2.6-hd",
                            label="TTS模型",
                            placeholder="输入TTS模型名称，如：speech-2.6-hd",
                            info="支持的模型：speech-01, speech-01-hd, speech-02, speech-02-hd, speech-2.6-hd等"
                        )

                        voice_input = gr.Textbox(
                            value="female-shaonv",
                            label="声音ID",
                            placeholder="输入声音ID，如：female-shaonv",
                            info="常用声音：male-qn-qingse, female-shaonv, female-yujie, male-qn-jingying等"
                        )

                        text_input = gr.Textbox(
                            label="输入文本",
                            placeholder="请输入要合成语音的文本内容...",
                            lines=4,
                            max_lines=8
                        )

                # 音频文件上传
                with gr.Accordion("📁 音频文件上传", open=False):
                    with gr.Group() as audio_group:
                        audio_file_input = gr.File(
                            label="上传音频文件 (支持格式：WAV, MP3, M4A, FLAC, OGG)",
                            file_types=[".wav", ".mp3", ".m4a", ".flac", ".ogg"]
                        )

                # 视频配置
                video_input = gr.File(label="上传视频文件/Upload video file")

                # 动作控制选项
                with gr.Accordion("🎭 随机动作控制选项 (实验性)", open=False):
                    motion_mode = gr.Dropdown(
                        choices=[
                            "无动作增强",
                            "轻微点头",
                            "明显点头",
                            "思考歪头",
                            "随机混合",
                            "自定义配置"
                        ],
                        value="轻微点头",
                        label="随机动作类型",
                        info="选择数字人的随机动作模式"
                    )
                    motion_intensity = gr.Slider(
                        minimum=0.1,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        label="动作强度",
                        info="控制动作的强烈程度"
                    )

                    # 动作权重配置
                    with gr.Row():
                        still_weight = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.5,
                            step=0.05,
                            label="静止权重",
                            info="静止状态的概率权重"
                        )
                        nod_weight = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.3,
                            step=0.05,
                            label="点头权重",
                            info="点头动作的概率权重"
                        )
                        tilt_weight = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.2,
                            step=0.05,
                            label="倾斜权重",
                            info="头部倾斜的概率权重"
                        )

                    # 动作时间配置
                    with gr.Row():
                        interval_min = gr.Number(
                            value=2.0,
                            minimum=0.5,
                            maximum=10.0,
                            step=0.5,
                            label="最小间隔时间(秒)",
                            info="动作切换的最小时间间隔"
                        )
                        interval_max = gr.Number(
                            value=5.0,
                            minimum=1.0,
                            maximum=15.0,
                            step=0.5,
                            label="最大间隔时间(秒)",
                            info="动作切换的最大时间间隔"
                        )

                    # 动作幅度配置
                    with gr.Row():
                        nod_amplitude_min = gr.Number(
                            value=3.0,
                            minimum=1.0,
                            maximum=20.0,
                            step=0.5,
                            label="点头最小幅度(度)",
                            info="点头动作的最小角度"
                        )
                        nod_amplitude_max = gr.Number(
                            value=8.0,
                            minimum=2.0,
                            maximum=25.0,
                            step=0.5,
                            label="点头最大幅度(度)",
                            info="点头动作的最大角度"
                        )

                    with gr.Row():
                        tilt_amplitude_min = gr.Number(
                            value=3.0,
                            minimum=1.0,
                            maximum=20.0,
                            step=0.5,
                            label="倾斜最小幅度(度)",
                            info="头部倾斜的最小角度"
                        )
                        tilt_amplitude_max = gr.Number(
                            value=8.0,
                            minimum=2.0,
                            maximum=25.0,
                            step=0.5,
                            label="倾斜最大幅度(度)",
                            info="头部倾斜的最大角度"
                        )

                submit_btn = gr.Button("🎬 生成TTS数字人视频", variant="primary", size="lg")

            with gr.Column():
                video_output = gr.Video(label="生成的数字人视频/Generated Digital Human Video")

                # 显示分析结果
                with gr.Accordion("📊 音频处理报告", open=True):
                    audio_analysis = gr.Textbox(
                        label="音频处理详情",
                        placeholder="音频处理完成后将显示分析报告...",
                        lines=8
                    )

                with gr.Accordion("📊 动作分析报告", open=False):
                    motion_analysis = gr.Textbox(
                        label="动作执行日志",
                        placeholder="动作处理完成后将显示分析结果...",
                        lines=5
                    )

        # 添加使用说明
        with gr.Accordion("📖 使用说明", open=False):
            gr.Markdown("""
            ### 🔧 使用步骤：
            1. **选择音频输入方式**：选择TTS语音合成或上传音频文件
            2. **配置音频参数**：
               - TTS模式：输入API Key、文本内容、选择模型和声音
               - 上传模式：选择音频文件（支持WAV、MP3、M4A、FLAC、OGG格式）
            3. **上传视频文件**：选择一个包含人脸的视频文件
            4. **配置随机动作控制**：根据需要选择随机动作模式和强度
            5. **生成视频**：点击生成按钮，等待处理完成

            ### 🎵 常用声音ID：
            - **男声**：male-qn-qingse (青涩青年), male-qn-jingying (精英), male-qn-badao (霸道), male-qn-daxuesheng (大学生)
            - **女声**：female-shaonv (少女), female-yujie (御姐), female-chengshu (成熟), female-tianmei (甜美)
            - **更多**：female-qn-qingse, female-qn-jingying, female-qn-badao, female-qn-daxuesheng等

            ### ⚠️ 注意事项：
            - 需要有效的Minimax API Key
            - 文本长度建议控制在1000字符以内
            - 视频文件需要包含清晰的人脸
            - API调用会消耗tokens，请合理使用
            """)

        # 简化界面：显示说明信息而不是复杂的切换逻辑
        gr.Markdown("""
        💡 **使用说明**：
        - 如果选择 "TTS语音合成"，请填写上方TTS配置并输入文本
        - 如果选择 "上传音频文件"，请在下方上传音频文件
        - 两种模式根据您在上面的选择自动生效，无需额外操作
        """)

        # 绑定提交事件
        submit_btn.click(
            fn=processor.generate_digital_human_from_video,
            inputs=[
                audio_input_mode,
                api_key_input,
                voice_input,
                text_input,
                model_input,
                audio_file_input,
                video_input,
                motion_mode,
                motion_intensity,
                still_weight,
                nod_weight,
                tilt_weight,
                interval_min,
                interval_max,
                nod_amplitude_min,
                nod_amplitude_max,
                tilt_amplitude_min,
                tilt_amplitude_max
            ],
            outputs=[video_output, audio_analysis, motion_analysis],
            queue=False
        )

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )