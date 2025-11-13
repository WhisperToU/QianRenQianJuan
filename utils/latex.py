import os
import re
import shutil
import subprocess
import tempfile
from docx import Document


def _copy_images_to_temp(latex_str, temp_dir):
    """
    扫描 LaTeX 代码中的 \includegraphics 并复制相关图片到临时目录。
    自动修正为 Pandoc 可识别的相对路径。
    """
    img_pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    matches = img_pattern.findall(latex_str)
    project_root = os.path.dirname(os.path.abspath(__file__))  # 当前 utils 所在路径
    project_root = os.path.abspath(os.path.join(project_root, ".."))  # 提升一层，指向项目根目录

    for img_path in matches:
        abs_path = os.path.join(project_root, img_path)
        if os.path.exists(abs_path):
            shutil.copy(abs_path, os.path.join(temp_dir, os.path.basename(img_path)))
            latex_str = latex_str.replace(img_path, os.path.basename(img_path))
        else:
            print(f"[警告] 未找到图片文件：{abs_path}")
    return latex_str


def latex_to_docx_file(latex_str):
    """
    将 LaTeX 文本（含图片）转换为完整 DOCX 文件，返回生成路径。
    """
    temp_dir = tempfile.mkdtemp()
    tex_file = os.path.join(temp_dir, "temp.tex")
    docx_file = os.path.join(temp_dir, "output.docx")

    # 自动添加文档头
    preamble = r"""
    \documentclass{article}
    \usepackage{amsmath, amssymb, graphicx}
    \usepackage{ctex}
    \begin{document}
    """
    ending = r"\end{document}"

    # 防止双重包裹
    if "\\begin{document}" in latex_str:
        tex_content = latex_str
    else:
        tex_content = preamble + latex_str + ending

    # 拷贝图片
    tex_content = _copy_images_to_temp(tex_content, temp_dir)

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    # 运行 Pandoc
    try:
        # 在临时目录运行 Pandoc（图片路径可解析）
        subprocess.run(
            ["pandoc", "temp.tex", "-s", "-o", "output.docx"],
            cwd=temp_dir,
            check=True
        )

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc 转换失败: {e}")

    return docx_file


def latex_to_docx_paragraph(latex_str):
    """
    向后兼容接口（返回段落列表）
    """
    try:
        docx_path = latex_to_docx_file(latex_str)
        doc = Document(docx_path)
        return doc.paragraphs
    except Exception as e:
        print("LaTeX 转换段落失败:", e)
        return []
