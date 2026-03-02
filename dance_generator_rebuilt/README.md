# Dance Generator Rebuilt

这是对旧版“舞曲列表生成器”的一次重构式重建，目标是保留原有核心工作流，同时把项目拆成更清晰的模块，并改成一个本地网页应用：

- `domain`：数据模型
- `services`：扫描、规则检查、导出、文件保存
- `web`：Starlette Web 入口
- `web_static`：单页前端资源

当前版本已覆盖的核心能力：

- 扫描目录并解析舞曲信息
- 网页表格编辑与拖拽重排
- 分场管理
- 规则检查
- 导出 `txt/html/pdf/png`
- 按当前顺序重命名并复制/移动舞曲文件

当前未迁移的扩展能力：

- 百度网盘上传
- 展示舞曲大屏
- 在线更新逻辑

## 运行

```bash
python -m dance_generator_rebuilt.web
```

也可以直接使用仓库根目录的一键启动脚本：

```bash
./run_web.sh
```

Windows:

```bat
run_web.bat
```

## 直接打开 HTML

如果你不想启动本地服务，也可以直接双击这个单文件版本：

`dance_generator_rebuilt/standalone.html`

它支持：

- 本地目录导入音频文件
- 排曲、分场、规则检查
- 音频预览
- 导出 TXT 和 HTML

它不支持浏览器直接批量重命名/复制本地文件，这是浏览器权限模型限制。

## 上线到网上

当前最适合上线的是静态单文件版本：

- 线上入口：[index.html](/Volumes/Extreme%20SSD/Ai/songlist_gen2%203/index.html)
- 实际页面：[standalone.html](/Volumes/Extreme%20SSD/Ai/songlist_gen2%203/dance_generator_rebuilt/standalone.html)

已经附带部署配置：

- Vercel: [vercel.json](/Volumes/Extreme%20SSD/Ai/songlist_gen2%203/vercel.json)
- Netlify: [netlify.toml](/Volumes/Extreme%20SSD/Ai/songlist_gen2%203/netlify.toml)
- GitHub Pages: [.github/workflows/deploy-static.yml](/Volumes/Extreme%20SSD/Ai/songlist_gen2%203/.github/workflows/deploy-static.yml)

可选上线方式：

1. GitHub Pages
   把仓库推到 GitHub，启用 Pages，并允许 Actions 部署。
2. Vercel
   导入这个仓库，框架选择 `Other`，无需构建命令。
3. Netlify
   导入这个仓库，发布目录填 `.`。

限制说明：

- 这是纯前端静态站点，不能在用户机器上直接批量重命名或复制本地文件。
- 浏览器对本地目录读取依赖用户手动选择文件夹，属于预期限制。

## 目录结构

```text
dance_generator_rebuilt/
  README.md
  assets.py
  web.py
  domain/
  services/
  web_static/
```
