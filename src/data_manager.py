"""
=============================================================================
 数据管理模块 — 游戏数据持久化
=============================================================================
 所属功能块: 核心引擎
 功能描述  : 处理游戏数据的 JSON 序列化与反序列化
             包含排行榜记录、玩家设置等数据的本地存取
=============================================================================
"""
import json
import os
import sys
from datetime import datetime
import shutil

# 数据文件路径
DATA_FILE = "data.json"

# 用于防止重复记录的全局变量
_last_record = None

def get_data_file_path():
    """
    获取数据文件的完整路径
    尝试在用户目录下创建数据文件，如果失败则使用程序目录
    
    Returns:
        str: 数据文件的完整路径
    """
    # 尝试获取用户文档目录
    try:
        import platform
        system = platform.system()

        if system == "Windows":
            # Windows系统使用Documents/My Games/shoot目录
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            data_dir = os.path.join(documents_path, "My Games", "shoot")
        elif system == "Linux" and 'ANDROID_STORAGE' in os.environ:
            # Android 使用外部存储
            data_dir = os.path.join('/sdcard', '.shoot_data')
        else:
            # 其他系统使用用户主目录下的.shoot文件夹
            data_dir = os.path.join(os.path.expanduser("~"), ".shoot")

        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 返回完整的文件路径
        return os.path.join(data_dir, DATA_FILE)
    except:
        # 如果无法创建目录，则使用程序目录
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, DATA_FILE)

def load_settings():
    """
    加载游戏设置数据
    
    Returns:
        dict: 包含排行榜和设置数据的字典
    """
    data_file_path = get_data_file_path()

    # 如果文件存在，尝试加载数据
    if os.path.exists(data_file_path):
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 如果是字典格式，说明是设置数据
                if isinstance(data, dict):
                    return data
                # 如果是列表格式，说明是排行榜数据，需要转换
                elif isinstance(data, list):
                    return {"leaderboard": data, "settings": {}}
        except (json.JSONDecodeError, IOError):
            # 如果文件损坏或无法读取，返回默认设置
            return {"leaderboard": [], "settings": {}}
    else:
        # 如果文件不存在，创建默认数据文件
        default_data = {"leaderboard": [], "settings": {}}
        save_all_data(default_data)
        return default_data

def save_all_data(data):
    """
    保存所有游戏数据（排行榜和设置）
    
    Args:
        data: 要保存的所有数据
        
    Returns:
        bool: 保存成功返回True，否则返回False
    """
    data_file_path = get_data_file_path()

    try:
        with open(data_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False

def add_game_record(final_score, enemies_defeated):
    """
    添加游戏记录到排行榜
    
    Args:
        final_score (int): 最终得分
        enemies_defeated (int): 击败的敌人数量
        
    Returns:
        bool: 添加成功返回True，否则返回False
    """
    global _last_record

    # 检查是否与上一条记录完全相同（防止重复保存）
    current_record_data = (final_score, enemies_defeated)
    if _last_record == current_record_data:
        return False  # 防止重复记录

    # 更新最后记录的数据
    _last_record = current_record_data

    # 加载现有数据
    all_data = load_settings()
    data = all_data.get("leaderboard", [])

    # 创建新记录
    record = {
        "score": final_score,
        "enemies": enemies_defeated
    }

    # 添加记录
    data.append(record)

    # 按分数排序（降序）
    data.sort(key=lambda x: x["score"], reverse=True)

    # 只保留前5条记录
    data = data[:5]

    # 保存数据
    all_data["leaderboard"] = data
    return save_all_data(all_data)

def get_leaderboard_data():
    """
    获取排行榜数据
    
    Returns:
        list: 排行榜数据列表，按分数降序排列
    """
    all_data = load_settings()
    data = all_data.get("leaderboard", [])
    # 按分数排序（降序）
    data.sort(key=lambda x: x["score"], reverse=True)
    return data

def save_settings(settings):
    """
    保存游戏设置
    
    Args:
        settings (dict): 要保存的设置数据
        
    Returns:
        bool: 保存成功返回True，否则返回False
    """
    # 加载现有数据
    all_data = load_settings()
    # 更新设置数据
    all_data["settings"] = settings
    # 保存所有数据
    return save_all_data(all_data)

def get_settings():
    """
    获取游戏设置
    
    Returns:
        dict: 游戏设置数据
    """
    all_data = load_settings()
    return all_data.get("settings", {})

def reset_last_record():
    """
    重置最后记录的数据
    """
    global _last_record
    _last_record = None