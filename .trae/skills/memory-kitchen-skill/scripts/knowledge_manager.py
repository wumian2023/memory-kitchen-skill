#!/usr/bin/env python3
"""
知识库管理器 (Knowledge Manager)

提供知识库的增删改查功能，包括：
- 删除知识（软删除）
- 恢复知识
- 批量操作
- 清理已删除知识
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Set
import glob

# 导入配置
try:
    from config import get_knowledge_base_dir
except ImportError:
    def get_knowledge_base_dir():
        return "./knowledge_base"


class KnowledgeManager:
    """知识库管理器"""
    
    def __init__(self, knowledge_dir: Optional[str] = None):
        """
        初始化知识库管理器
        
        Args:
            knowledge_dir: 知识库目录，默认使用配置中的目录
        """
        if knowledge_dir is None:
            knowledge_dir = get_knowledge_base_dir()
        
        self.knowledge_dir = knowledge_dir
        self.deleted_items_file = os.path.join(knowledge_dir, 'deleted_items.json')
        self.deleted_items: Set[str] = set()  # 存储已删除知识的ID
        
        # 加载已删除的知识列表
        self._load_deleted_items()
    
    def _load_deleted_items(self):
        """加载已删除的知识列表"""
        if os.path.exists(self.deleted_items_file):
            try:
                with open(self.deleted_items_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.deleted_items = set(data.get('deleted_ids', []))
            except Exception as e:
                print(f"⚠️ 加载已删除列表失败: {e}")
                self.deleted_items = set()
    
    def _save_deleted_items(self):
        """保存已删除的知识列表"""
        try:
            with open(self.deleted_items_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'deleted_ids': list(self.deleted_items),
                    'updated_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存已删除列表失败: {e}")
    
    def delete_knowledge(self, knowledge_id: str, reason: str = "") -> bool:
        """
        删除知识（软删除）
        
        Args:
            knowledge_id: 知识条目ID
            reason: 删除原因
            
        Returns:
            bool: 是否成功删除
        """
        if knowledge_id in self.deleted_items:
            print(f"⚠️ 知识 {knowledge_id[:8]}... 已经被删除")
            return False
        
        self.deleted_items.add(knowledge_id)
        self._save_deleted_items()
        
        # 记录删除原因
        if reason:
            self._log_deletion_reason(knowledge_id, reason)
        
        print(f"✅ 已删除知识 {knowledge_id[:8]}...")
        return True
    
    def batch_delete(self, knowledge_ids: List[str], reason: str = "") -> Dict[str, bool]:
        """
        批量删除知识
        
        Args:
            knowledge_ids: 知识条目ID列表
            reason: 删除原因
            
        Returns:
            Dict: 每个ID的删除结果
        """
        results = {}
        for kid in knowledge_ids:
            results[kid] = self.delete_knowledge(kid, reason)
        return results
    
    def restore_knowledge(self, knowledge_id: str) -> bool:
        """
        恢复已删除的知识
        
        Args:
            knowledge_id: 知识条目ID
            
        Returns:
            bool: 是否成功恢复
        """
        if knowledge_id not in self.deleted_items:
            print(f"⚠️ 知识 {knowledge_id[:8]}... 未被删除")
            return False
        
        self.deleted_items.remove(knowledge_id)
        self._save_deleted_items()
        
        print(f"✅ 已恢复知识 {knowledge_id[:8]}...")
        return True
    
    def batch_restore(self, knowledge_ids: List[str]) -> Dict[str, bool]:
        """
        批量恢复知识
        
        Args:
            knowledge_ids: 知识条目ID列表
            
        Returns:
            Dict: 每个ID的恢复结果
        """
        results = {}
        for kid in knowledge_ids:
            results[kid] = self.restore_knowledge(kid)
        return results
    
    def is_deleted(self, knowledge_id: str) -> bool:
        """
        检查知识是否已被删除
        
        Args:
            knowledge_id: 知识条目ID
            
        Returns:
            bool: 是否已删除
        """
        return knowledge_id in self.deleted_items
    
    def filter_deleted(self, knowledge_items: List[Dict]) -> List[Dict]:
        """
        过滤掉已删除的知识
        
        Args:
            knowledge_items: 知识条目列表
            
        Returns:
            List: 未删除的知识列表
        """
        return [item for item in knowledge_items if not self.is_deleted(item.get('id', ''))]
    
    def get_deleted_items(self) -> List[str]:
        """
        获取所有已删除的知识ID
        
        Returns:
            List: 已删除的知识ID列表
        """
        return list(self.deleted_items)
    
    def _log_deletion_reason(self, knowledge_id: str, reason: str):
        """记录删除原因"""
        reason_file = os.path.join(self.knowledge_dir, 'deletion_log.json')
        
        log_entry = {
            'id': knowledge_id,
            'reason': reason,
            'deleted_at': datetime.now().isoformat()
        }
        
        # 加载现有日志
        logs = []
        if os.path.exists(reason_file):
            try:
                with open(reason_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # 添加新日志
        logs.append(log_entry)
        
        # 保存日志
        try:
            with open(reason_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 记录删除原因失败: {e}")
    
    def get_deletion_reason(self, knowledge_id: str) -> Optional[str]:
        """
        获取删除原因
        
        Args:
            knowledge_id: 知识条目ID
            
        Returns:
            str: 删除原因，如果没有记录则返回None
        """
        reason_file = os.path.join(self.knowledge_dir, 'deletion_log.json')
        
        if not os.path.exists(reason_file):
            return None
        
        try:
            with open(reason_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                for log in logs:
                    if log.get('id') == knowledge_id:
                        return log.get('reason', '')
        except:
            pass
        
        return None
    
    def cleanup_deleted_items(self, dry_run: bool = True) -> Dict:
        """
        清理已删除的知识（从JSON文件中永久删除）
        
        Args:
            dry_run: 是否为试运行模式（不实际删除）
            
        Returns:
            Dict: 清理统计信息
        """
        stats = {
            'scanned_files': 0,
            'modified_files': 0,
            'removed_items': 0,
            'details': []
        }
        
        # 扫描所有知识文件
        json_files = glob.glob(os.path.join(self.knowledge_dir, '*.json'))
        
        for file_path in json_files:
            if 'deleted_items.json' in file_path or 'deletion_log.json' in file_path:
                continue
            
            stats['scanned_files'] += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                
                if not isinstance(items, list):
                    continue
                
                original_count = len(items)
                # 过滤已删除的项
                filtered_items = [item for item in items if not self.is_deleted(item.get('id', ''))]
                removed_count = original_count - len(filtered_items)
                
                if removed_count > 0:
                    stats['modified_files'] += 1
                    stats['removed_items'] += removed_count
                    stats['details'].append({
                        'file': os.path.basename(file_path),
                        'removed': removed_count
                    })
                    
                    if not dry_run:
                        # 实际删除
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(filtered_items, f, ensure_ascii=False, indent=2)
                        print(f"✅ 已从 {os.path.basename(file_path)} 删除 {removed_count} 条知识")
                    else:
                        print(f"[试运行] 将从 {os.path.basename(file_path)} 删除 {removed_count} 条知识")
                        
            except Exception as e:
                print(f"⚠️ 处理文件 {file_path} 时出错: {e}")
        
        return stats
    
    def list_all_knowledge(self, include_deleted: bool = False) -> List[Dict]:
        """
        列出所有知识
        
        Args:
            include_deleted: 是否包含已删除的知识
            
        Returns:
            List: 知识条目列表
        """
        all_items = []
        
        # 扫描所有知识文件
        json_files = glob.glob(os.path.join(self.knowledge_dir, '*.json'))
        
        for file_path in json_files:
            if 'deleted_items.json' in file_path or 'deletion_log.json' in file_path:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            # 添加删除状态标记
                            item['_is_deleted'] = self.is_deleted(item.get('id', ''))
                            if include_deleted or not item['_is_deleted']:
                                all_items.append(item)
                                
            except Exception as e:
                print(f"⚠️ 读取文件 {file_path} 时出错: {e}")
        
        return all_items


# --- 命令行接口 ---
if __name__ == '__main__':
    import sys
    
    manager = KnowledgeManager()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python knowledge_manager.py list [all|deleted|active]")
        print("  python knowledge_manager.py delete <knowledge_id> [reason]")
        print("  python knowledge_manager.py restore <knowledge_id>")
        print("  python knowledge_manager.py cleanup [--force]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        mode = sys.argv[2] if len(sys.argv) > 2 else 'active'
        
        if mode == 'deleted':
            deleted_ids = manager.get_deleted_items()
            print(f"已删除的知识 ({len(deleted_ids)} 条):")
            for kid in deleted_ids:
                reason = manager.get_deletion_reason(kid)
                print(f"  - {kid[:8]}... {f'(原因: {reason})' if reason else ''}")
                
        elif mode == 'all':
            items = manager.list_all_knowledge(include_deleted=True)
            print(f"所有知识 ({len(items)} 条):")
            for item in items:
                status = "[已删除]" if item.get('_is_deleted') else "[有效]"
                print(f"  {status} {item.get('question', 'N/A')[:50]}...")
                
        else:  # active
            items = manager.list_all_knowledge(include_deleted=False)
            print(f"有效知识 ({len(items)} 条):")
            for item in items:
                print(f"  - {item.get('question', 'N/A')[:50]}...")
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("错误: 请提供知识ID")
            sys.exit(1)
        
        kid = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else ""
        manager.delete_knowledge(kid, reason)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("错误: 请提供知识ID")
            sys.exit(1)
        
        kid = sys.argv[2]
        manager.restore_knowledge(kid)
    
    elif command == 'cleanup':
        force = '--force' in sys.argv
        stats = manager.cleanup_deleted_items(dry_run=not force)
        
        print(f"\n清理统计:")
        print(f"  扫描文件: {stats['scanned_files']}")
        print(f"  修改文件: {stats['modified_files']}")
        print(f"  删除条目: {stats['removed_items']}")
        
        if not force:
            print("\n这是试运行模式，使用 --force 参数执行实际删除")
    
    else:
        print(f"未知命令: {command}")
