**Safe Password已上线，将会稍后更新文档，尽情体验！**


**全新实用工具！**

- Plus Photo Downloader:
- 这个是一个自动程序，可以帮助你下载谱时云上照片直播的图片，他是全自动且非交互式的，你只需要把照片直播的链接放进变量TARGET_URL然后运行他就可以了
- 运行环境：
- 1.注意需要selenium webdriver作为模拟网页浏览的根基
- 2.你还需要安装requests和tqdm（进度条）库
- 特性：
- 1.这个程序完全使用浏览器UI访问图库，而不是API访问，已解决每点击一个图片的密钥（比如sign=）不同而导致403 Forbidden（check sign failed）问题
- 2.由于这个程序使用浏览器UI，受制于略缩图加载速度和界面动画速度，所以获取原图链接的速度可能较慢，可以通过进度条查看剩余时间
- 3.这个程序的原理是先获取整个图库的原图链接，然后统一下载他们，所以在获取完所有链接之前不会下载任何图片
- 4.下载好的文件将保存在downloaded_images文件夹，暂时使用获取的顺序作为文件名

## New Practical Tool!

### Plus Photo Downloader

This is an automated program that helps you download images from a photo gallery during a live broadcast on the cloud. It is fully automated and non-interactive. You simply need to input the photo gallery link into the `TARGET_URL` variable, and the program will run on its own.

#### Environment Setup:
1. **Selenium WebDriver**: Required as the foundation for simulating web browsing.
2. **Python Libraries**:
   - `requests`
   - `tqdm` (for progress bar)

#### Features:
1. **Browser UI Access**: This program accesses the photo gallery through the browser's UI rather than using the API, solving the issue of the constantly changing `sign=` key (which leads to 403 Forbidden errors).
2. **Speed Limitation**: Since the program uses the browser UI, the speed of fetching original image links may be slower due to thumbnail loading times and interface animations. You can monitor the remaining time with a progress bar.
3. **Image Download Process**: The program first retrieves all the original image links before starting the download. No images are downloaded until all links have been gathered.
4. **Downloaded Files**: The images are saved in the `downloaded_images` folder, with filenames based on the order in which they were retrieved.
