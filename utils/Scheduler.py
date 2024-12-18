import threading
import time
from datetime import datetime, timedelta
from queue import PriorityQueue
from concurrent.futures import ThreadPoolExecutor
import logging
import inspect
from typing import Union, Tuple, Optional, Dict, Any

class Command:
    """命令封装类"""
    def __init__(self, code: str, globals_dict: dict, locals_dict: dict):
        self.code = code
        self.globals_dict = globals_dict
        self.locals_dict = locals_dict

    def execute(self):
        try:
            exec(self.code, self.globals_dict, self.locals_dict)
        except Exception as e:
            logging.error(f"Command execution failed: {e}")
            raise

class TimeParser:
    """时间解析类"""
    @staticmethod
    def parse(time_str: str) -> Tuple[float, str]:
        """
        解析时间字符串，返回执行时间戳和时间类型
        支持格式：
        - 单个数字: 表示延迟秒数
        - 两个数字: 表示小时和分钟
        """
        try:
            parts = time_str.strip().split()
            if len(parts) == 1:
                # 延迟秒数
                delay = float(parts[0])
                return time.time() + delay, "delay"
            elif len(parts) == 2:
                # 时 分
                hour = int(parts[0])
                minute = int(parts[1])
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError("Invalid time format")
                    
                target_time = datetime.now().replace(hour=hour, minute=minute, second=0)
                if target_time <= datetime.now():
                    target_time += timedelta(days=1)
                
                return target_time.timestamp(), "absolute"
            else:
                raise ValueError("Invalid time format")
        except ValueError as e:
            raise ValueError(f"Time parsing error: {e}")

class Scheduler:
    """调度器类"""
    def __init__(self):
        self._queue = PriorityQueue()
        self._running = True
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._wakeup_event = threading.Event()
        self._lock = threading.Lock()
        
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
    
    def add_command(self, command_str: str, context_globals: Optional[Dict] = None, 
                    context_locals: Optional[Dict] = None) -> None:
        """
        添加命令到调度器
        :param command_str: 完整的命令字符串，包括时间和代码
        :param context_globals: 全局上下文
        :param context_locals: 局部上下文
        """
        # 获取上下文
        if context_globals is None or context_locals is None:
            frame = inspect.currentframe().f_back
            context_globals = context_globals or frame.f_globals
            context_locals = context_locals or frame.f_locals

        # 分离时间和代码
        lines = command_str.strip().split('\n')
        if not lines:
            raise ValueError("Empty command")

        # 解析时间
        execute_time, _ = TimeParser.parse(lines[0])
        
        # 处理代码部分
        code = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        if not code.strip():
            raise ValueError("Empty code")

        # 创建命令对象
        cmd = Command(code, context_globals, context_locals)
        
        # 添加到队列
        with self._lock:
            self._queue.put((execute_time, cmd))
            self._wakeup_event.set()

    def add_raw_command(self, raw_command: str) -> None:
        """
        直接从get_command()函数获取的原始命令添加到调度器
        :param raw_command: get_command()返回的原始命令字符串
        """
        # 获取当前上下文
        frame = inspect.currentframe().f_back
        context_globals = frame.f_globals
        context_locals = frame.f_locals
        
        self.add_command(raw_command, context_globals, context_locals)

    def _scheduler_loop(self):
        """调度器主循环"""
        while self._running:
            try:
                if self._queue.empty():
                    self._wakeup_event.wait(timeout=0.1)
                    continue
                
                with self._lock:
                    if self._queue.empty():
                        continue
                    next_time, cmd = self._queue.queue[0]
                    now = time.time()
                
                if next_time <= now:
                    self._queue.get()
                    self._executor.submit(self._execute_task, cmd)
                else:
                    wait_time = next_time - now
                    self._wakeup_event.wait(timeout=min(wait_time, 1))
                self._wakeup_event.clear()
                    
            except Exception as e:
                logging.error(f"Scheduler error: {e}")

    def _execute_task(self, cmd: Command):
        """执行任务"""
        try:
            cmd.execute()
        except Exception as e:
            logging.error(f"Task execution failed: {e}")

    def stop(self):
        """停止调度器"""
        self._running = False
        self._wakeup_event.set()
        self._executor.shutdown(wait=False)

    @property
    def pending_tasks(self):
        """返回待执行的任务数量"""
        return self._queue.qsize()