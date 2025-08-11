import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import datetime

# --- 1. 数据处理和HTML表格生成部分 ---

def get_report_data():
    """
    模拟获取报告数据。在实际应用中，这会从数据库、API或其他数据源获取。
    """
    # 示例数据
    data_section1 = {
        'Project': ['pro_A', 'pro_B', 'pro_C', 'pro_D', 'summary'],
        'Compile_all': [0, 0, 0, 2, 2],
        'CodeCheck_total': [0, 2, 1, '-', 6],
        'Echecker_new': [0, 3, 0, '-', 5],
        'BuildMC_build': [0, 2, 1, 0, 6],
        'BuildMC_compile': [0, 3, 2, 6, 11],
        'fossbot_new': [0, 0, 0, 1, 1],
        'BepCloud_difference': [0, 1, 2, 4, 7],
        'UADP_SAL': [130, 45, 4, 20, 74],
        '车规_total': [0, 23, 4, 4, 33],
        'SensitiveInfo_total': [0, 4, 2, 4, 15],
        'CppCheck_total': [0, 5, 3, 0, 9],
        'Owner': ['杜满沛', '张瑞卿', '张瑞卿', '陶艺', '杜满沛']
    }
    df_section1 = pd.DataFrame(data_section1)

    data_section2 = {
        'Module': ['Module A', 'Module B', 'Module C'],
        'Errors': [5, 2, 0],
        'Warnings': [10, 3, 1],
        'PassRate': ['95%', '98%', '100%']
    }
    df_section2 = pd.DataFrame(data_section2)

    data_section3 = {
        'Test Suite': ['Unit Tests', 'Integration Tests', 'Performance Tests'],
        'Passed': [120, 80, 15],
        'Failed': [5, 2, 1],
        'Skipped': [3, 1, 0]
    }
    df_section3 = pd.DataFrame(data_section3)

    data_section4 = {
        'Issue Type': ['Bug', 'Feature', 'Refactor'],
        'Open': [15, 8, 3],
        'Closed': [20, 10, 5]
    }
    df_section4 = pd.DataFrame(data_section4)


    report_data = {
        "report_title": "底软CI平台版本集成每日报告",
        "project_name": "CloudDragon",
        "build_date": datetime.date.today().strftime('%Y-%m-%d'), # 动态生成日期
        "sections": {
            "Section1": {
                "title": "Section1 - 编译和检查结果",
                "data": df_section1,
                "highlight_columns": [
                    'Compile_all', 'CodeCheck_total', 'Echecker_new',
                    'BuildMC_build', 'BuildMC_compile', 'fossbot_new',
                    'BepCloud_difference', 'UADP_SAL', '车规_total',
                    'SensitiveInfo_total', 'CppCheck_total'
                ],
                "summary_row_index": df_section1[df_section1['Project'] == 'summary'].index[0] if 'summary' in df_section1['Project'].values else -1 # 假设summary行需要特殊高亮
            },
            "Section2": {
                "title": "Section2 - 模块质量概览",
                "data": df_section2,
                "highlight_columns": ['Errors', 'Warnings'],
                "summary_row_index": -1
            },
            "Section3": {
                "title": "Section3 - 测试报告",
                "data": df_section3,
                "highlight_columns": ['Failed'],
                "summary_row_index": -1
            },
            "Section4": {
                "title": "Section4 - 问题跟踪",
                "data": df_section4,
                "highlight_columns": ['Open'],
                "summary_row_index": -1
            },
        }
    }
    return report_data

def generate_report_css():
    """
    生成报告所需的内联CSS样式。
    """
    css = """
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f8f8f8; padding: 20px; }
        .container {margin: 0 auto; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 0 15px rgba(0, 0, 0, 0.1); border: 1px solid #e0e0e0; }
        h1, h2, h3 { color: #2c3e50; text-align: center; }
        p { margin-bottom: 15px; }
        .header-table, .navigation-table, .report-section-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        .header-table th, .header-table td,
        .navigation-table th, .navigation-table td,
        .report-section-table th, .report-section-table td {
            border: 1px solid #c0c0c0; /* 浅灰色边框 */
            padding: 10px 15px;
            text-align: left;
        }

        /* 顶部信息表格样式 */
        .header-table th { background-color: #34495e; color: white; text-align: center; font-weight: bold; }
        .header-table td { background-color: #ecf0f1; color: #333; }
        .header-table td.label { font-weight: bold; width: 150px; }

        /* 导航条样式 */
        .navigation-table th { background-color: #2980b9; color: white; text-align: center; font-weight: bold; padding: 12px; }
        .navigation-table td { background-color: #3498db; text-align: center; }
        .navigation-table td a { color: white; text-decoration: none; display: block; padding: 8px 0; }
        .navigation-table td a:hover { background-color: #2c3e50; }

        /* Section 标题样式 */
        .section-title {
            background-color: #3498db; /* 蓝色 */
            color: white;
            padding: 10px 15px;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }

        /* 主要报告表格样式 */
        .report-section-table thead th {
            background-color: #2c3e50; /* 深蓝色 */
            color: white;
            font-weight: bold;
            text-align: center;
            vertical-align: middle;
        }
        .report-section-table thead th.sub-header {
            background-color: #34495e; /* 稍浅的深蓝色 */
            font-weight: normal;
        }
        .report-section-table tbody tr:nth-child(even) { background-color: #f2f2f2; }
        .report-section-table tbody tr:hover { background-color: #e0e0e0; }

        /* 单元格高亮样式 */
        .highlight-data {
            background-color: #ffe0b2; /* 浅橙色背景 */
            color: #d35400; /* 深橙色文本 */
            font-weight: bold;
        }
        /* Summary 行高亮 */
        .summary-row {
            background-color: #fffacd !important; /* 浅黄色背景 */
            font-weight: bold;
        }
        /* 针对 Section1 的特殊高亮 */
        .section1-highlight-data {
            background-color: #ffccbc; /* 浅红色背景 */
            color: #c0392b; /* 深红色文本 */
            font-weight: bold;
        }
        /* 如果数据为0，可以有另一个样式 */
        .data-zero {
            color: #7f8c8d; /* 灰色 */
        }
    </style>
    """
    return css

def generate_top_info_html(report_data):
    """生成顶部项目名称和构建日期信息表格"""
    html = f"""
    <table class="header-table">
        <thead>
            <tr>
                <th colspan="2">{report_data['report_title']}</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="label">ProjectName</td>
                <td>{report_data['project_name']}</td>
            </tr>
            <tr>
                <td class="label">BuildDate</td>
                <td>{report_data['build_date']}</td>
            </tr>
        </tbody>
    </table>
    """
    return html

def generate_navigation_html(sections):
    """生成导航条表格"""
    nav_links = ""
    for section_id, section_info in sections.items():
        nav_links += f'<td><a href="#{section_id}">{section_info["title"].split(" - ")[0]}</a></td>' # 只显示 SectionX
    html = f"""
    <table class="navigation-table">
        <thead>
            <tr>
                <th colspan="{len(sections)}">Navigation</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                {nav_links}
            </tr>
        </tbody>
    </table>
    """
    return html

def generate_section_html(section_id, section_info):
    """
    生成单个Section的HTML表格。
    根据section_id判断是否是Section1，进行特殊处理。
    """
    df = section_info['data']
    highlight_cols = section_info['highlight_columns']
    summary_row_idx = section_info.get('summary_row_index', -1)

    html_table = f'<div id="{section_id}" class="section-title">{section_info["title"]}</div>'
    html_table += '<table class="report-section-table">'

    # --- 表头处理 ---
    if section_id == "Section1":
        # Section1 的复杂两层表头
        html_table += """
        <thead>
            <tr>
                <th rowspan="2">Project</th>
                <th colspan="1">Compile</th>
                <th colspan="1">CodeCheck</th>
                <th colspan="1">Echecker</th>
                <th colspan="2">BuildMC</th>
                <th colspan="1">fossbot</th>
                <th colspan="1">BepCLoud</th>
                <th colspan="1">UADP</th>
                <th colspan="1">车规</th>
                <th colspan="1">SensitiveInfo</th>
                <th colspan="1">CppCheck</th>
                <th rowspan="2">Owner</th>
            </tr>
            <tr>
                <th class="sub-header">all</th>
                <th class="sub-header">total</th>
                <th class="sub-header">new</th>
                <th class="sub-header">build</th>
                <th class="sub-header">compile</th>
                <th class="sub-header">new</th>
                <th class="sub-header">difference</th>
                <th class="sub-header">SAL</th>
                <th class="sub-header">total</th>
                <th class="sub-header">total</th>
                <th class="sub-header">total</th>
            </tr>
        </thead>
        <tbody>
        """
    else:
        # 其他Section的简单表头
        html_table += '<thead><tr>'
        for col in df.columns:
            html_table += f'<th>{col}</th>'
        html_table += '</tr></thead><tbody>'

    # --- 表格数据行处理 ---
    for r_idx, row in df.iterrows():
        row_class = "summary-row" if r_idx == summary_row_idx else ""
        html_table += f'<tr class="{row_class}">'
        for col_name, cell_value in row.items():
            cell_class = ""
            # 检查是否需要高亮
            if col_name in highlight_cols:
                # 针对Section1，如果数据是数字且非0，或者是非数字但有值
                if section_id == "Section1":
                    try:
                        num_val = int(cell_value)
                        if num_val > 0:
                            cell_class = "section1-highlight-data"
                        elif num_val == 0:
                            cell_class = "data-zero"
                    except ValueError: # 处理 '-' 等非数字情况
                        if cell_value != '-' and pd.notna(cell_value) and str(cell_value).strip() != '':
                            cell_class = "section1-highlight-data"
                else: # 其他Section的通用高亮
                    try:
                        num_val = int(cell_value)
                        if num_val > 0:
                            cell_class = "highlight-data"
                        elif num_val == 0:
                            cell_class = "data-zero"
                    except ValueError:
                         if cell_value != '-' and pd.notna(cell_value) and str(cell_value).strip() != '':
                            cell_class = "highlight-data"

            html_table += f'<td class="{cell_class}">{cell_value}</td>'
        html_table += '</tr>'
    html_table += '</tbody></table>'
    return html_table

def generate_full_report_html(report_data):
    """
    生成完整的HTML报告内容，包括CSS、顶部信息、导航和所有Section表格。
    """
    css_content = generate_report_css()
    top_info_html = generate_top_info_html(report_data)
    navigation_html = generate_navigation_html(report_data['sections'])

    sections_html = ""
    for section_id, section_info in report_data['sections'].items():
        sections_html += generate_section_html(section_id, section_info)

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{report_data['report_title']}</title>
        {css_content}
    </head>
    <body>
        <div class="container">
            {top_info_html}
            {navigation_html}
            {sections_html}
            <p style="text-align: center; margin-top: 30px; font-size: 12px; color: #777;">
                此邮件由自动化系统发送，请勿直接回复。<br/>
                &copy; {datetime.datetime.now().year} 你的公司
            </p>
        </div>
    </body>
    </html>
    """
    return full_html

# --- 2. 邮件发送封装函数 (与之前相同，直接复用) ---

def send_report_email(html_content: str,
                      receiver_emails: list,
                      subject: str,
                      sender_email: str,
                      sender_password: str,
                      cc_emails: list = None,
                      smtp_server: str = 'smtp.qq.com',
                      smtp_port: int = 465,
                      use_tls: bool = False):
    """
    发送包含HTML内容的邮件。

    Args:
        html_content (str): 邮件的HTML内容。
        receiver_emails (list): 收件人邮箱地址列表。
        subject (str): 邮件主题。
        sender_email (str): 发件人邮箱地址。
        sender_password (str): 发件人邮箱的授权码。
        cc_emails (list, optional): 抄送人邮箱地址列表。默认为None。
        smtp_server (str, optional): SMTP服务器地址。默认为'smtp.qq.com'。
        smtp_port (int, optional): SMTP服务器端口。默认为465 (SSL)。
        use_tls (bool, optional): 是否使用TLS加密 (适用于587端口)。默认为False。
    """
    msg = MIMEMultipart('alternative')
    msg['From'] = Header(f'每日报告系统 <{sender_email}>', 'utf-8')
    msg['To'] = Header(','.join(receiver_emails), 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')

    if cc_emails:
        msg['Cc'] = Header(','.join(cc_emails), 'utf-8')

    # 邮件的纯文本版本
    # 尝试从HTML中解析表格并转为字符串作为纯文本
    try:
        # pd.read_html 返回一个DataFrame列表，我们取第一个表格
        tables_from_html = pd.read_html(html_content)
        text_content = "这是一封每日报告邮件，请使用支持HTML的邮件客户端查看。\n\n"
        for i, df_parsed in enumerate(tables_from_html):
            if not df_parsed.empty:
                text_content += f"--- 表格 {i+1} ---\n"
                text_content += df_parsed.to_string(index=False, header=True) + "\n\n"
    except Exception as e:
        print(f"解析HTML生成纯文本失败: {e}. 将使用默认纯文本内容。")
        text_content = "这是一封每日报告邮件，请使用支持HTML的邮件客户端查看。\n" \
                       "（纯文本内容无法完全展示复杂表格，请查看HTML版本）"

    part1 = MIMEText(text_content, 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')

    msg.attach(part1)
    msg.attach(part2)

    try:
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)

        server.login(sender_email, sender_password)

        recipients = receiver_emails + (cc_emails if cc_emails else [])
        server.sendmail(sender_email, recipients, msg.as_string())

        server.quit()
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {e.args}")

# --- 3. 主执行逻辑和定时任务（示例） ---

if __name__ == "__main__":
    # 1. 获取报告数据
    report_data = get_report_data()

    # 2. 生成完整的HTML报告内容
    full_report_html = generate_full_report_html(report_data)
    print(full_report_html)

    # --- 配置邮件发送参数 ---
    # SENDER_EMAIL = 'your_email@qq.com' # 替换为你的发件邮箱
    # SENDER_PASSWORD = 'your_authorization_code' # 替换为你的邮箱授权码
    # RECEIVER_EMAILS = ['receiver1@example.com'] # 收件人列表
    # CC_EMAILS = ['cc1@example.com'] # 抄送人列表 (可选，如果没有则设为 [] 或 None)
    # EMAIL_SUBJECT = report_data['report_title'] + ' - ' + report_data['build_date']

    # # --- 立即发送一次邮件示例 ---
    # print("--- 正在发送一次性邮件 ---")
    # send_report_email(
    #     html_content=full_report_html,
    #     receiver_emails=RECEIVER_EMAILS,
    #     subject=EMAIL_SUBJECT,
    #     sender_email=SENDER_EMAIL,
    #     sender_password=SENDER_PASSWORD,
    #     cc_emails=CC_EMAILS,
    #     smtp_server='smtp.qq.com', # 根据你的邮箱服务商调整
    #     smtp_port=465, # 根据你的邮箱服务商调整 (465 for SSL, 587 for TLS)
    #     use_tls=False # 如果是587端口，设为True
    # )

    # --- 定时任务集成（示例，需要安装 schedule 库: pip install schedule） ---
    # import schedule
    # import time
    #
    # def daily_report_job():
    #     print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 正在执行每日报告任务...")
    #     current_report_data = get_report_data() # 每次执行时获取最新数据
    #     current_full_report_html = generate_full_report_html(current_report_data)
    #     current_email_subject = current_report_data['report_title'] + ' - ' + current_report_data['build_date']
    #
    #     send_report_email(
    #         html_content=current_full_report_html,
    #         receiver_emails=RECEIVER_EMAILS,
    #         subject=current_email_subject,
    #         sender_email=SENDER_EMAIL,
    #         sender_password=SENDER_PASSWORD,
    #         cc_emails=CC_EMAILS,
    #         smtp_server='smtp.qq.com',
    #         smtp_port=465,
    #         use_tls=False
    #     )
    #
    # # 每天早上8点发送
    # # schedule.every().day.at("08:00").do(daily_report_job)
    # # 或者每隔10秒发送一次，用于测试
    # # schedule.every(10).seconds.do(daily_report_job)
    #
    # # print("定时任务已启动，等待执行...")
    # # while True:
    # #     schedule.run_pending()
    # #     time.sleep(1)