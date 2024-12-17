# scheduler.py
import threading
import time
from datetime import datetime
from queue import PriorityQueue
from concurrent.futures import ThreadPoolExecutor
import logging
import inspect

class Scheduler:
    def __init__(self):
        self._queue = PriorityQueue()
        self._running = True
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._wakeup_event = threading.Event()
        
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
    
    def add(self, delay_seconds, cmd_str, context_globals=None, context_locals=None):
        """
        添加任务到调度器
        :param delay_seconds: 延迟秒数
        :param cmd_str: 命令字符串或者可调用对象
        :param context_globals: 全局上下文
        :param context_locals: 局部上下文
        """
        # 如果没有提供上下文，尝试从调用栈获取
        if context_globals is None or context_locals is None:
            # 获取调用者的帧
            frame = inspect.currentframe().f_back
            context_globals = context_globals or frame.f_globals
            context_locals = context_locals or frame.f_locals

        # 计算执行时间
        execute_time = time.time() + delay_seconds
            
        # 将命令和上下文打包
        task = (cmd_str, context_globals, context_locals)
        self._queue.put((execute_time, task))
        
        try:
            if execute_time < self._queue.queue[0][0]:
                self._wakeup_event.set()
        except:
            self._wakeup_event.set()
    
    def add_at_time(self, hour, minute, second, cmd_str, context_globals=None, context_locals=None):
        """在指定时间执行任务"""
        if context_globals is None or context_locals is None:
            frame = inspect.currentframe().f_back
            context_globals = context_globals or frame.f_globals
            context_locals = context_locals or frame.f_locals
            
        now = datetime.now()
        execute_time = now.replace(hour=hour, minute=minute, second=second).timestamp()
        if execute_time <= time.time():
            execute_time += 24 * 3600
            
        task = (cmd_str, context_globals, context_locals)
        self._queue.put((execute_time, task))
        
        try:
            if execute_time < self._queue.queue[0][0]:
                self._wakeup_event.set()
        except:
            self._wakeup_event.set()
    
    def _scheduler_loop(self):
        """调度器循环"""
        while self._running:
            try:
                if self._queue.empty():
                    self._wakeup_event.wait(timeout=0.1)
                    continue
                
                next_time, task = self._queue.queue[0]
                now = time.time()
                
                if next_time <= now:
                    self._queue.get()
                    self._executor.submit(self._execute_task, task)
                    self._wakeup_event.clear()
                else:
                    wait_time = next_time - now
                    self._wakeup_event.wait(timeout=min(wait_time, 1))
                    self._wakeup_event.clear()
                    
            except Exception as e:
                logging.error(f"Scheduler error: {e}")
    
    def _execute_task(self, task):
        """在线程池中执行任务"""
        try:
            cmd_str, globals_dict, locals_dict = task
            if callable(cmd_str):
                cmd_str()
            else:
                exec(cmd_str, globals_dict, locals_dict)
        except Exception as e:
            logging.error(f"Task execution failed: {e}")
    
    def stop(self):
        """停止调度器"""
        self._running = False
        self._wakeup_event.set()
        self._executor.shutdown(wait=False)