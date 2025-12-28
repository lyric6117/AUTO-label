@echo off
chcp 65001 >nul
echo ========================================
echo YOLO标注代理系统 - 打包脚本
echo ========================================
echo.

set PACKAGE_NAME=tf_infer_package
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

set PACKAGE_DIR=%PACKAGE_NAME%_%TIMESTAMP%

echo 正在打包项目...
echo 包名: %PACKAGE_DIR%
echo.

if exist %PACKAGE_DIR% rmdir /s /q %PACKAGE_DIR%
mkdir %PACKAGE_DIR%

echo [1/6] 复制核心代码...
xcopy /E /I /Y agent %PACKAGE_DIR%\agent >nul
xcopy /E /I /Y api %PACKAGE_DIR%\api >nul
xcopy /E /I /Y utils %PACKAGE_DIR%\utils >nul
xcopy /E /I /Y config %PACKAGE_DIR%\config >nul
xcopy /E /I /Y frontend %PACKAGE_DIR%\frontend >nul
echo ✓ 核心代码复制完成

echo [2/6] 复制配置和脚本...
copy /Y requirements.txt %PACKAGE_DIR%\ >nul
copy /Y README.md %PACKAGE_DIR%\ >nul
copy /Y run_api.py %PACKAGE_DIR%\ >nul
copy /Y run_batch_inference.py %PACKAGE_DIR%\ >nul
copy /Y deploy.bat %PACKAGE_DIR%\ >nul
copy /Y deploy.sh %PACKAGE_DIR%\ >nul
echo ✓ 配置和脚本复制完成

echo [3/6] 创建目录结构...
mkdir %PACKAGE_DIR%\data
mkdir %PACKAGE_DIR%\data\temp
mkdir %PACKAGE_DIR%\logs
mkdir %PACKAGE_DIR%\models
mkdir %PACKAGE_DIR%\dataset
mkdir %PACKAGE_DIR%\dataset\v0_seed
mkdir %PACKAGE_DIR%\dataset\v0_seed\images
mkdir %PACKAGE_DIR%\dataset\v0_seed\labels
echo ✓ 目录结构创建完成

echo [4/6] 创建说明文件...
(
echo YOLO标注代理系统 - 部署包
echo.
echo 部署步骤:
echo 1. 解压此压缩包到目标服务器
echo 2. Windows: 双击运行 deploy.bat
echo 3. Linux/Mac: 运行 bash deploy.sh
echo 4. 将训练好的模型文件放入 models\best.pt
echo 5. 将测试数据放入 dataset\v0_seed\images\ 和 dataset\v0_seed\labels\
echo 6. 运行 python run_batch_inference.py 进行批量推理
echo 7. 运行 python run_api.py 启动API服务器
echo 8. 在浏览器中打开 frontend\index.html 使用Web界面
echo.
echo 注意事项:
echo - 需要Python 3.8+环境
echo - 首次运行会自动安装依赖
echo - 模型文件需要单独准备
echo - 数据集需要单独准备
) > %PACKAGE_DIR%\DEPLOY.txt
echo ✓ 说明文件创建完成

echo [5/6] 创建压缩包...
if exist %PACKAGE_DIR%.zip del %PACKAGE_DIR%.zip
powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%' -DestinationPath '%PACKAGE_DIR%.zip' -Force"
if %errorlevel% neq 0 (
    echo 错误: 压缩失败
    rmdir /s /q %PACKAGE_DIR%
    pause
    exit /b 1
)
echo ✓ 压缩包创建完成

echo [6/6] 清理临时文件...
rmdir /s /q %PACKAGE_DIR%
echo ✓ 临时文件清理完成

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 压缩包位置: %PACKAGE_DIR%.zip
echo 文件大小:
dir %PACKAGE_DIR%.zip | findstr %PACKAGE_DIR%.zip
echo.
echo 请将压缩包传输到目标服务器后解压部署
echo.
pause
