"""
=============================================================================
 音效管理模块 — 音效播放控制
=============================================================================
 所属功能块: 音效系统
 功能描述  : 管理游戏音效的加载、播放、音量控制，支持多音效同时播放
=============================================================================
"""
import pygame
import threading
from collections import deque
from src.config import SOUND_VOLUMES


class SoundManager:
    """
    音效管理器类
    管理游戏中的音效播放，支持同时播放多个相同或不同的音效
    """
    
    def __init__(self, sounds_dict):
        """
        初始化音效管理器
        
        Args:
            sounds_dict (dict): 音效字典，包含所有已加载的音效对象
        """
        self.sounds = sounds_dict
        self.active_sounds = []  # 存储当前正在播放的音效通道
        self.max_simultaneous_sounds = 100  # 最大同时播放音效数量
        
    def play_sound(self, sound_name, loops=0):
        """
        播放音效
        
        Args:
            sound_name (str): 音效名称
            loops (int): 循环播放次数，0表示播放一次，-1表示无限循环
        """
        if sound_name in self.sounds:
            # 检查是否达到最大同时播放数量
            if len(self.active_sounds) >= self.max_simultaneous_sounds:
                # 移除已经播放完毕的音效通道
                self.active_sounds = [channel for channel in self.active_sounds if channel.get_busy()]
                
                # 如果仍然达到上限，则不播放新音效
                if len(self.active_sounds) >= self.max_simultaneous_sounds:
                    return
            
            # 播放音效并跟踪播放通道
            channel = self.sounds[sound_name].play(loops)
            if channel and loops == 0:  # 只跟踪非循环音效
                self.active_sounds.append(channel)
                
    def set_volume(self, sound_name, volume):
        """
        设置特定音效的音量
        
        Args:
            sound_name (str): 音效名称
            volume (float): 音量值 (0.0 到 1.0)
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            
    def set_master_volume(self, volume):
        """
        设置主音量（影响所有音效）
        
        Args:
            volume (float): 音量值 (0.0 到 1.0)
        """
        for sound in self.sounds.values():
            # 基于原始音量设置新音量
            # 注意：这需要保存原始音量值，我们在初始化时从SOUND_VOLUMES获取
            sound_name = None
            for name, s in self.sounds.items():
                if s == sound:
                    sound_name = name
                    break
                    
            if sound_name and sound_name in SOUND_VOLUMES:
                sound.set_volume(SOUND_VOLUMES[sound_name] * volume)
                
    def stop_sound(self, sound_name):
        """
        停止特定音效的播放
        
        Args:
            sound_name (str): 音效名称
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
            
    def stop_all_sounds(self):
        """
        停止所有音效的播放
        """
        pygame.mixer.stop()
        self.active_sounds.clear()