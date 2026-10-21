import os
import folder_paths

class NumberingFolderCreater:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "prefix": ("STRING",{
                    "default": "",
                    "tooltip": "创建文件名时，加在序号前的文件夹前缀"
                }),
                "suffix": ("STRING",{
                    "default": "",
                    "tooltip": "创建文件名时，加在序号前的文件夹后缀"
                }),
                "step": ("INT",{
                    "default": 1,
                    "tooltip": "序号递增的步长"
                }),
                "width": ("INT",{
                    "default": 4,
                    "tooltip": "序号宽度（请设置尽量大，否则检测可能会有问题）"
                })
            }
        }

    RETURN_TYPES = ("STRING","INT")
    RETURN_NAMES = ("文件夹路径","当前文件夹序号")
    OUTPUT_TOOLTIPS = ("该文件夹在 ComfyUI 的默认输出文件夹中", "当前文件夹在同前后缀文件夹中的实际序号")
    CATEGORY = "File Operation/"
    FUNCTION = "execute"

    def execute(self, prefix, suffix, step, width):
        outDir = folder_paths.get_output_directory()
        names = os.listdir(outDir)

        folders = []
        for name in names:
            fullPath = outDir + name
            if os.path.isdir(fullPath):
                folders.append(name)

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

            if not folderName[len(prefix),len(prefix)+width].isdigit():
                continue

            maxNum = max(maxNum,int(folderName[len(prefix),len(prefix)+width]))

        newFolderName = prefix + str(maxNum + 1) + suffix

        os.mkdir(outDir + newFolderName)

        return (newFolderName, maxNum,)

NODE_CLASS_MAPPINGS = {"NumberingFolderCreater": NumberingFolderCreater}
NODE_DISPLAY_NAME_MAPPINGS = {"NumberingFolderCreater": "序号文件夹生成器"}