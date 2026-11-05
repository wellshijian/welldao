#!/usr/bin/env python3
"""
Automatically rebrand upstream Renly1994/xiaotang-daozai into WELL岛 (wellshijian/welldao).
Idempotent: can be run on upstream checkout or an already-rebranded checkout.
"""
import os
import re
import shutil

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Restore custom WELL icons over upstream icons
brand_ico = os.path.join(base_dir, "assets", "well-brand.ico")
brand_png = os.path.join(base_dir, "assets", "well-brand.png")
if os.path.exists(brand_ico):
    shutil.copyfile(brand_ico, os.path.join(base_dir, "assets", "daozai.ico"))
if os.path.exists(brand_png):
    shutil.copyfile(brand_png, os.path.join(base_dir, "assets", "daozai-logo.png"))

def replace_in_file(rel_path, pairs, encoding="utf-8"):
    path = os.path.join(base_dir, rel_path)
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    orig = content
    for item in pairs:
        if callable(item):
            content = item(content)
        else:
            old, new = item
            content = content.replace(old, new)
    if content != orig:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        print(f"Updated {rel_path}")

# 2. Cargo.toml
replace_in_file("Cargo.toml", [
    (lambda s: re.sub(r'(\[package\]\s+name\s*=\s*)"daozai"', r'\1"wellshijian"', s)),
    ('default-run = "daozai"', 'default-run = "wellshijian"'),
    (lambda s: re.sub(r'(\[\[bin\]\]\s+name\s*=\s*)"daozai"', r'\1"wellshijian"', s)),
    ('description = "岛仔：Windows 顶部的桌面伙伴与信息岛"', 'description = "WELL岛：Windows 顶部的桌面伙伴与信息岛"'),
    ('description = "wellshijian：Windows 顶部的桌面伙伴与信息岛"', 'description = "WELL岛：Windows 顶部的桌面伙伴与信息岛"'),
    ('Renly1994/xiaotang-daozai', 'wellshijian/welldao'),
])

# 3. app.rc
replace_in_file("app.rc", [
    ('VALUE "FileDescription", "岛仔"', 'VALUE "FileDescription", "WELL岛"'),
    ('VALUE "FileDescription", "wellshijian"', 'VALUE "FileDescription", "WELL岛"'),
    ('VALUE "InternalName", "Daozai"', 'VALUE "InternalName", "wellshijian"'),
    ('VALUE "OriginalFilename", "daozai.exe"', 'VALUE "OriginalFilename", "wellshijian.exe"'),
    ('VALUE "ProductName", "岛仔 Daozai"', 'VALUE "ProductName", "WELL岛"'),
    ('VALUE "ProductName", "wellshijian"', 'VALUE "ProductName", "WELL岛"'),
])

# 4. src/model.rs
replace_in_file("src/model.rs", [
    ('env_dir("APPDATA").join("Daozai")', 'env_dir("APPDATA").join("wellshijian")'),
])

# 5. src/tray.rs
replace_in_file("src/tray.rs", [
    ('const RUN_VALUE: PCWSTR = w!("Daozai");', 'const RUN_VALUE: PCWSTR = w!("wellshijian");'),
    ('const MUTEX_NAME: PCWSTR = w!("Local\\\\Daozai.SingleInstance");', 'const MUTEX_NAME: PCWSTR = w!("Local\\\\wellshijian.SingleInstance");'),
    ('let class = w!("DaozaiTray");', 'let class = w!("wellshijianTray");'),
    ('FindWindowW(w!("DaozaiTray")', 'FindWindowW(w!("wellshijianTray")'),
    ('w!("岛仔托盘")', 'w!("WELL岛托盘")'),
    ('w!("wellshijian托盘")', 'w!("WELL岛托盘")'),
    ('["开机启动", "吉祥物", "极简刘海", "关于岛仔", "退出", "设置…"]', '["开机启动", "吉祥物", "极简刘海", "关于 WELL岛", "退出", "设置…"]'),
    ('["开机启动", "吉祥物", "极简刘海", "关于 wellshijian", "退出", "设置…"]', '["开机启动", "吉祥物", "极简刘海", "关于 WELL岛", "退出", "设置…"]'),
    ('fill_tip(&mut nid.szTip, "岛仔");', 'fill_tip(&mut nid.szTip, "WELL岛");'),
    ('fill_tip(&mut nid.szTip, "wellshijian");', 'fill_tip(&mut nid.szTip, "WELL岛");'),
    ('"岛仔 {}\\n\\nWindows 桌面灵动岛小助手\\n退出请右键托盘图标，选择「退出」。"', '"WELL岛 {}\\n\\nWindows 桌面灵动岛小助手\\n退出请右键托盘图标，选择「退出」。"'),
    ('"wellshijian {}\\n\\nWindows 桌面灵动岛小助手\\n退出请右键托盘图标，选择「退出」。"', '"WELL岛 {}\\n\\nWindows 桌面灵动岛小助手\\n退出请右键托盘图标，选择「退出」。"'),
    ('let title = wide("关于岛仔");', 'let title = wide("关于 WELL岛");'),
    ('let title = wide("关于 wellshijian");', 'let title = wide("关于 WELL岛");'),
    ('"关于岛仔"', '"关于 WELL岛"'),
    ('"关于 wellshijian"', '"关于 WELL岛"'),
])

# 6. src/main.rs
replace_in_file("src/main.rs", [
    ('.with_title("岛仔")', '.with_title("WELL岛")'),
    ('.with_title("wellshijian")', '.with_title("WELL岛")'),
    ('eframe::run_native("岛仔", opts', 'eframe::run_native("WELL岛", opts'),
    ('eframe::run_native("wellshijian", opts', 'eframe::run_native("WELL岛", opts'),
    ('diagnostics::report("岛仔启动或运行失败。"', 'diagnostics::report("WELL岛 启动或运行失败。"'),
    ('diagnostics::report("wellshijian 启动或运行失败。"', 'diagnostics::report("WELL岛 启动或运行失败。"'),
])

# 7. src/extras.rs
replace_in_file("src/extras.rs", [
    ('with_title("岛仔设置")', 'with_title("WELL岛 设置")'),
    ('with_title("wellshijian 设置")', 'with_title("WELL岛 设置")'),
    ('setting_row(ui,"开机启动","登录 Windows 时自动打开岛仔"', 'setting_row(ui,"开机启动","登录 Windows 时自动打开 WELL岛"'),
    ('setting_row(ui,"开机启动","登录 Windows 时自动打开 wellshijian"', 'setting_row(ui,"开机启动","登录 Windows 时自动打开 WELL岛"'),
    ('c.text(42.0,116.0,"岛仔收起时常驻；极简模式保留细线"', 'c.text(42.0,116.0,"WELL岛 收起时常驻；极简模式保留细线"'),
    ('c.text(42.0,116.0,"wellshijian 收起时常驻；极简模式保留细线"', 'c.text(42.0,116.0,"WELL岛 收起时常驻；极简模式保留细线"'),
    ('setting_row(ui,"岛仔吉祥物"', 'setting_row(ui,"WELL岛吉祥物"'),
    ('setting_row(ui,"岛仔提醒"', 'setting_row(ui,"WELL岛提醒"'),
    ('settings_label(ui,"岛仔 Daozai");', 'settings_label(ui,"WELL岛");'),
    ('settings_label(ui,"wellshijian");', 'settings_label(ui,"WELL岛");'),
])

# 8. src/app.rs
replace_in_file("src/app.rs", [
    ('_ => ("岛仔", "设置", theme::WHITE),', '_ => ("WELL岛", "设置", theme::WHITE),'),
    ('_ => ("wellshijian", "设置", theme::WHITE),', '_ => ("WELL岛", "设置", theme::WHITE),'),
])

# 9. src/mail.rs, calendar.rs, grok_quota.rs, lyrics.rs, diagnostics.rs, system.rs, mail_reader.rs
replace_in_file("src/mail.rs", [
    ('pub const SERVICE: &str = "Daozai.Mail";', 'pub const SERVICE: &str = "wellshijian.Mail";'),
    ('输入应用名称（例如：岛仔）', '输入应用名称（例如：WELL岛）'),
    ('输入应用名称（例如：wellshijian）', '输入应用名称（例如：WELL岛）'),
])
replace_in_file("src/calendar.rs", [
    ('pub const SERVICE: &str = "Daozai.Calendar";', 'pub const SERVICE: &str = "wellshijian.Calendar";'),
    ('concat!("Daozai/",env!("CARGO_PKG_VERSION"))', 'concat!("wellshijian/",env!("CARGO_PKG_VERSION"))'),
])
replace_in_file("src/grok_quota.rs", [
    ('keyring::Entry::new("Daozai.GrokBot",slot)', 'keyring::Entry::new("wellshijian.GrokBot",slot)'),
])
replace_in_file("src/lyrics.rs", [
    ('concat!("Daozai/",env!("CARGO_PKG_VERSION")," (Windows)")', 'concat!("wellshijian/",env!("CARGO_PKG_VERSION")," (Windows)")'),
])
replace_in_file("src/diagnostics.rs", [
    ('"岛仔 {}\\n系统：{} / {}\\n时间（Unix 秒）：{timestamp}\\n{title}\\n{details}\\n"', '"WELL岛 {}\\n系统：{} / {}\\n时间（Unix 秒）：{timestamp}\\n{title}\\n{details}\\n"'),
    ('"wellshijian {}\\n系统：{} / {}\\n时间（Unix 秒）：{timestamp}\\n{title}\\n{details}\\n"', '"WELL岛 {}\\n系统：{} / {}\\n时间（Unix 秒）：{timestamp}\\n{title}\\n{details}\\n"'),
    ('w!("岛仔")', 'w!("WELL岛")'),
    ('w!("wellshijian")', 'w!("WELL岛")'),
    ('report("岛仔发生异常，请重新启动。"', 'report("WELL岛 发生异常，请重新启动。"'),
    ('report("wellshijian 发生异常，请重新启动。"', 'report("WELL岛 发生异常，请重新启动。"'),
])
replace_in_file("src/system.rs", [
    ('if app != "岛仔" && !body.is_empty() {', 'if app != "WELL岛" && !body.is_empty() {'),
    ('if app != "wellshijian" && !body.is_empty() {', 'if app != "WELL岛" && !body.is_empty() {'),
])
replace_in_file("src/mail_reader.rs", [
    ('.with_title("邮件全文 · 岛仔")', '.with_title("邮件全文 · WELL岛")'),
    ('.with_title("邮件全文 · wellshijian")', '.with_title("邮件全文 · WELL岛")'),
])

# 10. src/updates.rs
replace_in_file("src/updates.rs", [
    ('Renly1994/xiaotang-daozai', 'wellshijian/welldao'),
    ('.with_title("岛仔更新")', '.with_title("WELL岛 更新")'),
    ('.with_title("wellshijian 更新")', '.with_title("WELL岛 更新")'),
    ('"岛仔有新版本了"', '"WELL岛 有新版本了"'),
    ('"wellshijian 有新版本了"', '"WELL岛 有新版本了"'),
    ('!= "岛仔更新"', '!= "WELL岛 更新"'),
    ('!= "wellshijian 更新"', '!= "WELL岛 更新"'),
    ('.join("Daozai/Updates")', '.join("wellshijian/Updates")'),
    ('let name = format!("Daozai-v{}-windows-x64.zip", tag.trim_start_matches(\'v\'));', 'let name = "wellshijian-portable.zip".to_string();'),
])

# 11. installer/update.ps1, setup.nsi, install.ps1, uninstall.ps1
replace_in_file("installer/update.ps1", [
    ("Join-Path $env:LOCALAPPDATA 'Daozai\\Updates'", "Join-Path $env:LOCALAPPDATA 'wellshijian\\Updates'"),
    ("'daozai-update-'", "'wellshijian-update-'"),
    ("$name = 'Daozai-v' + $version + '-windows-x64/daozai.exe'\n        $entries = @($zip.Entries | Where-Object {$_.FullName.Replace('\\','/') -ceq $name})", "$entries = @($zip.Entries | Where-Object {$_.Name -ieq 'wellshijian.exe'})"),
    ("throw '更新包中缺少唯一的岛仔程序。'", "throw '更新包中缺少唯一的 WELL岛 程序。'"),
    ("throw '岛仔尚未退出，请稍后重试。'", "throw 'WELL岛 尚未退出，请稍后重试。'"),
    ("$key = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Daozai'", "$key = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\wellshijian'"),
    ("'岛仔更新'", "'WELL岛 更新'"),
])

replace_in_file("installer/setup.nsi", [
    ('!define APP_ID "Daozai"', '!define APP_ID "wellshijian"'),
    ('!define APP_NAME "岛仔"', '!define APP_NAME "WELL岛"'),
    ('!define APP_NAME "wellshijian"', '!define APP_NAME "WELL岛"'),
    ('VIAddVersionKey /LANG=2052 "LegalCopyright" "岛仔贡献者"', 'VIAddVersionKey /LANG=2052 "LegalCopyright" "WELL岛"'),
    ('VIAddVersionKey /LANG=2052 "LegalCopyright" "wellshijian"', 'VIAddVersionKey /LANG=2052 "LegalCopyright" "WELL岛"'),
    ('!define MUI_FINISHPAGE_TITLE "岛仔已安装"', '!define MUI_FINISHPAGE_TITLE "WELL岛 已安装"'),
    ('!define MUI_FINISHPAGE_TITLE "wellshijian 已安装"', '!define MUI_FINISHPAGE_TITLE "WELL岛 已安装"'),
    ('!define MUI_FINISHPAGE_RUN "$INSTDIR\\daozai.exe"', '!define MUI_FINISHPAGE_RUN "$INSTDIR\\wellshijian.exe"'),
    ('!define MUI_FINISHPAGE_RUN_TEXT "打开岛仔"', '!define MUI_FINISHPAGE_RUN_TEXT "打开 WELL岛"'),
    ('!define MUI_FINISHPAGE_RUN_TEXT "打开 wellshijian"', '!define MUI_FINISHPAGE_RUN_TEXT "打开 WELL岛"'),
    ('!define MUI_UNCONFIRMPAGE_TEXT_TOP "将卸载岛仔。设置、待办和连接记录会保留，重新安装后仍可使用。"', '!define MUI_UNCONFIRMPAGE_TEXT_TOP "将卸载 WELL岛。设置、待办和连接记录会保留，重新安装后仍可使用。"'),
    ('!define MUI_UNCONFIRMPAGE_TEXT_TOP "将卸载 wellshijian。设置、待办和连接记录会保留，重新安装后仍可使用。"', '!define MUI_UNCONFIRMPAGE_TEXT_TOP "将卸载 WELL岛。设置、待办和连接记录会保留，重新安装后仍可使用。"'),
    ('BrandingText "岛仔 · Daozai"', 'BrandingText "WELL岛"'),
    ('BrandingText "wellshijian"', 'BrandingText "WELL岛"'),
    ('"欢迎使用岛仔"', '"欢迎使用 WELL岛"'),
    ('"欢迎使用 wellshijian"', '"欢迎使用 WELL岛"'),
    ('"选择岛仔安装文件夹"', '"选择 WELL岛 安装文件夹"'),
    ('"选择 wellshijian 安装文件夹"', '"选择 WELL岛 安装文件夹"'),
    ('"岛仔需要 Windows 10 或 Windows 11 的 64 位系统。"', '"WELL岛 需要 Windows 10 或 Windows 11 的 64 位系统。"'),
    ('"wellshijian 需要 Windows 10 或 Windows 11 的 64 位系统。"', '"WELL岛 需要 Windows 10 或 Windows 11 的 64 位系统。"'),
    ('"岛仔需要 Windows 10 或 Windows 11。"', '"WELL岛 需要 Windows 10 或 Windows 11。"'),
    ('"wellshijian 需要 Windows 10 或 Windows 11。"', '"WELL岛 需要 Windows 10 或 Windows 11。"'),
    ('File /oname=daozai.exe "${SOURCE_EXE}"', 'File /oname=wellshijian.exe "${SOURCE_EXE}"'),
    ('CreateShortcut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\daozai.exe"', 'CreateShortcut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\wellshijian.exe"'),
    ('WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APP_ID}" \'"$INSTDIR\\daozai.exe"\'', 'WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APP_ID}" \'"$INSTDIR\\wellshijian.exe"\''),
    ('CreateShortcut "$SMPROGRAMS\\${APP_NAME}.lnk" "$INSTDIR\\daozai.exe"', 'CreateShortcut "$SMPROGRAMS\\${APP_NAME}.lnk" "$INSTDIR\\wellshijian.exe"'),
    ('CreateShortcut "$SMPROGRAMS\\${APP_NAME}设置.lnk" "$INSTDIR\\daozai.exe" "--settings"', 'CreateShortcut "$SMPROGRAMS\\${APP_NAME}设置.lnk" "$INSTDIR\\wellshijian.exe" "--settings"'),
    ('WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "${APP_NAME} Daozai"', 'WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"'),
    ('WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "岛仔"', 'WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "WELL岛"'),
    ('WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "wellshijian"', 'WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "WELL岛"'),
    ('WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\\daozai.exe,0"', 'WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\\wellshijian.exe,0"'),
    ('Delete "$INSTDIR\\daozai.exe"', 'Delete "$INSTDIR\\wellshijian.exe"'),
    ('Delete "$INSTDIR\\daozai-previous.exe"', 'Delete "$INSTDIR\\wellshijian-previous.exe"'),
    ('ReadRegStr $0 HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APP_ID}"\n  ${If} $0 == \'"$INSTDIR\\daozai.exe"\'', 'ReadRegStr $0 HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APP_ID}"\n  ${If} $0 == \'"$INSTDIR\\wellshijian.exe"\''),
])

print("rebrand_welldao.py finished successfully.")
