# encoding: utf-8

"""
扫描指定目录下的maven项目与webpack项目
判断是否有build编译文件(target/build/dist)

打印输出扫描结果：
    |  开发语言    |  项目类型  |  编译目录          | 占用空间  |
    | :-----     | :-----    | :-----            | :--:    |
    | java       | maven     | ./testPrj1/target | 100M    |
    | javascript | webpack   | ./testPrj2/build  | 1.2G    |

选择处理方式
    - 1. 输出报表
    - 2. 移动到指定目录（保留目录结构）
    - 3. 直接删除
"""
import os
import webbrowser
import shutil

# 忽略不检测的目录列表
ignore_dirs = ('web_inf', 'meta-inf', 'lib', 'node_modules', 'src')
# 需要检测的编译目录列表
compile_dirs = ('target', 'build', 'dist', 'output', 'outputs')
# 扫描结果存储列表
scan_list = []


def walk_dir(path):
    """
    递归读取判断目录

    :param path: 读取目录
    :return:
    """
    for d in os.listdir(path):
        if os.path.isdir(os.path.join(path, d)):
            check_dir(path, d)


def check_dir(root, dir):
    """
    检查是否为maven或webpack目录
        - 1. 过滤 . 号开始的目录
        - 2. 过滤要扫描的编译目录
        - 3. 过滤约定的依赖目录（WEB_INF/lib/node_modules）

    :param root: 父目录
    :param dir: 检测目录
    :return:
    """

    if dir.startswith('.'):
        # print('the path [{}] is in ignore list.'.format(dir))
        return False

    if dir.lower() in tuple(ignore_dirs):
        # print('the path [{}] is in ignore list.'.format(dir))
        return False

    if dir.lower() in tuple(compile_dirs):
        # 判断上层目录是否为maven项目
        if os.path.exists(os.path.join(root, 'pom.xml')):
            # print('the path [{}] is java maven compile dir.'.format(dir))
            scan_list.append(['java', 'maven', os.path.join(root, dir), get_file_size(os.path.join(root, dir))])
        elif os.path.exists(os.path.join(root, 'package.json')):
            # print('the path [{}] is javascript webpack compile dir.'.format(dir))
            # TODO: 进一步判断 vue/react/angular/native 项目
            scan_list.append(['javascript', 'webpack', os.path.join(root, dir), get_file_size(os.path.join(root, dir))])

    # 只有正常目录才继续扫描
    walk_dir(os.path.join(root, dir))


def get_file_size(file_path):
    """
    get size for file or folder

    :param file_path: 检测目录
    :return:
    """

    total_size = 0

    if not os.path.exists(file_path):
        return total_size

    if os.path.isfile(file_path):
        total_size = os.path.getsize(file_path)
        return total_size

    if os.path.isdir(file_path):
        with os.scandir(file_path) as dirEntryList:
            for curSubEntry in dirEntryList:
                cur_sub_entry_full_path = os.path.join(file_path, curSubEntry.name)
                if curSubEntry.is_dir():
                    cur_sub_folder_size = get_file_size(cur_sub_entry_full_path)
                    total_size += cur_sub_folder_size
                elif curSubEntry.is_file():
                    cur_sub_file_size = os.path.getsize(cur_sub_entry_full_path)
                    total_size += cur_sub_file_size

            return total_size


def readable_file_size(file_bytes, precision):
    """
    get size for file or folder

    :param file_bytes: 文件大小，单位：字节数bytes
    :param precision: 小数点后位数，可以是0
    :return:
    """

    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if abs(file_bytes) < 1024.0:
            return '%s %s' % (format(file_bytes, '.%df' % precision), unit)
        file_bytes /= 1024.0
    return '%s %s' % (format(file_bytes, '.%df' % precision), 'Yi')


def print_scan_list():
    """
    打印输出扫描结果列表

    :return:
    """

    total_size = 0
    for x in scan_list:
        total_size += x[3]
        print('\033[34m[\'{}\', \'{}\', \'{}\',\'{}\']'.format(x[0], x[1], x[2], readable_file_size(x[3], 2)))

    print('\033[0m')
    print('\033[34m*' * 80)
    print('\033[34m总占用空间：[{}]'.format(readable_file_size(total_size, 2)))
    print('\033[34m*' * 80)
    print('\033[0m')


def deal_compile_dirs(mode):
    """
    处理编译目录

    :param mode: 处理模式
    :return:
    """

    # 输出HTML报表文件
    if mode == '1':
        report_html()

    # 移动到指定目录
    elif mode == '2':
        print('移动到指定目录')
        move_scan_dirs()

    # 直接删除目录
    elif mode == '3':
        print('\033[31m安全起见，暂不提供，请用模式二移动自行后手动删除！\033[0m')


def report_html():
    """
    输出HTML报表

    :return:
    """

    # 命名生成的html
    gen_html = "扫描结果.html"
    # 打开文件，准备写入
    f = open(gen_html, 'w')

    # 准备相关变量
    total_size = 0
    table_list = ''

    for x in scan_list:
        total_size += x[3]
        x[3] = readable_file_size(x[3], 2)
        table_list += """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>\r\n
        """ % (x[0], x[1], x[2], x[3])

    html = """
    <html>
    <head>
        <meta charset="UTF-8"/>
        <title>扫描结果列表</title>
        <style>
            body {
                text-align: center
            }
        </style>
    </head>
    <body>
    <div>
        <p>扫描目录：[%s]</p>
        <table border="1" align="center">
            <tr>
                <th>语言</th>
                <th>类型</th>
                <th>目录</th>
                <th>大小</th>
            </tr>
            %s
        </table>
        <p>总占用空间：[%s]</p>
    </div>
    </body>
    </html>
    """ % (scan_dir, table_list, readable_file_size(total_size, 2))

    # 写入文件
    f.write(html)
    # 关闭文件
    f.close()

    # 运行完自动在网页中显示
    webbrowser.open(gen_html, new=1)

    print('\033[34m输出报表完成，请用浏览器打开报表文件：[{}]'.format(gen_html))


def move_scan_dirs():
    """
    移动编译目录列表到指定目录

    :return:
    """

    # 选择移动的备份目录
    dest_dir = input('请输入您需要移动的目标目录。[默认：./_recycle]\r\n') or './_recycle'

    if os.path.exists(dest_dir):
        confirm = input('执行操作后就不能撤回，确认要移动到[{}]目录吗？[Y/N]\r\n'.format(dest_dir))
        if confirm.upper() == 'Y':
            for x in scan_list:
                path_src = x[2]
                temp_path = path_src.replace(scan_dir, '')
                path_dest = os.path.join(dest_dir, temp_path)
                print(f'{temp_path} - > {path_dest}')
                shutil.move(path_src, path_dest)
        else:
            print('\033[31m用户取消操作\033[0m')
    else:
        print('\033[31m需要移动的目标目录不存在，请先手动创建！\033[0m')


if __name__ == '__main__':
    # 需要扫描的目录
    scan_dir = input('请输入要扫描的目录，默认为当前目录： \r\n') \
               or os.getcwd()

    if os.path.exists(scan_dir):
        # 每次扫描前清空结果
        scan_list = []

        print('\033[34m*' * 80)
        print('\033[34m开始检测目录：[{}]'.format(scan_dir))
        print('\033[34m*' * 80)
        print('\033[0m')

        if not scan_dir.endswith(os.sep):
            scan_dir += os.sep

        walk_dir(scan_dir)

        if scan_list:
            print_scan_list()

            # 选择处理方式
            err = 0
            deal_mode = input("请选择处理方式（输入数字，默认为1）：\r\n"
                              " 1) 输出报表(HTML)\r\n"
                              " 2) 移动到指定目录（保留目录结构） \r\n"
                              " 3) 直接删除（不可恢复，谨慎）\r\n") or '1'
            if deal_mode == '1':
                confirm = input('您选择的处理方式为：输出报表(HTML)，确认要执行吗？[Y/N]\r\n')
            elif deal_mode == '2':
                confirm = input('您选择的处理方式为：移动到指定目录（保留目录结构），确认要执行吗？[Y/N]\r\n')
            elif deal_mode == '3':
                confirm = input('您选择的处理方式为：直接删除，一旦执行后不可恢复，确认要执行吗？[Y/N]\r\n')
            else:
                err = 1
                print('\033[31m处理方法选择错误，不执行任何操作！\033[0m')

            # 如果不跳过就执行处理
            if err == 0 and confirm.upper() == 'Y':
                deal_compile_dirs(deal_mode)
            else:
                print('\033[31m用户取消操作\033[0m')
        else:
            print('\033[31m未发现任何编译目录\033[0m')

    else:
        print('\033[31m需要扫描的目录不存在，请确认是否输入正确！\033[0m')
