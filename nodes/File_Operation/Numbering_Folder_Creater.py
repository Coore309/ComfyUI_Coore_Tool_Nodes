import os
import folder_paths
import logging

log = logging.getLogger(__name__)

class NumberingFolderCreater:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prefix": ("STRING",{
                    "default": "",
                    "tooltip": "创建文件名时，加在序号前的文件夹前缀"
                }),
                "suffix": ("STRING",{
                    "default": "",
                    "tooltip": "创建文件名时，加在序号前的文件夹后缀"
                }),
                "basic_path": (["ComfyUI 输出文件夹","None"], {
                    "default": "ComfyUI 输出文件夹",
                    "tooltip": "基本路径，若为 None ，则必须在 path 中输入绝对路径"
                }),
                "path": ("STRING", {
                    "default": "",
                    "tooltip": "文件夹所在路径，若 basic_path 为 None ，则必须在此输入绝对路径"
                }),
                "step": ("INT",{
                    "default": 1,
                    "step": 1,
                    "tooltip": "序号递增的步长"
                }),
                "width": ("INT",{
                    "default": 4,
                    "tooltip": "序号宽度（请设置尽量大出需求量，否则检测可能会有问题）",
                    "min": 1,
                    "step": 1
                })
            },
            "optional": {
                "trigger": ("*", {
                    "forceInput": True,
                    "tooltip": "前驱输入接口，只有在前驱数据返回内容时，才会运行本节点。本节点不储存、不处理前驱数据"
                    }),
            }
        }

    RETURN_TYPES = ("STRING","INT")
    RETURN_NAMES = ("文件夹路径","当前文件夹序号")
    OUTPUT_TOOLTIPS = ("该文件夹在 ComfyUI 的默认输出文件夹中", "当前文件夹在同前后缀文件夹中的实际序号")
    CATEGORY = "Coore Tool Nodes/File Operation/"
    FUNCTION = "execute"

    @classmethod
    def IS_CHANGED(cls, prefix, suffix, basic_path, path, step, width, trigger):
        return float("nan")

    def execute(self, prefix, suffix, basic_path, path, step, width, trigger):
        mapPath = {
            "ComfyUI 输出文件夹": "output",
            "None": "none"
        }

        # path 预处理
        path = path.strip()
        path = path.replace("\\", "/")

        outDir = str()
        if (mapPath.get(basic_path) == "output"):
            outDir = os.path.join(folder_paths.get_output_directory(), path).replace("\\", "/")
        else:
            outDir = path

        try:
            os.makedirs(outDir, exist_ok = True)
        except Exception as e:
            raise ValueError(f"无法解析路径 {outDir}")
        
        log.info(f"当前输出文件夹为：{outDir}")
        log.info("开始扫描输出文件夹……")
        names = os.listdir(outDir)

        folders = []
        for name in names:
            fullPath = os.path.join(outDir, name).replace("\\", "/")
            if os.path.isdir(fullPath):
                folders.append(name)

        # 文件夹名检测
        maxNum = 0
        for folderName in folders:
            i = 0
            while i < len(folderName) and i < len(prefix) and folderName[i] == prefix[i]:
                i += 1

            if i != len(prefix):
                continue

            i += width
            while i < len(folderName) and i < len(suffix) and folderName[i] == suffix[i - len(prefix) - width]:
                i += 1

            if i != len(prefix) + width + len(suffix) and i != len(folderName):
                continue

            if not folderName[len(prefix):len(prefix)+width].isdigit():
                continue

            maxNum = max(maxNum,int(folderName[len(prefix):len(prefix)+width]))
        log.info(f"扫描完成！当前最大序号为 {maxNum}")

        # 拼接名字，创建文件夹
        newFolderName = prefix + str(maxNum + step).zfill(width) + suffix

        targetDir = os.path.join(outDir, newFolderName).replace("\\", "/")
        os.makedirs(targetDir, exist_ok = True)
        log.info(f"创建文件夹 {newFolderName} 于 {targetDir}")

        return (targetDir, maxNum,)

NODE_CLASS_MAPPINGS = {"NumberingFolderCreater": NumberingFolderCreater}
NODE_DISPLAY_NAME_MAPPINGS = {"NumberingFolderCreater": "序号文件夹生成器"}