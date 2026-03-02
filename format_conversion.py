import fitz #  pip pymupdf==1.21.0
import pdfkit
import os
import shutil
from imageio import imread, imsave
# from skimage import io


def corp_margin(img0):
    img = imread(img0)
    img2 = img.sum(axis=2)
    (row, col) = img2.shape
    raw_down = 0

    for r in range(row - 1, 0, -1):
        if img2.sum(axis=1)[r] < 750 * col:
            raw_down = r
            break

    new_img = img[0:raw_down + 1, 0:col, :]
    imsave(img0, new_img)


def pdf2png(pdf_path, filename='song-list'):
    zoom = 1.8
    rotate = 0
    # 打开PDF文件
    pdf = fitz.open(pdf_path)
    # 逐页读取PDF
    for pg in range(pdf.page_count):
        page = pdf[pg]
        # 设置缩放和旋转系数
        trans = fitz.Matrix(zoom, zoom).prerotate(rotate)
        pm = page.get_pixmap(matrix=trans, alpha=False)
        # 开始写图像
        if pdf.page_count == 1:
            pm.save(filename + ".png")
        else:
            pm.save(filename + str(pg) + ".png")
    pdf.close()


def path2abspath(path_css):
    # 生成包含绝对路径的CSS文件
    infile = open(path_css, "r", encoding='utf-8')  # 打开文件
    path_css0 = path_css.replace(".css", "_rep.css")
    outfile = open(path_css0, "w", encoding='utf-8')  # 内容输出
    for line in infile:  # 按行读文件，可避免文件过大，内存消耗
        outfile.write(line.replace('../css/', "C:/Users/Public/Documents/"))
    infile.close()  # 文件关闭
    outfile.close()
    return path_css0


def html2pdf(path_html, path_css, path_bg, path_wk, height='247.5', width='175', filename='song-list'):
    path_repcss = path2abspath(path_css)
    # 为了避免中文路径，将背景图片放置到用户文件夹中
    index = path_bg.rfind('\\')
    bgname = path_bg[index + 1:]
    shutil.copy(path_bg, "C:\\Users\\Public\\Documents\\" + bgname)

    config = pdfkit.configuration(wkhtmltopdf=path_wk)
    options = {
        'page-height': height,
        'page-width': width,
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-bottom': '0in',
        'margin-left': '0in',
        'image-quality': '300',
        'zoom': 1.43,
        'encoding': "UTF-8",
        'enable-local-file-access': None
    }

    pdfkit.from_file(path_html, filename + '.pdf', css=path_repcss, options=options, configuration=config)

    # 删除复制的背景图片
    os.remove("C:\\Users\\Public\\Documents\\" + bgname)


if __name__ == '__main__':
    # path_html = ".\\song-list.html"
    # path_wk = ".//wkhtmltopdf//bin//wkhtmltopdf.exe"
    #
    # # path_css = ".\\css\\wuqu.css"
    # # path_bg = ".\\css\\background.jpg"
    # # html2pdf(path_html, path_css, path_bg, path_wk)
    # # pdf2png('./song-list.pdf')
    # #
    # path_css_phone = ".\\css\\wuqu_phone.css"
    # path_hbdc = ".\\css\\HBDC.png"
    # path_html_phone = '.\\song-list-phone.html'
    # html2pdf(path_html_phone, path_css_phone, path_hbdc, path_wk, width='103', height='700', filename='song-list-phone')
    # pdf2png('./song-list-phone.pdf', filename='song-list-phone')
    #
    # corp_margin('./song-list-phone.png')

    corp_margin('D:\Guokr\Docement\wuqu\Code\Music\song-list.png')