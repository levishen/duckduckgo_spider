### Linux 前置环境设置
1. 安装chrome
yum install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

2. 安装依赖库
yum install mesa-libOSMesa-devel gnu-free-sans-fonts wqy-zenhei-fonts

3. 安装 chromedriver
- 从这个里面下载和chrome版本一致的驱动：
https://registry.npmmirror.com/binary.html?path=chromedriver/

- 将下载的文件解压
unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/
- 给予执行权限
chmod +x /usr/bin/chromedriver
