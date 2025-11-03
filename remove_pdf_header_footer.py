# Author: daizhonggeng
# Date: 2025-11-3
# Version: 1.0
# Email: daizhonggeng@gisinfo.com

import fitz  # PyMuPDF
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import io
import tkinter as tk


def preview_header_footer(file_path, top_margin, bottom_margin):
    doc = fitz.open(file_path)
    page_num = len(doc) // 2  # 取中间页预览，正常第一页不会有页眉页脚
    page = doc[page_num]

    # 修正上下边距
    rects = [
        fitz.Rect(0, 0, page.rect.width, top_margin),  # 上边距
        fitz.Rect(0, page.rect.height - bottom_margin, page.rect.width, page.rect.height)  # 下边距
    ]

    # 缩放渲染 100%
    scale = 1.0
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    img = pix.tobytes("ppm")
    image = Image.open(io.BytesIO(img)).convert("RGBA")

    # 创建透明覆盖层
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    for r in rects:
        draw.rectangle(
            [(r.x0 * scale, r.y0 * scale), (r.x1 * scale, r.y1 * scale)],
            fill=(255, 0, 0, 120)  # 红色半透明
        )

    # 合成图像
    image = Image.alpha_composite(image, overlay)

    # 显示在 Tkinter 窗口
    preview_win = tk.Toplevel()
    preview_win.title("页眉页脚预览")
    canvas = tk.Canvas(preview_win, width=image.width, height=image.height)
    canvas.pack()

    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo  # 防止被回收


# 用于删除页眉和页脚
def remove_header_footer(file_path, top_margin, bottom_margin):
    doc = fitz.open(file_path)
    for page in doc:
        # 上页眉
        if top_margin > 0:
            r_top = fitz.Rect(0, page.rect.height - top_margin, page.rect.width, page.rect.height)
            page.add_redact_annot(r_top, fill=(1, 1, 1))
        # 下页脚
        if bottom_margin > 0:
            r_bottom = fitz.Rect(0, 0, page.rect.width, bottom_margin)
            page.add_redact_annot(r_bottom, fill=(1, 1, 1))
        page.apply_redactions()
    output_path = file_path.replace(".pdf", "_rmhf.pdf")
    doc.save(output_path)
    doc.close()
    messagebox.showinfo("完成", f"页眉页脚已删除，输出文件：{output_path}")


# 浏览文件
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF 文件", "*.pdf")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)


# 启动预览功能
def start_preview():
    try:
        file_path = entry_file.get()
        top = float(entry_top.get())
        bottom = float(entry_bottom.get())
        preview_header_footer(file_path, top, bottom)
    except Exception as e:
        messagebox.showerror("错误", str(e))


# 启动删除功能
def start_remove():
    try:
        file_path = entry_file.get()
        top = float(entry_top.get())
        bottom = float(entry_bottom.get())
        remove_header_footer(file_path, top, bottom)
    except Exception as e:
        messagebox.showerror("错误", str(e))


# 创建GUI界面
root = tk.Tk()
root.title("PDF页眉页脚删除")

# 文件选择框
tk.Label(root, text="PDF 文件:").grid(row=0, column=0, padx=5, pady=5)
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="浏览", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

# 上边距输入框
tk.Label(root, text="上边距(pt):").grid(row=1, column=0, padx=5, pady=5)
entry_top = tk.Entry(root)
entry_top.insert(0, "75")
entry_top.grid(row=1, column=1, padx=5, pady=5)

# 下边距输入框
tk.Label(root, text="下边距(pt):").grid(row=2, column=0, padx=5, pady=5)
entry_bottom = tk.Entry(root)
entry_bottom.insert(0, "75")
entry_bottom.grid(row=2, column=1, padx=5, pady=5)

# 预览和删除按钮
tk.Button(root, text="预览", command=start_preview).grid(row=3, column=0, padx=5, pady=5)
tk.Button(root, text="删除页眉页脚", command=start_remove).grid(row=3, column=1, padx=5, pady=5)

root.mainloop()
