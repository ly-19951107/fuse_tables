# 1、python环境安装
推荐安装Anaconda，下载地址为https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-2020.11-Linux-x86_64.sh

下载完成后，拷贝至目标服务器，执行`sh Anaconda3-2020.11-Linux-x86_64.sh`命令安装，安装过程中所有配置保持默认即可。

安装完成后，执行`source ~/.bashrc`来使配置生效。


# 2、依赖包安装
所有需要的第三方依赖包列表在`requirements.txt`文件中，在有网环境中，直接执行`pip install -r requirements.txt`来进行安装。

如果目标服务器无法联网，那么按照以下方案进行安装：

将`requirements.txt`拷贝至一个与目标服务器版本相同的（包括操作系统版本与python版本）、可联网的服务器上（通常是虚拟机）；假设拷贝后文件的目录是`/home/requirements.
   txt`，则在`/home`目录下执行:
   ```shell
   pip wheel --wheel-dir=./wheels -r requirements.txt
   ```
然后将`wheels`文件夹拷贝至算法服务器上，假设在算法服务器上`wheels`文件夹的所在目录为`/home/wheels`，则在`/home`目录下执行：
```shell
pip install --no-index --find-links wheels -r requirements.txt
```
成功执行后，则环境安装完成。

# 3、启动服务
在代码的根目录下（假设为`/home/code/fuse-table`）执行：
正式运行时执行：
```shell
gunicorn -c gunicorn_cfg.py app:app
```
测试环境下执行`python run.py`,参数在`application.cfg`文件下修改