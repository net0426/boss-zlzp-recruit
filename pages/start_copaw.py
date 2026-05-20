import subprocess
import os
import sys
import time
import psutil
# 全局进程（只保存PID，不保存句柄，彻底避免句柄无效错误）
ai_pid = None

class LocalAIHeadlessRunner:
    def __init__(self):
        # 你的配置不变
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(project_root)
        from config.config import AI_CONFIG

        self.SERVER_PATH = AI_CONFIG['SERVER_PATH']
        self.MODEL_PATH = AI_CONFIG['MODEL_PATH']
        self.PORT = str(AI_CONFIG['PORT'])
        self.CTX_SIZE = str(AI_CONFIG['CTX_SIZE'])
        self.BATCH_SIZE = str(AI_CONFIG['BATCH_SIZE'])

    def start_ai(self):
        global ai_pid
        # 路径检查
        if not os.path.exists(self.SERVER_PATH):
            print(f"❌ 找不到 llama-server.exe")
            return
        if not os.path.exists(self.MODEL_PATH):
            print(f"❌ 找不到模型文件")
            return

        cmd = [
            self.SERVER_PATH,
            "--model", self.MODEL_PATH,
            "--port", str(self.PORT),
            "--ctx-size", str(self.CTX_SIZE),
            "--batch-size", self.BATCH_SIZE,
            "--host", "127.0.0.1"
        ]

        try:
            # ✅ 隐藏窗口启动
            proc = subprocess.Popen(
                cmd,
                creationflags=0x08000000,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            ai_pid = proc.pid
            print(f"✅ AI 后台启动成功，进程ID：{ai_pid}")
        except Exception as e:
            print(f"❌ 启动失败：{e}")


def stop_ai():
    """✅ 最稳定关闭方式：只杀进程，不碰句柄，永远不报错"""
    global ai_pid
    try:
        # Windows 强制关闭 llama-server，无任何句柄操作
        subprocess.run(
            ["taskkill", "/F", "/IM", "llama-server.exe"],
            creationflags=0x08000000,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        ai_pid = None
        print("✅ AI 已安全关闭")
    except:
        print("✅ 无运行中的AI服务")


if __name__ == "__main__":
    app = LocalAIHeadlessRunner()
    app.start_ai()
    time.sleep(30)
    stop_ai()